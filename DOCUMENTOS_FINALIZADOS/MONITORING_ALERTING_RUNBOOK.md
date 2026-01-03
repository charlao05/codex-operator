# MONITORING_ALERTING_RUNBOOK.md

## Guia de Monitoramento e Alertas - NEXUS
### Versão 1.0 | Data: 2026-01-02 | Status: PRODUCTION-READY

---

## 📊 SEÇÃO 1: MONITORING ARCHITECTURE

### 1.1 Stack Utilizado

```
GCP Cloud Monitoring (core platform)
    ├── Metrics Collection (Cloud Run, Cloud SQL, Cloud Load Balancer)
    ├── Custom Metrics (application-level)
    ├── Log Aggregation (Cloud Logging)
    └── Alerting Policy Engine

├── Cloud Logging
│   ├── Application logs (stderr, stdout)
│   ├── System logs (GCP audit logs)
│   └── Export to Cloud Storage (archive)

└── Cloud Trace (APM)
    ├── Distributed tracing
    ├── Latency analysis
    └── Performance profiling

Third-party Integrations:
├── PagerDuty (incident escalation)
├── Slack (notifications)
└── Google Workspace (email alerts)
```

---

### 1.2 Key Metrics by Component

#### Cloud Run Service
- **Request metrics:**
  - Request count (per endpoint)
  - Request latency (P50, P95, P99)
  - Error rate (4xx, 5xx)
  - Status code distribution

- **Resource metrics:**
  - CPU utilization
  - Memory utilization
  - Disk I/O
  - Network bandwidth

- **Custom metrics:**
  - Active users
  - Feature flag adoption %
  - Database queries per request
  - Cache hit ratio

#### Cloud SQL (PostgreSQL)
- **Connection metrics:**
  - Active connections
  - Connection pool utilization
  - Wait time for connections

- **Query performance:**
  - Query execution time (P50, P95, P99)
  - Slow queries (>1s)
  - Query count per minute
  - Lock contention

- **Storage metrics:**
  - Disk usage %
  - WAL archive size
  - Backup success rate
  - Replication lag (if Multi-AZ)

- **Replica metrics (if applicable):**
  - Replication lag (ms)
  - Replica CPU/memory
  - Binary log size

#### Cloud Load Balancer
- **Traffic metrics:**
  - Request count
  - Request rate (req/min)
  - Bandwidth (in/out)
  - RPS by region/country

- **Health metrics:**
  - Healthy backend count
  - Unhealthy backend count
  - Health check latency

- **Security metrics:**
  - Blocked requests (Cloud Armor)
  - Rate-limited requests
  - DDoS attack indicators

---

## 🚨 SEÇÃO 2: ALERTING POLICIES

### 2.1 API Performance Alerts

#### Alert: API Latency High (P95 >500ms)
```yaml
Policy: API_Latency_High_P95
Condition:
  - Metric: run.googleapis.com/request_latencies
    Filter: resource.service_name="nexus-api"
    Aggregate: p95
    Duration: 10 minutes
    Threshold: >500 ms

Notification:
  - Email: devops-team@nexus.app
  - Slack: #alerts

Runbook: Latency troubleshooting
  1. Check Cloud Monitoring dashboard
  2. Identify slow endpoint
  3. Check database performance
  4. Check Cloud Run resource usage
```

**Action Items When Triggered:**
- [ ] Check which endpoint is slow (filter logs)
- [ ] Check database query performance (CloudSQL metrics)
- [ ] Increase Cloud Run instances if CPU high (>70%)
- [ ] Kill long-running queries if needed
- [ ] Restart Cloud Run if memory high (>80%)

---

#### Alert: API Error Rate High (>1%)
```yaml
Policy: API_Error_Rate_High
Condition:
  - Metric: run.googleapis.com/request_count
    Filter: metric.response_code_class="5xx"
    Aggregate: rate
    Duration: 5 minutes
    Threshold: >1% of total requests

Notification:
  - PagerDuty: severity=high, escalate to on-call
  - Slack: #incidents (page @incident-commander)
  - Email: devops-team@nexus.app

Auto-Actions:
  - Create incident ticket in Jira
  - Open war room Zoom link
```

**Action Items When Triggered:**
- [ ] Check Cloud Run logs for 500 errors
- [ ] Check database connectivity (test connection)
- [ ] Check Cloud SQL slow query log
- [ ] Rollback recent deployment if time-correlated
- [ ] Page incident commander if sustained >5 min

---

### 2.2 Database Alerts

#### Alert: Cloud SQL CPU High (>80%)
```yaml
Policy: CloudSQL_CPU_High
Condition:
  - Metric: cloudsql.googleapis.com/database/cpu/utilization
    Filter: resource.database_id="nexus-prod:postgres"
    Aggregate: average
    Duration: 15 minutes
    Threshold: >80%

Notification:
  - Email: dba-team@nexus.app
  - Slack: #database-alerts
```

**Action Items:**
- [ ] Check top 10 queries consuming CPU
- [ ] Kill long-running queries if blocking
- [ ] Check for missing indexes (EXPLAIN ANALYZE)
- [ ] Consider upgrading instance class if sustained

---

#### Alert: Cloud SQL Disk Usage High (>80%)
```yaml
Policy: CloudSQL_Disk_High
Condition:
  - Metric: cloudsql.googleapis.com/database/disk/utilization
    Threshold: >80%
    Duration: 10 minutes

Notification:
  - PagerDuty: severity=high
  - Slack: #incidents
```

**Action Items:**
- [ ] Check disk usage breakdown (logs vs data)
- [ ] Archive old logs if CloudLogging taking space
- [ ] Expand disk if permanent
- [ ] Vacuum database if unused space

---

#### Alert: Backup Failure
```yaml
Policy: CloudSQL_Backup_Failed
Condition:
  - Event: cloudsql.googleapis.com/database/backup_failed
  - Last backup: >24 hours ago

Notification:
  - PagerDuty: severity=critical
  - Email: dba-team@nexus.app
  - Slack: #incidents
```

**Action Items:**
- [ ] Check backup logs in Cloud SQL console
- [ ] Check available disk space
- [ ] Check network connectivity to Cloud Storage
- [ ] Manually trigger backup if needed
- [ ] Update backup schedule if permanently changed

---

### 2.3 Security & Compliance Alerts

#### Alert: Suspicious Database Access Pattern
```yaml
Policy: Suspicious_DB_Access
Condition:
  - Metric: cloudsql.googleapis.com/database/network/connections
    Filter: source_ip NOT IN ["10.8.0.0/28"] (VPC Connector)
    Aggregate: count
    Duration: 5 minutes
    Threshold: >0 (any external connection)

Notification:
  - PagerDuty: severity=critical
  - Email: security-team@nexus.app
  - Slack: #security-incidents
```

**Action Items:**
- [ ] Verify source IP (should only be VPC Connector)
- [ ] Check if public IP enabled (should be no)
- [ ] Review recent database access logs
- [ ] Revoke credentials if compromised
- [ ] Escalate to incident response if unauthorized

---

#### Alert: Excessive Failed Login Attempts
```yaml
Policy: Failed_Logins_High
Condition:
  - Log query: severity="WARNING" AND message contains "Failed login"
    Aggregate: count
    Duration: 15 minutes
    Threshold: >10 in 15 min

Notification:
  - Email: security-team@nexus.app
  - Slack: #security
```

**Action Items:**
- [ ] Check logs for source IP
- [ ] Is it automated attack? (check User-Agent)
- [ ] Implement rate limiting if needed
- [ ] Alert user if their account (email notification)
- [ ] Reset password as precaution

---

### 2.4 Infrastructure Alerts

#### Alert: Cloud Run Out of Memory
```yaml
Policy: CloudRun_Memory_Critical
Condition:
  - Metric: run.googleapis.com/container_memory_utilization
    Threshold: >95%
    Duration: 2 minutes

Notification:
  - PagerDuty: severity=high
  - Slack: #incidents
```

**Action Items:**
- [ ] Increase memory allocation (512MB → 1024MB)
- [ ] Check for memory leak in code (Cloud Trace)
- [ ] Increase max instances (autoscaling may not keep up)
- [ ] Investigate if traffic spike or sustained

---

#### Alert: Certificate Expiration Warning
```yaml
Policy: SSL_Certificate_Expiring
Condition:
  - Google Managed Certificate: expires within 30 days

Notification:
  - Email: ops-team@nexus.app (30 days warning)
  - Email: ops-team@nexus.app (7 days warning)
```

**Action Items:**
- [ ] Google handles auto-renewal (no action needed)
- [ ] Verify renewal succeeded (check GCP console)
- [ ] Monitor certificate validity (before expiry)

---

## 📈 SEÇÃO 3: DASHBOARDS

### 3.1 Main Operations Dashboard

**Name:** NEXUS Operations Overview
**URL:** [link to dashboard]
**Refresh:** auto (30s)
**Audience:** On-call engineer, DevOps team

**Panels:**

| Panel | Metric | Threshold | Goal |
|-------|--------|-----------|------|
| **API Request Rate** | requests/min | - | >1000 = healthy |
| **API Error Rate** | % 5xx errors | <1% | 0% |
| **API Latency (P95)** | latency in ms | <500ms | <200ms |
| **Cloud Run CPU** | CPU % | 70% = alert | 20-40% |
| **Cloud Run Memory** | Memory % | 80% = alert | 50-70% |
| **CloudSQL CPU** | CPU % | 80% = alert | 30-50% |
| **CloudSQL Connections** | # active | 20 = pool limit | <10 |
| **Disk Usage** | % used | 80% = alert | <70% |
| **Backup Status** | Last backup | >24h = alert | Every 24h ✅ |
| **TLS Certificate** | Days to expiry | <30 = alert | >90 days ✅ |

---

### 3.2 Database Performance Dashboard

**Name:** NEXUS Database Deep Dive
**URL:** [link to dashboard]
**Refresh:** auto (1 min)
**Audience:** DBA, backend engineers

**Panels:**
- Query execution time (histogram P50, P95, P99)
- Slow queries log (>1s queries, top 10)
- Active connections over time
- Cache hit ratio
- Lock contention
- Disk IOPS
- Replication lag (if applicable)
- Backup size & duration
- WAL archive growth

---

### 3.3 Security Dashboard

**Name:** NEXUS Security Monitoring
**URL:** [link to dashboard]
**Refresh:** auto (1 min)
**Audience:** Security team

**Panels:**
- Failed login attempts (time series)
- API requests by source IP
- Cloud Armor blocked requests
- Rate limit hits
- Unusual access patterns
- Certificate expiration status
- Vulnerability scan results
- Incident summary (open + recent)

---

## 📊 SEÇÃO 4: LOG AGGREGATION & ANALYSIS

### 4.1 Cloud Logging Configuration

#### Log Sinks (Auto-Export)

**Sink 1: Archive to Cloud Storage**
```
Sink Name: logs-archive-monthly
Destination: gs://nexus-logs-archive/logs/
Filter: resource.type="cloud_run_revision"
Retention: 1 year
Compression: gzip
Format: JSON
Partition: By date (YYYY/MM/DD)
```

**Sink 2: Export Critical Errors to BigQuery**
```
Sink Name: errors-to-bigquery
Destination: projects/nexus-prod/datasets/logs_dataset
Filter: severity="ERROR" OR severity="CRITICAL"
Retention: 2 years (for analysis)
```

---

### 4.2 Useful Log Queries

#### Find Slow Queries (>1s)
```sql
resource.type="cloudsql_database"
resource.labels.database_id="nexus-prod:postgres"
severity >= "WARNING"
```

#### Find Failed Authentication Attempts
```sql
protoPayload.methodName="cloudsql.instances.update" OR
"authentication failure" OR
"invalid password"
```

#### Find API Errors by Endpoint
```sql
resource.type="cloud_run_revision"
httpRequest.status >= 500
| stats count() by httpRequest.requestUrl
```

#### Find High Memory Usage Events
```sql
resource.type="cloud_run_revision"
labels.container_name="nexus-api"
"Memory exceeded" OR "OOM"
```

---

## 🔧 SEÇÃO 5: TROUBLESHOOTING GUIDE

### 5.1 API Latency Troubleshooting Tree

```
API Latency HIGH (P95 >500ms)?
│
├─ YES: Is it all endpoints or specific ones?
│   ├─ All endpoints:
│   │  ├─ Check Cloud Run CPU/Memory (high?)
│   │  │  └─ YES → Increase resources
│   │  ├─ Check CloudSQL CPU/connections (high?)
│   │  │  └─ YES → Check slow queries, kill long-running
│   │  └─ Check network latency (VPC issues?)
│   │     └─ YES → Check VPC Connector health
│   │
│   └─ Specific endpoints:
│       ├─ Check endpoint logs (errors? exceptions?)
│       ├─ Check database query (EXPLAIN ANALYZE)
│       ├─ Missing index? (look for sequential scans)
│       └─ External API calls? (third-party latency)
│
└─ NO: Latency normal, continue monitoring
```

---

### 5.2 Database Troubleshooting Tree

```
CloudSQL CPU High (>80%)?
│
├─ YES: Check pg_stat_statements top 10
│   ├─ One query using >50% CPU?
│   │  ├─ Missing index? → Add index
│   │  ├─ Full table scan? → Optimize query
│   │  └─ Stuck transaction? → Kill session
│   │
│   └─ Many queries contributing?
│       ├─ Traffic spike? → Increase resources
│       ├─ Scheduled maintenance job? → Reschedule
│       └─ New feature deployed? → Optimize queries
│
└─ NO: CPU normal, continue monitoring
```

---

## 📋 SEÇÃO 6: ESCALATION & ON-CALL

### 6.1 On-Call Rotation

**Primary On-Call Engineer:**
- Phone: [number]
- Email: [email]
- Slack: @on-call
- Schedule: [link to calendar]
- Duration: 1 week
- Rotation starts: Monday 9am UTC

**On-Call Responsibilities:**
- [ ] Monitor alerts in PagerDuty (24/7)
- [ ] Respond to P1/P2 alerts within 15 min
- [ ] Update status page every 15 min during incident
- [ ] Page incident commander for P1 after 5 min
- [ ] Post post-mortem within 24h of incident

---

### 6.2 Escalation Contacts

| Level | Name | Title | Phone | Email |
|-------|------|-------|-------|-------|
| L1 | [name] | On-Call Engineer | [phone] | [email] |
| L2 | [name] | Incident Commander | [phone] | [email] |
| L3 | [name] | CTO | [phone] | [email] |
| L4 | [name] | CEO | [phone] | [email] |

**Escalation Trigger:**
- L1 → L2: P1 incident ongoing >5 min
- L2 → L3: Customer-facing issue or data breach
- L3 → L4: Regulatory/media risk

---

### 6.3 On-Call Tools Access

**Required Access:**
- [ ] GCP Cloud Console (Monitoring, Logging, Cloud Run, CloudSQL)
  - Account: [email]
  - MFA: [app/method]

- [ ] PagerDuty (incident management)
  - Account: [email]
  - API token: [stored in Secret Manager]

- [ ] Slack (team communication)
  - Account: [email]
  - Channels: #alerts, #incidents, #oncall

- [ ] GitHub (source code, runbooks)
  - Account: [email]
  - SSH key: [configured]

- [ ] Jira (ticket tracking)
  - Account: [email]
  - Project: NEXUS-OPS

- [ ] Cloud SQL Console
  - Instance: nexus-prod
  - User: admin (password in Secret Manager)

**Getting Started Checklist:**
- [ ] Verify all access working
- [ ] Download runbooks locally
- [ ] Add contacts to phone
- [ ] Test PagerDuty alert (silence after test)

---

## ✅ SEÇÃO 7: TRAINING & MAINTENANCE

### 7.1 Team Training

- [ ] All engineers trained on monitoring stack: [date]
- [ ] Annual refresher scheduled: [date]
- [ ] New team member onboarding: [time ~2h]
- [ ] Last tabletop drill: [date, result]

**New Team Member Training:**
1. [ ] Watch [Monitoring Overview Video] (~20 min)
2. [ ] Read this runbook (~40 min)
3. [ ] Tour Cloud Monitoring dashboards (~30 min)
4. [ ] Walk through sample incident (~30 min)
5. [ ] Shadow on-call rotation (1 week, follow along)
6. [ ] Be on-call with backup (1 week)
7. [ ] Full on-call rotation begins

---

### 7.2 Alert Tuning & Optimization

**Quarterly Alert Review Process:**
1. [ ] Identify noisy alerts (>5 false positives in quarter)
2. [ ] Adjust thresholds based on historical data
3. [ ] Remove unnecessary alerts
4. [ ] Add new alerts based on incident retrospectives
5. [ ] Update runbooks based on new findings

**Target Alert Metrics:**
- False positive rate: <5%
- Alert resolution time: <30 min average
- Customer impact from missed alerts: 0

---

### 7.3 Dashboard Maintenance

**Monthly:**
- [ ] Review dashboard for outdated panels
- [ ] Add new metrics based on feature launches
- [ ] Fix broken data sources
- [ ] Verify thresholds still appropriate

**Quarterly:**
- [ ] Full dashboard redesign consideration
- [ ] Stakeholder feedback collection
- [ ] Add panels for new features

---

## 📚 SEÇÃO 8: REFERENCE MATERIAL

### 8.1 GCP Documentation
- [Cloud Monitoring Documentation](https://cloud.google.com/monitoring/docs)
- [Cloud Logging Documentation](https://cloud.google.com/logging/docs)
- [Cloud Trace Documentation](https://cloud.google.com/trace/docs)
- [Cloud Run Metrics](https://cloud.google.com/run/docs/monitoring)
- [Cloud SQL Monitoring](https://cloud.google.com/sql/docs/postgres/monitoring)

### 8.2 Useful Tools
- [Cloud Console](https://console.cloud.google.com)
- [Cloud Monitoring](https://console.cloud.google.com/monitoring) (GCP dashboard)
- [Cloud Logging](https://console.cloud.google.com/logs) (GCP dashboard)
- [PagerDuty](https://pagerduty.com)
- [Slack](https://slack.com)

---

## 📝 APPROVAL & SIGN-OFF

```
Document Approved:

Director of Engineering: _________________________ Date: __/__/__
On-Call Lead: _________________________ Date: __/__/__
SRE Lead: _________________________ Date: __/__/__
```

**Document Version:** 1.0
**Effective Date:** 2026-01-02
**Last Updated:** 2026-01-02
**Next Review:** 2026-04-02 (quarterly)

---

**Questions or issues with monitoring setup?**
Contact: monitoring-team@nexus.app
