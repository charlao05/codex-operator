#!/usr/bin/env powershell
<#
.SYNOPSIS
    Deploy Landing Page para Vercel - Automatic Deployment Script

.DESCRIPTION
    Este script faz deploy da landing page para Vercel em 1 comando
    Opções: Vercel CLI (rápido) ou Upload via Web

.EXAMPLE
    .\deploy-landing.ps1
#>

Write-Host "
╔═══════════════════════════════════════════════════════════════════════════╗
║                    🚀 DEPLOY LANDING PAGE - VERCEL                        ║
╚═══════════════════════════════════════════════════════════════════════════╝
" -ForegroundColor Cyan

# ============================================================================
# OPÇÃO 1: Vercel CLI (Automático - Recomendado)
# ============================================================================

Write-Host "
📋 MÉTODO 1: Vercel CLI (Automático)

Pré-requisitos:
  1. Instalar Node.js: https://nodejs.org
  2. npm install -g vercel
  3. vercel login (autenticar com GitHub/GitLab)

Se já tem Vercel CLI instalado, rodar:
" -ForegroundColor Yellow

Write-Host "
  cd C:\Users\Charles\Desktop\codex-operator
  vercel --prod
" -ForegroundColor Green

Write-Host "
✅ Resultado: Landing LIVE em <seu-projeto>.vercel.app
" -ForegroundColor Green

# ============================================================================
# OPÇÃO 2: Upload Manual via Vercel Web (Mais simples)
# ============================================================================

Write-Host "
📋 MÉTODO 2: Deploy Manual via Web (Mais Simples)

Passo a Passo:
  1. Ir em https://vercel.com/dashboard
  2. Click em 'Add New...' → 'Project'
  3. Selecionar 'HTML/CSS/JS' ou 'Other'
  4. Upload a pasta 'landing/' diretamente
  5. Configurar:
     - Framework: None (HTML estático)
     - Root Directory: landing
     - Build Command: (deixar vazio)
     - Output Directory: (deixar vazio)
  6. Click 'Deploy'

✅ Resultado: Landing LIVE em <seu-projeto>.vercel.app
" -ForegroundColor Yellow

# ============================================================================
# OPÇÃO 3: GitHub + Vercel (Automático contínuo)
# ============================================================================

Write-Host "
📋 MÉTODO 3: GitHub + Vercel (Melhor para futuro)

Passo a Passo:
  1. Criar repo GitHub: https://github.com/new
     - Nome: codex-operator
     - Private/Public conforme preferir

  2. Fazer push local:
     git remote add origin https://github.com/SEU_USER/codex-operator.git
     git branch -M main
     git push -u origin main

  3. Conectar Vercel:
     - Ir em https://vercel.com
     - Click 'Import Project'
     - Selecionar repo GitHub
     - Configurar (mesmas settings acima)
     - Click 'Deploy'

  4. Pronto! Cada push = deploy automático

✅ Resultado:
  - Landing URL: https://codex-operator.vercel.app
  - Deploy automático em cada git push
" -ForegroundColor Green

# ============================================================================
# INSTRUÇÕES RÁPIDAS
# ============================================================================

Write-Host "
═══════════════════════════════════════════════════════════════════════════

🎯 OPÇÃO RECOMENDADA: GitHub + Vercel (Método 3)

Por quê?
  ✅ Deploy automático em cada push
  ✅ Histórico de versões
  ✅ Fácil de colaborar
  ✅ Zero-downtime deployments

Tempo total: ~5 minutos (primeira vez)

═══════════════════════════════════════════════════════════════════════════
" -ForegroundColor Cyan

# ============================================================================
# VERIFICAR VERCEL CLI
# ============================================================================

Write-Host "
🔍 Verificando se Vercel CLI está instalado..." -ForegroundColor Yellow

try {
    $version = vercel --version 2>&1
    if ($version -match "^Vercel") {
        Write-Host "✅ Vercel CLI encontrado: $version" -ForegroundColor Green
        Write-Host "
Pode rodar agora:
  vercel --prod

" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Vercel CLI não instalado" -ForegroundColor Red
    Write-Host "
Instalar:
  npm install -g vercel
  vercel login

Depois:
  vercel --prod

" -ForegroundColor Yellow
}

# ============================================================================
# FORM SUBMISSION OPTIONS
# ============================================================================

Write-Host "
═══════════════════════════════════════════════════════════════════════════

📧 CONFIGURAR FORM SUBMISSION (Lead Capture)

Opção 1: Formspree (FREE até 50/mês)
  1. Ir em https://formspree.io
  2. Conectar GitHub
  3. Criar novo form
  4. Copiar form ID
  5. Substituir em landing/index.html:
     <form action='https://formspree.io/f/[SEU_ID]' method='POST'>

Opção 2: Google Forms (100% FREE)
  1. Criar form em https://forms.google.com
  2. Copiar form action URL
  3. Substituir em landing/index.html:
     <form action='[URL_GOOGLE_FORMS]' method='POST'>

Opção 3: Email direto (Simples)
  1. Deixar form como email
  2. Usar Formspree ou similar

═══════════════════════════════════════════════════════════════════════════
" -ForegroundColor Yellow

Write-Host "
🚀 PRÓXIMO PASSO:

1. Escolher método de deploy (GitHub+Vercel recomendado)
2. Seguir instruções acima
3. Landing fica LIVE em ~5 minutos
4. Configurar form submission
5. Testar form com 1 submissão
6. Copiar URL final

Charles, qual método você quer usar?
  A) Vercel CLI (rápido, se tem Node)
  B) Upload Web (simples, manual)
  C) GitHub + Vercel (melhor, recomendado)
" -ForegroundColor Green
