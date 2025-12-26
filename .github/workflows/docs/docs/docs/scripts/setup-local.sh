#!/bin/bash
set -e

echo '[Setup] Configurando CODEX-OPERATOR...'

# 1. Criar pasta config
echo '[1/4] Criando config/...'
mkdir -p config

# 2. Copiar templates
echo '[2/4] Copiando templates...'
if [ -f 'config/credentials.template.json' ]; then
  cp config/credentials.template.json config/credentials.json
fi

if [ -f 'config/sa-key.template.json' ]; then
  cp config/sa-key.template.json config/sa-key.json
fi

# 3. Copiar .env.example
echo '[3/4] Copiando .env.example'
if [ -f '.env.example' ]; then
  cp .env.example .env.local
else
  echo 'ERRO: .env.example nao encontrado!'
  exit 1
fi

echo '[4/4] Pronto!'
echo ''
echo 'Proximas etapas:'
echo '1. Editar config/sa-key.json'
echo '2. Editar .env.local com seus secrets'
echo '3. pip install -e .[dev]'
echo '4. pytest tests/'
echo ''
echo 'IMPORTANTE: Nunca commitar config/sa-key.json ou .env.local!'
