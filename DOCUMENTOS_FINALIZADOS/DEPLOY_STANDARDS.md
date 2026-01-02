# DEPLOY_STANDARDS.md

## Padrões Obrigatórios de Deployment - NEXUS
### Versão 1.0 | Data: 2026-01-02 | Status: AUDIT-APPROVED

---

## 🔐 SEÇÃO 1: PRÉ-REQUISITOS OBRIGATÓRIOS

### 1.1 Infraestrutura de Banco de Dados

#### PostgreSQL RDS (Production)
- **Versão Mínima:** PostgreSQL 14.x ou superior
- **Configuração GCP (Cloud SQL):**
  - [ ] VPC dedicada (não default)
  - [ ] Multi-AZ habilitado para HA
  - [ ] Backup automático: retenção mínima 30 dias
  - [ ] Encryption at rest: Cloud KMS managed key obrigatório
  - [ ] Encryption in transit: SSL/TLS enforced (sslmode=require)
  - [ ] Flags: log_statement='ddl', log_connections=on, log_disconnections=on

#### Segurança PostgreSQL (Compliance-Grade)
- **Authentication Methods:**
  - [ ] pg_hba.conf configurado com: md5/scram-sha-256
  - [ ] LDAP/GSSAPI para usuários administrativos
  - [ ] Trust auth APENAS para localhost (restrição absoluta)

- **Row Level Security (RLS):**
  - [ ] RLS habilitado em todas as tabelas com dados sensíveis
  - [ ] Políticas de segurança granular por role/user
  - [ ] Auditoria de alterações RLS via CloudLogging
  - [ ] Teste de RLS bypass: realizado e documentado

- **Roles e Permissões:**
  - [ ] Criar roles segregados: `app_user`, `app_admin`, `analytics`, `backup`
  - [ ] Princípio de menor privilégio (PoLP) aplicado
  - [ ] Revogar SUPERUSER de `app_user`
  - [ ] GRANT específico por schema/table/column
  - [ ] Audit trail: [log file path]

#### Backup e Recuperação
- **Strategy:** Backup diário + WAL archiving contínuo
  - [ ] Teste de recuperação (RTO/RPO) documentado
  - [ ] Armazenamento de backups em Cloud Storage (multi-region)
  - [ ] Retenção: 30 dias production, 7 dias staging
  - [ ] Restore test realizado: [data], tempo: [XX min]
  - [ ] Documentação: [link para runbook]

#### Cloud SQL Security Groups
- **Authorized Networks:**
  - [ ] App tier private IP (Cloud Run): 10.x.x.x/32
  - [ ] SSH bastion: [IP específico]/32
  - [ ] Nenhuma regra 0.0.0.0/0
  - [ ] Public IP: DISABLED (obrigatório)

---

### 1.2 Autenticação e Identidade (Clerk)

#### Setup Obrigatório
- **Environment Variables:**
  - [ ] `CLERK_SECRET_KEY` armazenado em Secret Manager
  - [ ] `CLERK_PUBLISHABLE_KEY` versionado no código
  - [ ] Nenhuma chave em .env files (use `example.env` somente)
  - [ ] Rotation policy: 90 dias automático

- **Configurações:**
  - [ ] Multi-factor authentication (MFA) obrigatório para admin
  - [ ] Session timeout: 30 min (web), 8h (mobile)
  - [ ] Email verification obrigatória
  - [ ] Password policy: min 12 chars, complexidade HIGH (reqs: 1 uppercase, 1 número, 1 special)
  - [ ] Account lockout: 5 tentativas em 15 min

- **Auditoria:**
  - [ ] Logging de login/logout/failed attempts: ENABLED
  - [ ] Alerts para múltiplas tentativas de falha: CONFIGURED
  - [ ] Dashboard de atividades: [link para acesso]

---

### 1.3 Infraestrutura de Container (Cloud Run)

#### Configuração de Build
- **Docker Image Standards:**
  - [ ] Non-root user (UID 1000+)
  - [ ] Minimal base image: node:20-alpine ou distroless
  - [ ] Scan de vulnerabilidades via Container Analysis: PASSED
  - [ ] Score de segurança mínimo: B+ (requer >85%)
  - [ ] SBOM gerado e armazenado

- **Build Pipeline:**
  - [ ] Signed commits via GPG obrigatório
  - [ ] Code scanning (SAST) antes de merge: 0 HIGH/CRITICAL
  - [ ] Dependency scanning: 0 known vulnerabilities
  - [ ] Tag de imagem: `gcr.io/nexus-prod/api:{version}-{commit_hash}`
  - [ ] Build reproducibility: TESTED

#### Deployment ao Cloud Run
- **Configurações Obrigatórias:**
  - [ ] Requester Pays: DISABLED
  - [ ] Min instances: 1, Max instances: 10
  - [ ] Memory: 512MB (monitorado, ajustar se necessário)
  - [ ] CPU: 1 vCPU (always allocated)
  - [ ] Timeout: 3600s
  - [ ] Concurrency: 100 req/instance
  - [ ] Revision labeling: enabled

- **Security:**
  - [ ] Ingress: internal (Cloud Load Balancer apenas)
  - [ ] VPC Connector obrigatório (subnet: 10.8.0.0/28)
  - [ ] Service Account com permissões mínimas (Cloud Build, Secret Manager, Cloud Logging)
  - [ ] Secrets Manager para env vars
  - [ ] AllowUnauthenticated: DISABLED (LB handles auth)

#### Monitoramento
- [ ] Cloud Logging: retention 30 days (configurável)
- [ ] Cloud Monitoring dashboards: 4 dashboards (Overview, Database, API, Infrastructure)
- [ ] Alertas configurados:
  - [ ] Error rate >1%: PAGERDUTY
  - [ ] CPU >70%: EMAIL
  - [ ] Memory >80%: EMAIL
  - [ ] Slow queries (>1s): EMAIL
- [ ] Cloud Trace: APM habilitado, sampling 10%
- [ ] Budget alert: >$1000/mês

---

### 1.4 API Gateway & TLS

#### Certificados SSL/TLS
- **Requirements:**
  - [ ] TLS 1.2 mínimo (preferir 1.3)
  - [ ] HSTS header: `max-age=31536000; includeSubDomains; preload`
  - [ ] Certificate pinning para mobile apps (pubkey pinning)
  - [ ] Auto-renewal via Google Managed Certificates (default)
  - [ ] Certificate validity: checked monthly

#### Cloud Load Balancer
- [ ] IP whitelisting: [especificar países/IPs se necessário]
- [ ] Rate limiting: 1000 req/min por IP
- [ ] DDoS protection: Cloud Armor ENABLED
- [ ] WAF rules: SQL injection, XSS, RFI, LFI (OWASP 4.0)
- [ ] Custom rules: [especificar caso necessário]
- [ ] Geo-restriction: [especificar if needed]

---

### 1.5 CI/CD Pipeline (GitHub Actions)

#### Stages Obrigatórios
```yaml
Pipeline Stages:
  1. Lint: ESLint + Prettier checks
  2. Type: TypeScript compilation (strict mode)
  3. Test: Unit + Integration (>80% coverage obrigatório)
  4. Security: Dependency scan + SAST (Semgrep)
  5. Build: Docker image build + container scan
  6. Deploy: Staging → wait for approval → Production
  7. Smoke Test: Health checks + critical path validation
  8. Rollback: Automated if error rate >5% within 5 min
```

#### Approval Gates (OBRIGATÓRIO)
- [ ] Code review: 2 aprovações mínimo (diferentes pessoas)
- [ ] Manual approval antes de prod: pelo menos 1 approver
- [ ] Assinatura digital de release notes
- [ ] CODEOWNERS configured: [lista de owners]

---

## 🎯 SEÇÃO 2: CONFIGURAÇÕES POR AMBIENTE

### 2.1 Staging Environment
- [ ] Espelho exato de production (GCP project, PostgreSQL version)
- [ ] Data: snapshot de produção (anonymized com masking rules)
- [ ] Acesso: VPN restrito + MFA obrigatório
- [ ] TTL: ambiente automaticamente destruído após 30 dias (cost control)
- [ ] Backup: 7 dias retenção

### 2.2 Production Environment
- [ ] Isolamento total via project-id isolado (nexus-prod-XXXX)
- [ ] Disaster recovery plano: RTO 1h, RPO 5min
- [ ] Backup: 30 dias retenção (verificado mensalmente)
- [ ] Restore drills: realizado mensalmente (1º dia do mês)
- [ ] Documentação: [link para runbooks]

---

## 📊 SEÇÃO 3: AUDITORIA E COMPLIANCE

### 3.1 Logging Obrigatório
- [ ] Cloud Audit Logs: todas as alterações (Admin Activity, Data Access)
- [ ] Application Logs: cada request HTTP (request ID, user ID, endpoint, status, latency)
- [ ] Access Logs: database connections, API calls, secret access
- [ ] Audit logs: deletions, permission changes, config changes
- [ ] Retention: 1 ano mínimo (armazenado em Cloud Storage para compliance)
- [ ] Log integrity: imutabilidade habilitada (GCS versioning)

### 3.2 Compliance Frameworks
- [ ] **LGPD (Brasil):**
  - [ ] Dados PII encrypted em repouso
  - [ ] Direito de exclusão implementado (delete user endpoint)
  - [ ] Consentimento documentado e auditável
  - [ ] Data processing agreement: [link]

- [ ] **GDPR:**
  - [ ] Consentimento explícito (cookie banner, explicit consent)
  - [ ] Direito ao esquecimento (GDPR Art. 17)
  - [ ] Data Subject Access Request (DSAR): processado em <30 dias
  - [ ] Privacy by design: implemented
  - [ ] DPA: signed with cloud provider

- [ ] **SOC 2 Type II readiness:**
  - [ ] Acesso controlado (rbac, mfa)
  - [ ] Monitoramento e alertas
  - [ ] Incident response plan
  - [ ] Backup & disaster recovery testado

- [ ] **PCI DSS (se aplicável):**
  - [ ] Tokenização de pagamentos obrigatória
  - [ ] Nunca armazenar CVV ou dados de cartão
  - [ ] Conformidade validada por third-party

### 3.3 Vulnerability Management
- [ ] Scanning mensal de vulnerabilidades (automated)
- [ ] Patches críticas: aplicadas em 48h
- [ ] Patches de segurança: aplicadas em 1 semana
- [ ] Penetration testing: anual (terceiros independentes)
- [ ] Bug bounty program: ativo (Bugcrowd/HackerOne)
- [ ] Disclosure policy: published

---

## ✅ SEÇÃO 4: CHECKLIST PRÉ-DEPLOYMENT

### 4.1 Configuração Técnica
- [ ] PostgreSQL RDS criado + testado
- [ ] VPC security groups configurados (tested ingress/egress)
- [ ] Clerk auth setup completo (MFA, session timeout, email verification)
- [ ] Cloud Run service deployment testado
- [ ] Load balancer + SSL configurado
- [ ] VPC Connector criado e testado
- [ ] CI/CD pipeline executando com sucesso
- [ ] Monitoring alerts ativos e testados
- [ ] Logging pipeline funcionando

### 4.2 Segurança
- [ ] Scan de segurança PASSED (0 HIGH/CRITICAL vulnerabilities)
- [ ] Secrets não expostas (git-secrets check, git history clean)
- [ ] CORS policies configuradas corretamente (whitelist domains only)
- [ ] CSRF tokens habilitados
- [ ] Content Security Policy header: configured
- [ ] SQL injection protection: parameterized queries only
- [ ] XSS protection: input validation + output encoding

### 4.3 Performance
- [ ] Load testing realizado (1000 concurrent users)
  - [ ] Test duration: 10 minutes
  - [ ] Results: [link to report]
- [ ] Latência P95: <500ms
- [ ] P99: <2s
- [ ] Error rate: <0.1%
- [ ] Database queries otimizadas (index analysis, explain plans)
- [ ] Connection pool tuned
- [ ] Cache strategy implementado (Redis, if needed)

### 4.4 Compliance
- [ ] Privacy policy publicada e atualizada
- [ ] Terms of service review completo
- [ ] Data retention policy documentada
- [ ] Audit logging funcionando
- [ ] User consent tracking implementado
- [ ] Right to deletion flow testado
- [ ] Data export feature testado

---

## 🔄 SEÇÃO 5: PROCESSO DE ROLLBACK

### Cenários de Rollback Automático
- [ ] Error rate >5% por 5 minutos consecutivos
- [ ] Latência P95 >2s por 10 minutos consecutivos
- [ ] Database connection failures (não consegue conectar)
- [ ] Out of memory errors
- [ ] Critical service unavailable

### Procedimento Manual
1. [ ] Pause canary deployment (em Cloud Run console)
2. [ ] Revert service to previous revision (tag: previous)
3. [ ] Notify team via PagerDuty
4. [ ] Validate rollback (health checks, smoke tests)
5. [ ] Communicate via status.nexus.app
6. [ ] Root cause analysis (post-mortem dentro de 24h)

### Runbook
- [ ] Rollback runbook: [link]
- [ ] Team trained: [date]
- [ ] Rollback test realizado: [date], tempo de rollback: [XX min]

---

## 📝 ASSINATURA DE COMPLIANCE

**Documento assinado digitalmente:**

```
Aprovado por: _________________________ Data: ___________
Função: Infrastructure Lead

Revisado por: _________________________ Data: ___________
Função: Security Officer

Auditado por: _________________________ Data: ___________
Função: Compliance Officer
```

**Histórico de Auditoria:**
- Todas as alterações registradas no GitHub (commits + pull requests)
- Changelog: [link para histórico]
- Próxima revisão: 2026-04-02 (90 dias)

---

## 📎 REFERÊNCIAS

- [GCP Cloud Run Best Practices](https://cloud.google.com/run/docs/quickstarts/build-and-deploy)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/sql-syntax.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
