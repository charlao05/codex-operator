# Dashboard KPI - Google Sheets Template

Cole este conteúdo em um Google Sheet e atualize diariamente:

## ABA 1: RESUMO EXECUTIVO
```
DATA: [auto, =TODAY()]

WAVE 1
- Total enviados: 5
- Abertos: 0 (0%)
- Clicks: 0 (0%)
- Respostas: 0 (0%)
- Demos agendadas: 0
- Taxa de conversão email→demo: 0%

WAVE 2 (quando rodado)
- Total enviados: 5
- Abertos: 0 (0%)
- Clicks: 0 (0%)
- Respostas: 0 (0%)
- Demos agendadas: 0

MÉTRICAS GERAIS
- CAC estimado: R$ [envios × custo por email]
- LTV estimado: R$ [preço × lifetime em meses]
- Ciclo vendas (email→pagamento): [X dias]
- MRR (Monthly Recurring Revenue): R$ 0
- Churn rate: 0%

STATUS
- Landing: LIVE ✓
- Calendly: [STATUS]
- CRM: [CONECTADO/NÃO]
- Pagamentos: [CONFIGURADO/NÃO]
```

## ABA 2: LEADS EM TEMPO REAL
```
| Data | Nome | Email | Fonte | Status | Demo Agendada | Data Demo | Trial Iniciado | Converteu |
|------|------|-------|-------|--------|---------------|-----------|----------------|-----------|
| 5/12 | Mariana | contato@... | Wave1 | Enviado | Não | - | - | - |
| 5/12 | Juliana | atendimento@... | Wave1 | Enviado | Não | - | - | - |
```

## ABA 3: ANÁLISE A/B
```
WAVE 2 A/B SPLIT
Variante A (Direto): [X enviados, Y abertos, Z respostas]
Variante B (ROI): [X enviados, Y abertos, Z respostas]

Vencedor: [A ou B]
Incremento: [X%]
Recomendação: Usar vencedor para Wave 3 e além
```

## ABA 4: PIPELINE DE VENDAS
```
| Contato | Status | Dias no Pipeline | Próximo Ação | Data Ação |
|---------|--------|------------------|-------------|-----------|
| Mariana | Lead (Enviado) | 1 | Follow-up 48h | 6/12 |
| ... | ... | ... | ... | ... |
```

## ABA 5: FINANCEIRO
```
Receita:
- MRR atuais: R$ 0
- Potencial (se 3 conversões): R$ 735/mês
- Projeção 90 dias: R$ [3 × R$245]

Custos:
- Infraestrutura: R$ 0 (Netlify free + Scripts)
- Domínio: R$ 0 (opcional, +R$ 50/ano se tiver)
- Calendly: R$ 0 (free) ou R$ 10-12/mês (Pro)
- Stripe/PagSeguro: 2.9% + R$ 0.30 por transação

Resultado:
- Investimento até break-even: ~R$ 100
- Dias até break-even: ~20 dias (1 cliente × R$245)
```

---

Acesse: https://docs.google.com/spreadsheets (criar novo)
Compartilhe comigo para eu preencher atualizações conforme entram dados.
