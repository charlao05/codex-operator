# Checklist Go-Live – Codex Operator

Use este checklist antes de demonstrar para clientes ou iniciar vendas.

## 1. Ambiente e Dependências
- [ ] `.env` preenchido com todas as variáveis críticas: `OPENAI_API_KEY`, `DEFAULT_BROWSER`, Gmail (SMTP e/ou OAuth), WhatsApp, Telegram, Google Calendar.
- [ ] Ambiente virtual ativo e dependências instaladas: `pip install -r requirements.txt`.
- [ ] Navegadores Playwright instalados: `python -m playwright install`.
- [ ] Testes rápidos: `python -m src.cli test` (esperado 3/3).
- [ ] Verifique se `logs/automation.log` é atualizado após cada execução (auditoria).

## 2. Integrações de Comunicação
- [ ] **Gmail API / OAuth**: executar `python -m src.integrations.setup_gmail_oauth` e garantir `GMAIL_CREDENTIALS_FILE` apontando para o token salvo. Validar com `python -m src.orchestrator nf --sales-file data/test_sale_gmail.json --send-gmail`.
- [ ] **SMTP**: confirmar App Password ou credenciais e testar `python -m src.orchestrator nf --sales-file data/test_sale_gmail.json --send-email`.
- [ ] **Telegram Bot**: obter `TELEGRAM_TEST_CHAT_ID`, atualizar `.env` e testar `python -m src.orchestrator nf --sales-file data/test_sale_gmail.json --send-telegram <CHAT_ID>`.
- [ ] **WhatsApp Business**: revisar tokens no `.env` e, se necessário, executar script de teste em `src/integrations/test_whatsapp_send.py`.
- [ ] **Google Calendar**: verificar `GOOGLE_SERVICE_ACCOUNT_FILE` e rodar `python -m src.orchestrator nf --sales-file data/test_sale_gmail.json --create-event` (em ambiente de teste).

## 3. Workflows e Demos
- [ ] Demo web pronta: `python -m src.cli demo --demo instagram` (ou direto `python -m src.workflows.instagram_lead_express`).
- [ ] Demo de qualificação: `python -m src.cli demo --demo qualificacao` ou `python -m src.workflows.lead_qualificacao` com dados reais do nicho.
- [ ] Dry-run do agente genérico para objetivo específico do cliente: `python -m src.orchestrator executar --site instagram --objetivo "..." --dry-run`.
- [ ] Validar automações específicas do pacote (ex.: `src/workflows/cobranca_automatica.py`, etc.) com dados de exemplo e registrar resultados.

## 4. Auditoria e Comunicação
- [ ] Registrar cada execução relevante em `logs/automation.log` (já automático via `logging_utils`).
- [ ] Em tarefas sensíveis, documentar plano + comando e aguardar aprovação (vide `AGENTS.md`).
- [ ] Manter registro das execuções piloto (data, objetivo, status, incidentes) para usar como prova em vendas.
- [ ] Revisar `STATUS_EMAIL_TELEGRAM.md` e `ROADMAP_AGENCIA.md` para alinhar próximos passos comerciais antes de reuniões.

Com todos os itens acima concluídos, o stack está pronto para demonstrações ao vivo e para ser entregue como serviço recorrente.
