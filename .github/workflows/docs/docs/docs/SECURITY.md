# Security Policy - CODEX-OPERATOR

## Princípios Fundamentais

1. **Nunca commitar secrets** - `.gitignore` protege automaticamente
2. **Usar environment variables** - Em produção via plataforma (Heroku, Cloud Run, etc.)
3. **Rotacionar secrets a cada 90 dias** - Chaves antigas devem expirar
4. **Audit logs** - Registrar quem usou qual secret

---

## Secrets Management

### Desenvolvimento Local

✅ Usar `.env.local` (nunca commitar)
✅ Usar `credentials.template.json` como referência
❌ NUNCA copiar valores reais para o repositório

```bash
# Verificar que .env.local está em .gitignore
cat .gitignore | grep .env.local
```

### GitHub Actions

✅ Usar `${{ secrets.SECRET_NAME }}` em workflows
✅ Secrets NÃO aparecem em logs
❌ Nunca hardcodar secrets em YAML

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
```

### Produção

✅ Usar managed secrets (Heroku Config Vars, Cloud Run Secrets, Kubernetes Secrets)
✅ Não hardcodar em environment variables não-criptografadas
✅ Rotacionar quarterly

```bash
# Heroku
heroku config:set SECRET_NAME=value

# Google Cloud Run
gcloud run deploy ... --set-env-vars SECRET_NAME=value

# Kubernetes
kubectl create secret generic app-secrets --from-literal=SECRET_NAME=value
```

---

## Detecção de Secrets

Usamos `detect-secrets` para evitar commits acidentais:

```bash
# Escanear código
detect-secrets scan --baseline .secrets.baseline

# Se encontrar um novo secret (falso positivo?)
detect-secrets audit .secrets.baseline
```

### Verificação Pré-Commit

O pre-commit hook bloqueia commits com padrões de secrets:

```bash
# Simular
pre-commit run detect-secrets --all-files
```

---

## Incident Response

### Se você expos um secret:

1. **Imediatamente** (próximos minutos)
   - Revogar o secret na fonte (OpenAI, Google, GitHub, etc.)
   - Reescrever histórico Git se necessário
   ```bash
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch secrets.json' \
     --prune-empty --tag-name-filter cat -- --all
   git push origin --force --all
   ```

2. **Documentar** (próximas horas)
   - Abrir issue privada no GitHub
   - Descrever: qual secret, quando, por quanto tempo foi visível
   - Notificar o time

3. **Investigar** (próximas 24h)
   - Verificar logs de API se houve acesso não-autorizado
   - Checar activity logs de contas (OpenAI, Google, Docker Hub, etc.)
   - Revisar Git history em todos os branches

---

## Checklist de Segurança Pré-Produção

- [ ] Todos os secrets em GitHub Secrets (não em `.env`)
- [ ] Templates contêm APENAS placeholders (YOUR_*, REPLACE_*, etc.)
- [ ] `.gitignore` contém `.env`, `config/sa-key.json`, `credentials.json`
- [ ] `detect-secrets` executado: `.secrets.baseline` atualizado
- [ ] Testes de integração rodam sem expor chaves (mocks)
- [ ] Documentação menciona nunca logar secrets
- [ ] Team conhece política de rotação (90 dias)
- [ ] Pre-commit hooks funcionando
- [ ] CI/CD não expõe secrets em logs ou artefatos

---

## Rotação de Secrets

### A cada 90 dias:

1. **OpenAI API Key**
   - Ir em https://platform.openai.com/api-keys
   - Criar nova chave
   - Atualizar em GitHub Secrets + produção
   - Revogar chave antiga

2. **PyPI Token**
   - Ir em https://pypi.org/account
   - Gerar novo token
   - Atualizar em GitHub Secrets
   - Revogar token antigo

3. **Docker Hub Token**
   - Docker Hub → Settings → Security → Access Tokens
   - Criar novo token
   - Atualizar em GitHub Secrets
   - Revogar token antigo

4. **Chaves de Integração** (WhatsApp, Telegram, etc.)
   - Seguir processo similar na plataforma
   - Atualizar imediatamente
   - Testar antes de revogar

---

## Monitoramento

### Alerts para Atividades Suspeitas

- Falha de autenticação em GitHub Actions
- Múltiplas tentativas de API falhadas
- Acesso de IP inesperado
- Deploy não-autorizado

```bash
# Ver logs de GitHub Actions
gh run list --limit 10
gh run view <run-id> --log
```

---

## Ferramentas de Segurança

- `detect-secrets` - Detecta padrões de secrets no código
- `git-secrets` - Pre-commit hook para Git
- `trufflehog` - Escaneia repositório procurando secrets

```bash
# Instalar
pip install detect-secrets
brew install git-secrets
pip install truffleHog

# Usar
detect-secrets scan
git secrets --scan
truffleHog git https://github.com/seu-user/seu-repo
```

---

## Contato de Segurança

Se descobrir uma vulnerabilidade:

1. **NÃO** abrir issue pública
2. **NÃO** postar em fóruns públicos
3. Enviar email privado para: [insira email de contato]
4. Incluir: descrição, passos para reproduzir, impacto

---

## Referências

- [OWASP - Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub - Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [detect-secrets Documentation](https://detect-secrets.readthedocs.io/)

---

**Próximas leituras:** [SETUP-SECRETS.md](./SETUP-SECRETS.md) | [DEPLOYMENT.md](./DEPLOYMENT.md)
