# 🚀 GUIA RÁPIDO - CUSTOMIZAÇÃO DE DOCUMENTOS

**Data:** 2 de janeiro de 2026
**Status:** Pronto para usar

---

## 📋 O QUE FOI FEITO

Foram criados **3 arquivos Python + 1 template**:

| Arquivo | Função | Status |
|---------|--------|--------|
| `extract_placeholders.py` | Extrai todos os 1.235 placeholders | ✅ Executado |
| `customize_documents.py` | Substitui placeholders automaticamente | ✅ Pronto |
| `CUSTOMIZATION_VALUES.md` | Template para preencher com seus dados | ✅ Criado |
| `PLACEHOLDERS_REPORT.csv` | Relatório CSV com todos os placeholders | ✅ Gerado |

---

## 🎯 FLUXO DE CUSTOMIZAÇÃO (4 PASSOS)

### PASSO 1: Preencher Dados ⏳
```
📝 Abrir: CUSTOMIZATION_VALUES.md
🖊️  Preencher com seus valores reais
💾 Salvar o arquivo
```

**Tempo estimado:** 30-45 minutos

**Campos obrigatórios:**
- [x] Nome da empresa
- [x] CNPJ
- [x] 5 pessoas (IC, Security, Comms, Tech, CTO)
- [x] 5 emails dessas pessoas
- [x] 5 telefones
- [x] URLs de produção
- [x] Links GCP/GitHub
- [x] Contatos regulatórios

### PASSO 2: Rodar Script ✅
```bash
cd c:/Users/Charles/Desktop/codex-operator
python customize_documents.py
```

**Tempo estimado:** <1 minuto

**O que acontece:**
1. Script lê `CUSTOMIZATION_VALUES.md`
2. Extrai todos os valores preenchidos
3. Substitui todos os placeholders nos 5 documentos
4. Salva documentos finalizados em `DOCUMENTOS_FINALIZADOS/`

### PASSO 3: Revisar Documentos 👀
```
📂 Abrir pasta: DOCUMENTOS_FINALIZADOS/
📄 Revisar cada arquivo
✅ Confirmar substituições corretas
```

**Tempo estimado:** 15-20 minutos

**O que procurar:**
- [x] Nenhum placeholder `[xxx]` restante
- [x] Nenhum `[MISSING: ...]` ou `[EMPTY: ...]`
- [x] URLs corretas
- [x] Nomes reais preenchidos
- [x] Emails/telefones corretos

### PASSO 4: Deploy ✅
```
1. Copiar arquivos de DOCUMENTOS_FINALIZADOS/
2. Substituir originais em Downloads/
3. Fazer commit no GitHub
4. Publicar em repositório privado
```

---

## 📊 ESTATÍSTICAS

```
Total de placeholders: 1.235
Placeholders críticos: 88

Distribuição:
├─ DEPLOY_STANDARDS.md: 195 (7 críticos)
├─ GO_LIVE_CHECKLIST.md: 596 (15 críticos)
├─ SECURITY_COMPLIANCE_MATRIX.md: 98 (30 críticos)
├─ INCIDENT_RESPONSE_PLAYBOOK.md: 226 (14 críticos)
└─ MONITORING_ALERTING_RUNBOOK.md: 120 (22 críticos)
```

**Depois da customização:**
```
Placeholders restantes: 0
Documentos prontos: 5 ✅
Status: 100% PRODUCTION-READY
```

---

## 🔍 VALIDAÇÃO

O script automaticamente:

1. ✅ **Verifica** se CUSTOMIZATION_VALUES.md existe
2. ✅ **Alerta** se valores estão incompletos
3. ✅ **Conta** número de substituições
4. ✅ **Marca** valores faltantes com `[MISSING: ...]`
5. ✅ **Gera** relatório de substituições

---

## 🛠️ FERRAMENTAS CRIADAS

### 1. extract_placeholders.py
**Função:** Encontra todos os placeholders nos 5 documentos

```bash
python extract_placeholders.py
```

**Saída:**
- Console: Resumo de placeholders por documento
- CSV: `PLACEHOLDERS_REPORT.csv` com todos os detalhes

---

### 2. customize_documents.py
**Função:** Customiza automaticamente os 5 documentos

```bash
python customize_documents.py
```

**Entrada:** `CUSTOMIZATION_VALUES.md` (preenchido)

**Saída:** 5 documentos customizados em `DOCUMENTOS_FINALIZADOS/`

---

### 3. CUSTOMIZATION_VALUES.md
**Função:** Template para preencher com seus dados

**Seções:**
- Empresa (nome, CNPJ, domínio)
- Equipe (5 pessoas + backups)
- Links (GitHub, GCP, Slack)
- URLs de produção
- Contatos regulatórios
- App Store configs
- On-call rotation
- Assinaturas digitais

---

## ⚡ ATALHOS

### Comando completo (uma linha):
```bash
cd c:/Users/Charles/Desktop/codex-operator && python customize_documents.py
```

### Verificar se arquivo existe:
```bash
ls -la CUSTOMIZATION_VALUES.md
```

### Contar placeholders restantes:
```bash
grep -r "\[" DOCUMENTOS_FINALIZADOS/ | wc -l
```

---

## 🚨 ERROS COMUNS

### ❌ "CUSTOMIZATION_VALUES.md not found"
**Solução:** Certifique-se que preencheu e salvou o arquivo

### ❌ "[MISSING: company.name]" nos documentos
**Solução:** O valor não foi preenchido em CUSTOMIZATION_VALUES.md

### ❌ Nenhuma substituição aconteceu
**Solução:** Verificar se CUSTOMIZATION_VALUES.md tem valores reais (sem colchetes)

---

## ✅ CHECKLIST FINAL

Antes de fazer deploy:

- [ ] CUSTOMIZATION_VALUES.md preenchido 100%
- [ ] Script execute sem erros
- [ ] DOCUMENTOS_FINALIZADOS/ tem 5 arquivos
- [ ] Nenhum placeholder `[xxx]` restante
- [ ] Todos os emails/telefones reais
- [ ] Todas as URLs válidas
- [ ] Assinaturas digitais coletadas
- [ ] Arquivos revisados manualmente

---

## 📞 SUPORTE

**Se tiver dúvidas:**

1. Verificar `PLACEHOLDERS_REPORT.csv`
2. Rever `TEMPLATE_CUSTOMIZACAO.md`
3. Reler seção "Como usar este arquivo" em CUSTOMIZATION_VALUES.md

---

## 🎯 PRÓXIMO PASSO

**AGORA:**

```bash
# 1. Editar arquivo
code CUSTOMIZATION_VALUES.md

# 2. Preencher com seus dados
# (Substituir [Seu nome aqui] por seu nome real, etc)

# 3. Salvar

# 4. Rodar customização
python customize_documents.py

# 5. Revisar em DOCUMENTOS_FINALIZADOS/

# 6. Fazer deploy
```

---

**🚀 Seus 5 documentos compliance-grade estarão 100% prontos para produção!**

Data: 2 de janeiro de 2026
Status: ✅ READY TO USE
