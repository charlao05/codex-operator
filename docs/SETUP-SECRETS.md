# Setup de Secrets para codex-operator

Este documento descreve os secrets e variáveis de ambiente necessárias para rodar o projeto em produção e local.

## Secrets / Env recomendados
- `OPENAI_API_KEY` — chave da OpenAI (usada por `src/utils/llm_client.py`).
- `PYPI_API_TOKEN` — token API do PyPI (usado pelo workflow de publish).
- `DOCKERHUB_USERNAME` & `DOCKERHUB_TOKEN` — credenciais para push de imagem Docker.
- Gmail options (escolha uma):
  - Service Account (recomendado para produção):
    - `GMAIL_SERVICE_ACCOUNT_FILE` — conteúdo JSON do service account (colar como secret).
    - `GMAIL_DELEGATED_USER` — usuário delegado para envio (ex: 'no-reply@seu-domínio.com').
  - App Password (simples):
    - `GMAIL_APP_PASSWORD` — senha de app do Gmail (usar junto com `SENDER_EMAIL`).
  - OAuth Credentials (dev/local):
    - `GMAIL_CREDENTIALS_FILE` — arquivo `gmail_authorized_user.json` (colocar no servidor e definir caminho em `.env`).
  - Access Token (temporário):
    - `GMAIL_ACCESS_TOKEN` — token Bearer (expira rápido; só para testes).

- SMTP (fallback / alternativa):
  - `EMAIL_SMTP_HOST` (ex: `smtp.gmail.com`)
  - `EMAIL_SMTP_PORT` (ex: `587`)
  - `EMAIL_SMTP_USER`
  - `EMAIL_SMTP_PASSWORD` (ou use `GMAIL_APP_PASSWORD`)
  - `SENDER_EMAIL`

- WhatsApp (opcional):
  - `WHATSAPP_TOKEN`
  - `WHATSAPP_PHONE_ID`

- Telegram (opcional):
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_TEST_CHAT_ID`

- Google Calendar (opcional):
  - `GOOGLE_CALENDAR_ID`

## Recomendações práticas
1. Prefira `GMAIL_SERVICE_ACCOUNT_FILE` + `GMAIL_DELEGATED_USER` em produção.
2. Se não tiver GSuite, use `GMAIL_APP_PASSWORD` + `SENDER_EMAIL` (SMTP fallback).
3. Armazene secrets no GitHub: Settings → Secrets → Actions (use os nomes acima).
4. Para tokens JSON (service account), cole o conteúdo do JSON como o valor do secret e, em runtime, escreva o arquivo para `config/sa-key.json` e defina `GMAIL_SERVICE_ACCOUNT_FILE` com o caminho.

## Testes locais
- .env mínimo para testes locais (arquivo `.env`):

```
OPENAI_API_KEY=sk-...
SENDER_EMAIL=seu-email@gmail.com
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=seu-email@gmail.com
EMAIL_SMTP_PASSWORD=SUA_APP_PASSWORD
```

- Comandos para testar envio via SMTP localmente:

```bash
python -m pip install -r requirements.txt
python -c "from src.integrations.email_api import EmailAPI; e=EmailAPI(); print(e.send_email(['destino@example.com'], 'Assunto teste', 'Corpo'))"
```

## Observações
- Workflow de publicação usa `PYPI_API_TOKEN` e `DOCKERHUB_*`. Se o GitHub tiver problemas de faturamento, workflows não irão rodar — mas PRs e commits funcionam.

---
Gerado automaticamente pelo assistente para facilitar o setup de produção.
