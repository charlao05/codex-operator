# Guia Rápido: Agente de Prazos & DAS (v1.0)

## O que é?

O **Agente de Prazos & DAS** monitora automaticamente as obrigações fiscais e financeiras do MEI, alertando sobre prazos críticos.

**Problema que resolve:**
> "MEI esquece DAS, DASN, contas, levando a multas e cancelamento de CNPJ"

**Solução que oferece:**
> "Sistema avisa com tempo de sobra sobre cada obrigação vencendo, com ações prontas"

---

## Instalação (5 min)

### 1. Verificar pré-requisitos
```bash
# Terminal PowerShell
cd C:\Users\Charles\Desktop\codex-operator

# Ativar venv
& .venv\Scripts\Activate.ps1

# Verificar Python e imports
python -c "from src.agents.deadlines_agent import check_deadlines; print('✅ OK')"
```

### 2. Dados de exemplo
Os arquivos já estão criados:
- `data/mei_obligations.json` — Obrigações do MEI (editável)
- `src/agents/deadlines_agent.py` — Agente core
- `src/workflows/prazos_criticos.py` — Workflow executável

---

## Uso

### **Opção 1: Executar direto (Recomendado para começar)**

```bash
python -m src.workflows.prazos_criticos
```

**Output:**
```
============================================================
[RELATORIO] PRAZOS - João Silva - Consultoria
============================================================

[RESUMO]
   Total de alertas: 1
   [CRITICO] Críticos: 1
   [ALTO] Altos: 0

[PRAZOS PROXIMOS]
   [CRITICO] DASN Anual 2024
      Vence: 2025-05-31 (-170d)

[NOTIFICACAO]
🔴 CRÍTICO - Ação imediata necessária:
  • DASN Anual 2024 vence em -170 dias

[ACOES SUGERIDAS]
   1. Declarar DASN
      https://www8.receita.federal.gov.br/simplesnacional/
      ...
```

---

### **Opção 2: Salvar relatório em JSON**

```bash
python -m src.workflows.prazos_criticos --salvar
```

Salva em: `logs/deadlines_report.json`

Conteúdo:
```json
{
  "success": true,
  "timestamp": "2025-11-17T11:45:30",
  "mei_id": "mei_001",
  "mei_name": "João Silva - Consultoria",
  "total_alerts": 1,
  "critical_count": 1,
  "high_count": 0,
  "alerts": [
    {
      "obligation_id": "dasn_2024",
      "name": "DASN Anual 2024",
      "type": "dasn",
      "due_date": "2025-05-31",
      "days_remaining": -170,
      "priority": "critical"
    }
  ],
  "message": "...",
  "actions": [...]
}
```

---

### **Opção 3: Debug (Ver tudo)**

```bash
python -m src.workflows.prazos_criticos --debug
```

Mostra logs completos + JSON estruturado.

---

## Personalizar: Adicionar suas obrigações

### Passo 1: Editar `data/mei_obligations.json`

```json
{
  "mei_id": "seu_mei_id",
  "mei_name": "Seu Nome - Seu Negócio",
  "cnpj": "XX.XXX.XXX/0001-XX",
  "obligations": [
    {
      "id": "das_dec_2025",
      "type": "das",
      "name": "DAS Dezembro 2025",
      "due_date": "2026-01-20",
      "estimated_value": 121.50,
      "priority": "high",
      "status": "pending"
    },
    {
      "id": "aluguel_jan",
      "type": "fixed_expense",
      "name": "Aluguel Janeiro 2026",
      "due_date": "2026-01-05",
      "estimated_value": 1500.00,
      "priority": "high",
      "status": "pending"
    }
  ]
}
```

### Passo 2: Rodar
```bash
python -m src.workflows.prazos_criticos
```

---

## Integração com Orquestrador (Futuro)

```bash
# Quando CLI estiver pronta:
orchestrator prazos --mei-id mei_001 --salvar
```

---

## Arquitetura (para devs)

### Fluxo:
```
JSON (obrigações)
    ↓
check_deadlines() → lista de DeadlineAlert
    ↓
generate_reminder_message() → texto humanizado
    ↓
suggest_action() → ações + URLs
    ↓
exibir_resultado() → relatório formatado
```

### Funções principais:

**`deadlines_agent.py`**
- `load_obligations(path)` — carrega JSON
- `check_deadlines(path)` — detecta alertas
- `generate_reminder_message(alerts)` — retorna texto simples
- `generate_reminder_message_with_llm(alerts)` — LLM (opcional, mais custoso)
- `suggest_action(alert)` — retorna ação + steps

**`prazos_criticos.py`**
- `executar_prazos_criticos()` — orquestra tudo
- `exibir_resultado(resultado)` — formata output

---

## Próximas Features (Roadmap)

- ⏳ **WhatsApp Integration:** Enviar alertas via WhatsApp
- ⏳ **Email Notifications:** Alertas por e-mail
- ⏳ **Auto-pay Links:** Gerar links de pagamento direto
- ⏳ **Recurring Alerts:** Lembretes automáticos (tipo cron)
- ⏳ **Dashboard Web:** Visualizar alertas em painel

---

## Troubleshooting

**Q: "Arquivo não encontrado"**
```
FileNotFoundError: data/mei_obligations.json
```
A: Crie o arquivo com estrutura básica:
```bash
python -c "
import json
data = {
    'mei_id': 'test',
    'mei_name': 'Test MEI',
    'obligations': []
}
with open('data/mei_obligations.json', 'w') as f:
    json.dump(data, f, indent=2)
"
```

**Q: "Nenhum alerta"**
A: Verifique se há obrigações com datas próximas. Alertas são gerados para:
- Datas vencidas (days_remaining <= 0)
- Ou nos períodos 30d, 14d, 7d, 1d antes do vencimento

**Q: "Mensagem vazia"**
A: Fallback automático gera mensagem simples. Se LLM estiver configurado, será mais personalizada.

---

## Métricas de Sucesso

Após 1 mês de uso:
- ✅ 100% das obrigações monitoradas
- ✅ 0 multas por atraso
- ✅ 2+ horas economizadas/mês em verificação manual

---

**Suporte:** Consulte `docs/product_map_mei.md` e `docs/fluxo_prazos_das.md` para arquitetura completa.
