# Crear conta Netlify e persistir landing

## Step 1: Criar conta Netlify (gratuita)
1. Acesse: https://app.netlify.com/signup
2. Registre com email: charles.rsilva05@gmail.com (ou similar)
3. Confirme email

## Step 2: Drag-and-drop da landing
1. Vá para: https://app.netlify.com/drop
2. Arraste a pasta `landing/` (ou o arquivo `landing/index.html`)
3. Netlify criará um site permanente com URL: `seu-site-aleatorio.netlify.app`

## Step 3: Conectar domínio customizado (opcional)
Se tiver domínio (ex: codex.com.br):
1. Em Netlify, vá para: Site Settings → Domain Management
2. Aponte o DNS do seu domínio para Netlify (instruções fornecidas)
3. URL ficará: `codex.com.br`

## Result
Site persistente, HTTPS automático, deploy contínuo (se conectar GitHub).

---

# Integrar Netlify Forms → Google Sheets

## Step 1: Confirmar form na landing
O `landing/index.html` já tem:
```html
<form name="contact" method="POST" netlify>
```

Netlify detecta automaticamente e ativa capturas.

## Step 2: Configurar notificação por email
Em Netlify Site Settings → Forms:
- Email de notificação: charles.rsilva05@gmail.com
- Você recebe email cada vez que alguém preenche o form.

## Step 3: Integrar com Google Sheets (Zapier ou Make.com)
1. Crie webhook em Zapier: "Netlify Form Submission" → "Google Sheets"
2. Mapeie campos: name, email, whatsapp, profession
3. Sheets criará linha automática cada lead
4. URL do Sheets para monitorar: https://sheets.google.com (seu arquivo)

Alternativa simples: exportar manualmente de Netlify > Forms a cada 24h.

---

# Próximas ações executadas pelo agent
- [ ] Enviar Wave 2 A/B (você define App Password e eu executo)
- [ ] Ativar agendamento de follow-ups 48h (task Windows)
- [ ] Criar link Calendly e atualizar landing com CTA único
- [ ] Gerar contrato simples + checklist de demo
- [ ] Criar dashboard KPIs em Google Sheets
