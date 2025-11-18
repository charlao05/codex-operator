"""CLI simples para orquestrar planejamento e execução de automações."""

from __future__ import annotations

import argparse
import json
import sys

from src.agents import site_agent
from src.agents import nf_agent
from src.utils.logging_utils import get_logger

logger = get_logger("orchestrator")


# Lembrar: respeite sempre os Termos de Uso do serviço alvo antes de rodar automações.

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Orquestrador de automações")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    executar_parser = subparsers.add_parser("executar", help="Planeja e executa um objetivo")
    executar_parser.add_argument("--site", required=True, help="Nome do site em config/sites.yaml")
    executar_parser.add_argument("--objetivo", required=True, help="Objetivo em texto livre")
    executar_parser.add_argument("--dry-run", action="store_true", help="Gera o plano mas NÃO executa o navegador (safe)")
    executar_parser.add_argument("--save-plan", help="Caminho para salvar o plano gerado como JSON")

    nf_parser = subparsers.add_parser("nf", help="Gerar instruções para emissão de nota fiscal a partir de arquivo de vendas")
    nf_parser.add_argument("--sales-file", required=True, help="Caminho para o arquivo JSON contendo a venda ou lista de vendas")
    nf_parser.add_argument("--send-whatsapp", help="(Opcional) Enviar mensagem via WhatsApp para este número (+55 DDD NNNNNNNNN)")
    nf_parser.add_argument("--send-telegram", help="(Opcional) Enviar mensagem via Telegram para este chat_id")
    nf_parser.add_argument("--save-output", help="(Opcional) Salvar resultado em JSON")

    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if args.comando == "executar":
        site = args.site
        objetivo = args.objetivo
        logger.info("Recebido comando executar | site=%s | objetivo=%s", site, objetivo)
        try:
            plano = site_agent.planejar(site, objetivo)
            logger.info("Plano gerado:\n%s", json.dumps(plano, ensure_ascii=False, indent=2))

            if getattr(args, "save_plan", None):
                try:
                    with open(args.save_plan, "w", encoding="utf-8") as f:
                        json.dump(plano, f, ensure_ascii=False, indent=2)
                    logger.info("Plano salvo em %s", args.save_plan)
                except Exception:
                    logger.exception("Falha ao salvar o plano em %s", args.save_plan)

            if args.dry_run:
                logger.info("Dry-run habilitado — não executando o navegador.")
                return 0

            site_agent.executar_plano(site, plano)
            return 0
        except Exception as exc:  # noqa: BLE001
            logger.exception("Falha ao executar automação: %s", exc)
            return 1

    if args.comando == "nf":
        sales_file = getattr(args, "sales_file", None)
        if not sales_file:
            logger.error("Parâmetro --sales-file é obrigatório para o comando 'nf'.")
            return 1

        try:
            data = nf_agent.load_sales(sales_file)
        except ValueError as exc:
            logger.exception("Arquivo de vendas inválido: %s", exc)
            return 1

        if data is None:
            logger.error("Arquivo de vendas não encontrado ou vazio: %s", sales_file)
            return 1

        # Se o JSON contém uma lista de vendas, processa todas; se for um único objeto, processa apenas ele
        sales = data if isinstance(data, list) else [data]
        results = []
        for sale in sales:
            try:
                out = nf_agent.prepare_invoice_steps(sale)
                results.append(out)
                logger.info("Resultado para venda: %s", json.dumps(out, ensure_ascii=False, indent=2))

                # Enviar via WhatsApp se --send-whatsapp foi fornecido
                send_whatsapp = getattr(args, "send_whatsapp", None)
                if send_whatsapp:
                    try:
                        from src.integrations.whatsapp_api import send_nf_notification
                        client_name = sale.get("client_name", sale.get("cliente_nome", "Cliente"))
                        amount = sale.get("amount", sale.get("valor_total", 0.0))
                        ws_result = send_nf_notification(send_whatsapp, client_name, float(amount), out["explicacao"])
                        logger.info("Mensagem WhatsApp enviada: %s", ws_result)
                    except Exception as ws_err:
                        logger.exception("Falha ao enviar WhatsApp: %s", ws_err)

                # Enviar via Telegram se --send-telegram foi fornecido
                send_telegram = getattr(args, "send_telegram", None)
                if send_telegram:
                    try:
                        from src.integrations.telegram_api import send_nf_notification as send_nf_telegram
                        client_name = sale.get("client_name", sale.get("cliente_nome", "Cliente"))
                        amount = sale.get("amount", sale.get("valor_total", 0.0))
                        tg_result = send_nf_telegram(send_telegram, client_name, float(amount), out["explicacao"])
                        logger.info("Mensagem Telegram enviada: %s", tg_result)
                    except Exception as tg_err:
                        logger.exception("Falha ao enviar Telegram: %s", tg_err)

            except Exception:
                logger.exception("Falha ao processar registro de venda: %s", sale)

        # Salvar em arquivo se --save-output foi fornecido
        save_output = getattr(args, "save_output", None)
        if save_output:
            try:
                with open(save_output, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                logger.info("Resultado salvo em %s", save_output)
            except Exception as save_err:
                logger.exception("Falha ao salvar resultado em %s: %s", save_output, save_err)

        # Saída final: imprime JSON agregando resultados
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    logger.error("Comando desconhecido: %s", args.comando)
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
