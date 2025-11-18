# Fluxo – Agente de Atendimento & Agenda (MEI)

## Objetivo
Evitar atraso em responder clientes e reduzir troca de mensagens para marcar horários. Fornecer respostas prontas e sugestões de horários ao MEI.

## Entradas
- `data/mensagens_clientes.json` — mensagens vindas do WhatsApp/Instagram
- `data/mei_schedule.json` — configuração simples de agenda do MEI

## Processamento
- `attendance_agent.processar_mensagens`:
  - Carrega a agenda e mensagens
  - Para cada mensagem:
    - Gera 3 slots sugeridos (função `sugerir_slots_basicos`)
    - Chama LLM para gerar resposta pronta (função `gerar_resposta_com_ia`)

## Saída
- Lista de respostas sugeridas (impressas no terminal)
- Arquivo de output (opcional no futuro)

## Extensões futuras
- Integração com Playwright para enviar resposta via WhatsApp Web/Instagram Web
- Confirmação automática e criação de evento em calendário
- Verificação de conflitos e ajuste dinâmico de slots

## Como rodar (PowerShell)
```powershell
& .venv\Scripts\Activate.ps1
python -m src.workflows.atendimento_automatico
```

## Observações
- O LLM chamado é o `llm_client` do projeto. A função usada tenta detectar `gerar_texto_simples` ou `gerar_resposta`; ajuste conforme seu `src/utils/llm_client.py`.
- Workflow de demo não envia mensagens; apenas gera o texto que seria enviado.
