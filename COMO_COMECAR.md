# Como Começar: 5 Passos Simples

**Tempo total: 10 minutos**

---

## Passo 1: Ativar o Ambiente (1 min)

```powershell
cd C:\Users\Charles\Desktop\codex-operator
.\.venv\Scripts\Activate.ps1
```

---

## Passo 2: Rodar a Demo Instagram (3 min)

```powershell
python -m src.cli demo --demo instagram
```

**O que vai acontecer:**
1. Navegador abre (Chromium)
2. Entra em `https://www.instagram.com/accounts/login/`
3. Aguarda o campo de usuário aparecer
4. Clica no campo
5. Fechaautomaticamente após 15 segundos

**Tempo total:** ~30 segundos

**Como você se sentirá:** "Uau, isso funciona mesmo!"

---

## Passo 3: Rodar os Testes (2 min)

```powershell
python -m src.cli test
```

**Resultado esperado:**
```
[PASSOU] Teste 1: Importacao de modulos
[PASSOU] Teste 2: Qualificacao de lead
[PASSOU] Teste 3: Config carregamento

Total: 3/3 testes passaram
```

---

## Passo 4: Qualificar um Lead Fictício (1 min)

```powershell
python -m src.workflows.lead_qualificacao
```

**Resultado esperado:**
```
{
  "classificacao": "Quente",
  "pontuacao": 9,
  "justificativa": "Alto interesse, orçamento definido, prazo curto",
  "acao_sugerida": "Ligar",
  "tags": ["imobiliaria", "venda", "luxo"]
}
```

---

## Passo 5: Ler a Documentação (3 min)

Leia na seguinte ordem:

1. **README.md** — Overview geral (2 min)
2. **ROADMAP_AGENCIA.md** — Visão comercial (3 min)
3. **README_DEV.md** — Detalhes técnicos (5 min)

---

## Pronto! O Que Fazer Agora?

### Opção 1: Entender o Código
- Abra `src/cli.py` e veja como funciona a interface
- Abra `src/agents/site_agent.py` e entenda o fluxo
- Abra `src/workflows/lead_qualificacao.py` e veja a lógica

### Opção 2: Criar um Novo Workflow
Copie `src/workflows/instagram_lead_express.py` e customize para seu caso.

### Opção 3: Começar a Vender
- Escolha um nicho (imobiliária? estética? e-commerce?)
- Pesquise 10 clientes potenciais
- Faça uma demo ao vivo com eles
- Feche o 1º cliente

---

## Comandos Rápidos

```powershell
# Ver todas as demos
python -m src.cli demo

# Rodar demo específica
python -m src.cli demo --demo instagram
python -m src.cli demo --demo qualificacao

# Rodar testes
python -m src.cli test

# Rodar workflow
python -m src.cli workflow --workflow instagram_lead_express

# Agente genérico
python -m src.cli agent --site instagram --objetivo "seu objetivo"
```

---

## Próximo Passo Recomendado

**Escolha UM dos 3:**

### 1. Se Você Quer Entender a Tecnologia
→ Leia `README_DEV.md` + explore o código

### 2. Se Você Quer Vender
→ Leia `ROADMAP_AGENCIA.md` + escolha um nicho

### 3. Se Você Quer Testar com Dados Reais
→ Crie um script similar a `lead_qualificacao.py` com seus dados

---

## FAQ Rápido

**P: Preciso de chave OpenAI para testar?**  
R: Sim, para `demo --demo qualificacao`. Para `demo --demo instagram` não precisa.

**P: Quanto tempo leva pra criar um novo workflow?**  
R: 30 minutos (cópia + adaptação).

**P: Quanto posso cobrar pra implementar uma automação?**  
R: Setup R$ 1.200-2.500 + Recorrência R$ 500-1.000/mês.

**P: Qual nicho é mais fácil começar?**  
R: Imobiliárias ou estética (têm muitos leads, querem qualificar rápido).

**P: Quantos clientes preciso pra ganhar bem com isso?**  
R: 5-10 clientes em recorrência = R$ 2.5k-10k/mês.

---

## Sucesso!

Você tem tudo pronto. Agora é só executar. 🚀

**Primeiro comando a rodar:**
```powershell
python -m src.cli demo --demo instagram
```

Faz isso agora mesmo!
