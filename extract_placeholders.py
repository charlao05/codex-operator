#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair e validar placeholders nos documentos compliance.
Gera relatorio CSV com todos os [placeholders] pendentes.
"""

import re
import os
import csv
from typing import Dict, List, Tuple, Any

# ============================================================================
# CONFIGURACAO
# ============================================================================

DOCUMENTS: List[str] = [
    "c:/Users/Charles/Downloads/DEPLOY_STANDARDS.md",
    "c:/Users/Charles/Downloads/GO_LIVE_CHECKLIST.md",
    "c:/Users/Charles/Downloads/SECURITY_COMPLIANCE_MATRIX.md",
    "c:/Users/Charles/Downloads/INCIDENT_RESPONSE_PL"
    "AYBOOK.md",
    "c:/Users/Charles/Downloads/MONITORING_ALERTING_RUNBOOK.md",
]

OUTPUT_CSV = "c:/Users/Charles/Desktop/codex-operator/PLACEHOLDERS_REPORT.csv"
OUTPUT_LOG = "c:/Users/Charles/Desktop/codex-operator/placeholders_extract.log"

# Padroes de placeholder
PLACEHOLDER_PATTERN = r"\[([^\]]+)\]"

# Categorias de placeholders
CRITICAL_KEYWORDS: set[str] = {
    "link", "name", "email", "phone", "contact", "url", "endpoint",
    "key", "secret", "token", "password", "username"
}

# ============================================================================
# FUNCOES
# ============================================================================


def extract_placeholders(file_path: str) -> List[Tuple[str, int, str]]:
    """
    Extrai todos os placeholders de um arquivo.

    Returns:
        Lista de tuples: (placeholder_text, line_number, full_line)
    """
    placeholders: List[Tuple[str, int, str]] = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                matches = re.finditer(PLACEHOLDER_PATTERN, line)
                for match in matches:
                    placeholder: str = match.group(1)
                    placeholders.append((placeholder, line_num, line.strip()))
    except Exception as e:
        print(f"❌ Erro ao ler {file_path}: {e}")

    return placeholders


def categorize_placeholder(placeholder: str) -> str:
    """Categoriza a criticidade do placeholder."""
    placeholder_lower: str = placeholder.lower()

    if any(keyword in placeholder_lower for keyword in CRITICAL_KEYWORDS):
        return "🔴 CRÍTICO"
    elif placeholder_lower in ["pending", "tbd", "tba", "tbf", "date", "signature"]:
        return "🟡 ALTO"
    else:
        return "🟢 MÉDIO"


def process_all_documents() -> Dict[str, List[Tuple[str, int, str]]]:
    """Processa todos os documentos e extrai placeholders."""
    results: Dict[str, List[Tuple[str, int, str]]] = {}

    for doc_path in DOCUMENTS:
        if not os.path.exists(doc_path):
            print(f"⚠️  Arquivo não encontrado: {doc_path}")
            continue

        doc_name: str = os.path.basename(doc_path)
        print(f"📋 Processando: {doc_name}...", end=" ", flush=True)

        placeholders = extract_placeholders(doc_path)
        results[doc_path] = placeholders

        print(f"✅ {len(placeholders)} placeholders encontrados")

    return results


def generate_csv_report(results: Dict[str, List[Tuple[str, int, str]]]) -> None:
    """Gera relatorio CSV com todos os placeholders."""
    rows: List[Dict[str, str | int]] = []

    for doc_path, placeholders in results.items():
        doc_name: str = os.path.basename(doc_path)

        for placeholder, line_num, full_line in placeholders:
            severity: str = categorize_placeholder(placeholder)

            rows.append({
                'Documento': doc_name,
                'Placeholder': f"[{placeholder}]",
                'Linha': line_num,
                'Contexto': full_line[:80],  # Primeiros 80 chars
                'Severidade': severity,
                'Status': '⏳ Pendente',
                'Preenchido Com': '',
                'Data': '',
            })

    # Ordenar por severidade (crítico primeiro)
    severity_order: Dict[str, int] = {'🔴 CRÍTICO': 0, '🟡 ALTO': 1, '🟢 MÉDIO': 2}
    rows.sort(key=lambda x: severity_order.get(str(x['Severidade']), 3))

    # Escrever CSV
    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n✅ Relatório CSV gerado: {OUTPUT_CSV}")
    except Exception as e:
        print(f"❌ Erro ao gerar CSV: {e}")


def print_summary(results: Dict[str, List[Tuple[str, int, str]]]) -> None:
    """Imprime resumo dos placeholders."""
    print("\n" + "="*70)
    print("📊 RESUMO DE PLACEHOLDERS POR DOCUMENTO")
    print("="*70)

    total_placeholders: int = 0
    critical_count: int = 0

    for doc_name, placeholders in results.items():  # type: ignore
        critical: int = sum(1 for p, _, _ in placeholders  # type: ignore
                            if "link" in p.lower() or "name" in p.lower()
                            or "email" in p.lower() or "phone" in p.lower())

        print(f"\n📄 {doc_name}")
        print(f"   Total: {len(placeholders)}")
        print(f"   Críticos: {critical} 🔴")

        # Mostrar alguns exemplos
        if placeholders:
            print("   Exemplos:")
            for placeholder, line_num, _ in placeholders[:3]:  # type: ignore
                print(f"     - [{placeholder}] (linha {line_num})")
            if len(placeholders) > 3:
                print(f"     ... e {len(placeholders) - 3} mais")

        total_placeholders += len(placeholders)
        critical_count += critical

    print("\n" + "="*70)
    print(f"📈 TOTAL GERAL: {total_placeholders} placeholders")
    print(f"🔴 CRÍTICOS: {critical_count}")
    print("="*70 + "\n")


def print_critical_list(results: Dict[str, List[Tuple[str, int, str]]]) -> None:
    """Lista apenas os placeholders críticos."""
    print("\n" + "="*70)
    print("🔴 PLACEHOLDERS CRÍTICOS (OBRIGATÓRIOS)")
    print("="*70)

    critical_items: List[Dict[str, str | int]] = []

    for doc_path, placeholders in results.items():
        doc_name: str = os.path.basename(doc_path)

        for placeholder, line_num, full_line in placeholders:
            if any(keyword in placeholder.lower()
                   for keyword in ["link", "name", "email", "phone", "contact"]):
                critical_items.append({
                    'doc': doc_name,
                    'placeholder': placeholder,
                    'line': line_num,
                    'context': full_line
                })

    for i, item in enumerate(critical_items, 1):
        context_value: Any = item['context']
        context_str: str = str(context_value) if context_value else ""
        print(f"\n{i}. [{item['placeholder']}] em {item['doc']}:{item['line']}")
        print(f"   Contexto: {context_str[:70]}")


# ============================================================================
# MAIN
# ============================================================================

# MAIN
# ============================================================================

def main() -> None:
    """Funcao principal."""
    print("\n🔍 EXTRATOR DE PLACEHOLDERS - DOCUMENTOS COMPLIANCE\n")

    # Validar caminhos
    invalid_docs: List[str] = [d for d in DOCUMENTS if not os.path.exists(d)]
    if invalid_docs:
        print("⚠️  Documentos não encontrados:")
        for doc in invalid_docs:
            print(f"   - {doc}")
        print("\nCertifique-se que os documentos estão em Downloads!\n")

    # Processar documentos
    print(f"📂 Processando {len(DOCUMENTS)} documentos...\n")
    results = process_all_documents()

    if not results:
        print("\n❌ Nenhum documento foi processado com sucesso!")
        return

    # Gerar relatorios
    print_summary(results)
    print_critical_list(results)
    generate_csv_report(results)

    print("✅ EXTRAÇÃO COMPLETA!\n")
    print("Próximos passos:")
    print(f"1. Abrir: {OUTPUT_CSV}")
    print("2. Preencher coluna 'Preenchido Com'")
    print("3. Marcar 'Status' como ✅ Completo")
    print("\n")


if __name__ == "__main__":
    main()
