# Fluxo – Agente de Cobrança Automática (MEI)

## Objetivo
Detectar faturas vencidas e gerar mensagens educadas de cobrança (futuro: enviar via WhatsApp).

## Entrada
- `data/mei_collections.json` — faturas abertas, status (overdue/pending)

## Processamento
- `collections_agent.find_overdue()` — filtra faturas vencidas
- `collections_agent.generate_collection_message()` — cria mensagem via LLM

## Saída
```json
{
  "count": 1,
  "results": [
    {
      "invoice_id": "inv_001",
      "message": "[Mensagem educada de cobrança]"
    }
  ]
}
```

## Rodar
```powershell
python -m src.workflows.cobranca_automatica
```

## Futuro
- Envio automático via WhatsApp/SMS
- Escalonamento: 1º aviso, 2º aviso com desconto, etc.
- Integração com sistema de pagamento
