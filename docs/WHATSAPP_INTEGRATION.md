# Integração WhatsApp Business API

## Visão Geral

O CODEX-OPERATOR integra a API do WhatsApp Business (Meta) para enviar mensagens automaticamente a partir dos workflows. Você pode:

- Enviar instruções de nota fiscal
- Enviar mensagens de cobrança
- Enviar confirmações de atendimento
- Enviar notificações e alertas

## Setup Inicial

### 1. Obter Credenciais

Acesse [Meta Business Manager](https://business.facebook.com/wa/manage/) e obtenha:

1. **Token de Acesso** (`WHATSAPP_TOKEN`)
   - Gerar em: Settings → API Access Token
   - Válido por 24h a 60 dias (depende da configuração)

2. **ID do Número de Telefone** (`WHATSAPP_PHONE_ID`)
   - Encontrar em: Phone Numbers → Seu Número → ID do Número

3. **ID da Conta de Negócios** (`WHATSAPP_ACCOUNT_ID`)
   - Encontrar em: Account Settings → Business Account ID

4. **Número de Teste** (`WHATSAPP_TEST_NUMBER`)
   - Um número validado para testes (ex: +1 555 632 2287)

### 2. Configurar Variáveis de Ambiente

Edite ou crie `.env` na raiz do projeto:

```bash
WHATSAPP_TOKEN="EAAcxRRtaFvsBP6HM7ICG..."
WHATSAPP_PHONE_ID="798331036704792"
WHATSAPP_ACCOUNT_ID="1569380564419258"
WHATSAPP_TEST_NUMBER="+1 555 632 2287"
```

**⚠️ Nunca versione credenciais!** Sempre adicione `.env` ao `.gitignore`.

## Uso

### Via Orchestrator (Subcomando `nf`)

```powershell
# Enviar instruções de NF + mensagem WhatsApp
& .venv\Scripts\python.exe -m src.orchestrator nf \
  --sales-file data/test_sale.json \
  --send-whatsapp "+55119999999"

# Com opção de salvar resultado em arquivo
& .venv\Scripts\python.exe -m src.orchestrator nf \
  --sales-file data/test_sale.json \
  --send-whatsapp "+55119999999" \
  --save-output resultado.json
```

### Via Código Python

```python
from src.integrations.whatsapp_api import WhatsAppAPI, send_nf_notification

# Cliente baixo nível
api = WhatsAppAPI()
api.send_text_message("+55119999999", "Sua nota fiscal foi gerada!")

# Helper para notificação de NF
send_nf_notification(
    recipient_number="+55119999999",
    client_name="João Silva",
    nf_value=250.0,
    custom_message="Sua NFS-e está pronta!"
)
```

## Tipos de Mensagem Suportados

### 1. Texto Simples

```python
api.send_text_message("+55119999999", "Olá, sua nota foi emitida!")
```

### 2. Template Pré-aprovado

```python
api.send_template_message(
    recipient_number="+55119999999",
    template_name="hello_world",  # template criado na Meta
    template_language="pt_BR"
)
```

### 3. Documento/Arquivo

```python
api.send_document_message(
    recipient_number="+55119999999",
    document_url="https://example.com/nf_123.pdf",
    document_filename="nf_123.pdf"
)
```

## Referência da API

### Classe `WhatsAppAPI`

**Inicialização:**
```python
api = WhatsAppAPI(
    phone_number_id="798331036704792",
    access_token="EAAcxRR...",
    api_version="v22.0"  # padrão
)
```

**Métodos:**

- `send_text_message(recipient_number, message_text)` → `Dict[str, Any]`
  - Enviar mensagem de texto simples
  - Retorna resposta da API com `message_id`

- `send_template_message(recipient_number, template_name, template_language="pt_BR")` → `Dict[str, Any]`
  - Enviar mensagem usando template
  - Template deve estar pré-aprovado na conta Business

- `send_document_message(recipient_number, document_url, document_filename="documento.pdf")` → `Dict[str, Any]`
  - Enviar documento (PDF, imagem, etc)
  - `document_url` deve ser pública ou com token de acesso

### Função `send_nf_notification`

```python
send_nf_notification(
    recipient_number: str,          # Número do cliente
    client_name: str,               # Nome do cliente (usado na mensagem)
    nf_value: float,                # Valor da NF
    custom_message: Optional[str] = None  # Mensagem customizada
) → Dict[str, Any]
```

Exemplo:
```python
send_nf_notification(
    recipient_number="+55119999999",
    client_name="João Silva",
    nf_value=250.0
)
```

## Formato de Resposta

Sucesso:
```json
{
  "messages": [
    {
      "id": "wamid.HBEUGh23h2837h",
      "message_status": "accepted"
    }
  ],
  "contacts": [
    {
      "input": "+55119999999",
      "wa_id": "5511999999999"
    }
  ]
}
```

Erro (ex: credenciais inválidas):
```json
{
  "error": "Client error '401 Unauthorized' for url '...'",
  "status": "failed"
}
```

## Troubleshooting

| Erro | Causa | Solução |
|------|-------|---------|
| `401 Unauthorized` | Token expirado ou inválido | Regenerar token em Meta Business Manager |
| `400 Bad Request` | Formato de número incorreto | Usar formato: `+55 DDD NNNNNNNNN` |
| `403 Forbidden` | Conta Business sem acesso à API | Verificar permissões em Meta Business Manager |
| `Connection failed` | Sem conexão com internet | Verificar conectividade |

## Boas Práticas

1. **Nunca versione tokens** — sempre use `.env` e `.gitignore`
2. **Teste antes de produção** — use `WHATSAPP_TEST_NUMBER`
3. **Valide números** — antes de enviar, confirme o formato `+55 DDD NNNNNNNNN`
4. **Rate limiting** — a Meta tem limites de envio (respeite para não ser bloqueado)
5. **Trate erros** — sempre capture exceções ao enviar mensagens
6. **Log tudo** — o módulo registra sucesso/erro automaticamente

## Testes Unitários

Rodar testes:
```powershell
& .venv\Scripts\python.exe -m pytest src/tests/test_whatsapp_api.py -v
```

Resultado esperado: 6/6 tests passed

## Próximas Melhorias

- [ ] Suporte a mídia (imagens, áudio, vídeo)
- [ ] Webhook para receber mensagens (two-way communication)
- [ ] Suporte a múltiplos templates
- [ ] Dashboard web para visualizar histórico de mensagens
- [ ] Rate limiting local para evitar bloqueios
- [ ] Integração com CRM para tracking de contactos

## Referências

- [Meta WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages)
- [Meta Business Manager](https://business.facebook.com/)
- [Webhook Listeners](https://developers.facebook.com/docs/whatsapp/webhooks/components)
