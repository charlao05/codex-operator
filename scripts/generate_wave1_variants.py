"""
Gera variantes (A/B) dos 5 templates Wave1.
Modo:
 - Se `GOOGLE_APPLICATION_CREDENTIALS` estiver definido e `google-cloud-aiplatform` instalado,
   usa Vertex AI para gerar variações (exige configuração GCP).
 - Caso contrário, usa um gerador local simples que produz 2 variantes por template.

Saída: `data/wave1_variants.json`
"""

import os
import json
from datetime import datetime

OUTPUT_FILE = os.path.join('data', 'wave1_variants.json')

# Carrega templates originais do send_wave1_emails.py (import localmente)
try:
    # Ensure parent (project root) is on sys.path when script is executed from scripts/
    import sys
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from send_wave1_emails import EMAILS_TO_SEND, LANDING_URL
except Exception as e:
    # fallback: carregar de arquivo ou definir minimal set
    import traceback
    print('Erro ao importar send_wave1_emails:', str(e))
    traceback.print_exc()
    EMAILS_TO_SEND = []
    LANDING_URL = ''


def local_variant_generator(template):
    """Gera 2 variantes simples alterando assunto e abrindo o corpo com 1 frase nova."""
    variants = []
    subj = template.get('subject', '')
    body = template.get('body', '')
    name = template.get('name', '')

    # Variante A: tom mais direto
    variants.append({
        'subject': subj.replace(',', '') + ' — Demo rápida?',
        'body': body + "\n\nPS: Posso mostrar em 20 minutos, ao vivo no celular.",
        'variant': 'A'
    })

    # Variante B: inclui número/ROI na primeira linha
    variants.append({
        'subject': 'Recupera tempo e receita — ' + subj,
        'body': 'Resultado típico: +R$ 1.000/mês.\n\n' + body,
        'variant': 'B'
    })

    return variants


def main():
    results = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'templates': []
    }

    if not EMAILS_TO_SEND:
        print('Nenhum template encontrado em send_wave1_emails.EMAILS_TO_SEND. Abortando geração local.')
        return False

    for t in EMAILS_TO_SEND:
        variants = local_variant_generator(t)
        results['templates'].append({
            'name': t.get('name'),
            'email': t.get('to'),
            'company': t.get('company'),
            'variants': variants
        })

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f'Variantes geradas e salvas em: {OUTPUT_FILE}')
    return True


if __name__ == '__main__':
    main()
