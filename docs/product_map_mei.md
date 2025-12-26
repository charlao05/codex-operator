# Mapa Produto MEI – Dores → Agentes

Conecta a pesquisa "Automatização de Rotinas para MEI" com a implementação concreta no `codex-operator`.

---

## Dores Principais (do Documento de Pesquisa)

1. **Atraso em responder clientes** (WhatsApp, redes sociais, e-mail)
2. **Agenda manual e confusa** (agendamentos sem sistema, conflitos de horário)
3. **Finanças desorganizadas** (sem controle de receitas/despesas, decisões cegas)
4. **Burocracia fiscal** (emissão de notas, DAS, DASN, dúvidas de impostos)
5. **Esquecimento de prazos** (DAS, contas, tarefas, levando a multas e cancelamento de CNPJ)

---

## Agentes Planejados (Vertical Slices)

### Agente 1: Prazos & DAS (🔴 PRIORIDADE 1 — Implementação Imediata)

**Dor que resolve:** Esquecimento de prazos fiscais (multas, cancelamento de CNPJ)

**Promessa pro MEI:**
> "Você nunca mais esquece DAS, DASN ou contas importantes. O sistema avisa com tempo de sobra."

**Fluxo técnico:**
- **Entrada:** Arquivo JSON/Spreadsheet com datas de obrigações (DAS, DASN, aluguel, água, etc.)
- **Processamento:**
  - Daily job: verifica o que vence em 30d, 7d, 1d
  - LLM: gera mensagem humanizada com aviso urgente
  - (Futuro) Playwright: abre portal de governo pra gerar DAS/boleto
- **Saída:** Notificação (CLI, WhatsApp, e-mail) + link/instruções pra pagar

**Arquivos a criar:**
- `src/agents/deadlines_agent.py` — lógica principal
- `src/workflows/prazos_criticos.py` — workflow executável
- `data/mei_obligations.json` — exemplo de obrigações

**Stack:**
- LLM (OpenAI) para gerar mensagens
- Playwright (futuro) para abrir portais do governo
- JSON simples para configuração

---

### Agente 2: Atendimento & Agendamento (🟡 PRIORIDADE 2 — Próximas 2 semanas)

**Dor que resolve:** Atraso em responder clientes + agenda manual confusa

**Promessa pro MEI:**
> "Mensagens de clientes respondidas automaticamente em minutos. Agendamentos confirmados no chat, sem WhatsApp manual."

**Fluxo técnico:**
- **Entrada:** Mensagem copiada do WhatsApp Web / Instagram Web ou API oficial
- **Processamento:**
  - LLM: analisa mensagem, detecta se é pedido de horário/informação
  - Consulta agenda JSON local
  - Gera resposta pronta + opções de horário (se aplicável)
- **Saída:**
  - Resposta pronta (para MEI copiar ou enviar direto via Playwright)
  - Confirmação de agendamento adicionado à agenda

**Arquivos a criar:**
- `src/agents/attendance_agent.py`
- `src/workflows/atendimento_automatico.py`
- `data/mei_schedule.json`

**Stack:**
- LLM para NLP e geração de respostas
- Playwright para integração com WhatsApp Web / Instagram Web (simulador ou bot official API depois)

---

### Agente 3: Financeiro Explicador (🟡 PRIORIDADE 2 — Próximas 3 semanas)

**Dor que resolve:** Finanças desorganizadas, impossibilidade de entender lucro/prejuízo

**Promessa pro MEI:**
> "Seu lucro deste mês explicado em português claro. Sabe exatamente quanto ganhou, gastou e o que pode melhorar."

**Fluxo técnico:**
- **Entrada:** JSON/Spreadsheet com receitas e despesas do mês
- **Processamento:**
  - Análise: total faturado, despesas, lucro, variação vs mês anterior
  - LLM: gera narrativa explicativa (tipo consultor falando em português simples)
- **Saída:**
  - Relatório narrativo (via CLI, e-mail, WhatsApp)
  - Alertas de anomalias (gasto acima da média, etc.)

**Arquivos a criar:**
- `src/agents/finance_agent.py`
- `src/workflows/relatorio_financeiro.py`
- `data/mei_finances_example.json`

**Stack:**
- LLM para análise e narração
- Sem Playwright necessário (processamento só de dados)

---

### Agente 4: Nota Fiscal Automática (🟠 PRIORIDADE 3 — Próximas 4 semanas)

**Dor que resolve:** Esquecimento / complicação de emitir notas, não-conformidade fiscal

**Promessa pro MEI:**
> "Toda venda gera nota fiscal automaticamente. Você não precisa lembrar, sistema faz sozinho."

**Fluxo técnico:**
- **Entrada:** Venda registrada (no sistema, via formulário, ou lido de integração)
- **Processamento:**
  - Validação de dados (cliente, valor, serviço/produto)
  - Chamada a API de NFS-e (prefeitura) ou geração de NF-e simulada
  - LLM: gera resumo/confirmação
- **Saída:**
  - NF gerada e enviada automaticamente
  - Confirmação ao MEI
  - (Futuro) Integração com sistema de cobrança

**Arquivos a criar:**
- `src/agents/nf_agent.py`
- `src/integrations/gov_api.py` — stubs para prefeitura/Receita
- `src/workflows/nota_fiscal_automatica.py`

**Stack:**
- LLM para geração de resumos
- Playwright para simular abertura de portais (MVP), depois APIs reais
- Integração com governo (via APIs onde existem)

---

### Agente 5: Cobrança Automática (🟠 PRIORIDADE 3 — Próximas 5 semanas)

**Dor que resolve:** Cliente não paga, MEI não lembra de cobrar, perde receita

**Promessa pro MEI:**
> "Cliente com atraso recebe lembrete automático. Você só se envolve se passar X dias."

**Fluxo técnico:**
- **Entrada:** Recebível (vencimento, cliente, valor)
- **Processamento:**
  - Daily job: verifica recebíveis em atraso
  - LLM: gera mensagem de cobrança educada
  - (Futuro) Envia via WhatsApp / SMS automaticamente
- **Saída:**
  - Notificação para cliente
  - Alerta ao MEI com status de cobrança

**Arquivos a criar:**
- `src/agents/collections_agent.py`
- `src/workflows/cobranca_automatica.py`

**Stack:**
- LLM para mensagens de cobrança
- Playwright + WhatsApp API (futuro)

---

## Arquitetura Geral

```
src/
├── agents/
│   ├── __init__.py
│   ├── site_agent.py                 (existente: navegação genérica)
│   ├── deadlines_agent.py             (NOVO: Prazos & DAS)
│   ├── attendance_agent.py            (NOVO: Atendimento & Agenda)
│   ├── finance_agent.py               (NOVO: Relatórios Financeiros)
│   ├── nf_agent.py                    (NOVO: Nota Fiscal Automática)
│   └── collections_agent.py           (NOVO: Cobrança Automática)
│
├── workflows/
│   ├── prazos_criticos.py             (NOVO: executa deadlines_agent)
│   ├── atendimento_automatico.py      (NOVO: executa attendance_agent)
│   ├── relatorio_financeiro.py        (NOVO: executa finance_agent)
│   ├── nota_fiscal_automatica.py      (NOVO: executa nf_agent)
│   └── cobranca_automatica.py         (NOVO: executa collections_agent)
│
├── integrations/
│   ├── __init__.py
│   ├── gov_api.py                     (NOVO: stubs para APIs governo)
│   ├── whatsapp_api.py                (NOVO: integração WhatsApp — futuro)
│   └── open_finance.py                (NOVO: integração com bancos — futuro)
│
└── data/
    └── (exemplos de JSONs)
```

---

## Modelo de Dados Básico

Cada agente trabalha com dados simples (JSON):

### Obrigações do MEI (`mei_obligations.json`)
```json
{
  "mei_id": "mei_001",
  "obligations": [
    {
      "id": "das_nov_2025",
      "type": "das",
      "name": "DAS Novembro 2025",
      "due_date": "2025-11-20",
      "estimated_value": 121.50,
      "status": "pending",
      "cnpj": "XX.XXX.XXX/0001-XX"
    },
    {
      "id": "dasn_2024",
      "type": "dasn",
      "name": "DASN Anual 2024",
      "due_date": "2025-05-31",
      "status": "pending"
    },
    {
      "id": "rent_dec_2025",
      "type": "fixed_expense",
      "name": "Aluguel Dezembro",
      "due_date": "2025-12-05",
      "estimated_value": 1500.00,
      "status": "pending"
    }
  ]
}
```

### Agenda do MEI (`mei_schedule.json`)
```json
{
  "mei_id": "mei_001",
  "appointments": [
    {
      "id": "apt_001",
      "client": "João Silva",
      "service": "Consulta",
      "date": "2025-11-18",
      "time": "14:00",
      "duration_minutes": 60,
      "status": "confirmed"
    }
  ],
  "available_slots": [
    { "date": "2025-11-18", "times": ["10:00", "15:00", "16:00"] },
    { "date": "2025-11-19", "times": ["09:00", "11:00", "14:00"] }
  ]
}
```

### Finanças do MEI (`mei_finances.json`)
```json
{
  "mei_id": "mei_001",
  "month": "2025-11",
  "revenues": [
    {
      "id": "rev_001",
      "source": "Serviço consultoria",
      "amount": 2000.00,
      "date": "2025-11-10"
    }
  ],
  "expenses": [
    {
      "id": "exp_001",
      "category": "Aluguel",
      "amount": 1500.00,
      "date": "2025-11-05",
      "paid": true
    }
  ]
}
```

---

## Próximos Passos (Implementação)

### ✅ Passo 1 – Estrutura (HOJE)
- Criar pasta `docs/` com este mapa
- Criar `src/agents/deadlines_agent.py` com stubs
- Criar `data/mei_obligations.json` de exemplo

### ✅ Passo 2 – Implementar Agente 1 (SEMANA 1)
- Implementar `deadlines_agent.py` completo
- Criar `workflows/prazos_criticos.py` executável
- Testar com JSON de exemplo
- Documentar fluxo

### ✅ Passo 3 – Agentes 2-5 (SEMANAS 2-5)
- Prioridade = nessa ordem (Atendimento → Financeiro → NF → Cobrança)
- Cada um segue o mesmo padrão de Agente 1

---

## KPIs de Sucesso (Por Agente)

| Agente | Métrica | Target |
|--------|---------|--------|
| Prazos & DAS | Tempo economizado/mês | >= 2h |
| Atendimento | Taxa de resposta automática | >= 60% |
| Financeiro | Relatórios gerados/mês | 4+ (semanal/mensal) |
| NF | Notas geradas automaticamente | 100% |
| Cobrança | Atrasos cobrados sem ação MEI | >= 80% |

---

**Status:** Ready to Code
**Próximo:** Implementar `deadlines_agent.py`
