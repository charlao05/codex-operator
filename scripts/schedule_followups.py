"""
Gera mensagens de follow-up para contatos que ainda não responderam.
Modo de uso:
  - `python scripts/schedule_followups.py` -> gera `logs/followups_to_send.json` com follow-ups
  - Se quiser enviar automaticamente, rode com `--send` e defina `$env:GMAIL_APP_PASSWORD` (mesmo fluxo do send_wave1_emails)

Lógica básica:
  - Carrega `wave1_sending_results.json` e `email_monitoring_wave1.json`
  - Seleciona contatos com status 'enviado' e que não responderam
  - Gera mensagem de follow-up curta e registra em arquivo
"""
import json
import os
from datetime import datetime, timedelta
import argparse

IN_SEND = 'wave1_sending_results.json'
IN_MON = 'email_monitoring_wave1.json'
OUT_DIR = 'logs'
OUT_FILE = os.path.join(OUT_DIR, 'followups_to_send.json')

os.makedirs(OUT_DIR, exist_ok=True)

with open(IN_SEND, 'r', encoding='utf-8') as f:
    send_data = json.load(f)

try:
    with open(IN_MON, 'r', encoding='utf-8') as f:
        mon = json.load(f)
except Exception:
    mon = {}

results = send_data.get('results', [])
followups = []
now = datetime.now().isoformat()

for r in results:
    # Check monitoring for response (simple heuristic)
    email = r.get('email')
    responded = False
    if mon:
        contacts = mon.get('contacts') or mon.get('data') or []
        for c in contacts:
            if c.get('email') == email and c.get('respondeu'):
                responded = True
                break
    if r.get('status') == 'enviado' and not responded:
        # build follow-up
        followups.append({
            'email': email,
            'name': r.get('name'),
            'company': r.get('company'),
            'subject': f"Só um lembrete rápido, {r.get('name')} — demo rápida?",
            'body': f"Oi {r.get('name')},\n\nSó passando pra lembrar do convite pra uma demo rápida de 20 minutos.\n\nSe quiser, agendo no horário que for melhor pra você: { 'https://celadon-profiterole-b8e733.netlify.app' }\n\nAbraço,\nCharles",
            'scheduled_at': now
        })

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump({'generated_at': now, 'followups': followups}, f, indent=2, ensure_ascii=False)

print('Followups prepared:', OUT_FILE)

# Optional send path (not executed by default)
parser = argparse.ArgumentParser()
parser.add_argument('--send', action='store_true', help='Enviar os followups via SMTP (requer GMAIL_APP_PASSWORD)')
args = parser.parse_args()

if args.send:
    # Lazy import to avoid SMTP deps at top-level
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    GMAIL_ADDRESS = 'charles.rsilva05@gmail.com'
    GMAIL_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
    if not GMAIL_PASSWORD:
        import getpass
        GMAIL_PASSWORD = getpass.getpass('Enter Gmail App Password: ')
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
    sent = 0
    for fup in followups:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_ADDRESS
        msg['To'] = fup['email']
        msg['Subject'] = fup['subject']
        msg.attach(MIMEText(fup['body'], 'plain', 'utf-8'))
        try:
            server.send_message(msg)
            sent += 1
        except Exception as e:
            print('Error sending to', fup['email'], e)
    server.quit()
    print('Sent followups:', sent)
