# Integração Gmail API

## Resumo

Cliente para envio de emails via **Gmail API** com suporte a:
- **Service Account + Domain-Wide Delegation** (recomendado para servidores)
- **OAuth 2.0 Credentials** (para contas pessoais/workspace)

Módulo: `src.integrations.gmail_api.GmailAPI`

## Configuração

### Opção 1: Service Account + Delegation (Recomendado para MEI com Workspace)

1. **No Google Cloud Console:**
   - Habilitar Gmail API
   - Criar Service Account (JSON) — fazer download do arquivo
   - Copiar email da Service Account (ex: `automacao@seu-projeto.iam.gserviceaccount.com`)

2. **No Google Admin (Workspace):**
   - Ir para `Admin Console → Security → Domain-wide delegation`
   - Autorizar a Service Account com scope: `https://www.googleapis.com/auth/gmail.send`

3. **No `.env`:**
   ```env
   GMAIL_SERVICE_ACCOUNT_FILE=/caminho/para/service-account.json
   GMAIL_DELEGATED_USER=seu-usuario@seu-dominio.com.br
   SENDER_EMAIL=noreply@seu-dominio.com.br
   ```

### Opção 2: OAuth 2.0 Credentials (Para Contas Pessoais)

1. **No Google Cloud Console:**
   - Habilitar Gmail API
   - Criar `OAuth 2.0 Desktop Application` (ou Web App)
   - Fazer download do JSON

2. **Obter Token Autorizado:**
   - Usar `google-auth-oauthlib` para autorizar via browser
   - Salvar token autorizado (requer consentimento do usuário)

3. **No `.env`:**
   ```env
   GMAIL_CREDENTIALS_FILE=/caminho/para/authorized-user-tokens.json
   SENDER_EMAIL=seu-email@gmail.com
   ```

## Uso Básico

### Via Python

```python
from src.integrations.gmail_api import GmailAPI

gmail = GmailAPI()
resultado = gmail.send_message(
    recipients=["cliente@example.com"],
    subject="Instruções para NFS-e",
    body="Segue as instruções...",
    sender="noreply@seu-dominio.com"
)
print(resultado)  # {"status": "sent", "id": "msg-id"}
```

### Via Orchestrator CLI

```bash
# Enviar via Gmail API (a partir de arquivo de venda)
python -m src.orchestrator nf --sales-file data/test_sale_gmail.json --send-gmail

# Combinar com outras integrações (Calendar + Email + Gmail)
python -m src.orchestrator nf \
  --sales-file data/test_sale_gmail.json \
  --send-gmail \
  --create-event \
  --send-email
```

## Troubleshooting

| Erro | Causa | Solução |
|------|-------|---------|
| `Invalid credentials` | Token expirado ou arquivo inválido | Refazer OAuth flow ou verificar Service Account JSON |
| `Invalid delegated user` | Usuário não delegado no Google Admin | Configurar domain-wide delegation no Google Admin |
| `Forbidden: insufficient permissions` | Service Account sem scope de email | Adicionar scope `gmail.send` na delegation |
| `Not found: message not sent` | Erro na formatação do email | Verificar `SENDER_EMAIL` e recipients |

## Custos

**Gmail API:** Gratuito (sem quotas oficiais publicadas para envio)

**Importante:** Respeitar rate limits:
- ~1.000 mensagens/dia por Service Account
- Para volume maior, implementar fila + backoff

## Referências

- [Gmail API Docs](https://developers.google.com/gmail/api)
- [Domain-Wide Delegation](https://developers.google.com/workspace/guides/create-credentials)
- [OAuth 2.0 for Desktop](https://developers.google.com/identity/protocols/oauth2/native-app)
