# Integração Telegram Bot API

## Visão Geral

O CODEX-OPERATOR integra a Telegram Bot API (gratuita) para enviar mensagens automaticamente. Você pode:

- ✅ Enviar instruções de nota fiscal
- ✅ Enviar mensagens de cobrança
- ✅ Enviar confirmações de atendimento
- ✅ Enviar documentos (PDFs, imagens)
- ✅ Usar formatação Markdown ou HTML
- ✅ Enviar para usuários individuais ou grupos

**Vantagem:** Telegram é 100% gratuito, rápido e confiável!

## Setup Inicial

### 1. Criar um Bot no Telegram

1. Abra o Telegram e procure por **@BotFather**
2. Digite `/start`
3. Digite `/newbot`
4. Siga as instruções (nome e username do bot)
5. Você receberá um **Token** (salve-o!)

Exemplo de token: `123456789:ABCDEFGhIjklmnOpqrsTUvwXYz_aBcDeF`

### 2. Obter seu Chat ID

Existem 2 formas:

**Opção A: Usar @userinfobot**
1. Abra o Telegram e procure por **@userinfobot**
2. Clique em `/start`
3. Você verá seu ID de usuário (ex: `987654321`)

**Opção B: Enviar mensagem para o bot**
1. Inicie uma conversa com seu bot (procure pelo username)
2. Envie qualquer mensagem
3. Acesse `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
4. Procure por `"chat":{"id":123456789}`

### 3. Configurar Variáveis de Ambiente

Edite ou crie `.env` na raiz do projeto:

```bash
TELEGRAM_BOT_TOKEN="123456789:ABCDEFGhIjklmnOpqrsTUvwXYz_aBcDeF"
TELEGRAM_TEST_CHAT_ID="987654321"
```

**⚠️ Nunca versione credenciais!** Sempre adicione `.env` ao `.gitignore`.

## Uso

### Via Orchestrator (Subcomando `nf`)

```powershell
# Enviar instruções de NF + mensagem Telegram
& .venv\Scripts\python.exe -m src.orchestrator nf \
  --sales-file data/test_sale.json \
  --send-telegram 987654321

# Enviar para WhatsApp E Telegram simultaneamente
& .venv\Scripts\python.exe -m src.orchestrator nf \
  --sales-file data/test_sale.json \
  --send-whatsapp "+55119999999" \
  --send-telegram 987654321

# Com opção de salvar resultado
& .venv\Scripts\python.exe -m src.orchestrator nf \
  --sales-file data/test_sale.json \
  --send-telegram 987654321 \
  --save-output resultado.json
```

### Via Código Python

```python
from src.integrations.telegram_api import TelegramAPI, send_nf_notification

# Cliente básico - enviar mensagem simples
api = TelegramAPI()
api.send_message(
    987654321,
    "*Atenção!* Sua nota fiscal foi gerada!\n\n"
    "Valor: R$ 250,00",
    parse_mode="Markdown"
)

# Helper para notificação de NF
send_nf_notification(
    chat_id=987654321,
    client_name="João Silva",
    nf_value=250.0
)
```

## Tipos de Mensagem Suportados

### 1. Texto Simples (com Markdown)

```python
api.send_message(
    987654321,
    "*Olá!* Sua nota foi emitida.\n"
    "Valor: `R$ 250,00`",
    parse_mode="Markdown"
)
```

**Formatação Markdown suportada:**
- `*texto*` → **negrito**
- `_texto_` → *itálico*
- `` `código` `` → código inline
- `[Link](https://example.com)` → link

### 2. Documento/Arquivo

```python
api.send_document(
    987654321,
    "https://example.com/nf_123.pdf",
    caption="*Sua Nota Fiscal* (NFS-e)",
    parse_mode="Markdown"
)
```

### 3. Foto/Imagem

```python
api.send_photo(
    987654321,
    "https://example.com/comprovante.jpg",
    caption="Comprovante de pagamento"
)
```

## Referência da API

### Classe `TelegramAPI`

**Inicialização:**
```python
api = TelegramAPI(bot_token="123456:ABC-DEF...")
# ou deixe vazio para usar TELEGRAM_BOT_TOKEN do .env
api = TelegramAPI()
```

**Métodos:**

- `send_message(chat_id, message_text, parse_mode="Markdown")` → `Dict[str, Any]`
  - Enviar mensagem de texto
  - Suporte a Markdown, HTML ou MarkdownV2
  - Retorna: `{"ok": True, "result": {"message_id": 123, ...}}`

- `send_document(chat_id, document_url, caption=None, parse_mode="Markdown")` → `Dict[str, Any]`
  - Enviar documento (PDF, DOC, etc)
  - `document_url` deve ser pública

- `send_photo(chat_id, photo_url, caption=None, parse_mode="Markdown")` → `Dict[str, Any]`
  - Enviar foto/imagem
  - Suporta JPEG, PNG, GIF, WEBP

### Função `send_nf_notification`

```python
send_nf_notification(
    chat_id: str,               # ID do chat (número ou @username)
    client_name: str,           # Nome do cliente
    nf_value: float,            # Valor da NF
    custom_message: str = None  # Mensagem customizada (opcional)
) → Dict[str, Any]
```

**Exemplo:**
```python
send_nf_notification(
    chat_id=987654321,
    client_name="João Silva",
    nf_value=250.0,
    custom_message="Sua nota foi emitida! ✅"
)
```

## Formato de Resposta

### Sucesso
```json
{
  "ok": true,
  "result": {
    "message_id": 42,
    "chat": {"id": 987654321},
    "text": "Sua mensagem aqui",
    "date": 1700252400
  }
}
```

### Erro
```json
{
  "ok": false,
  "error_code": 400,
  "description": "Bad Request: chat not found"
}
```

## Troubleshooting

| Erro | Causa | Solução |
|------|-------|---------|
| `chat not found` | Chat ID inválido | Verificar chat ID com @userinfobot |
| `Unauthorized` | Token inválido/expirado | Regenerar token com @BotFather |
| `message text is empty` | Texto vazio | Fornecer mensagem válida |
| `Connection timeout` | Sem internet | Verificar conectividade |
| `Bad Request` | Formato inválido | Verificar parse_mode (Markdown/HTML) |

## Boas Práticas

1. **Nunca versione tokens** — sempre use `.env`
2. **Teste com seu ID** — antes de enviar para clientes
3. **Use Markdown** — para mensagens mais formatadas
4. **Captura de erros** — sempre trate exceções
5. **Logs** — o módulo registra sucesso/erro automaticamente
6. **Respeite usuários** — não spam, respeite privacidade
7. **Grupo vs Individual** — use chat_id do grupo para listas

## Exemplo Completo

```python
from src.integrations.telegram_api import TelegramAPI

api = TelegramAPI()

# Mensagem formatada
msg = """
*📋 Nota Fiscal Emitida*

Cliente: `João Silva`
Valor: `R$ 250,00`
Data: `17/11/2025`

[Abrir NFS-e](https://prefeitura.sp.gov.br/nfs-e/123)
"""

result = api.send_message(987654321, msg, parse_mode="Markdown")

if result["ok"]:
    print(f"✅ Mensagem enviada! ID: {result['result']['message_id']}")
else:
    print(f"❌ Erro: {result['description']}")
```

## Próximas Melhorias

- [ ] Suporte a inline buttons (teclado com botões)
- [ ] Webhook para receber mensagens (two-way)
- [ ] Suporte a grupos e channels
- [ ] Rate limiting local
- [ ] Dashboard de histórico de mensagens

## Referências

- [Telegram Bot API Official Docs](https://core.telegram.org/bots/api)
- [BotFather](https://t.me/BotFather) — criar e gerenciar bots
- [userinfobot](https://t.me/userinfobot) — obter seu ID
- [Markdown Guide](https://core.telegram.org/bots/style#markdown-style)

## Comparação: WhatsApp vs Telegram

| Aspecto | WhatsApp | Telegram |
|---------|----------|----------|
| **Custo** | Pago (Meta) | ✅ Grátis |
| **Setup** | Complexo (Business Account) | ✅ Simples (@BotFather) |
| **Velocidade** | Média | ✅ Rápida |
| **Rate Limits** | Rigorosos | ✅ Flexíveis |
| **Formatação** | Limitada | ✅ Completa (Markdown) |
| **Documentos** | Sim | ✅ Sim (+ mídias) |
| **Grupos** | Sim | ✅ Sim |

**Recomendação:** Use Telegram para testes e comunicação geral, WhatsApp para alertas críticos de clientes.
