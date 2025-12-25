"""
Send Wave 2 with A/B split between Variant A and Variant B.
Usage:
  python scripts/send_wave2_ab.py --dry-run
  python scripts/send_wave2_ab.py           # real send (requires GMAIL_APP_PASSWORD env or interactive)

Split logic: round-robin assignment between variants A and B to balance.
"""
import os
import json
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_FILE = os.path.join(PROJECT_ROOT, 'data', 'wave1_variants.json')
GMAIL_ADDRESS = 'charles.rsilva05@gmail.com'


def load_variants():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    templates = data.get('templates', [])
    return templates


def build_ab_emails(templates):
    emails = []
    for idx, t in enumerate(templates):
        variants = t.get('variants', [])
        var_a = None
        var_b = None
        for v in variants:
            if v.get('variant') == 'A':
                var_a = v
            if v.get('variant') == 'B':
                var_b = v
        # fallback: if one variant missing, duplicate the other
        if not var_a and var_b:
            var_a = var_b
        if not var_b and var_a:
            var_b = var_a

        # Assign target: even index -> A, odd index -> B (round-robin)
        chosen = var_a if (idx % 2 == 0) else var_b
        subject = chosen.get('subject')
        body = chosen.get('body')

        emails.append({
            'to': t.get('email'),
            'name': t.get('name'),
            'company': t.get('company'),
            'subject': subject,
            'body': body,
            'variant': chosen.get('variant')
        })
    return emails


def send_emails(emails, dry_run=True):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    results = []

    if dry_run:
        print('\nDRY-RUN A/B: nenhuma conexão SMTP será estabelecida.\n')
        for idx, e in enumerate(emails, 1):
            print(f"[{idx}/{len(emails)}] PARA: {e['to']} | VARIANT: {e['variant']} | ASSUNTO: {e['subject']}")
            results.append({'index': idx, 'email': e['to'], 'status': 'simulado', 'variant': e['variant'], 'timestamp': timestamp})
        out = os.path.join(PROJECT_ROOT, 'wave2_ab_sending_results_simulated.json')
        with open(out, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': timestamp, 'mode': 'dry-run', 'results': results}, f, indent=2, ensure_ascii=False)
        print('\nSimulação salva em:', out)
        return True
    else:
        GMAIL_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
        if not GMAIL_PASSWORD:
            import getpass
            GMAIL_PASSWORD = getpass.getpass('Enter Gmail App Password (input hidden): ')
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        except Exception as e:
            print('Erro na conexão SMTP:', e)
            return False

        sent = 0
        for idx, e in enumerate(emails, 1):
            try:
                msg = MIMEMultipart()
                msg['From'] = GMAIL_ADDRESS
                msg['To'] = e['to']
                msg['Subject'] = e['subject']
                msg.attach(MIMEText(e['body'], 'plain', 'utf-8'))
                server.send_message(msg)
                sent += 1
                results.append({'index': idx, 'email': e['to'], 'status': 'enviado', 'variant': e['variant'], 'timestamp': timestamp})
                print(f'[{idx}/{len(emails)}] Enviado: {e["to"]} (Variant {e["variant"]})')
            except Exception as ex:
                results.append({'index': idx, 'email': e['to'], 'status': 'falha', 'erro': str(ex), 'variant': e.get('variant'), 'timestamp': timestamp})
                print(f'[{idx}/{len(emails)}] Falha: {e["to"]} -', ex)
        server.quit()
        out = os.path.join(PROJECT_ROOT, 'wave2_ab_sending_results.json')
        with open(out, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': timestamp, 'total_sent': sent, 'results': results}, f, indent=2, ensure_ascii=False)
        print('\nResultados salvos em:', out)
        return sent == len(emails)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Simula o envio')
    args = parser.parse_args()

    templates = load_variants()
    emails = build_ab_emails(templates)
    success = send_emails(emails, dry_run=args.dry_run)
    exit(0 if success else 1)
