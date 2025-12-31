# Codex-Operator — Resumo da Versão v0.8

## O Que é o Codex-Operator?

O **Codex-Operator** é uma plataforma de automação open-source em Python, desenvolvida para **automatizar processos administrativos de pequenos negócios (MEI)** e integrá-los com múltiplos canais de comunicação.

**Propósito principal:**
- Reduzir trabalho manual (cobranças, agendamentos, emissão de notas fiscais)
- Orquestrar fluxos multi-canal (WhatsApp, Telegram, Email, Google Calendar)
- Usar LLM (OpenAI) para gerar textos, instruções e decisões automatizadas
- Ser extensível e customizável para diferentes tipos de negócio

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│               ORCHESTRATOR (CLI / src/orchestrator.py)       │
│  Subcomandos: executar, nf                                  │
│  Flags: --sales-file, --send-whatsapp, --send-telegram,    │
│         --send-email, --send-gmail, --create-event          │
└──────────────┬──────────────────────────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
   ┌───▼────┐      ┌──▼─────┐
   │ AGENTS  │      │WORKFLOWS│
   └────┬────┘      └──┬──────┘
        │              │
   ┌────┴────────────┬─┴─────────────┐
   │                 │                │
┌──▼───────┐  ┌─────▼──────┐  ┌─────▼──────────┐
│nf_agent  │  │finance_     │  │attendance_     │
│(NFS-e)   │  │agent        │  │agent           │
└──┬───────┘  └─────┬──────┘  └─────┬──────────┘
   │                │               │
   │      ┌─────────┴───────────────┘
   │      │
   │      └─────────────────┬──────────────────────┐
   │                        │                      │
   │                   ┌────▼─────┐      ┌────────▼──────┐
   │                   │INTEGRATIONS   │UTILS          │
   │                   │              │               │
   │      ┌────────────┼──────────────┼──────────────┐ │
   │      │            │              │              │ │
 ┌─▼──┬───▼───┬────────▼──┬──────┬────▼──┬────────┬─▼─▼─┐
 │WA  │Telegram│Gmail API  │Calend│SMTP   │LLM    │Logging
 │API │API     │+Service   │ar    │Email  │Client │Utils
 │    │        │Account    │API   │       │       │
 └─────┴────────┴───────────┴──────┴───────┴───────┴───────┘
```

---

## Funcionalidades Implementadas (v0.8)

### 1. **NF Agent** (Emissão de Nota Fiscal)
- Lê registros de venda (JSON)
- Valida campos obrigatórios
- Usa LLM para gerar instruções passo-a-passo
- Retorna: steps, explicação, missing_fields

### 2. **Orchestrator CLI**
Subcomandos:
- `executar --site <site> --objetivo <objetivo>` — executa automações de browser
- `nf --sales-file <path>` — processa vendas e gera NFS-e
  - `--send-whatsapp <numero>` — envia via WhatsApp
  - `--send-telegram <chat_id>` — envia via Telegram
  - `--send-email` — envia via SMTP
  - `--send-gmail` — envia via Gmail API
  - `--create-event` — cria evento no Google Calendar
  - `--save-output <arquivo>` — salva resultado em JSON

### 3. **Integrações Disponíveis**

#### WhatsApp Business API (Meta)
- Envio de mensagens text, template, documento
- Autenticação via Bearer token
- Status: ✅ Implementado e testado

#### Telegram Bot API
- Envio de mensagens, documentos, fotos
- Comandos remotos opcionais (webhook/polling)
- Status: ✅ Implementado e testado

#### Google Calendar API
- Cria eventos automaticamente
- Service Account ou OAuth
- Suporte a delegação de domínio
- Status: ✅ Implementado e testado (testes com injeção de serviço falso)

#### Gmail API
- Envio de emails via Gmail API
- Suporta:
  1. Service Account + domain-wide delegation
  2. OAuth credentials file
  3. Access token Bearer (Cloud Shell)
- Status: ✅ Implementado (requer credentials reais para teste live)

#### Email SMTP
- Envio via SMTP (Gmail, Outlook, etc.)
- Suporte a SSL (porta 465) e STARTTLS (porta 587)
- Suporte a anexos
- Status: ✅ Implementado e testado

### 4. **Testes Unitários**
- **40 testes passando** ✅
- Cobertura de:
  - NF Agent (validação, load_sales, missing_fields)
  - WhatsApp API (mocked)
  - Telegram API (mocked)
  - Google Calendar (injeção de serviço falso)
  - Gmail API (injeção de serviço falso)
  - Email SMTP (monkeypatch de smtplib)

### 5. **Documentação**
Criados:
- `docs/GOOGLE_INTEGRATION.md` — setup de Google Calendar
- `docs/GMAIL_INTEGRATION.md` — setup de Gmail API (Service Account, OAuth, Bearer token)
- `docs/EMAIL_INTEGRATION.md` — setup de SMTP

---

## Como Usar

### Instalação

```bash
# Clone/abra o workspace
cd c:\Users\Charles\Desktop\codex-operator

# Ative o virtualenv
.venv\Scripts\Activate.ps1

# Instale dependências
pip install -r requirements.txt

# Instale Google APIs opcionais
pip install google-api-python-client google-auth google-auth-httplib2
```

### Configuração (`.env`)

```env
OPENAI_API_KEY="sk-..."

# WhatsApp
WHATSAPP_TOKEN="..."
WHATSAPP_PHONE_ID="..."

# Telegram
TELEGRAM_BOT_TOKEN="..."

# Google Calendar
GOOGLE_SERVICE_ACCOUNT_FILE="/caminho/service-account.json"
GOOGLE_CALENDAR_ID="primary"

# Gmail (escolha uma opção)
GMAIL_SERVICE_ACCOUNT_FILE="/caminho/sa-key.json"  # ou
GMAIL_CREDENTIALS_FILE="/caminho/oauth-creds.json"  # ou
GMAIL_ACCESS_TOKEN="ya29..."  # access token do gcloud

# Email SMTP
EMAIL_SMTP_HOST="smtp.gmail.com"
EMAIL_SMTP_PORT="587"
EMAIL_SMTP_USER="seu-email@gmail.com"
EMAIL_SMTP_PASSWORD="app-password-16-chars"  # pragma: allowlist secret
SENDER_EMAIL="seu-email@gmail.com"
```

### Exemplos de Uso

```bash
# Gerar instruções de NFS-e
python -m src.orchestrator nf --sales-file data/test_sale.json

# Com envio por WhatsApp
python -m src.orchestrator nf --sales-file data/test_sale.json \
  --send-whatsapp "+5511999999999"

# Com envio por Telegram
python -m src.orchestrator nf --sales-file data/test_sale.json \
  --send-telegram 123456789

# Com envio de email + criação de evento
python -m src.orchestrator nf --sales-file data/test_sale.json \
  --send-email --create-event

# Com envio por Gmail API
python -m src.orchestrator nf --sales-file data/test_sale.json \
  --send-gmail

# Combo completo (multi-canal)
python -m src.orchestrator nf --sales-file data/test_sale.json \
  --send-whatsapp "+5511999999999" \
  --send-telegram 123456789 \
  --send-email \
  --create-event \
  --save-output output.json
```

### Rodar Testes

```bash
# Todos os testes
python -m pytest -q

# Apenas um arquivo
python -m pytest -q src/tests/test_nf_agent.py

# Com cobertura
python -m pytest --cov=src src/tests/
```

---

## Histórico de Versões (Git Tags)

| Versão | Mudanças |
|--------|----------|
| v0.5-nf-agent | NF Agent com validação, load_sales robusto, orchestrator CLI |
| v0.6-whatsapp | WhatsApp Business API integration |
| v0.7-telegram | Telegram Bot API integration |
| v0.8-calendar-email | Google Calendar, Gmail API, Email SMTP + testes + docs |

---

## O Que Não Faz (Limitações Atuais)

- ❌ Suporte a filas/workers (execução síncrona por padrão)
- ❌ Painel web/dashboard
- ❌ Integração com pagamentos (PagSeguro, Stripe, etc.)
- ❌ Geração automática de PDFs (NFS-e é apenas instruções)
- ❌ Autenticação/RBAC (sem controle de usuários)
- ❌ Banco de dados relacional (apenas JSON local)

---

## Próximos Passos Recomendados

### Curto Prazo
1. **Configurar credenciais reais** do Gmail/Google Calendar
2. **Implementar webhooks** para receber respostas (WhatsApp, Telegram)
3. **Adicionar suporte a filas** (Celery + Redis) para processamento assíncrono

### Médio Prazo
1. **Painel web** (FastAPI + Vue.js) para visualizar automações
2. **Integração com pagamentos** (webhook de confirmação de pagamento)
3. **Geração de PDFs** (relatórios, boletos, NFS-e)
4. **Multi-tenant** (suporte a múltiplas empresas no mesmo servidor)

### Longo Prazo
1. **Marketplace de automações** (componentes reutilizáveis)
2. **CI/CD automático** (GitHub Actions)
3. **Deployment em produção** (Docker, Cloud Run, VPS)
4. **Analytics e dashboards** (Grafana + Prometheus)

---

## Troubleshooting

### Gmail 403 "Insufficient Permission"
- Problema: Token não tem escopo `gmail.send`
- Solução: Regenerar token com escopo correto ou usar Service Account

### Email não chega (SMTP)
- Verificar `EMAIL_SMTP_HOST`, `EMAIL_SMTP_PORT`, credenciais
- Se Gmail: habilitar "Senhas de App" (2FA ativo)
- Verificar logs em `logs/automation.log`

### Testes falhando
- Executar: `pip install -r requirements.txt`
- Para Google APIs: `pip install google-api-python-client google-auth`

---

## Contato e Suporte

- **Logs**: `logs/automation.log`
- **Documentação**: `docs/`
- **Código-fonte**: `src/`

---

**Última atualização:** 17 de novembro de 2025
**Versão:** v0.8-calendar-email
**Status:** ✅ Pronto para testes e extensão
