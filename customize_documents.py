#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para customizar automaticamente os 5 documentos compliance.
Lê CUSTOMIZATION_VALUES.md e substitui todos os placeholders nos documentos.
"""

import re
import os
from typing import Any

# ============================================================================
# CONFIGURACAO
# ============================================================================

CUSTOMIZATION_FILE = "c:/Users/Charles/Desktop/codex-operator/CUSTOMIZATION_VALUES.md"

SOURCE_DOCUMENTS = {
    "DEPLOY_STANDARDS": "c:/Users/Charles/Downloads/DEPLOY_STANDARDS.md",
    "GO_LIVE_CHECKLIST": "c:/Users/Charles/Downloads/GO_LIVE_CHECKLIST.md",
    "SECURITY_COMPLIANCE_MATRIX": "c:/Users/Charles/Downloads/SECURITY_COMPLIANCE_MATRIX.md",
    "INCIDENT_RESPONSE_PLAYBOOK": "c:/Users/Charles/Downloads/INCIDENT_RESPONSE_PLAYBOOK.md",
    "MONITORING_ALERTING_RUNBOOK": "c:/Users/Charles/Downloads/MONITORING_ALERTING_RUNBOOK.md",
}

OUTPUT_DIR = "c:/Users/Charles/Desktop/codex-operator/DOCUMENTOS_FINALIZADOS"

# Mapeamento de placeholders → chaves de customização
PLACEHOLDER_MAP = {
    # Informações da empresa
    "[Seu nome aqui - quem faz o triage?]": "company.incident_commander.name",
    "[seu-email]": "company.incident_commander.email",
    "[Seu representante na EU]": "company.eu_representative",

    # URLs e Links
    "[link para runbook]": "links.incident_response_playbook",
    "[link para acesso]": "links.gcp_monitoring_dashboard",
    "[link para runbooks]": "links.runbooks_github",
    "[link to IRP]": "links.incident_response_playbook",
    "[link to dashboard]": "links.gcp_monitoring_dashboard",
    "[calendar link]": "links.oncall_calendar",

    # Contatos
    "[name, phone, email]": "contacts.incident_commander_full",
    "[backup name]": "contacts.backup_name",
    "[ANPD contact]": "contacts.anpd",
    "[email list]": "contacts.alert_recipients",

    # URLs de produção
    "[primary-email@domain.com]": "production.google_play_email",
    "https://nexus.app/privacy": "production.privacy_policy_url",
    "https://nexus.app/terms": "production.terms_url",
    "[email]": "production.support_email",
}

# ============================================================================
# FUNCOES
# ============================================================================


def parse_customization_file(file_path: str) -> dict[str, Any]:
    """
    Parse do arquivo CUSTOMIZATION_VALUES.md e extrai valores.
    Retorna dicionário com todos os valores de customização.
    """
    values: dict[str, Any] = {
        "company": {},
        "team": {},
        "links": {},
        "contacts": {},
        "production": {},
        "custom": {}
    }

    if not os.path.exists(file_path):
        print(f"❌ ERRO: Arquivo não encontrado: {file_path}")
        print("   Execute o TEMPLATE_CUSTOMIZACAO.md primeiro!")
        return values

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extrair valores do markdown
        # Padrão: "Nome": "Seu nome aqui - quem faz o triage?"
        # ou: Nome: [Seu nome aqui]

        # Extrair nome da empresa
        match = re.search(r"Nome Legal:\s*([^\n]+)", content)
        if match:
            values["company"]["name"] = match.group(1).strip()

        # Extrair CNPJ
        match = re.search(r"CNPJ:\s*([^\n]+)", content)
        if match:
            values["company"]["cnpj"] = match.group(1).strip()

        # Extrair Incident Commander
        match = re.search(r"Incident Commander:\s*([^\n]+)", content)
        if match:
            ic_info = match.group(1).strip()
            values["company"]["incident_commander"] = {"name": ic_info}

        # Extrair email do IC
        match = re.search(r"Email do IC:\s*([^\n]+)", content)
        if match:
            email = match.group(1).strip()
            if "incident_commander" in values["company"]:
                values["company"]["incident_commander"]["email"] = email

        # Extrair URLs de produção
        match = re.search(r"## URLs de Produção(.*?)##", content, re.DOTALL)
        if match:
            urls_section = match.group(1)
            prod_email = re.search(r"Email Google Play:\s*([^\n]+)", urls_section)
            if prod_email:
                values["production"]["google_play_email"] = prod_email.group(1).strip()

        # Extrair links
        match = re.search(r"## Links Importantes(.*?)##", content, re.DOTALL)
        if match:
            links_section = match.group(1)
            dashboard = re.search(r"Dashboard GCP:\s*([^\n]+)", links_section)
            if dashboard:
                values["links"]["gcp_monitoring_dashboard"] = dashboard.group(1).strip()

    except Exception as e:
        print(f"❌ Erro ao ler customization: {e}")

    return values


def extract_custom_values_from_markdown(file_path: str) -> dict[str, Any]:
    """Extrai valores customizados da seção markdown do arquivo."""
    custom_values: dict[str, Any] = {}

    if not os.path.exists(file_path):
        return custom_values

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Procurar por seção "## Valores Customizados" ou similar
        match = re.search(r"## Valores Customizados(.*?)(?:##|$)", content, re.DOTALL)
        if match:
            section = match.group(1)
            # Extrair pares key: value
            pairs = re.findall(r"(\w+):\s*(.+)", section)
            for key, value in pairs:
                custom_values[key.strip()] = value.strip()

    except Exception as e:
        print(f"❌ Erro ao extrair valores: {e}")

    return custom_values


def get_value_from_dict(values, path: str) -> str:  # type: ignore
    """
    Busca um valor no dicionário usando notação ponto.
    Exemplo: "company.incident_commander.name"
    """
    try:
        parts = path.split('.')
        current = values  # type: ignore
        for key in parts:
            if not isinstance(current, dict):
                return f"[ERROR: {path}]"
            current = current.get(key)  # type: ignore
            if current is None:
                return f"[EMPTY: {path}]"
        return str(current)  # type: ignore
    except Exception:
        return f"[ERROR: {path}]"


def substitute_placeholders(content: str, values: dict[str, Any]) -> tuple[str, int]:
    """
    Substitui todos os placeholders no conteúdo.
    Retorna: (conteúdo modificado, número de substituições)
    """
    modified_content = content
    count = 0

    # Substituir placeholders mapeados
    for placeholder, lookup_path in PLACEHOLDER_MAP.items():
        if placeholder in modified_content:
            value = get_value_from_dict(values, lookup_path)
            if not value.startswith("["):  # Só substitui se achou um valor
                modified_content = modified_content.replace(placeholder, value)
                count += 1

    # Substituir placeholders genéricos [xxx]
    def replace_generic(match: re.Match[str]) -> str:
        placeholder_content = match.group(1)
        # Tentar buscar como chave customizada
        if placeholder_content in values.get("custom", {}):
            return str(values["custom"][placeholder_content])
        return match.group(0)  # Retorna original se não achar

    modified_content = re.sub(r"\[([^\]]+)\]", replace_generic, modified_content)

    return modified_content, count


def customize_documents(values: dict[str, Any]) -> None:
    """Processa todos os documentos e substitui placeholders."""

    # Garantir que o diretório de saída existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n" + "="*70)
    print("🔄 CUSTOMIZANDO DOCUMENTOS")
    print("="*70)

    total_substitutions = 0

    for doc_key, doc_path in SOURCE_DOCUMENTS.items():
        if not os.path.exists(doc_path):
            print(f"⚠️  {doc_key}: Arquivo não encontrado")
            continue

        print(f"\n📄 Processando: {doc_key}...", end=" ", flush=True)

        try:
            # Ler documento original
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Substituir placeholders
            modified_content, count = substitute_placeholders(content, values)
            total_substitutions += count

            # Salvar documento customizado
            output_filename = os.path.basename(doc_path)
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)

            print(f"✅ {count} placeholders substituídos")

        except Exception as e:
            print(f"❌ Erro: {e}")

    print("\n" + "="*70)
    print(f"✅ CUSTOMIZAÇÃO COMPLETA: {total_substitutions} substituições")
    print(f"📁 Documentos salvos em: {OUTPUT_DIR}")
    print("="*70)


def print_summary(values: dict[str, Any]) -> None:
    """Imprime um resumo dos valores carregados."""
    print("\n" + "="*70)
    print("📋 RESUMO DE CUSTOMIZAÇÃO")
    print("="*70)

    if values.get("company", {}).get("name"):
        print(f"\n🏢 Empresa: {values['company'].get('name', 'N/A')}")

    if values.get("company", {}).get("incident_commander"):
        ic = values['company']['incident_commander']
        print(f"🔴 Incident Commander: {ic.get('name', 'N/A')}")
        if ic.get('email'):
            print(f"   Email: {ic.get('email', 'N/A')}")
        if ic.get('phone'):
            print(f"   Phone: {ic.get('phone', 'N/A')}")

    if values.get("links"):
        print(f"\n🔗 Links carregados: {len(values['links'])} endereços")

    if values.get("production"):
        print(f"🌐 URLs de produção: {len(values['production'])} configuradas")

    print("\n" + "="*70)

# ============================================================================
# MAIN
# ============================================================================

# ============================================================================


def main() -> None:
    """Função principal."""
    print("\n🎯 CUSTOMIZADOR DE DOCUMENTOS COMPLIANCE\n")

    # Validar arquivo de customização
    if not os.path.exists(CUSTOMIZATION_FILE):
        print(f"❌ ERRO: {CUSTOMIZATION_FILE} não encontrado!")
        print("\n📝 Passos para criar o arquivo:")
        print("1. Copiar TEMPLATE_CUSTOMIZACAO.md para CUSTOMIZATION_VALUES.md")
        print("2. Preencher com valores reais da sua empresa")
        print("3. Executar este script novamente\n")
        return

    # Carregar valores de customização
    print("📖 Lendo arquivo de customização...")
    values = parse_customization_file(CUSTOMIZATION_FILE)
    custom_values = extract_custom_values_from_markdown(CUSTOMIZATION_FILE)

    if custom_values:
        values["custom"].update(custom_values)

    # Mostrar resumo
    print_summary(values)

    # Confirmar antes de customizar
    response = input("\n✅ Deseja customizar os documentos? (S/n): ").strip().lower()
    if response and response != 's':
        print("❌ Operação cancelada.")
        return

    # Customizar documentos
    customize_documents(values)

    print("\n✨ Próximos passos:")
    print(f"1. Revisar documentos em: {OUTPUT_DIR}")
    print("2. Verificar se todos os placeholders foram substituídos")
    print("3. Fazer upload para o repositório")
    print("\n")


if __name__ == "__main__":
    main()
