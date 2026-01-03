# 📝 TEMPLATE DE CUSTOMIZAÇÃO - VALORES EXEMPLO

**Use este arquivo como guia para preencher os 88 placeholders críticos.**

---

## 🏢 INFORMAÇÕES DA EMPRESA

```
Nome Legal: NEXUS BRASIL LTDA
CNPJ: XX.XXX.XXX/0001-XX
Sede: São Paulo, SP - Brasil
Domínio Principal: nexus.app
Email Suporte: support@nexus.app
Website: https://nexus.app
```

---

## 👥 EQUIPE DE INCIDENTES (CRÍTICO!)

### Incident Commander
```
Nome: [Seu nome aqui - quem faz o triage?]
Telefone: +55 (11) 9XXXX-XXXX
Email: [seu-email]@nexus.app
Backup: [Nome do backup]
```

### Security Lead
```
Nome: [Responsável por segurança]
Telefone: +55 (11) 9XXXX-XXXX
Email: [segurança-email]@nexus.app
Backup: [Backup name]
```

### Communications Lead
```
Nome: [Responsável por comunicação]
Telefone: +55 (11) 9XXXX-XXXX
Email: [comms-email]@nexus.app
Backup: [Backup name]
```

### Technical Lead
```
Nome: [Responsável técnico]
Telefone: +55 (11) 9XXXX-XXXX
Email: [tech-email]@nexus.app
Backup: [Backup name]
```

### CTO/Executive
```
Nome: [CTO ou diretor]
Telefone: +55 (11) 9XXXX-XXXX
Email: [cto-email]@nexus.app
Backup: [Backup name]
```

---

## 🔗 LINKS & REFERÊNCIAS

### Documentos Internos
```
Incident Response Plan: https://github.com/seu-repo/INCIDENT_RESPONSE_PLAYBOOK.md
Monitoring Runbook: https://github.com/seu-repo/MONITORING_ALERTING_RUNBOOK.md
Compliance Matrix: https://github.com/seu-repo/SECURITY_COMPLIANCE_MATRIX.md
Deploy Standards: https://github.com/seu-repo/DEPLOY_STANDARDS.md
Go-Live Checklist: https://github.com/seu-repo/GO_LIVE_CHECKLIST.md
```

### Google Cloud Platform
```
GCP Project ID: seu-projeto-prod-xxxxx
Cloud Console: https://console.cloud.google.com
Cloud Monitoring: https://console.cloud.google.com/monitoring?project=seu-projeto-prod-xxxxx
Cloud Logging: https://console.cloud.google.com/logs?project=seu-projeto-prod-xxxxx
Cloud Run Service: https://console.cloud.google.com/run?project=seu-projeto-prod-xxxxx
Cloud SQL Instance: https://console.cloud.google.com/sql?project=seu-projeto-prod-xxxxx
```

### Ferramentas Operacionais
```
PagerDuty Organization: https://seu-empresa.pagerduty.com
Slack Workspace: https://seu-empresa.slack.com
Jira Project: https://seu-empresa.atlassian.net/projects/NEXUS
GitHub Repository: https://github.com/seu-usuario/nexus-ops-runbooks
```

### URLs de Produção
```
Privacy Policy: https://nexus.app/privacy
Terms of Service: https://nexus.app/terms
Support Portal: https://support.nexus.app
Status Page: https://status.nexus.app
```

---

## 📋 RESPONSÁVEIS POR DOCUMENTOS

| Documento | Owner | Email | Última Review |
|-----------|-------|-------|-----------------|
| Data Classification Policy | [Nome] | [email]@nexus.app | __/__/____ |
| Data Retention Policy | [Nome] | [email]@nexus.app | __/__/____ |
| Access Control Policy | [Nome] | [email]@nexus.app | __/__/____ |
| Incident Response Plan | [Nome] | [email]@nexus.app | __/__/____ |
| Vendor Management | [Nome] | [email]@nexus.app | __/__/____ |
| Change Management | [Nome] | [email]@nexus.app | __/__/____ |
| Data Breach Procedure | [Nome] | [email]@nexus.app | __/__/____ |

---

## 🚨 CONTATOS REGULATÓRIOS

### Brasil (LGPD)
```
ANPD Contact: [Órgão/contato principal da ANPD se necessário]
DPO Name: [Data Protection Officer]
DPO Email: dpo@nexus.app
DPO Phone: +55 (11) 9XXXX-XXXX
```

### Europa (GDPR)
```
EU Representative Name: [Seu representante na EU]
EU Representative Email: [email-eu]@nexus.app
EU Representative Address: [Endereço na EU]
```

### USA (CCPA)
```
Business Contact (CA): [Contato para California]
Email: [email]@nexus.app
```

---

## 🔐 CHAVES & SECRETS

**⚠️ NÃO PREENCHER AQUI! Apenas referência:**

Armazenar em:
- Google Secret Manager (produção)
- `.env.local` (desenvolvimento - nunca commitar)
- `credentials.json` (Google Cloud)

Exemplos (fictícios):
```
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
GOOGLE_CLOUD_API_KEY=AIzaSyxxxxxxxxxxxxxxxx
CLERK_SECRET_KEY=sk_live_xxxxxxxxxxxxx
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
DATABASE_URL=postgresql://user:password@host/db
```

---

## 📊 DASHBOARDS (URLs GCP)

### Operations Dashboard
```
URL: https://console.cloud.google.com/monitoring/dashboards/custom/nexus-operations?project=seu-projeto
Responsável: [Tech Lead]
Atualizado: __/__/____
```

### Database Dashboard
```
URL: https://console.cloud.google.com/monitoring/dashboards/custom/nexus-database?project=seu-projeto
Responsável: [Tech Lead]
Atualizado: __/__/____
```

### Security Dashboard
```
URL: https://console.cloud.google.com/monitoring/dashboards/custom/nexus-security?project=seu-projeto
Responsável: [Security Lead]
Atualizado: __/__/____
```

---

## 📞 ON-CALL ROTATION

### L1: On-Call Engineer
| Nome | Período | Telefone | Email |
|------|---------|----------|-------|
| [Engineer 1] | Jan 1-7 | +55 9XXXX-XXXX | [email]@nexus.app |
| [Engineer 2] | Jan 8-14 | +55 9XXXX-XXXX | [email]@nexus.app |
| [Rotation List] | [Google Calendar Link] | | |

### L2: Incident Commander
```
Primário: [IC Name] - +55 9XXXX-XXXX - [ic@nexus.app]
Backup: [Backup Name] - +55 9XXXX-XXXX - [backup@nexus.app]
```

### L3: CTO
```
Primário: [CTO Name] - +55 9XXXX-XXXX - [cto@nexus.app]
Backup: [Backup Name] - +55 9XXXX-XXXX - [backup@nexus.app]
```

### L4: CEO (Escalação final)
```
Nome: [CEO Name] - +55 9XXXX-XXXX - [ceo@nexus.app]
```

---

## 🎯 ASSINATURAS DIGITAIS (Compliance)

```
SECURITY & COMPLIANCE MATRIX APPROVED BY:

Chief Information Security Officer (CISO):
  Name: _________________________
  Email: _________________________
  Date: __/__/____

Legal Counsel:
  Name: _________________________
  Email: _________________________
  Date: __/__/____

Compliance Officer:
  Name: _________________________
  Email: _________________________
  Date: __/__/____

Data Protection Officer (DPO):
  Name: _________________________
  Email: _________________________
  Date: __/__/____
```

---

## 📱 APP STORE CONFIGS

### Google Play Store
```
Developer Account Email: [seu-email@gmail.com]
Organization Name: NEXUS BRASIL LTDA
App Bundle ID: com.nexus.app
App Name: NEXUS
Support Email: support@nexus.app
Privacy Policy URL: https://nexus.app/privacy
```

### Apple App Store
```
Developer Account Email: [seu-email@icloud.com]
Team ID: XXXXXXXXX (10 chars)
Bundle Identifier: com.nexus.app
App Name: NEXUS
Support URL: https://nexus.app/support
Privacy Policy URL: https://nexus.app/privacy
```

---

## ✅ CHECKLIST DE PREENCHIMENTO

- [ ] **Equipe de Incidentes** (5 pessoas + backups)
- [ ] **Links internos** (GitHub repos, runbooks)
- [ ] **URLs de Produção** (domínios, privacy, terms)
- [ ] **Dashboards GCP** (monitoring, logging)
- [ ] **Contatos Regulatórios** (LGPD, GDPR, CCPA)
- [ ] **On-Call Rotation** (Google Calendar)
- [ ] **Assinaturas Digitais** (4 pessoas)
- [ ] **App Store Configs** (Google + Apple)
- [ ] **Policy Owners** (responsáveis por docs)

---

## 🚀 PRÓXIMO PASSO

1. ✅ **Copiar este template**
2. ✅ **Preencher com seus dados**
3. ✅ **Salvar como `CUSTOMIZATION_VALUES.md`**
4. ✅ **Criar script para substituir placeholders automaticamente**

**Quer que eu crie o script de substituição automática?** 🤖
