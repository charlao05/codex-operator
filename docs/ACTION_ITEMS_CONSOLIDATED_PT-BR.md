# 🎯 NEXUS - PONTOS DE AÇÃO CONSOLIDADOS
## Documento Definitivo de Tarefas Requeridas

**Data:** 04 de janeiro de 2026  
**Status:** 🔴 REQUER AÇÃO DO USUÁRIO (Charles)  
**Responsabilidade:** Ação imediata para manter cronograma  

---

## ⚠️ RESUMO EXECUTIVO

Você tem **9 pontos críticos** que requerem sua ação direta. Não posso executar algumas delas sem dados de segurança reais:

| # | Tarefa | Status | Prioridade | Responsável |
|---|--------|--------|-----------|-------------|
| 1 | Gerar Google Service Account (sa-key.json) | ❌ Pendente | 🔴 ALTA | Charles |
| 2 | Gerar AdSense Service Account | ❌ Pendente | 🔴 ALTA | Charles |
| 3 | Gerar Gmail App Password | ❌ Pendente | 🔴 ALTA | Charles |
| 4 | Gerar Stripe LIVE Keys | ❌ Pendente | 🟡 MÉDIA | Charles |
| 5 | Gerar Clerk LIVE Keys | ❌ Pendente | 🟡 MÉDIA | Charles |
| 6 | Testar Google Calendar Integration | ⏳ Bloqueado | 🟡 MÉDIA | Comet (após 1,2,3) |
| 7 | Testar Google AdSense Integration | ⏳ Bloqueado | 🟡 MÉDIA | Comet (após 1,2) |
| 8 | Testar Email SMTP | ⏳ Bloqueado | 🟡 MÉDIA | Comet (após 3) |
| 9 | Deploy em GCP Cloud Run | ⏳ Pendente | 🟡 MÉDIA | Comet (após 1-5) |

---

## 🚨 TAREFAS QUE SÓ VOCÊ (CHARLES) PODE FAZER

### 1️⃣ GOOGLE SERVICE ACCOUNT (Para Google Calendar)

**O que é:** Arquivo JSON de autenticação para acessar o Google Calendar

**Passo-a-passo:**
1. Acesse: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Clique em "Create Service Account"
3. Nome: `nexus-calendar-sa`
4. Clique em "Create and Continue"
5. Conceda role: "Editor" (temporário, reduzir depois)
6. Clique em "Continue"
7. Na aba "Keys", clique "Add Key" → "Create new key"
8. Selecione "JSON"
9. Clique em "Create"
10. O arquivo `sa-key.json` será baixado

**Próximo:** Fazer upload em `config/sa-key.json`

---

### 2️⃣ GOOGLE ADSENSE SERVICE ACCOUNT

**O que é:** Arquivo JSON para acessar Google AdSense API

**Passo-a-passo:**
1. Acesse: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Clique em "Create Service Account"
3. Nome: `nexus-adsense-sa`
4. Clique em "Create and Continue"
5. Conceda role: "Admin" de AdSense (se disponível) ou "Editor"
6. Clique em "Continue"
7. Na aba "Keys", clique "Add Key" → "Create new key"
8. Selecione "JSON"
9. Clique em "Create"
10. O arquivo será baixado (renomear para `adsense-sa-key.json`)

**Próximo:** Fazer upload em `config/adsense-sa-key.json`

---

### 3️⃣ GMAIL APP PASSWORD

**O que é:** Senha especial do Gmail para uso em aplicações

**Passo-a-passo:**
1. Acesse sua conta Google: https://myaccount.google.com
2. Vá para "Segurança" (menu esquerdo)
3. Ative "Verificação em 2 etapas" (se não estiver ativada)
4. Volte a "Segurança"
5. Role para baixo até "Senhas de app"
6. Selecione "Mail" e "Windows Computer"
7. Clique em "Generate"
8. Copie a senha de 16 caracteres

**Guardar em:** .env como `EMAIL_SMTP_PASSWORD=xxx`

---

### 4️⃣ STRIPE LIVE KEYS (Para Produção)

**O que é:** Chaves de produção do Stripe (não teste)

**Passo-a-passo:**
1. Acesse: https://dashboard.stripe.com/apikeys
2. Mude de "Test mode" para "Live mode"
3. Copie:
   - `STRIPE_SECRET_KEY` (começa com `sk_live_`)
   - `STRIPE_PUBLISHABLE_KEY` (começa com `pk_live_`)

**Guardar em:** .env + GCP Secret Manager

---

### 5️⃣ CLERK LIVE KEYS

**O que é:** Chaves de produção do Clerk Auth

**Passo-a-passo:**
1. Acesse: https://dashboard.clerk.com
2. Vá para "API Keys"
3. Copie:
   - Secret Key
   - Publishable Key

**Guardar em:** .env + GCP Secret Manager

---

## 🤖 TAREFAS QUE COMET VAI EXECUTAR

### A) Fazer Upload dos Arquivos JSON

**Quando estiver pronto:**
- [ ] Arquivo `sa-key.json` (Google Service Account)
- [ ] Arquivo `adsense-sa-key.json` (AdSense)

**Comet vai fazer:**
```bash
# Copiar para pasta certa
cp ~/Downloads/sa-key.json config/
cp ~/Downloads/adsense-sa-key.json config/

# Validar
python scripts/validate_config.py
```

---

### B) Testar Integrações

**Google Calendar:**
```bash
curl -X GET http://localhost:8000/api/google/calendar/health
# Esperado: { \"status\": \"healthy\", \"calendars\": [...] }
```

**Google AdSense:**
```bash
curl -X GET http://localhost:8000/api/google/adsense/health
# Esperado: { \"status\": \"healthy\", \"earnings\": [...] }
```

**Email SMTP:**
```bash
curl -X POST http://localhost:8000/api/email/test \
  -H \"Content-Type: application/json\" \
  -d '{\"to\": \"seu_email@gmail.com\", \"subject\": \"Test\"}'
# Esperado: { \"status\": \"sent\" }
```

---

### C) Deploy em GCP Cloud Run

**Quando tudo estiver OK:**
```bash
# 1. Criar secrets em GCP
gcloud secrets create STRIPE_SECRET_KEY --data-file=-
gcloud secrets create OPENAI_API_KEY --data-file=-
# ... (13 secrets no total)

# 2. Deploy
gcloud run deploy nexus-api \
  --source . \
  --region southamerica-east1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars=...

# 3. Validar
curl https://nexus-api.run.app/health
```

---

## 📋 CHECKLIST DE CONCLUSÃO

### Fase 1: Coleta de Credenciais (Charles) - 🔴 PRIORITÁRIO

- [ ] **Google Service Account** baixado e pronto
  - Arquivo: `sa-key.json`
  - Caminho: Enviar para Comet
  
- [ ] **Google AdSense Service Account** baixado e pronto
  - Arquivo: `adsense-sa-key.json`
  - Caminho: Enviar para Comet
  
- [ ] **Gmail App Password** copiado
  - Guardar: Privado (não compartilhar)
  - Enviar: Via .env para Comet
  
- [ ] **Stripe LIVE Keys** copiadas (se pronto para produção)
  - Secret Key: `sk_live_...`
  - Publishable Key: `pk_live_...`
  
- [ ] **Clerk LIVE Keys** copiadas (se pronto para produção)
  - Secret Key
  - Publishable Key

### Fase 2: Validação Local (Comet) - 🟡 BLOQUEADO

- [ ] Fazer upload dos arquivos JSON
- [ ] Validar configuração local
- [ ] Testar Google Calendar
- [ ] Testar Google AdSense
- [ ] Testar Email SMTP
- [ ] Testar Stripe (pagamentos)
- [ ] Testar Clerk (autenticação)

### Fase 3: Deploy Produção (Comet + Charles) - 🟡 BLOQUEADO

- [ ] Ativar GCP Secret Manager
- [ ] Sincronizar 13 secrets
- [ ] Deploy em Cloud Run
- [ ] Testar endpoints em produção
- [ ] Configurar monitoring
- [ ] Go-live!

---

## 📞 PRÓXIMOS PASSOS

### ✋ O QUE COMET PRECISA DE VOCÊ (Imediato)

1. **Gerar Google Service Account (sa-key.json)** → Enviar arquivo
2. **Gerar Google AdSense SA (adsense-sa-key.json)** → Enviar arquivo
3. **Gerar Gmail App Password** → Copiar e guardar (privado)
4. **Opcionalmente:** Gerar Stripe LIVE + Clerk LIVE (para produção depois)

### ⚡ O QUE COMET FAZ SOZINHO

Quando receber os arquivos/senhas acima, Comet vai:
- ✅ Fazer upload dos JSONs para `config/`
- ✅ Atualizar `.env` com credenciais
- ✅ Testar todas as integrações
- ✅ Gerar scripts de deployment
- ✅ Deploy em Cloud Run
- ✅ Validar em produção

---

## 🎯 TIMELINE

| Fase | Quando | O que | Quem |
|------|--------|-------|------|
| 1 | HOJE (04/jan) | Coletar credenciais | Charles |
| 2 | HOJE+1h | Upload e validação | Comet |
| 3 | HOJE+2h | Testar integrações | Comet |
| 4 | HOJE+3h | Deploy produção | Comet |
| 5 | HOJE+4h | Go-live NEXUS | Charles |

---

## 🔐 SEGURANÇA - IMPORTANTE

⚠️ **NÃO COMPARTILHE NUNCA:**
- Arquivo `sa-key.json`
- Arquivo `adsense-sa-key.json`
- Senhas de app
- STRIPE_SECRET_KEY
- OPENAI_API_KEY

✅ **SEGURO COMPARTILHAR:**
- Nomes de arquivos
- Instruções de como gerar
- Mensagens de confirmação ("pronto")
- Erros de validação (sem dados sensíveis)

---

## 🆘 DÚVIDAS?

Qualquer problema com a geração das credenciais, avise-me e Comet ajuda a diagnosticar.

**Status:** Aguardando suas ações (Charles)  
**Próximo:** Começar com Google Service Account
