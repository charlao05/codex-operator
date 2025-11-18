# Setup Gmail Pessoal (OAuth)

Para usar sua conta **charles.rsilva05@gmail.com** e enviar emails, siga:

## Passo 1: Baixar Credenciais OAuth do Google Cloud Console

1. Abra: https://console.cloud.google.com/
2. Selecione projeto: **agendamento-n8n-476415**
3. Vá para: **APIs & Services** → **Credentials**
4. Clique: **Create Credentials** → **OAuth client ID**
5. Tipo: **Desktop application**
6. Clique: **Create**
7. Clique: **Download JSON**
8. Renomeie para `credentials.json` e coloque em: `c:\Users\Charles\Desktop\codex-operator\`

## Passo 2: Gerar Token Autorizado

```powershell
cd c:\Users\Charles\Desktop\codex-operator

# Instale a biblioteca OAuth:
pip install google-auth-oauthlib

# Execute o script de setup (vai abrir navegador):
python -m src.integrations.setup_gmail_oauth
```

## Passo 3: Atualize .env

Depois que o script criar `gmail_authorized_user.json`, atualize:

```env
GMAIL_CREDENTIALS_FILE="gmail_authorized_user.json"
```

## Passo 4: Teste

```powershell
python -m src.orchestrator nf --sales-file data/test_sale_gmail.json --send-gmail
```

---

## Opção B: Usar App Password (SMTP)

Se preferir usar **SMTP** (mais simples):

1. Ative 2-Step Verification: https://myaccount.google.com/security
2. Gere App Password: https://myaccount.google.com/apppasswords
3. Copie a senha (16 caracteres)
4. Atualize `.env`:
```env
EMAIL_SMTP_PASSWORD="seu-app-password-aqui"
```
5. Teste:
```powershell
python -m src.orchestrator nf --sales-file data/test_sale_gmail.json --send-email
```
