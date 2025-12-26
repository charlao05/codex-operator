# Codex Operator - Agência de Automação com IA

**Motor de automação web + IA para gerar receita recorrente.**

Este projeto é uma **máquina de automações** que transforma objetivos em linguagem natural em fluxos automatizados, usando:
- **Playwright** para navegar na web
- **OpenAI** para planejar ações com IA
- **Python** para orquestração
- **Workflows** especializados em casos de marketing/vendas

---

## Requisitos

- Python 3.10+ (recomendado 3.12)
- API Key da OpenAI
- Playwright (navegadores)

---

## Setup Rápido (Windows)

```powershell
# 1. Criar ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Instalar navegadores Playwright
python -m playwright install

# 4. Configurar .env
copy .env.example .env
# Editar .env e adicionar sua OPENAI_API_KEY
```

---

## Como Usar

### Modo 1: Demonstração Comercial (RECOMENDADO PARA COMEÇAR)

Ver todas as demos disponíveis:
```powershell
python -m src.cli demo
```

Rodar demo específica (Instagram Login):
```powershell
python -m src.cli demo --demo instagram
```

Rodar demo de Qualificação de Lead:
```powershell
python -m src.cli demo --demo qualificacao
```

### Modo 2: Rodar Testes Automatizados

```powershell
python -m src.cli test
```

Resultado esperado: **3/3 testes passam**

### Modo 3: Rodar Workflow Específico

```powershell
python -m src.cli workflow --workflow instagram_lead_express
```

### Modo 4: Agente Genérico (Avançado)

```powershell
python -m src.cli agent --site instagram --objetivo "abrir a tela de login e clicar no campo de usuario"
```

Ou usar o orquestrador direto:
```powershell
python -m src.orchestrator executar --site instagram --objetivo "seu objetivo aqui"
```

---

## Workflows Disponíveis

### 1. Instagram Lead Express
Demonstra automação de acesso ao painel de login do Instagram.
- **Tempo:** ~30 segundos
- **Pacote comercial:** Setup R$ 1.200 + Recorrência R$ 500/mês
- **Código:** `src/workflows/instagram_lead_express.py`

### 2. Lead Qualificação Automática
Classifica leads em Quente/Morno/Frio usando IA.
- **Tempo:** ~5 segundos por lead
- **Pacote comercial:** Setup R$ 1.500 + Recorrência R$ 600/mês
- **Código:** `src/workflows/lead_qualificacao.py`

---

## Estrutura do Projeto

```
codex-operator/
├── README.md                           # Este arquivo
├── README_DEV.md                       # Documentação técnica
├── ROADMAP_AGENCIA.md                  # Visão comercial
├── requirements.txt                    # Dependências
├── .env                                # Variáveis de ambiente
│
├── config/
│   └── sites/
│       └── instagram.yaml              # Configuração por site
│
├── src/
│   ├── cli.py                          # Interface de linha de comando
│   ├── orchestrator.py                 # Orquestrador principal
│   ├── browser/
│   │   ├── actions.py                  # Ações primitivas (7 tipos)
│   │   └── playwright_client.py        # Setup do navegador
│   ├── agents/
│   │   └── site_agent.py               # Agente (planejar + executar)
│   ├── utils/
│   │   ├── llm_client.py               # Cliente OpenAI
│   │   ├── config_loader.py            # Configurações por site
│   │   └── logging_utils.py            # Setup de logs
│   ├── workflows/
│   │   ├── instagram_lead_express.py   # Demo comercial
│   │   └── lead_qualificacao.py        # Qualificação de leads
│   └── tests/
│       └── test_workflows.py           # Testes automatizados
│
└── data/ + logs/                       # Resultados de execução
```

---

## Packaging & Deployment

Breve resumo das entregas para comercializar o projeto:

- CI: GitHub Actions que roda `pre-commit`, `pytest`, constrói wheel e gera imagem Docker (arquivo `.github/workflows/ci.yml`).
- Empacotamento: `pyproject.toml` presente para gerar wheel via `python -m build`.
- Container: `Dockerfile` mínimo para testes e deploy. Customize `CMD`/entrypoint para sua aplicação.
- Segurança: `credentials.template.json` e `config/sa-key.template.json` mantêm placeholders; `detect-secrets` baseline está gerado.

Para criar artefatos localmente:

```powershell
python -m pip install --upgrade pip build
pip install -r requirements.txt
python -m build
docker build -t codex-operator:local .
```

Para publicar: criar tag semântico (ex: `v1.0.0`), criar release no GitHub e publicar wheel/Docker image conforme suas credenciais de registro.


## Ações Suportadas

O agente consegue executar estes tipos de ação automaticamente:

| Ação | Descrição | Exemplo |
|------|-----------|---------|
| `open_url` | Abre uma URL | `open_url` → `https://www.instagram.com/accounts/login/` |
| `wait_selector` | Aguarda elemento aparecer | `wait_selector` → `input[name='username']` |
| `click` | Clica em um elemento | `click` → `button[type='submit']` |
| `type` | Digita texto em campo | `type` → username/email/senha |
| `press_key` | Pressiona tecla (Enter, Tab, etc) | `press_key` → `Enter` |
| `wait_seconds` | Aguarda N segundos | `wait_seconds` → `2` |

---

## Fluxo de Execução

```
1. Usuario define objetivo em linguagem natural
              ↓
2. `site_agent.planejar()` → Chama OpenAI
              ↓
3. OpenAI retorna JSON com passos
              ↓
4. `site_agent.executar_plano()` → Executa cada passo no Playwright
              ↓
5. Navegador fecha automaticamente (com 15s pra inspeção)
              ↓
6. Resultado registrado em logs/automation.log
```

---

## Exemplos de Uso

### Exemplo 1: Qualificar um Lead

```python
from src.workflows.lead_qualificacao import qualificar_lead

lead = {
    "nome": "João Silva",
    "email": "joao@email.com",
    "interesse": "Venda de imovel",
    "orcamento": "R$ 800.000",
    "prazo": "20 dias"
}

resultado = qualificar_lead(lead)
print(resultado)
# Retorna: {"classificacao": "Quente", "pontuacao": 9, ...}
```

### Exemplo 2: Rodar Fluxo Completo de Login do Instagram

```python
from src.workflows.instagram_lead_express import executar_lead_express

resultado = executar_lead_express()
# Abre navegador, navega para Instagram, clica no campo de usuario
# Fecha automaticamente apos 15 segundos
```

---

## Documentação Adicional

- **`README_DEV.md`** - Desenvolvimento: setup técnico, tipos de ação, logs
- **`ROADMAP_AGENCIA.md`** - Estratégia comercial: nichos, pacotes, preços
- **`CHECKLIST_CONCLUSAO.md`** - Roadmap executado com sucesso

---

## Logs

Todos os logs são salvos em `logs/automation.log` com:
- Timestamps precisos
- Nível de severidade (INFO, WARNING, ERROR)
- Rastreamento completo de execução
- Format rotativo (máx 2MB por arquivo)

Exemplo:
```
2025-11-17 00:26:36 - src.workflows.lead_qualificacao - INFO - Qualificando lead: {'nome': 'Maria Santos', ...}
2025-11-17 00:26:39 - src.workflows.lead_qualificacao - INFO - Lead qualificado como: Quente (pontuação: 9)
```

---

## Testes

Rodar suite de testes:
```powershell
python -m src.cli test
```

Ou com pytest diretamente:
```powershell
pytest src/tests/test_workflows.py -v
```

---

## Modelo de Negócio

### Pacote 1: Instagram Lead Express
- **Setup:** R$ 1.200 (configuração, testes, documentação)
- **Recorrência:** R$ 500/mês (manutenção, suporte, otimização)

### Pacote 2: Lead Qualificação Automática
- **Setup:** R$ 1.500
- **Recorrência:** R$ 600/mês

### Pacote 3: Fluxo Completo
- **Setup:** R$ 2.500
- **Recorrência:** R$ 1.000/mês

---

## Próximos Passos

1. **Executar uma demo:** `python -m src.cli demo --demo instagram`
2. **Rodar testes:** `python -m src.cli test`
3. **Escolher um nicho** (imobiliária, estética, e-commerce)
4. **Pesquisar clientes** naquele nicho
5. **Fazer pitch** com demo ao vivo
6. **Fechar 1º cliente** e criar case de sucesso

---

## Ressalvas Importantes

- Respeite sempre os **Termos de Uso** das plataformas automatizadas
- Para ações sensíveis (postar, deletar, editar dados críticos), **sempre peça aprovação explícita** antes de executar
- Use responsavelmente e transparentemente com os clientes

---

## Status

✅ **Production-Ready v0.2-comercial**

- Infraestrutura técnica: 100% completa
- Workflows especializados: 2 testados com sucesso
- Documentação técnica + comercial: 100% completa
- Modelo de negócio: definido com preços

Pronto para começar a vender automações de IA. 🚀

---

**Data:** 17 de novembro de 2025
**Desenvolvedor:** Charles (com Codex Copilot)
**Status:** Ativo e em evolução
