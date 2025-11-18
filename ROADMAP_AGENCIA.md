# Roadmap: Agência de Automação com IA

## ✅ Fase 1: Infra Técnica (COMPLETA)

### 1.1. Ponto Estável Congelado
- [x] Documentação de setup em `README_DEV.md`
- [x] Instruções claras: como rodar agente, workflows, testes
- [x] Histórico de versões (v0.1-stable marcado)

### 1.2. Motor de Ações Expandido
- [x] `src/browser/actions.py`
  - ✅ `abrir_url(page, url)`
  - ✅ `clicar(page, selector)`
  - ✅ `digitar(page, selector, texto)`
  - ✅ `esperar_selector(page, selector, timeout_ms)`
  - ✅ `type_text(page, selector, text)` [alias melhorado]
  - ✅ `press_key(page, key)` [novo]
  - ✅ `wait_seconds(page, seconds)` [novo]

- [x] `src/agents/site_agent.py`
  - ✅ `planejar(site, objetivo)` - gera plano via LLM
  - ✅ `executar_plano(site, plano)` - executa passos
  - ✅ Suporta formato LLM: `{"tipo": "open_url", "parametros": {...}}`
  - ✅ Suporta formato legado: `{"acao": "abrir_url", "url": "..."}`
  - ✅ Mapeia todos os tipos de ação (open_url, click, type, press_key, wait_selector, wait_seconds)

### 1.3. Configuração por Site (Base pra Pacotes)
- [x] `config/sites/instagram.yaml`
  - Nome, URLs base
  - Seletores CSS (usuario, senha, botão login)
  - Timeouts customizáveis
  
- [x] `src/utils/config_loader.py`
  - Suporta novo padrão: `config/sites/{site}.yaml`
  - Fallback: `config/sites.yaml` (compatibilidade)
  - Carrega automaticamente por site

### 1.4. Prompt do LLM Especializado
- [x] `src/utils/llm_client.py`
  - System prompt focado em automação de **marketing + vendas + atendimento**
  - Documentação clara de tipos de ação suportados
  - Regras obrigatórias: sempre responde com JSON
  - Contexto do site passado como parâmetro

---

## ✅ Fase 2: Workflows de Negócio (COMPLETA)

### 2.1. Demo Comercial (Instagram Lead Express)
- [x] `src/workflows/instagram_lead_express.py`
  - Abre painel de login do Instagram
  - Clica no campo de usuário
  - Fluxo simples e estável
  - **Uso:** Demo pro cliente / prova de conceito

### 2.2. Fluxo de Qualificação (Sem Navegador)
- [x] `src/workflows/lead_qualificacao.py`
  - `qualificar_lead(dict)` → classifica em Quente/Morno/Frio
  - Retorna: classificação, pontuação, justificativa, ação sugerida, tags
  - `qualificar_lote_leads(list)` → processa múltiplos leads
  - **Uso:** Processar respostas de formulário, CRM, etc.

---

## 📋 Fase 3: Produto + Comercial (ROADMAP FUTURO)

### 3.1. Pacotes de Automação a Vender

#### Pacote 1: "Instagram Lead Express" (MVP)
```
Setup (one-time): R$ 1.200
├─ Configurar account do cliente
├─ Adaptar seletores/URLs
├─ Testes end-to-end
├─ Documentação de uso

Recorrência (mensal): R$ 500
├─ Manutenção do fluxo
├─ Ajuste de prompts (IA)
├─ Suporte 1h resposta
├─ Relatório mensal simples
```

#### Pacote 2: "Lead Qualificação Automática"
```
Setup (one-time): R$ 1.500
├─ Integração com CRM/formulário
├─ Calibração de critérios
├─ Testes com dados reais

Recorrência (mensal): R$ 600
├─ Processamento mensal
├─ Ajuste de critérios
├─ Análise + otimização
```

#### Pacote 3: "Fluxo Completo" (Qualificação + Resposta)
```
Setup (one-time): R$ 2.500
├─ Integração de todo pipeline
├─ Respostas automáticas personalizadas

Recorrência (mensal): R$ 1.000
├─ Monitoramento full-stack
├─ Otimizações
├─ Relatório detalhado
```

### 3.2. Nichos-Alvo (Com Priorização)

**Prioridade 1 (Próximos 30 dias):**
- Imobiliárias (qualificação de leads de site/formulário)
- Estética/Clínicas (agendamento automático)

**Prioridade 2 (Próximos 60 dias):**
- E-commerce (follow-up de carrinho abandonado)
- Academias (qualificação + proposta de trial)

### 3.3. Estratégia Comercial (5 Passos)

1. **Domínio da Ferramenta** ✅
   - Você sabe usar o codex-operator
   - Consegue demonstrar em tempo real
   - Gera confiança no cliente

2. **Definição de Nicho + Fluxo** (próximo)
   - Escolher 1 nicho (ex: imobiliárias)
   - Definir 1 fluxo de alto valor (ex: qualificação de leads)

3. **Abordagem Consultiva** (próximo)
   - Auditoria gratuita (30min)
   - Demo ao vivo do agente
   - Oferta clara: setup + recorrência

4. **Prova de Conceito** (próximo)
   - Rodas fluxo com dados reais do cliente (1 semana)
   - Mostra resultados: tempo economizado, leads qualificados
   - Build trust → fecha venda

5. **Implementação + Suporte** (próximo)
   - Setup completo
   - Documentação + treinamento (30min)
   - Suporte mensal / otimização

---

## 🎯 Próximos Passos (Recomendados)

### Imediato (Hoje/Amanhã):
1. Testar `instagram_lead_express.py` com dados reais
2. Testar `lead_qualificacao.py` com exemplo de lead
3. Gravar vídeo de tela (2-3 min) do agente em ação → asset de marketing

### Curto Prazo (1-2 semanas):
1. Escolher 1 nicho-alvo (imobiliária? estética?)
2. Pesquisar 5-10 clientes potenciais nesse nicho
3. Montar pitch simples (1 página) + demo
4. Abordagem consultiva com 3 clientes

### Médio Prazo (1-2 meses):
1. Fechar 1º cliente
2. Criar case de sucesso (antes/depois, economia, resultados)
3. Escalar pra outros nichos
4. Documentar processos de implementação (playbooks)

---

## 📊 Métricas de Sucesso

- [ ] 1 workflow rodando sem erro (instagram_lead_express)
- [ ] 1 fluxo de qualificação testado (lead_qualificacao)
- [ ] 3 clientes em pipeline
- [ ] 1º cliente fechado
- [ ] 1º case de sucesso publicado
- [ ] MRR (Monthly Recurring Revenue) > R$ 1.000/mês

---

## 🚀 Visão Final

Você transformou o "agente de navegador" em uma **máquina de gerar automações de marketing**. 

Isso significa:
- Qualquer fluxo repetitivo de web + formulário vira produto
- Cada novo cliente = novo "pacote customizado" (baixo custo de adaptação)
- Oportunidade de escalar com mais agentes (ou equipe)
- Recorrência mensal de manutenção + otimização = receita previsível

**Você está pronto pra vender. A infraestrutura técnica está em pé. Agora é comercial.** 💪

---

## 📂 Estrutura Final do Projeto

```
codex-operator/
├── README.md                           # Público (visão geral)
├── README_DEV.md                       # Técnico (desenvolvimento)
├── README_AGENCIA.md                   # (Futuro) Comercial
├── requirements.txt                    # Dependências
├── .env                                # Variáveis de ambiente
├── config/
│   └── sites/
│       └── instagram.yaml              # Configuração Instagram
├── src/
│   ├── orchestrator.py                 # CLI principal
│   ├── browser/
│   │   ├── actions.py                  # Ações primitivas (7 funções)
│   │   └── playwright_client.py        # Setup do navegador
│   ├── agents/
│   │   └── site_agent.py               # Agente (planejar + executar)
│   ├── utils/
│   │   ├── llm_client.py               # Cliente OpenAI
│   │   ├── config_loader.py            # Carregador de configs
│   │   └── logging_utils.py            # Setup de logs
│   └── workflows/
│       ├── exemplo_instagram_login.py  # Simples (legado)
│       ├── instagram_lead_express.py   # Demo comercial ✨
│       └── lead_qualificacao.py        # Qualificação de leads ✨
└── data/
    └── (resultados, logs, etc.)
```

---

## 💡 Pensamentos Finais

Este roadmap conecta **tecnologia + produto + comercial** de forma integrada:

1. **Tecnologia** está sólida: agente consegue navegar web, chamar LLM, executar automações
2. **Produto** está pronto: workflows especializados em casos de uso reais
3. **Comercial** está mapeado: nichos, pacotes, preços, estratégia de abordagem

A pergunta agora é: **qual nicho você ataca primeiro?** 🎯
