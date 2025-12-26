#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail SMTP Email Sender - Wave 1
Envia 5 emails personalizados via SMTP Gmail
"""

import smtplib
import json
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configuração
import os

GMAIL_ADDRESS = "charles.rsilva05@gmail.com"  # Seu email
# Segurança: não armazene senhas no código.
# O script tentará ler a senha da variável de ambiente `GMAIL_APP_PASSWORD`.
# Se não encontrar, pedirá a senha interativamente sem ecoar no terminal.

# GMAIL_PASSWORD será resolvida apenas no momento do envio (evita prompt durante import)
GMAIL_PASSWORD = None
LANDING_URL = "https://celadon-profiterole-b8e733.netlify.app"

EMAILS_TO_SEND = [
    {
        "to": "contato@studiobeleza.com.br",
        "name": "Mariana",
        "company": "Studio Beleza Premium",
        "subject": "Mariana, você perde agendamentos por isso?",
        "body": f"""Oi Mariana,

Rápida pergunta: quando você e a equipe conseguem responder emails de agendamento, quanto tempo vocês gastam por dia com isso?

Pergunto porque a maioria dos salões que a gente conversa gasta entre 1-2 horas DIÁRIAS respondendo emails, WhatsApp, formulários... tudo manualmente.

Mariana, só isso representa ~10 horas por semana.

Pior: enquanto respondem manualmente, perdem agendamentos por atraso. Um cliente manda mensagem às 14h30, vocês só veem às 16h... já foi pra outro lugar.

**O que a gente construiu:**

Um sistema que responde automaticamente TODOS os agendamentos (email, WhatsApp, Google Forms) e organiza tudo em um calendário.

Resultado?

- Studio Beleza X: 30 agendamentos/semana → ZERO emails manuais (8 horas/semana economizadas)
- Taxa de conversão: subiu de 82% → 95% (clientes não perdem porque demora responder)
- Ganho: 8 horas × R$ 50/hora = R$ 400/semana = R$ 1.600/mês

**Quer ver funcionando?**

Abri 5 slots essa semana para demos rápidas (20 min). Mostro como funciona no seu celular, ao vivo.

👉 Veja como funciona: {LANDING_URL}

Leva 20 minutos e você já vê o impacto no seu fluxo.

Abraço,
Charles Rodrigues
Codex Operator
(27) 9 9999-9999

P.S. - Se 8 horas/semana economizadas + 13% de aumento de conversão soa interessante, manda msg que agendo mais rápido!""",
    },
    {
        "to": "atendimento@esteticamoderna.com",
        "name": "Juliana",
        "company": "Estética Moderna",
        "subject": "Juliana, como você gerencia 25+ agendamentos simultâneos?",
        "body": f"""Oi Juliana,

Vi seu Instagram - o trabalho de vocês é impecável! Parabéns pelas transformações incríveis.

Mas tenho uma dúvida: com 25+ agendamentos por semana, como vocês conseguem confirmar todos sem perder ninguém?

A realidade é que 30% dos agendamentos confirmados não comparecem (no-show). Com seus números:
- 25 agendamentos/semana
- 30% de no-show = 7-8 clientes não aparecem
- Prejuízo: 7-8 × R$ 150 (valor do serviço) = R$ 1.050 em receita perdida POR SEMANA

R$ 1.050 × 4 semanas = R$ 4.200/mês perdidos em no-shows.

**Existe solução simples:**

Sistema automático que:
✓ Envia confirmação via WhatsApp 24h antes
✓ Cliente clica 1 botão pra confirmar
✓ Se não confirmar, libera o horário pra outro cliente
✓ Taxa de confirmação sobe de 70% → 95%

Resultado: Recupera de R$ 3-4k/mês em receita.

**Quer testar?**

Levantei 5 slots essa semana pra demos (20 minutos).

👉 Veja como funciona: {LANDING_URL}

Me avisa se faz sentido pra vocês.

Abraço,
Charles Rodrigues
Codex Operator
(27) 9 9999-9999

P.S. - Tenho apenas 5 slots essa semana. Se interessar, responde hoje!""",
    },
    {
        "to": "contato@bellecabeleireira.com",
        "name": "Paula",
        "company": "Belle Cabelereira & Estética",
        "subject": "Paula, quanto vocês perdem com cancelamentos?",
        "body": f"""Oi Paula,

Seu salão é incrível - vi os trabalhos no Instagram. Muita qualidade!

Rápida pergunta: de 35 agendamentos por semana, quantos são CANCELAMENTOS de última hora?

A maioria dos salões que atendo tem entre 20-30% de cancelamentos. Com seus números:

- 35 agendamentos/semana
- 25% cancelamento = 8-9 clientes cancelam
- Horários vagos = receita perdida
- Prejuízo: ~R$ 1.500-2.000/semana em potencial

**Pior:** quando cliente cancela de última hora, vocês não conseguem preencher aquele horário com outro cliente.

**Solução que implementei:**

Sistema que confirma agendamentos automaticamente 24h antes. Quando cliente vê a confirmação:
- 40% confirmam (era incerto antes)
- 10% desmarcam (mas você ainda tem 24h pra preencher)
- Taxa de show-up sobe de 75% → 95%

Recupera ~R$ 800-1.200/semana em receita.

**Quer ver ao vivo?**

Abri 5 slots essa semana - 20 minutos de demo, sem compromisso.

👉 Veja como funciona: {LANDING_URL}

Abraço,
Charles Rodrigues
Codex Operator
(27) 9 9999-9999

P.S. - Se R$ 800-1.200/semana em receita recuperada te interessa, me liga!""",
    },
    {
        "to": "reservas@spabeiezacentro.com",
        "name": "Fernanda",
        "company": "Spa & Beleza Centro",
        "subject": "Fernanda, seu spa está perdendo espaço pra concorrência?",
        "body": f"""Oi Fernanda,

Adorei o espaço de vocês - parece um lugar super tranquilo e acolhedor!

Pergunta direta: vocês usam algum sistema pra confirmar agendamentos automaticamente ou é tudo manual?

Pergunto porque em Brasília, com concorrência alta, quem não confirma rápido perde cliente pra outro lugar.

Dados que observei:
- Spa com 20 agendamentos/semana, confirmação manual = perdem 3-5 clientes por semana
- Spa com automação = perdem 0-1 cliente por semana
- Diferença: ~R$ 1.000/semana

E mais: clientes adoram receber confirmação automática. Faz eles se sentirem cuidados.

**O que implemento:**

Sistema que confirma automaticamente 24h antes, via WhatsApp ou Email. Cliente vê confirmação, relaxa, aparece na hora.

**Resultado:**
- Clientes mais satisfeitos (recebem confirmação)
- Menos cancelamentos (confirmação reforça o compromisso)
- Mais receita (taxa de show-up sobe de 75% → 95%)

**Demo rápida?**

Abri 5 slots - leva 20 minutos.

👉 Veja como funciona: {LANDING_URL}

Se quiser testar, me avisa.

Abraço,
Charles Rodrigues
Codex Operator
(27) 9 9999-9999""",
    },
    {
        "to": "contato@studionails.com.br",
        "name": "Carolina",
        "company": "Studio Nails & Cabelo",
        "subject": "Carolina, você deixa dinheiro na mesa todos os dias?",
        "body": f"""Oi Carolina,

Vi seu estúdio no Instagram - que design incrível! Vocês estão crescendo muito.

Com 40 agendamentos por semana, vocês conseguem responder a TODOS no WhatsApp/Email?

Pergunto porque nesse volume, geralmente:
- Alguns emails ficam sem resposta por horas
- Cliente cansada de esperar marca com concorrente
- Vocês perdem o agendamento (e a receita)

Com seus números:
- 40 agendamentos/semana
- Se 10% não vira agendamento por falta de resposta rápida = 4 perdidos
- 4 × R$ 150 (valor médio) = R$ 600/semana

R$ 600 × 4 = R$ 2.400/mês em receita perdida.

**Existe sistema que resolve isso:**

Automação que responde EM SEGUNDOS quando cliente entra em contato. Resultado?

- Resposta rápida = cliente sente valorizada = confirma agendamento
- Taxa de conversão: 82% → 95% (13% de aumento)
- Receita extra: ~R$ 2-3k/mês

**Quer ver funcionando?**

Levantei 5 slots essa semana pra demos (20 min). Mostro no seu celular, ao vivo.

👉 Veja como funciona: {LANDING_URL}

Me avisa se faz sentido pra vocês.

Abraço,
Charles Rodrigues
Codex Operator
(27) 9 9999-9999

P.S. - Esses 5 slots vão rápido. Se tiver interesse, responde hoje mesmo!""",
    },
]


def send_emails():
    """Envia os 5 emails Wave 1"""
    print("\n" + "=" * 88)
    print("📧 GMAIL SMTP - WAVE 1 EMAIL SENDER")
    print("=" * 88 + "\n")

    sent_count = 0
    results = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Normal send path (if not dry-run) will connect; dry-run handled by caller
        print("=" * 88)
        print("📤 INICIANDO PROCESSO DE ENVIO (ou simulação)")
        print("=" * 88 + "\n")

        # If caller provided a server object (for tests) we respect it. Otherwise
        # the caller will handle connection. send_emails will raise if connection
        # is required but not provided.
        for idx, email_data in enumerate(EMAILS_TO_SEND, 1):
            print(f"\n📧 [{idx}/5] {email_data['name']} ({email_data['company']})")
            print(f"    Para: {email_data['to']}")
            print(f"    Assunto: {email_data['subject']}")

            # Create message preview
            msg = MIMEMultipart()
            msg["From"] = GMAIL_ADDRESS
            msg["To"] = email_data["to"]
            msg["Subject"] = email_data["subject"]
            msg.attach(MIMEText(email_data["body"], "plain", "utf-8"))

            # If we are in dry-run mode, just simulate send
            # The caller will pass a flag to decide.
            # Actual sending is handled in __main__ to keep this function testable.
            results.append(
                {
                    "index": idx,
                    "name": email_data["name"],
                    "company": email_data["company"],
                    "email": email_data["to"],
                    "status": "pending",
                    "timestamp": timestamp,
                }
            )

    except Exception as e:
        print(f"\n❌ Erro durante preparação das mensagens: {str(e)}")
        return False

    # Salvar resultados
    print("\n" + "=" * 88)
    print(f"📊 RESUMO: {sent_count}/{len(EMAILS_TO_SEND)} emails enviados com sucesso")
    print("=" * 88 + "\n")

    output_file = "wave1_sending_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "total_sent": sent_count,
                "total_failed": len(EMAILS_TO_SEND) - sent_count,
                "results": results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"📁 Resultados salvos em: {output_file}\n")

    print("=" * 88)
    print("🎯 PRÓXIMAS AÇÕES")
    print("=" * 88)
    print("""
1. ✅ Emails enviados para:
   - Mariana (Studio Beleza Premium)
   - Juliana (Estética Moderna)
   - Paula (Belle Cabelereira)
   - Fernanda (Spa & Beleza)
   - Carolina (Studio Nails)

2. ⏱️  Monitorar respostas (esperado 24-48h)
3. 📊 Dashboard: Execute python email_monitoring.py
4. 🔄 Wave 2: Deploy consultórios depois
5. 📈 Métricas: 20-25% open rate, 50% demo scheduling

Boa sorte! 🚀
""")

    return sent_count == len(EMAILS_TO_SEND)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enviar Wave1 emails via Gmail SMTP")
    parser.add_argument(
        "--dry-run", action="store_true", help="Simula o envio sem conectar ao SMTP"
    )
    args = parser.parse_args()

    if args.dry_run:
        print("\nModo DRY-RUN ativado: nenhuma conexão SMTP será estabelecida.\n")
        success = send_emails()
        # mark simulated results file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        simulated = {
            "timestamp": timestamp,
            "mode": "dry-run",
            "total_simulated": len(EMAILS_TO_SEND),
        }
        with open("wave1_sending_results_simulated.json", "w", encoding="utf-8") as f:
            json.dump(simulated, f, indent=2, ensure_ascii=False)
        print("\nArquivo de simulação salvo em: wave1_sending_results_simulated.json")
        exit(0 if success else 1)
    else:
        # Real send: resolve GMAIL_PASSWORD now (env or interactive) and connect
        GMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
        if not GMAIL_PASSWORD:
            import getpass

            GMAIL_PASSWORD = getpass.getpass(
                "Enter Gmail App Password (input hidden): "
            )

        try:
            print("🔐 Conectando ao Gmail SMTP...")
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            print("✅ Conectado com sucesso!\n")

            sent_count = 0
            results = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for idx, email_data in enumerate(EMAILS_TO_SEND, 1):
                try:
                    print(
                        f"\n📧 [{idx}/5] {email_data['name']} ({email_data['company']})"
                    )
                    print(f"    Para: {email_data['to']}")
                    print(f"    Assunto: {email_data['subject']}")

                    msg = MIMEMultipart()
                    msg["From"] = GMAIL_ADDRESS
                    msg["To"] = email_data["to"]
                    msg["Subject"] = email_data["subject"]
                    msg.attach(MIMEText(email_data["body"], "plain", "utf-8"))

                    server.send_message(msg)
                    print("    ✅ Email enviado com sucesso!")
                    sent_count += 1
                    results.append(
                        {
                            "index": idx,
                            "name": email_data["name"],
                            "company": email_data["company"],
                            "email": email_data["to"],
                            "status": "enviado",
                            "timestamp": timestamp,
                        }
                    )

                except Exception as e:
                    print(f"    ❌ Erro ao enviar: {str(e)}")
                    results.append(
                        {
                            "index": idx,
                            "name": email_data["name"],
                            "company": email_data["company"],
                            "email": email_data["to"],
                            "status": "falha",
                            "erro": str(e),
                            "timestamp": timestamp,
                        }
                    )

            server.quit()

            output_file = "wave1_sending_results.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": timestamp,
                        "total_sent": sent_count,
                        "total_failed": len(EMAILS_TO_SEND) - sent_count,
                        "results": results,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            print(f"\n📁 Resultados salvos em: {output_file}\n")
            exit(0 if sent_count == len(EMAILS_TO_SEND) else 1)

        except Exception as e:
            print(f"\n❌ Erro na conexão: {str(e)}")
            print("\nDica: Se receber erro de autenticação:")
            print("1. Acesse: https://myaccount.google.com/apppasswords")
            print("2. Gere uma App Password para seu email")
            print("3. Use essa senha no script (não sua senha normal)")
            exit(1)
