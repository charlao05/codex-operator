# Fluxo de Execução: Agente de Prazos & DAS

## Visão Geral

O **Agente de Prazos & DAS** resolve a dor #5 do documento MEI:

> **"Você nunca mais esquece DAS, DASN ou contas importantes. O sistema avisa com tempo de sobra."**

---

## Arquitetura de Fluxo

```
┌─────────────────────────────────────────────────────────────┐
│ ENTRADA: Arquivo JSON de Obrigações (mei_obligations.json) │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
      ┌──────────────────────────────────────┐
      │ deadlines_agent.load_obligations()   │
      │ Carrega dados de obrigações do MEI   │
      └────────────┬─────────────────────────┘
                   │
                   ▼
      ┌──────────────────────────────────────┐
      │ deadlines_agent.check_deadlines()    │
      │ Detecta o que vence em 30d, 7d, 1d  │
      │ Ordena por prioridade                │
      └────────────┬─────────────────────────┘
                   │
                   ▼
      ┌──────────────────────────────────────┐
      │ deadlines_agent.generate_reminder()  │
      │ LLM: dados estruturados → texto      │
      │ Humaniza: "Faltam 3 dias pro DAS"   │
      └────────────┬─────────────────────────┘
                   │
                   ▼
      ┌──────────────────────────────────────┐
      │ deadlines_agent.suggest_action()     │
      │ Para cada alerta: ação + URL + steps │
      └────────────┬─────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│ SAÍDA: Objeto com alertas + mensagem + ações sugeridas      │
│                                                               │
│ {                                                             │
│   "alerts": [{ id, name, days_remaining, priority, url }],  │
│   "message": "Faltam 3 dias pro DAS...",                    │
│   "actions": [{ suggested_action, url, steps }]              │
│ }                                                             │
└──────────────────────────────────────────────────────────────┘
```

---

## Passo-a-Passo Técnico

### **Passo 1: Preparação (Desenvolvimento Local)**

```bash
# Terminal PowerShell no VS Code

# 1a. Ativar venv
& C:\Users\Charles\Desktop\codex-operator\.venv\Scripts\Activate.ps1

# 1b. Verificar que os arquivos foram criados
Get-Content data/mei_obligations.json | ConvertFrom-Json | Select-Object mei_name, obligations.length

# 1c. Testar imports
python -c "from src.agents.deadlines_agent import check_deadlines; print('✅ Imports OK')"
```

**Saída esperada:**
```
mei_name            obligations.length
--------            -------------------
João Silva - Con...                   8
✅ Imports OK
```

---

### **Passo 2: Teste do Agente (Unitário)**

```bash
# Executa deadlines_agent.py com testes locais
python -m src.agents.deadlines_agent
```

**O que acontece:**
1. Carrega `data/mei_obligations.json`
2. Detecta alertas (obrigações próximas de vencer)
3. Gera mensagem com LLM
4. Loga resultado

**Saída esperada:**
```
[INFO] === Teste: Agente de Prazos & DAS ===

[INFO] 1. Carregando obrigações...
[INFO]    MEI: João Silva - Consultoria
[INFO]    Obrigações: 8

[INFO] 2. Verificando prazos próximos...
[INFO]    DAS Novembro 2025 - 3d restantes
[INFO]    DASN Anual 2024 - 195d restantes
[INFO]    ...

[INFO] 3. Gerando mensagem...
[INFO]    Seu DAS de novembro vence em 3 dias...

[INFO] 4. Sugestões de ação:
[INFO]    DAS Novembro 2025: Gerar DAS
[INFO]    URL: https://servicos.receita.federal.gov.br/
```

---

### **Passo 3: Teste do Workflow (Integrado)**

```bash
# Executa o workflow completo
python -m src.workflows.prazos_criticos
```

**Fluxo executado:**
1. ✅ Carrega obrigações
2. ✅ Detecta alertas
3. ✅ Gera mensagem (com LLM)
4. ✅ Sugere ações para os 3 mais urgentes
5. ✅ Exibe relatório formatado

**Saída esperada:**
```
============================================================
📋 RELATÓRIO DE PRAZOS - João Silva - Consultoria
============================================================

📊 RESUMO:
   Total de alertas: 5
   🔴 Críticos: 1
   ⚠️  Altos: 2

📌 PRAZOS PRÓXIMOS:

   🔴 DASN Anual 2024
      Vence: 2025-05-31 (195d)
      [sem valor]

   ⚠️  DAS Novembro 2025
      Vence: 2025-11-20 (3d)
      Valor: R$ 121.50

💬 NOTIFICAÇÃO:

[Mensagem gerada pelo LLM aqui]

✅ AÇÕES SUGERIDAS:

   1. Declarar DASN
      🔗 https://www8.receita.federal.gov.br/simplesnacional/
      Passos:
        • Entre no Simples Nacional
        • Selecione 'DASN Anual'

   2. Gerar DAS
      ...
```

---

### **Passo 4: Com Opções (Salvar Relatório)**

```bash
# Executa e salva relatório em JSON
python -m src.workflows.prazos_criticos --salvar
```

**Resultado:**
- Exibe o mesmo relatório acima
- Salva JSON completo em `logs/deadlines_report.json`

**Conteúdo do JSON:**
```json
{
  "success": true,
  "timestamp": "2025-11-17T14:30:00.123456",
  "mei_id": "mei_001",
  "mei_name": "João Silva - Consultoria",
  "total_alerts": 5,
  "critical_count": 1,
  "high_count": 2,
  "alerts": [
    {
      "obligation_id": "dasn_2024",
      "name": "DASN Anual 2024",
      "type": "dasn",
      "due_date": "2025-05-31",
      "days_remaining": 195,
      "priority": "critical",
      "estimated_value": null
    },
    ...
  ],
  "message": "[mensagem gerada pelo LLM]",
  "actions": [...]
}
```

---

### **Passo 5: Integração com Orquestrador (Futuro)**

```bash
# (Quando CLI completa estiver pronta)
orchestrator prazos --mei-id mei_001 --dry-run
```

Este comando futuramente:
1. Carrega MEI específico
2. Executa agente
3. (--dry-run) mostra alertas sem enviar notificações

---

## Fluxo de Dados (JSON → LLM → Mensagem)

### **Entrada** (`data/mei_obligations.json`)
```json
{
  "mei_id": "mei_001",
  "mei_name": "João Silva - Consultoria",
  "obligations": [
    {
      "id": "das_nov_2025",
      "name": "DAS Novembro 2025",
      "due_date": "2025-11-20",
      "estimated_value": 121.50,
      "priority": "high"
    },
    ...
  ]
}
```

### **Processamento** (Agent)

**Função 1: `check_deadlines()`**
```python
alerts = check_deadlines("data/mei_obligations.json")
# Retorna:
# [
#   DeadlineAlert(
#     name="DAS Novembro 2025",
#     days_remaining=3,
#     priority="high",
#     due_date="2025-11-20"
#   ),
#   ...
# ]
```

**Função 2: `generate_reminder_message()`**
```python
message = generate_reminder_message(alerts, mei_name="João Silva")
# Chama LLM com:
#   "Tenho esses prazos vencendo: DAS em 3 dias (R$121.50),
#    Aluguel em 18 dias (R$1500)...
#    Gere uma mensagem curta e motivadora."
#
# LLM responde:
# "Ó João! Seu DAS de novembro vence em 3 dias (dia 20).
#  Valor: R$121.50. Quer que eu abra o portal da Receita?"
```

**Função 3: `suggest_action()`**
```python
action = suggest_action(alert)
# Retorna:
# {
#   "suggested_action": "Gerar DAS",
#   "action_type": "open_portal",
#   "url": "https://servicos.receita.federal.gov.br/",
#   "steps": [
#     "Clique em 'DAS'",
#     "Insira seu CNPJ",
#     "Gere o DAS para novembro",
#     "Imprima ou pague online"
#   ]
# }
```

### **Saída** (Workflow)
```
💬 NOTIFICAÇÃO:

Ó João! Seu DAS de novembro vence em 3 dias (dia 20).
Valor: R$121.50. Quer que eu abra o portal da Receita?

✅ AÇÕES:
1. Gerar DAS
   🔗 https://servicos.receita.federal.gov.br/
   Passos:
   • Clique em 'DAS'
   • Insira seu CNPJ
```

---

## Mapeamento de Tipos de Obrigação → Ações

| Tipo | Exemplo | Ação Sugerida | URL |
|------|---------|---------------|-----|
| `das` | DAS Nov 2025 | Gerar DAS | receita.federal.gov.br |
| `dasn` | DASN Anual 2024 | Declarar DASN | simples.nacional.gov.br |
| `fixed_expense` | Aluguel | Pagar conta | (conforme contrato) |
| `utility` | Água, Luz, Internet | Pagar conta | (app do provedor) |
| `registration` | Renovação CNPJ | Manter ativo | gov.br/empresas |

---

## Próximos Passos (Após Implementação Agente 1)

### **Curto prazo (Esta semana):**
1. ✅ Criar agente de deadlines
2. ✅ Testar com dados de exemplo
3. ⏳ **Integrar com notificações** (WhatsApp stub)
4. ⏳ **Conectar ao orquestrador** CLI

### **Médio prazo (Próximas 2 semanas):**
1. ✅ Agente 2: Atendimento & Agendamento
2. ⏳ Dashboard web simples (listar alertas)
3. ⏳ Integração com WhatsApp Business API

### **Longo prazo (v0.4+):**
1. ⏳ Automação de pagamento (via Open Banking)
2. ⏳ Integração com contador online (automação de DASN)
3. ⏳ Notas fiscais automáticas

---

## Troubleshooting

### **Problema: "Arquivo não encontrado"**
```python
FileNotFoundError: data/mei_obligations.json
```
**Solução:**
```bash
# Verify arquivo existe
Test-Path data/mei_obligations.json

# Se não, crie vazio:
@{ mei_id = "mei_001"; obligations = @() } | ConvertTo-Json | Out-File data/mei_obligations.json
```

### **Problema: LLM chamada falha**
```
Error: OpenAI API key not found
```
**Solução:**
```bash
# Verifique .env
cat .env | grep OPENAI_API_KEY

# Se não existir, crie:
echo "OPENAI_API_KEY=sk-..." > .env
```

### **Problema: Mensagem vazia**
Se LLM falha, fallback automático retorna mensagem simples:
```
⚠️ IMPORTANTE - Próximos dias:
  • DAS Novembro 2025 vence em 3 dias
  • Aluguel Dezembro 2025 vence em 18 dias
```

---

## KPIs & Métricas

Após implementação, medir:

- **Alertas detectados/mês:** Target = 100% das obrigações cobertas
- **Tempo economizado/MEI:** Target >= 2h/mês (vs. verificação manual)
- **Taxa de ação:** % de MEIs que clicam em "Abrir portal" após notificação
- **Redução de multas:** Comparar antes/depois da implementação

---

**Status:** ✅ Pronto para Implementação  
**Próximo:** Executar Passo 1 no terminal
