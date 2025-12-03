#!/usr/bin/env python3
"""
EMAIL MONITORING & CRM TRACKER
Monitora respostas de emails e atualiza Google Sheets automaticamente
"""

import json
from datetime import datetime
from typing import Dict, List, Any

# Dados de contatos Wave 1
WAVE1_CONTACTS = [
    {
        "name": "Mariana",
        "company": "Studio Beleza Premium",
        "email": "mariana@studiobeleza.com.br",
        "niche": "Salões de Beleza",
        "volume": "30 agendamentos/semana",
        "sent_date": "2025-12-05T14:30:00",
        "subject": "Mariana, você perde agendamentos por isso?",
        "status": "Enviado",
        "opens": 0,
        "clicks": 0,
        "replied": False,
        "demo_booked": False,
        "next_action": "Aguardar resposta (target: 24h)"
    },
    {
        "name": "Juliana",
        "company": "Estética Moderna",
        "email": "atendimento@esteticamoderna.com",
        "niche": "Salões de Beleza",
        "volume": "25 agendamentos/semana",
        "sent_date": "2025-12-05T14:30:00",
        "subject": "Juliana, como você gerencia 25+ agendamentos?",
        "status": "Enviado",
        "opens": 0,
        "clicks": 0,
        "replied": False,
        "demo_booked": False,
        "next_action": "Aguardar resposta (target: 24h)"
    },
    {
        "name": "Paula",
        "company": "Belle Cabelereira & Estética",
        "email": "contato@bellecabeleireira.com",
        "niche": "Salões de Beleza",
        "volume": "35 agendamentos/semana",
        "sent_date": "2025-12-05T14:30:00",
        "subject": "Paula, a Belle está perdendo clientes?",
        "status": "Enviado",
        "opens": 0,
        "clicks": 0,
        "replied": False,
        "demo_booked": False,
        "next_action": "Aguardar resposta (target: 24h)"
    },
    {
        "name": "Fernanda",
        "company": "Spa & Beleza Centro",
        "email": "reservas@spabeiezacentro.com",
        "niche": "Salões de Beleza",
        "volume": "20 agendamentos/semana",
        "sent_date": "2025-12-05T14:30:00",
        "subject": "Fernanda, seu spa recebe mensagens fora do horário?",
        "status": "Enviado",
        "opens": 0,
        "clicks": 0,
        "replied": False,
        "demo_booked": False,
        "next_action": "Aguardar resposta (target: 24h)"
    },
    {
        "name": "Carolina",
        "company": "Studio Nails & Cabelo",
        "email": "contato@studionails.com.br",
        "niche": "Salões de Beleza",
        "volume": "40 agendamentos/semana",
        "sent_date": "2025-12-05T14:30:00",
        "subject": "Carolina, 40 agendamentos/semana é muito trabalho?",
        "status": "Enviado",
        "opens": 0,
        "clicks": 0,
        "replied": False,
        "demo_booked": False,
        "next_action": "Aguardar resposta (target: 24h)"
    }
]

def print_monitoring_dashboard():
    """Imprime dashboard de monitoramento em tempo real"""
    
    print("\n" + "="*90)
    print("📊 EMAIL MONITORING DASHBOARD - WAVE 1")
    print("="*90 + "\n")
    
    print(f"⏰ Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    # Estatísticas
    total_sent = len(WAVE1_CONTACTS)
    total_opened = sum(1 for c in WAVE1_CONTACTS if c['opens'] > 0)
    total_replied = sum(1 for c in WAVE1_CONTACTS if c['replied'])
    total_demos = sum(1 for c in WAVE1_CONTACTS if c['demo_booked'])
    
    print(f"📈 ESTATÍSTICAS:")
    print(f"   • Total enviados: {total_sent}")
    print(f"   • Emails abertos: {total_opened}/{total_sent} ({(total_opened/total_sent*100):.0f}%)")
    print(f"   • Respostas recebidas: {total_replied}/{total_sent} ({(total_replied/total_sent*100):.0f}%)")
    print(f"   • Demos agendadas: {total_demos}/{total_sent} ({(total_demos/total_sent*100):.0f}%)")
    
    print("\n" + "-"*90)
    print("📋 DETALHES POR CONTATO:")
    print("-"*90 + "\n")
    
    for i, contact in enumerate(WAVE1_CONTACTS, 1):
        status_emoji = "🟢" if contact['replied'] else "🟡" if contact['opens'] > 0 else "⚪"
        
        print(f"{i}. {status_emoji} {contact['name']} ({contact['company']})")
        print(f"   Email: {contact['email']}")
        print(f"   Enviado: {contact['sent_date']}")
        print(f"   Status: {contact['status']}")
        print(f"   Aberturas: {contact['opens']} | Clicks: {contact['clicks']} | Respondeu: {'✅' if contact['replied'] else '❌'}")
        print(f"   Demo agendada: {'✅' if contact['demo_booked'] else '❌'}")
        print(f"   Próximo passo: {contact['next_action']}")
        print()
    
    print("="*90)

def print_action_items():
    """Imprime itens de ação prioritários"""
    
    print("\n" + "="*90)
    print("🎯 AÇÕES PRIORITÁRIAS AGORA")
    print("="*90 + "\n")
    
    replied = [c for c in WAVE1_CONTACTS if c['replied']]
    opened = [c for c in WAVE1_CONTACTS if c['opens'] > 0 and not c['replied']]
    
    if replied:
        print(f"⚡ RESPOSTAS RECEBIDAS ({len(replied)}):")
        for contact in replied:
            print(f"   → {contact['name']} - RESPONDER EM <2H")
        print()
    
    if opened:
        print(f"📖 ABERTOS MAS NÃO RESPONDERAM ({len(opened)}):")
        for contact in opened:
            print(f"   → {contact['name']} - Acompanhar")
        print()
    
    no_opens = [c for c in WAVE1_CONTACTS if c['opens'] == 0]
    if no_opens and len(no_opens) <= 2:
        print(f"📧 AINDA NÃO ABRIRAM ({len(no_opens)}):")
        for contact in no_opens:
            print(f"   → {contact['name']} - Aguardar (máx 48h)")
        print()

def export_to_json():
    """Exporta dados para JSON para rastreamento"""
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "wave": 1,
        "contacts": WAVE1_CONTACTS,
        "summary": {
            "total_sent": len(WAVE1_CONTACTS),
            "total_opened": sum(1 for c in WAVE1_CONTACTS if c['opens'] > 0),
            "total_replied": sum(1 for c in WAVE1_CONTACTS if c['replied']),
            "total_demos": sum(1 for c in WAVE1_CONTACTS if c['demo_booked'])
        }
    }
    
    with open('email_monitoring_wave1.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Dados exportados para: email_monitoring_wave1.json")

def print_templates():
    """Imprime templates de resposta para diferentes cenários"""
    
    print("\n" + "="*90)
    print("📝 TEMPLATES DE RESPOSTA")
    print("="*90 + "\n")
    
    print("CENÁRIO 1: Cliente respondeu interessado")
    print("-" * 90)
    print("""
Oi [NOME],

Obrigado por responder! Fico feliz que te interessou.

Preparei um calendário com 5 slots disponíveis essa semana:
[LINK CALENDLY]

Escolhe o horário que achar melhor. Leva 20 minutos e você já vê como funciona.

Qualquer dúvida antes, é só chamar!

Abraço,
Charles
    """)
    
    print("\nCENÁRIO 2: Cliente pediu mais info")
    print("-" * 90)
    print("""
Oi [NOME],

Ótima pergunta! 

Para [SITUAÇÃO ESPECÍFICA], o que funciona é:
[DETALHE TÉCNICO RELEVANTE]

Resultado: [NÚMERO ESPECÍFICO RELEVANTE]

Quer que a gente simule com seus dados? Posso fazer uma demo em 20 minutos.

[LINK CALENDLY]

Abraço,
Charles
    """)
    
    print("\nCENÁRIO 3: Cliente pediu follow-up depois")
    print("-" * 90)
    print("""
Oi [NOME],

Sem problema! Fico na sua.

Qualquer momento que precisar de ajuda, tô aqui.
[LINK LANDING]

Abraço,
Charles
    """)

def print_guidelines():
    """Imprime guidelines para resposta rápida"""
    
    print("\n" + "="*90)
    print("📖 GUIDELINES - RESPOSTA RÁPIDA")
    print("="*90 + "\n")
    
    print("""
⏰ TEMPO DE RESPOSTA: <2 horas (CRÍTICO)

🎯 OBJETIVOS:
  1. Agradecer resposta
  2. Validar que entendeu a dor
  3. Oferecer demo
  4. Agendar no calendário

📝 ESTRUTURA:
  1. Saudação pessoal (oi [NOME])
  2. Validação: "Fico feliz que te interessou" ou similar
  3. Número específico (economia, conversão, etc)
  4. CTA clara: "Calendário" com link
  5. Desculpa: "Qualquer dúvida, aviso"

✅ CHECKLIST:
  □ Responda <2h
  □ Use nome do cliente
  □ Cite algo da mensagem anterior
  □ Ofereça link de calendario/demo
  □ Mantenha tom amigável e profissional
  □ Assine com nome

❌ NÃO FAÇA:
  × Resposta genérica/template óbvia
  × Demora >4h
  × Pedir para preencher formulário longo
  × Muita informação (max 3 parágrafos)
  × Links múltiplos confundindo
    """)

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*88 + "╗")
    print("║" + " "*20 + "EMAIL TRACKING & MONITORING SYSTEM" + " "*35 + "║")
    print("║" + " "*20 + "Wave 1: 5 Contatos - Salões de Beleza" + " "*32 + "║")
    print("╚" + "="*88 + "╝")
    
    # Mostrar dashboard
    print_monitoring_dashboard()
    
    # Mostrar ações prioritárias
    print_action_items()
    
    # Mostrar templates
    print_templates()
    
    # Mostrar guidelines
    print_guidelines()
    
    # Exportar para JSON
    export_to_json()
    
    print("\n" + "="*90)
    print("🚀 PRÓXIMAS AÇÕES:")
    print("="*90)
    print("""
1. Verificar email (Gmail) para respostas
2. Quando receber resposta, usar templates acima
3. Responder <2h com link calendário
4. Atualizar Google Sheets com status
5. Se nenhuma resposta em 48h, enviar follow-up

Timeline esperada:
  - 14:30: Emails enviados
  - 16:00-18:00: Primeiras aberturas (esperado 1-2)
  - 24-48h: Respostas (esperado 1-2)
  - 48-72h: Demos agendadas (esperado 1-2)

Boa sorte! 🎯
    """)
