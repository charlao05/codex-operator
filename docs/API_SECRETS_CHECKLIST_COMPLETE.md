# 🔐 API & SECRETS CHECKLIST COMPLETO

**Data:** 04/01/2026  
**Status:** Documentação Oficial - 13 APIs em 6 categorias  
**Críticos:** 5 (Stripe, OpenAI, Google Cloud, Clerk, Database)

---

## 📊 RESUMO EXECUTIVO

Para integração total **Codex-Operator + NEXUS**, configure **13 APIs/Secrets** em **6 categorias**.

**Status Atual:**
- ✅ **Configurados:** 1/13 (Stripe LIVE pronto)
- ⏳ **Pendentes:** 12/13
- 🔴 **Críticos:** 5

---

## 1️⃣ PAGAMENTOS & MONETIZACAO

### Stripe Payment API
**Prioridade:** 🔴 CRÍTICA | **Status:** ✅ PRONTO

**Variáveis:**
```bash
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx          # Backend (já tem LIVE)
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx     # Frontend
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx        # Webhooks
STRIPE_MODE=test                                  # test ou live
```

**Testar:** `curl http://localhost:8000/api/payments/health`

**Armazenar no Secret Manager:**
```bash
gcloud config set project agendamento-n8n-476415
echo -n "sk_live_SUA_CHAVE" | gcloud secrets create stripe-secret-key --data-file=- --replication-policy=automatic
echo -n "pk_live_SUA_CHAVE" | gcloud secrets create stripe-publishable-key --data-file=- --replication-policy=automatic
```

**Custo:** Gratuito (% por transação)

---

### Google AdSense API
**Prioridade:** 🟡 ALTA | **Status:** ⏳ PENDENTE

**Variáveis:**
```bash
GOOGLE_ADSENSE_SA_KEY=config/adsense-sa-key.json     # Service Account JSON
GOOGLE_ADSENSE_ACCOUNT_ID=ca-pub-xxxxxxxxxxxxx       # Seu Account ID
```

**Onde obter:** https://www.google.com/adsense/start/

**Custo:** Gratuito

---

## 2️⃣ INTELIGENCIA ARTIFICIAL

### OpenAI API
**Prioridade:** 🔴 CRÍTICA | **Status:** ⏳ PENDENTE

**Variáveis:**
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

**Onde obter:** https://platform.openai.com → API keys

**Custo:** Pay-as-you-go (~$0.002/1K tokens GPT-4o mini)

---

## 3️⃣ AUTENTICACAO & AUTORIZACAO

### Clerk Authentication API
**Prioridade:** 🔴 CRÍTICA | **Status:** ⏳ PENDENTE

**Variáveis:**
```bash
CLERK_SECRET_KEY=sk_live_xxxxxxxxxxxxx           # Backend
CLERK_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxx      # Frontend
```

**Onde obter:** https://dashboard.clerk.com → Applications → API Keys

**Custo:** Gratuito até 10.000 MAU

---

### JWT Secret
**Prioridade:** 🟡 ALTA | **Status:** ⏳ PENDENTE

**Gerar (PowerShell):**
```powershell
-join ((1..32) | ForEach-Object { '{0:X2}' -f (Get-Random -Max 256) })
```

**Variável:**
```bash
JWT_SECRET=a1b2c3d4e5f6...64caracteres...xyz
```

---

## 4️⃣ COMUNICACAO & NOTIFICACOES

### Gmail (SMTP)
**Prioridade:** 🟡 ALTA | **Status:** ⏳ PENDENTE

**Variáveis:**
```bash
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=seu_email@gmail.com
EMAIL_SMTP_PASSWORD=xxxx xxxx xxxx xxxx    # App Password (16 dígitos)
```

**Como obter App Password:**
1. https://myaccount.google.com/security
2. Ativar "Verificação em 2 etapas"
3. Gerar "Senhas de app" para Email

**Custo:** Gratuito

---

### WhatsApp Business API
**Prioridade:** 🟢 MÉDIA | **Status:** ⏳ OPCIONAL

**Variáveis:**
```bash
WHATSAPP_TOKEN=EAAxxx...
WHATSAPP_PHONE_ID=xxxxxx
WHATSAPP_ACCOUNT_ID=xxxxxx
```

**Custo:** Gratuito até 1.000 conversas/mês

---

### Telegram Bot API
**Prioridade:** 🟢 MÉDIA | **Status:** ⏳ OPCIONAL

**Variáveis:**
```bash
TELEGRAM_BOT_TOKEN=xxxxxx:xxxxxxxxxxxxxx
TELEGRAM_TEST_CHAT_ID=123456789
```

**Como obter:** Conversar com @BotFather no Telegram

**Custo:** Gratuito

---

## 5️⃣ GOOGLE CLOUD PLATFORM

### Google Cloud Service Account
**Prioridade:** 🟡 ALTA | **Status:** ⏳ PENDENTE

**Variáveis:**
```bash
GOOGLE_SERVICE_ACCOUNT_FILE=config/sa-key.json
GOOGLE_CALENDAR_ID=primary
GOOGLE_CLOUD_API_KEY=AIzaSyxxxxxxxxxxxxxxxx
```

**APIs para ativar:**
- Google Calendar API
- Gmail API
- AdSense Management API
- Google Drive API

**Custo:** Gratuito (free tier generoso)

---

## 6️⃣ BANCO DE DADOS & INFRAESTRUTURA

### Database URL
**Prioridade:** 🔴 CRÍTICA | **Status:** ⏳ PENDENTE

**Desenvolvimento (SQLite):**
```bash
DATABASE_URL=sqlite:///./test.db
```

**Produção (Cloud SQL):**
```bash
DATABASE_URL=postgresql://user:pass@/dbname?host=/cloudsql/project:region:instance
```

**Custo:** 
- SQLite: Gratuito
- Cloud SQL: ~$7-25/mês

---

### Google Secret Manager
**Prioridade:** 🟡 ALTA (Produção) | **Status:** ⏳ PENDENTE

**Como usar:**
```bash
# Criar secret
echo -n "seu_valor" | gcloud secrets create nome-secret --data-file=- --replication-policy=automatic

# Acessar secret
SEU_ENV=$(gcloud secrets versions access latest --secret="nome-secret")
```

**Custo:** Gratuito até 10.000 acessos/mês

---

## ✅ CHECKLIST RÁPIDO DE EXECUCAO

### Nível 1 - CRÍTICO (Sistema não funciona sem)
- [ ] `STRIPE_SECRET_KEY` - Pagamentos
- [ ] `STRIPE_PUBLISHABLE_KEY` - Frontend
- [ ] `OPENAI_API_KEY` - IA/Automação
- [ ] `CLERK_SECRET_KEY` - Autenticação
- [ ] `DATABASE_URL` - Banco de dados

### Nível 2 - IMPORTANTE
- [ ] `GOOGLE_SERVICE_ACCOUNT_FILE` - Google APIs
- [ ] `EMAIL_SMTP_USER` + `EMAIL_SMTP_PASSWORD` - Emails
- [ ] `JWT_SECRET` - Sessões
- [ ] `GOOGLE_ADSENSE_SA_KEY` - AdSense

### Nível 3 - OPCIONAL
- [ ] `WHATSAPP_TOKEN` - WhatsApp (opcional)
- [ ] `TELEGRAM_BOT_TOKEN` - Telegram (opcional)
- [ ] `STRIPE_WEBHOOK_SECRET` - Webhooks (depois)

---

## 🔒 SEGURANÇA - REGRAS OBRIGATÓRIAS

### ❌ NUNCA FAÇA
1. Commit de secrets no Git (`.env` em `.gitignore`)
2. Expor chaves LIVE em público
3. Compartilhar chaves por email/chat

### ✅ SEMPRE FAÇA
1. Use variáveis de ambiente (via `.env` ou Secret Manager)
2. Rode chaves de teste (`sk_test_`) em dev
3. Use Secret Manager em produção

---

## 💰 ESTIMATIVA DE CUSTOS

**Desenvolvimento (Grátis):** ~$0-5/mês
**Produção (Pequena):** ~$40-125/mês + % transações
**Produção (Média 1K users):** ~$300-500/mês + % transações

---

## 📞 RECURSOS OFICIAIS

- **Stripe:** https://stripe.com/docs
- **OpenAI:** https://platform.openai.com/docs
- **Clerk:** https://clerk.com/docs
- **Google Cloud:** https://cloud.google.com/docs
- **AdSense:** https://support.google.com/adsense

---

**Criado:** 04/01/2026  
**Última atualização:** 04/01/2026 - 12:15 -03  
**Status:** ✅ COMPLETO - PRONTO PARA IMPLEMENTAÇÃO
