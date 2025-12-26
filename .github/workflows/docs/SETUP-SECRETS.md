# Configurar Secrets para CODEX-OPERATOR

## Visão Geral

Este guia mostra como configurar os secrets (credenciais) necessários para rodar o CODEX-OPERATOR em desenvolvimento local ou em produção.

### Tipos de Configuração

1. **Desenvolvimento Local** (.env.local)
2. **GitHub Actions** (Repository Secrets)
3. **Produção** (Servidor/Container)

---

## Opção A: Desenvolvimento Local

### 1. Preparar Arquivo .env.local

```bash
cp .env.example .env.local
```

### 2. Configurar Cada Secret

#### OPENAI_API_KEY

1. Acesse https://platform.openai.com/api-keys
2. Clique em "Create new secret key"
3. Copie a chave
4. Em `.env.local`, adicione:

```
OPENAI_API_KEY=sk-proj-seu-valor-aqui
```

#### GOOGLE_APPLICATION_CREDENTIALS (Google Service Account)

1. Acesse https://console.cloud.google.com/iam-admin/serviceaccounts
2. Selecione seu projeto
3. Crie uma Service Account (ou use uma existente)
4. Clique em "Create Key" → JSON
5. Salve o arquivo em `config/sa-key.json`
6. Em `.env.local`, adicione:

```
GOOGLE_APPLICATION_CREDENTIALS=config/sa-key.json
```

#### WHATSAPP_TOKEN e WHATSAPP_PHONE_ID

1. Acesse https://business.facebook.com/wa/manage/
2. Acesse "API Setup"
3. Copie seu **Access Token**
4. Copie seu **Phone Number ID**
5. Em `.env.local`:

```
WHATSAPP_TOKEN=EAAfaKajjJnkBAI...
WHATSAPP_PHONE_ID=123456789
```

#### TELEGRAM_BOT_TOKEN

1. Converse com @BotFather no Telegram
2. Use `/newbot` e siga as instruções
3. Copie o token gerado
4. Em `.env.local`:

```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

#### EMAIL/SMTP (Gmail)

**Opção 1: Gmail App Password (recomendado para testes)**

1. Acesse https://myaccount.google.com/security
2. Clique "App passwords"
3. Gere uma App Password
4. Em `.env.local`:

```
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=seu@gmail.com
EMAIL_SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SENDER_EMAIL=seu@gmail.com
```

**Opção 2: Google Service Account (para APIs)**

Use a mesma Service Account JSON do GOOGLE_APPLICATION_CREDENTIALS.

### 3. Carregar em Python

```python
from dotenv import load_dotenv
import os

load_dotenv('.env.local')
openai_key = os.getenv('OPENAI_API_KEY')
```

---

## Opção B: GitHub Actions (CI/CD)

### 1. Acessar GitHub Secrets

1. Vá para **Settings** do repositório
2. Clique em **Secrets and variables** → **Actions**
3. Clique em **New repository secret**

### 2. Adicionar Secrets

Adicione cada secret com o botão **New repository secret**:

| Secret Name | Valor | Onde obter |
|---|---|---|
| `OPENAI_API_KEY` | sk-proj-... | https://platform.openai.com/api-keys |
| `PYPI_API_TOKEN` | pypi-... | https://pypi.org/account |
| `DOCKERHUB_USERNAME` | seu-usuario | Docker Hub |
| `DOCKERHUB_TOKEN` | dckrpat-... | Docker Hub Security |
| `GMAIL_APP_PASSWORD` | xxxx xxxx xxxx | Gmail Security |

### 3. Usar em Workflows

No seu `.github/workflows/*.yml`:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
        run: pytest -v
```

---

## Opção C: Produção (Servidor/Container)

### Docker Compose

```yaml
services:
  codex:
    image: seu-usuario/codex-operator:latest
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      WHATSAPP_TOKEN: ${WHATSAPP_TOKEN}
      WHATSAPP_PHONE_ID: ${WHATSAPP_PHONE_ID}
    secrets:
      - sa-key
    volumes:
      - ./config/sa-key.json:/app/config/sa-key.json

secrets:
  sa-key:
    file: ./config/sa-key.json
```

### Heroku

```bash
heroku config:set OPENAI_API_KEY=sk-proj-...
heroku config:set WHATSAPP_TOKEN=EAAfaKajjJnkBA...
heroku config:set WHATSAPP_PHONE_ID=123456789
```

### Google Cloud Run

```bash
gcloud run deploy codex-operator \
  --set-env-vars OPENAI_API_KEY=sk-proj-... \
  --set-env-vars WHATSAPP_TOKEN=EAAfaKajjJnkBA... \
  --set-secrets sa_key=projects/PROJECT_ID/secrets/sa-key
```

---

## ✅ Checklist de Segurança

- [ ] Nunca commitar `.env.local` (já protegido por .gitignore)
- [ ] Nunca commitar `config/sa-key.json` (já protegido por .gitignore)
- [ ] Usar `secrets.SECRET_NAME` em workflows GitHub
- [ ] Rotacionar secrets a cada 90 dias
- [ ] Não compartilhar secrets por Slack/Email
- [ ] Revogar secrets expostos imediatamente

---

## Solução de Problemas

### "ModuleNotFoundError: No module named 'dotenv'"

```bash
pip install python-dotenv
```

### "OPENAI_API_KEY not found"

1. Verifique se `.env.local` existe
2. Execute `cat .env.local` e confirme que tem `OPENAI_API_KEY=...`
3. Reinicie seu terminal ou Python REPL

### "Google Service Account unauthorized"

1. Confirme que a Service Account tem permissões (Editor, Viewer, etc.)
2. Verifique se o arquivo JSON não está corrompido
3. Confirme que está no caminho correto: `config/sa-key.json`

---

## Próximas Etapas

- Leia [DEPLOYMENT.md](./DEPLOYMENT.md) para fazer deploy em produção
- Leia [SECURITY.md](./SECURITY.md) para políticas de segurança
