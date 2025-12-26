"""
CLI Aprimorada - Codex Operator
================================

Interface de linha de comando com múltiplos modos:
- demo: executar demonstrações comerciais
- test: rodar testes de workflows
- workflow: executar workflows específicos
- agent: rodar agente genérico
"""

import sys
import argparse
import json

from src.utils.logging_utils import get_logger
from src.workflows import instagram_lead_express, lead_qualificacao
from src.agents import site_agent

logger = get_logger(__name__)


def cmd_demo(args) -> int:
    """Executa uma demonstração comercial."""

    demo_name = args.demo or "all"

    demos = {
        "instagram": {
            "nome": "Instagram Lead Express",
            "descricao": "Automacao de acesso ao painel de login do Instagram",
            "funcao": instagram_lead_express.executar_lead_express,
        },
        "qualificacao": {
            "nome": "Lead Qualificacao Automatica",
            "descricao": "Classificacao de leads com IA (Quente/Morno/Frio)",
            "funcao": lambda: demo_qualificacao_lead(),
        },
    }

    if demo_name == "all":
        print("\n" + "=" * 70)
        print("DEMOS DISPONIVEIS".center(70))
        print("=" * 70)
        for key, info in demos.items():
            print(f"\n{key.upper()}")
            print(f"  Nome: {info['nome']}")
            print(f"  Descricao: {info['descricao']}")

        print("\n" + "=" * 70)
        print("Para rodar uma demo especifica, use:")
        print("  python -m src.cli demo --demo instagram")
        print("  python -m src.cli demo --demo qualificacao")
        print("=" * 70 + "\n")
        return 0

    if demo_name not in demos:
        logger.error(f"Demo '{demo_name}' nao encontrada.")
        return 1

    print("\n" + "=" * 70)
    print(f"INICIANDO DEMO: {demos[demo_name]['nome']}".center(70))
    print("=" * 70 + "\n")

    try:
        resultado = demos[demo_name]["funcao"]()

        print("\n" + "=" * 70)
        print("RESULTADO".center(70))
        print("=" * 70)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        print("=" * 70 + "\n")

        return 0
    except Exception as exc:
        logger.exception(f"Erro ao executar demo '{demo_name}': {exc}")
        return 1


def cmd_test(args) -> int:
    """Executa testes dos workflows."""

    print("\n" + "=" * 70)
    print("SUITE DE TESTES - Workflows".center(70))
    print("=" * 70 + "\n")

    tests = [
        ("Teste 1: Importacao de modulos", teste_importacao),
        ("Teste 2: Qualificacao de lead", teste_qualificacao),
        ("Teste 3: Config carregamento", teste_config),
    ]

    resultados = []
    for nome, func in tests:
        try:
            print(f"[EXECUTANDO] {nome}...", end=" ")
            sucesso = func()
            status = "OK" if sucesso else "FALHOU"
            print(f"[{status}]")
            resultados.append((nome, sucesso))
        except Exception as exc:
            print(f"[ERRO: {exc}]")
            resultados.append((nome, False))

    print("\n" + "=" * 70)
    print("RESUMO DE TESTES".center(70))
    print("=" * 70)

    sucessos = sum(1 for _, ok in resultados if ok)
    total = len(resultados)

    for nome, ok in resultados:
        status = "PASSOU" if ok else "FALHOU"
        print(f"{nome:50} [{status}]")

    print(f"\nTotal: {sucessos}/{total} testes passaram")
    print("=" * 70 + "\n")

    return 0 if sucessos == total else 1


def cmd_workflow(args) -> int:
    """Executa um workflow especifico."""

    workflow_name = args.workflow
    workflows = {
        "instagram_lead_express": instagram_lead_express.executar_lead_express,
    }

    if workflow_name not in workflows:
        logger.error(f"Workflow '{workflow_name}' nao encontrado.")
        print("\nWorkflows disponiveis:")
        for name in workflows.keys():
            print(f"  - {name}")
        return 1

    print(f"\n[EXECUTANDO] Workflow: {workflow_name}\n")

    try:
        resultado = workflows[workflow_name]()
        print(f"\n[SUCESSO] {resultado.get('mensagem', 'Workflow completado')}")
        return 0
    except Exception as exc:
        logger.exception(f"Erro ao executar workflow: {exc}")
        return 1


def cmd_agent(args) -> int:
    """Executa o agente generico."""

    site = args.site
    objetivo = args.objetivo

    print(f"\n[AGENTE] Site: {site} | Objetivo: {objetivo}\n")

    try:
        plano = site_agent.planejar(site, objetivo)
        print(f"\n[PLANO GERADO] {len(plano.get('steps', []))} passos")
        print(json.dumps(plano, indent=2, ensure_ascii=False))

        print("\n[EXECUTANDO PLANO]")
        site_agent.executar_plano(site, plano)

        print("\n[SUCESSO] Plano executado com sucesso!")
        return 0
    except Exception as exc:
        logger.exception(f"Erro ao executar agente: {exc}")
        return 1


# ============================================================================
# TESTES AUXILIARES
# ============================================================================


def teste_importacao() -> bool:
    """Testa se todos os modulos importam corretamente."""
    try:
        return True
    except Exception as exc:
        logger.error(f"Erro ao importar: {exc}")
        return False


def teste_qualificacao() -> bool:
    """Testa qualificacao de lead."""
    try:
        lead_teste = {
            "nome": "Teste",
            "interesse": "Alto",
            "orcamento": "Definido",
            "prazo": "15 dias",
        }
        resultado = lead_qualificacao.qualificar_lead(lead_teste)
        return "classificacao" in resultado and resultado["classificacao"] in [
            "Quente",
            "Morno",
            "Frio",
        ]
    except Exception as exc:
        logger.error(f"Erro no teste de qualificacao: {exc}")
        return False


def teste_config() -> bool:
    """Testa carregamento de config de site."""
    try:
        from src.utils import config_loader

        config = config_loader.carregar_config_site("instagram")
        return isinstance(config, dict) and len(config) > 0
    except Exception as exc:
        logger.error(f"Erro ao carregar config: {exc}")
        return False


def demo_qualificacao_lead() -> dict:
    """Demo de qualificacao de lead."""
    exemplo_lead = {
        "nome": "Carlos Silva",
        "email": "carlos@email.com",
        "interesse": "Venda de imovel comercial",
        "orcamento": "R$ 2.000.000",
        "prazo": "Precisa vender em 10 dias",
        "tipo_propriedade": "Sala comercial 300m2",
        "localizacao": "Centro da cidade",
    }

    resultado = lead_qualificacao.qualificar_lead(
        exemplo_lead, contexto_nicho="Imobiliaria comercial premium"
    )

    return {
        "status": "sucesso",
        "lead": exemplo_lead,
        "qualificacao": resultado,
    }


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Ponto de entrada da CLI."""

    parser = argparse.ArgumentParser(
        description="Codex Operator - Agencia de Automacao com IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Ver todas as demos disponiveis
  python -m src.cli demo

  # Rodar demo de Instagram
  python -m src.cli demo --demo instagram

  # Rodar testes
  python -m src.cli test

  # Rodar workflow especifico
  python -m src.cli workflow --workflow instagram_lead_express

  # Rodar agente generico
  python -m src.cli agent --site instagram --objetivo "abrir login e clicar em usuario"
        """,
    )

    subparsers = parser.add_subparsers(dest="comando", help="Comando a executar")

    # Subcomando: demo
    parser_demo = subparsers.add_parser("demo", help="Executar demonstracao comercial")
    parser_demo.add_argument(
        "--demo",
        type=str,
        default="all",
        help="Nome da demo (instagram, qualificacao, ou 'all' para listar)",
    )
    parser_demo.set_defaults(func=cmd_demo)

    # Subcomando: test
    parser_test = subparsers.add_parser("test", help="Rodar testes dos workflows")
    parser_test.set_defaults(func=cmd_test)

    # Subcomando: workflow
    parser_workflow = subparsers.add_parser(
        "workflow", help="Executar workflow especifico"
    )
    parser_workflow.add_argument(
        "--workflow",
        type=str,
        required=True,
        help="Nome do workflow (instagram_lead_express, etc)",
    )
    parser_workflow.set_defaults(func=cmd_workflow)

    # Subcomando: agent
    parser_agent = subparsers.add_parser("agent", help="Executar agente generico")
    parser_agent.add_argument(
        "--site", type=str, required=True, help="Site alvo (instagram, etc)"
    )
    parser_agent.add_argument(
        "--objetivo", type=str, required=True, help="Objetivo da automacao"
    )
    parser_agent.set_defaults(func=cmd_agent)

    # Parse args
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n[CANCELADO] Execucao interrompida pelo usuario.")
        return 130
    except Exception as exc:
        logger.exception(f"Erro nao tratado: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
