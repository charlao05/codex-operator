# 🚀 DEPLOY LANDING PAGE - GUIA RÁPIDO

## OPÇÃO 1: Vercel (RECOMENDADO - 2 minutos)

### Pré-requisito:
- Conta GitHub (grátis)
- Conta Vercel (grátis, integra com GitHub)

### Passo a Passo:

**1. Fazer Push do Repo para GitHub:**
```powershell
cd C:\Users\Charles\Desktop\codex-operator
git remote add origin https://github.com/SEU_USER/codex-operator.git
git branch -M main
git push -u origin main
```

**2. Ir para https://vercel.com**
- Click "Sign Up" → "Continue with GitHub"
- Autorizar Vercel acessar seus repos
- Click "Import Project"
- Selecionar repo `codex-operator`
- Framework: "Other" (HTML estático)
- Root Directory: deixar vazio (usa raiz)
- Build Command: deixar em branco
- Output Directory: `landing`
- Click "Deploy"

**3. Pronto!** Vercel gera URL tipo: `https://codex-operator.vercel.app`

---

## OPÇÃO 2: Netlify (2 minutos)

**1. Ir para https://netlify.com**
- Click "Sign up" → "GitHub"
- Conectar GitHub account

**2. "New site from Git"**
- Escolher repo `codex-operator`
- Build command: deixar vazio
- Publish directory: `landing`
- Click "Deploy site"

**3. Pronto!** URL tipo: `https://codex-operator.netlify.app`

---

## OPÇÃO 3: GitHub Pages (1 minuto - MAIS RÁPIDO)

**1. Fazer Push (se ainda não fez):**
```powershell
git push origin main
```

**2. GitHub Repo Settings:**
- Ir em Settings → Pages
- Source: Branch "main", Folder "/landing"
- Click "Save"

**3. Pronto!** URL: `https://seu_user.github.io/codex-operator/`

---

## ✅ TESTE DE FORM APÓS DEPLOY

Após landing estar live, testar form:

**Opção A: Google Forms (FREE)**
```javascript
// Substituir action no form por:
<form action="https://docs.google.com/forms/d/e/SEU_FORM_ID/formResponse" method="POST">
```

**Opção B: Formspree (FREE até 50 submissões/mês)**
```html
<form action="https://formspree.io/f/SEU_FORM_ID" method="POST">
```

**Opção C: Simple Backend (FREE)**
```bash
curl https://formspree.io/f/mddqoqbo
```

---

## 🎯 CHECKLIST DEPLOY:

- [ ] Repo feito push para GitHub
- [ ] Vercel/Netlify/GitHub Pages configurado
- [ ] Landing acessível por URL pública
- [ ] Form testado (enviar 1 submissão de teste)
- [ ] Email de confirmação recebido
- [ ] ✅ Landing LIVE

**Tempo estimado:** 5-10 minutos total

---

## COMANDO RÁPIDO (Se já tem GitHub conectado):

```powershell
# 1. Push para GitHub
git add .
git commit -m "feat: Deploy landing page v1"
git push origin main

# 2. Depois ir em Vercel.com → Import → seu repo → Deploy
# (Takes 1 minute)

# Resultado: Landing LIVE em menos de 10 minutos
```

---

**PRÓXIMO PASSO:** Após landing estar LIVE, começar Tarefa 2 (Email prep)
