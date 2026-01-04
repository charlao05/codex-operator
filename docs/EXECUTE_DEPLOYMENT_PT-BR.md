# 🚀 GUIA DE EXECUÇÃO - DEPLOY NEXUS COMPLETO

**Data:** 03 de Janeiro de 2026  
**Versão:** 1.0  
**Responsável:** Charles Rodrigues Silva  
**Email:** charles.rsilva05@gmail.com  
**Telefone:** +55 (27) 9 9999-9999

---

## 📋 RESUMO

Este guia fornece instruções passo-a-passo para executar o deployment completo da plataforma NEXUS em Google Cloud Platform.

**O que será criado:**
- ✅ Google Cloud Project configurado (agendamento-n8n-476415)
- ✅ Cloud SQL PostgreSQL com High Availability
- ✅ Google Secret Manager com 7 secrets configurados
- ✅ Cloud Run com API NEXUS em produção
- ✅ Monitoramento e alertas 24/7
- ✅ Health checks e smoke tests automatizados

**Tempo estimado:** 45-60 minutos

---

## 📋 CHECKLIST PRÉ-REQUISITOS

Antes de começar, verifique se você tem:

### Software necessário
- [ ] **PowerShell 7+** instalado
  - Windows: Já vem com PowerShell
  - Mac/Linux: `brew install powershell` ou acesse https://microsoft.com/powershell
- [ ] **Google Cloud SDK (gcloud CLI)** instalado
  - https://cloud.google.com/sdk/docs/install
- [ ] **Docker Desktop** instalado e rodando
  - https://www.docker.com/products/docker-desktop
- [ ] **Git** instalado
  - `git --version` deve retornar versão

### Acesso e credenciais
- [ ] Conta Google/Gmail ativa
- [ ] Acesso a Google Cloud Platform (GCP)
- [ ] Projeto GCP `agendamento-n8n-476415` com billing ativado
- [ ] Acesso de admin ao projeto (roles: Compute Admin, Cloud SQL Admin, Secret Manager Admin)
- [ ] Chaves API:
  - [ ] Stripe Secret Key (sk_live_...)
  - [ ] OpenAI API Key (sk-proj-...)
  - [ ] Clerk Secret Key (sk_live_ ou sk_test_)
  - [ ] Clerk Publishable Key (pk_live_ ou pk_test_)

### Acesso ao repositório
- [ ] Você tem permissão para fazer push no `https://github.com/charlao05/codex-operator`
- [ ] SSH ou credenciais Git configuradas

---

## 🔧 PASSO 1: PREPARAR AMBIENTE

### 1.1 Abra PowerShell (Admin)

**Windows:**
1. Pressione `Win + X`
2. Selecione "Windows PowerShell (Admin)"

**Mac/Linux:**
```bash
open -a Terminal
# ou use seu terminal preferido
```

### 1.2 Clone o repositório

```powershell
git clone --branch hardening/datetime-detect-secrets https://github.com/charlao05/codex-operator.git
cd codex-operator
```

**Verificar:**
```powershell
ls scripts/DEPLOY_NEXUS_COMPLETE.ps1
# Deve mostrar: DEPLOY_NEXUS_COMPLETE.ps1
```

### 1.3 Autentique no Google Cloud

```powershell
# Login interativo
gcloud auth login

# Application default login (para Docker/Cloud)
gcloud auth application-default login

# Definir projeto padrão
gcloud config set project agendamento-n8n-476415

# Verificar
gcloud config list
```

---

## 🎯 PASSO 2: EXECUTAR O SCRIPT

### 2.1 Modo DRY-RUN (RECOMENDADO PRIMEIRO)

**Simula a execução sem fazer alterações reais:**

```powershell
./scripts/DEPLOY_NEXUS_COMPLETE.ps1 `
  -ProjectId "agendamento-n8n-476415" `
  -Region "us-central1" `
  -DryRun $true
```

**Saída esperada:**
```
=== NEXUS Complete Deployment ===
INFO: Project: agendamento-n8n-476415
INFO: Region: us-central1
INFO: Dry Run: True

INFO: Setting GCP Project to agendamento-n8n-476415...
SUCCESS: Project set
...
```

**Se vir erros:**
- `gcloud: not found` → Instale Google Cloud SDK
- `Permission denied` → Verifique credenciais (`gcloud auth login`)
- `Project not found` → Verifique ID do projeto

### 2.2 Modo COMPLETO (EXECUÇÃO REAL)

**Cria toda a infraestrutura e faz o deploy:**

```powershell
./scripts/DEPLOY_NEXUS_COMPLETE.ps1 `
  -ProjectId "agendamento-n8n-476415" `
  -Region "us-central1"
```

**⚠️ IMPORTANTE:**
- Isso vai CRIAR recursos reais e gerar custos
- Leia a tela antes de confirmar qualquer operação
- Tempo: ~45-60 minutos

**Saída esperada ao final:**
```
=== Deployment Complete ===
SUCCESS: NEXUS API is now live!
INFO: Next steps:
INFO:  1. Verify API endpoint at https://<cloud-run-url>
...
```

---

## 🔐 PASSO 3: CONFIGURAR SECRETS

### 3.1 Acessar Secret Manager

```powershell
# Abrir console do GCP
gcloud secrets list
```

**Ou via console web:**
1. Acesse: https://console.cloud.google.com/security/secret-manager
2. Selecione projeto `agendamento-n8n-476415`

### 3.2 Adicionar valores reais

```powershell
# Stripe Secret Key
gcloud secrets versions add stripe-secret-key --data-file=- <<< "sk_live_YOUR_ACTUAL_KEY"

# OpenAI API Key
gcloud secrets versions add openai-api-key --data-file=- <<< "sk-proj-YOUR_ACTUAL_KEY"

# Clerk Secret Key
gcloud secrets versions add clerk-secret-key --data-file=- <<< "sk_live_YOUR_ACTUAL_KEY"

# Clerk Publishable Key
gcloud secrets versions add clerk-publishable-key --data-file=- <<< "pk_live_YOUR_ACTUAL_KEY"
```

---

## ✅ PASSO 4: VALIDAR DEPLOYMENT

### 4.1 Obter URL do Cloud Run

```powershell
gcloud run services describe nexus-api --platform managed --region us-central1 --format="value(status.url)"
```

**Saída esperada:**
```
https://nexus-api-xxxxx-uc.a.run.app
```

### 4.2 Testar health endpoint

```powershell
# Substituir URL real
$url = "https://nexus-api-xxxxx-uc.a.run.app/health"
Invoke-WebRequest -Uri $url
```

**Resposta esperada (200 OK):**
```json
{
  "status": "ok"
}
```

### 4.3 Verificar logs

```powershell
gcloud run logs read nexus-api --region us-central1 --limit 50
```

---

## 📊 PASSO 5: MONITORAMENTO

### 5.1 Acessar dashboard

https://console.cloud.google.com/monitoring?project=agendamento-n8n-476415

### 5.2 Criar alertas

1. Monitoring > Alert policies > Create policy
2. Configurar para:
   - Error rate > 1%
   - P95 latency > 1s
   - CPU > 70%

---

## 🐛 TROUBLESHOOTING

| Erro | Causa | Solução |
|------|-------|----------|
| `gcloud: command not found` | Google Cloud SDK não instalado | Instale de https://cloud.google.com/sdk/docs/install |
| `Permission denied (403)` | Acesso insuficiente ao projeto | Peça admin para conceder roles |
| `Project not found (404)` | ID do projeto incorreto | Verifique em GCP Console |
| `Docker build failed` | Docker não rodando | `docker ps` deve funcionar |
| `Health check returns 500` | API com erro | `gcloud run logs read nexus-api` |

---

## 📞 SUPORTE

Em caso de dúvidas ou problemas:

1. Verifique os logs:
   ```powershell
   gcloud run logs read nexus-api --region us-central1 --limit 100
   ```

2. Contacte:
   - **Charles Rodrigues Silva**
   - Email: charles.rsilva05@gmail.com
   - Telefone: +55 (27) 9 9999-9999

3. Verifique documentação:
   - Cloud Run: https://cloud.google.com/run/docs
   - Cloud SQL: https://cloud.google.com/sql/docs
   - Secret Manager: https://cloud.google.com/secret-manager/docs

---

## ✨ PRÓXIMAS AÇÕES

Apos o deployment com sucesso:

1. [ ] Configurar domínio customizado (opcional)
2. [ ] Setup Google Play Store listing
3. [ ] Setup Apple App Store listing
4. [ ] Ativar HTTPS + security headers
5. [ ] Backup e disaster recovery plan
6. [ ] Compliance checklist (LGPD/GDPR/CCPA)

---

**Documento criado:** 03/01/2026  
**Última atualização:** 03/01/2026 - 22:45 -03  
**Status:** ✅ Pronto para execução
