# Fluxo – Agente Financeiro Explicador (MEI)

## Objetivo
Transformar dados desordenados de receitas/despesas em um resumo claro em português simples, destacando lucro/prejuízo e sugerindo ações de melhoria.

## Entrada
- `data/mei_finances_example.json` — receitas, despesas, período (mês)

## Processamento
- `finance_agent.load_finances()` — carrega JSON
- `finance_agent.summarize_finances()` — calcula totais + chama LLM para gerar texto explicativo

## Saída
```json
{
  "mei_id": "mei_001",
  "month": "2025-11",
  "total_revenue": 350.0,
  "total_expenses": 1700.0,
  "profit": -1350.0,
  "texto": "[Resumo explicativo do LLM]"
}
```

## Rodar
```powershell
python -m src.workflows.relatorio_financeiro
```

## Futuro
- Integração com Open Banking (ler extratos automaticamente)
- Gráficos de evolução mensal
- Alertas de anomalias (gasto muito acima da média)
