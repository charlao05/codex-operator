# Fluxo – Agente de Nota Fiscal Automática (MEI)

## Objetivo
Gerar instruções ou automatizar emissão de notas fiscais após uma venda, evitando esquecimento.

## Entrada
- Uma venda (cliente, valor) capturada manualmente ou de integração

## Processamento

- `src.agents.nf_agent.load_sales(path)` — carrega um arquivo JSON de vendas. Retorna `None` se o arquivo não existir; lança `ValueError` se o JSON for inválido.
- `src.agents.nf_agent.prepare_invoice_steps(sales_record)` — valida campos do registro de venda, monta passos e usa o LLM para gerar uma explicação amigável.

## Saída (formato)

O retorno de `prepare_invoice_steps` tem o formato:

```json
{
  "steps": [
    "Acesse o sistema de NFS-e da prefeitura (site ou portal municipal)",
    "Faça login com sua conta MEI",
    "Preencha dados do cliente: Fulano da Silva",
    "Informe o valor: R$ 250.00",
    "Gere e salve a NFS-e (XML/PDF) e envie para o cliente, se aplicável"
  ],
  "explicacao": "Texto gerado pelo LLM explicando passo-a-passo de forma simples",
  "missing_fields": ["cliente_cnpj_cpf"]
}
```

Observações:
- `steps`: lista de passos práticos e estruturados (List[str]).
- `explicacao`: texto em linguagem natural gerado pelo LLM (string). Se o LLM falhar, há um texto fallback.
- `missing_fields`: (opcional) lista de campos obrigatórios ausentes no registro de venda; presente quando a validação detecta falta de dados.

## Comportamento de validação

- Campos verificados (suporte a chaves em pt/en): `cliente_nome` / `client_name`, `cliente_cnpj_cpf` / `client_id`, `valor_total` / `amount`, `descricao_servicos` / `description`, `data_venda` / `date`.
- Se campos estiverem ausentes, `prepare_invoice_steps` inclui `missing_fields` no retorno e registra um `warning` no log.

## Exemplo de uso (modo `__main__`)

O `nf_agent` contém um exemplo executável que demonstra `prepare_invoice_steps` com um registro de venda fake. Executar diretamente:

```powershell
& .venv\Scripts\Activate.ps1
python -m src.agents.nf_agent
```

Para uso em workflows, prefira chamar `load_sales()` e `prepare_invoice_steps()` a partir de um workflow ou do `orchestrator`.

## Rodar
```powershell
python -m src.workflows.nota_fiscal_automatica
```

## Futuro
- Integração com API de NFS-e da prefeitura (emitir direto)
- Playwright para automatizar portal web
- Integração com WhatsApp para confirmar envio
