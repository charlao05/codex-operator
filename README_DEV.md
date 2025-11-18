# Codex Operator – Documentação de Desenvolvimento

**Versão Estável:** Agente de navegação com Playwright rodando no Instagram.

## Setup Local

### 1. Ativar o Ambiente Virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar Dependências

```powershell
pip install -r requirements.txt
python -m playwright install
```

### 3. Configurar .env

Crie um arquivo `.env` na raiz do projeto com:

```env
OPENAI_API_KEY=seu_api_key_aqui
DEFAULT_BROWSER=chromium
```

## Como Rodar o Agente

### Exemplo 1: Abrir Instagram e Clicar no Campo de Usuário

```powershell
.\.venv\Scripts\Activate.ps1
python -m src.orchestrator executar --site instagram --objetivo "abrir a tela de login do Instagram e clicar no campo de usuário"
```

### Dry-run (gerar plano sem abrir navegador)

Use `--dry-run` para gerar o plano via LLM sem executar o navegador (útil para testes):

```powershell
.\.venv\Scripts\Activate.ps1
python -m src.orchestrator executar --site instagram --objetivo "abrir a tela de login do Instagram" --dry-run
```

### Exemplo 2: Workflow Standalone

```powershell
.\.venv\Scripts\Activate.ps1
python -m src.workflows.exemplo_instagram_login
```

## Estrutura do Projeto

```
src/
├── browser/
│   ├── actions.py           # Ações primitivas (click, type, wait_selector, etc.)
│   ├── playwright_client.py # Inicialização do navegador
├── agents/
│   ├── site_agent.py        # Agente principal (planejar + executar)
├── utils/
│   ├── llm_client.py        # Cliente OpenAI para gerar planos
│   ├── config_loader.py     # Carregador de configs por site
│   ├── logging_utils.py     # Setup de logs
├── workflows/
│   ├── exemplo_instagram_login.py  # Exemplo simples
│   ├── instagram_lead_express.py   # (em desenvolvimento) Demo comercial
│   ├── lead_qualificacao.py        # (em desenvolvimento) Qualificação de leads
├── orchestrator.py          # CLI principal
```

## Fluxo de Execução

1. **Usuário submete objetivo** (via CLI ou código)
2. **`site_agent.planejar(site, objetivo)`** → chama LLM
   - LLM retorna JSON com `steps` (lista de ações)
   - Cada passo tem `tipo` (open_url, click, type, wait_selector, wait_seconds) e `parametros`
3. **`site_agent.executar_plano(site, plano)`** → executa no Playwright
   - Abre navegador
   - Executa cada passo em ordem
   - Fecha navegador com 15s de inspeção
4. **Logs detalhados** em `logs/automation.log`

## Tipos de Ação Suportados

- **open_url**: Abre uma URL (`parametros.url`)
- **click**: Clica num elemento (`parametros.selector`)
- **type**: Digita texto (`parametros.selector`, `parametros.text`)
- **wait_selector**: Aguarda elemento aparecer (`parametros.selector`, `parametros.timeout_ms`)
- **wait_seconds**: Aguarda N segundos (`parametros.seconds`)
- **press_key**: Pressiona uma tecla (`parametros.key`)

## Logs

Logs são salvos em `logs/automation.log` (formato rotativo, máx 2MB).

Exemplo de log:

```
2025-11-16 23:30:22 - src.agents.site_agent - INFO - Planejando objetivo 'abrir a tela de login do Instagram...'
2025-11-16 23:30:24 - src.utils.llm_client - INFO - Plano de ação gerado com sucesso: 3 passos.
2025-11-16 23:30:24 - src.agents.site_agent - INFO - Executando plano para site instagram
2025-11-16 23:30:25 - src.browser.actions - INFO - Abrindo URL: https://www.instagram.com/accounts/login/
```

## Pontos de Estabilidade

Este README marca a **versão v0.1-stable**:

- ✅ Navegador abre sem erros
- ✅ LLM gera planos em JSON válido
- ✅ Executor interpreta e executa passos
- ✅ Suporta Instagram login flow básico
- ⚠️ Requer OPENAI_API_KEY configurada
- ⚠️ Playwright exige Python 3.10+

## Próximas Evoluções

1. Config por site (YAML) para DRY
2. Workflows especializados (lead qualificação, resumo de reunião)
3. Integração com ferramentas externas (CRM, Zapier, etc.)
4. Dashboard de monitoramento de automações
