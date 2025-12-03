"""CLI simples para orquestrar planejamento e execução de automações com Priority Queue.

Versão v1.0: Integração de fila de prioridades (Min-Heap) para processamento eficiente
de tarefas baseado em urgência, deadline e custo computacional.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

from src.agents import site_agent
from src.agents import nf_agent
from src.core.agent_queue import AgentQueue, TaskPriority, create_deadline
from src.utils.logging_utils import get_logger
from src.utils.formatting_utils import clean_markdown

logger = get_logger("orchestrator")

# Instância global da fila de tarefas
_TASK_QUEUE = None


def get_task_queue(max_size: int = 1000) -> AgentQueue:
    """Obtém ou cria a instância global da fila de tarefas.
    
    Args:
        max_size: Tamanho máximo da fila (padrão: 1000).
    
    Returns:
        AgentQueue configurada.
    """
    global _TASK_QUEUE
    if _TASK_QUEUE is None:
        _TASK_QUEUE = AgentQueue(max_size=max_size)
        logger.info("Task queue inicializada com max_size=%d", max_size)
    return _TASK_QUEUE


# Lembrar: respeite sempre os Termos de Uso do serviço alvo antes de rodar automações.


def _handle_queue_stats() -> int:
    """Exibe estatísticas da fila."""
    queue = get_task_queue()
    print("\n" + queue.print_stats())
    return 0


def _handle_queue_list() -> int:
    """Lista todas as tarefas na fila."""
    queue = get_task_queue()
    tasks = queue.get_all_tasks()
    
    if not tasks:
        print("Fila vazia.")
        return 0
    
    print(f"\n{'ID':<12} {'PRIORITY':<10} {'AGENT':<20} {'CLIENT':<15} {'DEADLINE':<20} {'COST':<6}")
    print("-" * 83)
    
    for task in tasks:
        deadline_str = datetime.fromtimestamp(task.deadline).strftime("%Y-%m-%d %H:%M")
        print(f"{task.task_id:<12} {task.priority:<10} {task.agent_name:<20} {task.client_id:<15} {deadline_str:<20} {task.cost:<6}")
    
    print(f"\nTotal: {len(tasks)} tarefas")
    return 0


def _handle_queue_clear() -> int:
    """Limpa a fila."""
    queue = get_task_queue()
    size_before = queue.size()
    queue.clear()
    logger.info("Fila limpa. Tarefas removidas: %d", size_before)
    print(f"✓ Fila limpa ({size_before} tarefas removidas)")
    return 0


def _handle_queue_process(count: int) -> int:
    """Processa N tarefas da fila sequencialmente."""
    queue = get_task_queue()
    
    if queue.is_empty():
        print("Fila vazia. Nada a processar.")
        return 0
    
    processed = 0
    for i in range(count):
        task = queue.pop()
        if task is None:
            break
        
        processed += 1
        overdue_marker = " [OVERDUE]" if task.is_overdue() else ""
        print(f"[{i+1}] Processando: {task.agent_name} (client: {task.client_id}, priority: {task.priority}){overdue_marker}")
        logger.info("Task processed: task_id=%s, agent=%s, client=%s", task.task_id, task.agent_name, task.client_id)
    
    print(f"\n✓ {processed} tarefa(s) processada(s)")
    return 0


def _handle_queue_push(args) -> int:
    """Adiciona tarefa manualmente à fila."""
    queue = get_task_queue()
    
    try:
        deadline = create_deadline(days_ahead=args.days)
        payload = {}
        if args.payload:
            payload = json.loads(args.payload)
        
        task_id = queue.push(
            priority=args.priority,
            deadline=deadline,
            cost=args.cost,
            agent_name=args.agent,
            client_id=args.client,
            payload=payload,
        )
        
        if task_id is None:
            print("✗ Erro: Fila cheia. Aumente max_size ou processe tarefas.")
            return 1
        
        print(f"✓ Tarefa adicionada: {task_id}")
        print(f"  Agent: {args.agent}")
        print(f"  Client: {args.client}")
        print(f"  Priority: {args.priority}")
        print(f"  Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Cost: {args.cost}")
        
        return 0
    except json.JSONDecodeError:
        logger.exception("Erro ao decodificar payload JSON")
        print("✗ Erro: Payload JSON inválido")
        return 1
    except ValueError as e:
        logger.exception("Erro ao criar tarefa: %s", e)
        print(f"✗ Erro: {e}")
        return 1

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Orquestrador de automações com Priority Queue")
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
    nf_parser.add_argument("--create-event", action="store_true", help="(Opcional) Criar evento no Google Calendar para a emissão da nota")
    nf_parser.add_argument("--send-email", action="store_true", help="(Opcional) Enviar notificação por email ao cliente")
    nf_parser.add_argument("--send-gmail", action="store_true", help="(Opcional) Enviar notificação via Gmail API ao cliente")
    nf_parser.add_argument("--save-output", help="(Opcional) Salvar resultado em JSON")

    # Novo: queue management
    queue_parser = subparsers.add_parser("queue", help="Gerenciar fila de tarefas")
    queue_subparsers = queue_parser.add_subparsers(dest="queue_cmd", required=True)

    queue_subparsers.add_parser("stats", help="Mostrar estatísticas da fila")
    queue_subparsers.add_parser("list", help="Listar todas as tarefas na fila")
    
    queue_subparsers.add_parser("clear", help="Limpar todas as tarefas da fila")
    
    process_parser = queue_subparsers.add_parser("process", help="Processar N tarefas da fila")
    process_parser.add_argument("--count", type=int, default=1, help="Número de tarefas a processar (padrão: 1)")
    
    push_parser = queue_subparsers.add_parser("push", help="Adicionar tarefa manualmente à fila")
    push_parser.add_argument("--agent", required=True, help="Nome do agente (ex: nf_agent)")
    push_parser.add_argument("--client", required=True, help="ID do cliente")
    push_parser.add_argument("--priority", type=int, choices=[1,2,3,4,5], default=3, help="Prioridade: 1=CRITICAL, 5=DEFERRED (padrão: 3=MEDIUM)")
    push_parser.add_argument("--days", type=int, default=1, help="Dias até deadline (padrão: 1)")
    push_parser.add_argument("--cost", type=int, default=1, help="Custo computacional (padrão: 1)")
    push_parser.add_argument("--payload", help="Payload JSON (opcional)")

    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    # Novo: Comandos de gerenciamento de fila
    if args.comando == "queue":
        if args.queue_cmd == "stats":
            return _handle_queue_stats()
        elif args.queue_cmd == "list":
            return _handle_queue_list()
        elif args.queue_cmd == "clear":
            return _handle_queue_clear()
        elif args.queue_cmd == "process":
            return _handle_queue_process(args.count)
        elif args.queue_cmd == "push":
            return _handle_queue_push(args)
        else:
            logger.error("Comando de fila desconhecido: %s", args.queue_cmd)
            return 1

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
                        # Limpar Markdown para melhor apresentação no WhatsApp
                        msg_body = clean_markdown(out["explicacao"])
                        ws_result = send_nf_notification(send_whatsapp, client_name, float(amount), msg_body)
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
                        # Limpar Markdown para melhor apresentação no Telegram
                        msg_body = clean_markdown(out["explicacao"])
                        tg_result = send_nf_telegram(send_telegram, client_name, float(amount), msg_body)
                        logger.info("Mensagem Telegram enviada: %s", tg_result)
                    except Exception as tg_err:
                        logger.exception("Falha ao enviar Telegram: %s", tg_err)

                # Criar evento no Google Calendar se solicitado
                if getattr(args, "create_event", False):
                    try:
                        from src.integrations.google_calendar import GoogleCalendarAPI

                        gc = GoogleCalendarAPI()
                        gc_result = gc.create_event_from_sale(sale)
                        logger.info("Google Calendar result: %s", gc_result)
                    except Exception as gc_err:
                        logger.exception("Falha ao criar evento no Google Calendar: %s", gc_err)

                # Enviar email se solicitado
                if getattr(args, "send_email", False):
                    try:
                        from src.integrations.email_api import EmailAPI

                        email_api = EmailAPI()
                        # tenta obter email do cliente (client_email ou email)
                        recipient = sale.get("client_email") or sale.get("email")
                        if not recipient:
                            logger.warning("Venda não contém email do cliente; pulando envio de email: %s", sale)
                        else:
                            subj = f"Instruções para emissão da NFS-e — {sale.get('id', '')}"
                            # Limpar Markdown da explicação para ficar legível no email
                            body = clean_markdown(out.get("explicacao", ""))
                            em_result = email_api.send_email([recipient], subj, body)
                            logger.info("Resultado envio email: %s", em_result)
                    except Exception as em_err:
                        logger.exception("Falha ao enviar email: %s", em_err)

                # Enviar via Gmail API se solicitado
                if getattr(args, "send_gmail", False):
                    try:
                        from src.integrations.gmail_api import GmailAPI

                        gmail = GmailAPI()
                        gm_result = gmail.send_message_from_sale(sale)
                        logger.info("Resultado envio Gmail: %s", gm_result)
                    except Exception as gm_err:
                        logger.exception("Falha ao enviar via Gmail API: %s", gm_err)

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
