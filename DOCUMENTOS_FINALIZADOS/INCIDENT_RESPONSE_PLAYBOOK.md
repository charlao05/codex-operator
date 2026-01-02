# INCIDENT_RESPONSE_PLAYBOOK.md

## Playbook de Resposta a Incidentes - NEXUS
### Versão 1.0 | Data: 2026-01-02 | Status: APPROVED

---

## 🚨 SEÇÃO 1: OVERVIEW & STRUCTURE

### 1.1 Objetivo
Protocolo para identificar, comunicar e remediar incidentes de segurança ou disponibilidade que afetem NEXUS.

### 1.2 Escopo
- Incidentes de segurança (data breach, unauthorized access, malware)
- Incidentes de disponibilidade (service outage, performance degradation)
- Incidentes de compliance (policy violation, regulatory breach)
- Incidentes operacionais (misconfiguration, failed backup)

### 1.3 Responsáveis

| Função | Responsabilidades | Contato | Backup |
|--------|------------------|---------|--------|
| **Incident Commander** | Coordena resposta, toma decisões | [name, phone, email] | [backup name] |
| **Security Lead** | Investiga, classifica, remedia | [name, phone, email] | [backup name] |
| **Communications Lead** | Status updates, notifications | [name, phone, email] | [backup name] |
| **Technical Lead** | Executa mitigações, runbooks | [name, phone, email] | [backup name] |
| **CTO/Executive** | Aprovações, decisões críticas | [name, phone, email] | [backup name] |

### 1.4 Escalation Path
```
L1: Automated alert (PagerDuty)
  ↓
L2: On-call engineer (responds <15 min)
  ↓
L3: Incident Commander (called if severity CRITICAL/HIGH)
  ↓
L4: CTO/Executive (called if customer-facing or media risk)
  ↓
L5: Legal counsel (called for data breach scenarios)
```

---

## 📊 SEÇÃO 2: INCIDENT CLASSIFICATION

### 2.1 Severity Levels

#### CRITICAL (P1)
**Definition:** Service completely unavailable OR major data exposure OR ransomware
**Response Time:** <15 min acknowledgment, <1h mitigation
**Escalation:** Immediate (all hands)
**Examples:**
- Database fully down (no backup accessible)
- All API endpoints returning 500+ for >5 min
- Data breach affecting >100 users
- Ransomware detected on infrastructure
- Customer financial data exposed

**Response:**
- [ ] Declare incident in Slack #incidents channel
- [ ] Page all L3/L4 staff immediately
- [ ] Start war room (Zoom link: [here])
- [ ] Begin investigation + mitigation simultaneously
- [ ] Update status.nexus.app every 15 min
- [ ] Notify affected users <30 min if data breach

---

#### HIGH (P2)
**Definition:** Partial service degradation OR suspicious security activity OR confirmed vulnerability
**Response Time:** <30 min acknowledgment, <4h mitigation
**Escalation:** Incident Commander on-call
**Examples:**
- API latency >2s sustained (P95 threshold)
- Authentication service intermittently failing
- Unauthorized access attempt detected
- SQL injection attempt in logs
- Backup failure (recovery path still available)

**Response:**
- [ ] Log incident in Jira (label: security-incident)
- [ ] Page on-call team via PagerDuty
- [ ] Investigate root cause
- [ ] Implement temporary mitigation (if needed)
- [ ] Update status.nexus.app every 30 min
- [ ] Post-mortem within 24h

---

#### MEDIUM (P3)
**Definition:** Minor service issue OR low-risk vulnerability OR policy violation
**Response Time:** <1h acknowledgment, <1 day mitigation
**Escalation:** Email to security team
**Examples:**
- Single API endpoint slow (>1s)
- Low-severity vulnerability discovered (CVSS <7.0)
- Log access inconsistency (non-critical)
- Failed password update (user reports issue)
- Configuration drift detected (non-critical)

**Response:**
- [ ] Create ticket in Jira (label: medium-priority)
- [ ] Email security lead + tech lead
- [ ] Investigate within 24h
- [ ] Plan remediation for next sprint
- [ ] No public status update (internal only)

---

#### LOW (P4)
**Definition:** Cosmetic issues OR very low-risk findings OR FYI alerts
**Response Time:** <4h acknowledgment, <1 week mitigation
**Escalation:** Email to relevant team only
**Examples:**
- Minor UI bug (no data impact)
- Informational security scan finding
- Duplicate log entries
- Unused API endpoint warning

**Response:**
- [ ] Create ticket in Jira (backlog)
- [ ] No escalation needed
- [ ] Address in next sprint

---

## 🔍 SEÇÃO 3: INCIDENT RESPONSE PROCEDURES

### 3.1 Detection & Reporting

**Alert Sources:**
- [ ] Automated monitoring (PagerDuty)
  - Error rate >1% for 5 min
  - Latency P95 >2s for 10 min
  - CPU >80% for 15 min
  - Disk >80%
  - Backup failure

- [ ] Manual reporting
  - User reports via support@nexus.app
  - Team member notices issue
  - Security scan discovers vulnerability

- [ ] Third-party notification
  - Security vendor alerts (vulnerability databases)
  - User reports via HackerOne/bug bounty
  - Regulatory authority notification

**Initial Response (First 5 minutes):**
```
1. Acknowledge alert in PagerDuty (within 5 min)
2. Determine: is this real? (not a false positive)
3. Classify severity level (P1/P2/P3/P4)
4. If CRITICAL: page entire team immediately
5. If HIGH: page on-call engineer + SM
6. If MEDIUM/LOW: create ticket + email
7. Open Slack channel: #incident-YYYY-MM-DD-HH-MM
8. Post initial message with classification + severity
```

---

### 3.2 Investigation Phase (First 30 minutes for P1/P2)

**Incident Commander Actions:**
- [ ] Declare incident code (e.g., INC-2026-0001)
- [ ] Assign roles (IC, Security Lead, Tech Lead, Comms Lead)
- [ ] Start war room (Zoom + Slack channel)
- [ ] Gather initial facts:
  - When did it start? (exact time)
  - What systems affected?
  - Affected users/data?
  - Business impact?
  - External visibility? (customer-facing?)

**Security Lead Investigation:**
- [ ] Check CloudLogging for suspicious activities
  - Unusual API calls?
  - Failed authentication attempts?
  - Privilege escalation?
  - Data access anomalies?

- [ ] Check Cloud Audit Logs for admin changes
  - Who made changes?
  - What was changed?
  - When?
  - Authorized?

- [ ] Check for known vulnerability signatures
  - Is this a known CVE?
  - Are we vulnerable?
  - Has it been exploited?

- [ ] Interview affected users (if needed)
  - What were they doing when error occurred?
  - Any unusual requests?
  - Did they see any data anomalies?

**Technical Lead Investigation:**
- [ ] Check service health in Cloud Monitoring
  - Is service fully down or degraded?
  - Which services affected?
  - Error rates, latencies?

- [ ] Check Cloud Run revision status
  - Latest deployment working?
  - Rollback to previous revision needed?

- [ ] Check database status
  - Connections normal?
  - Slow queries?
  - Lock contention?
  - Disk space?

- [ ] Check network connectivity
  - VPC routes correct?
  - Security groups allowing traffic?
  - Load balancer health checks passing?

---

### 3.3 Mitigation Phase (Parallel with Investigation)

**For Service Outage:**
1. [ ] Attempt restart: Cloud Run service revision
   - Roll back to last known good: [revision hash]
   - Time to rollback: ~2 min
   - Verify service health: GET /health

2. [ ] If restart fails, check Cloud SQL
   - Can app connect to database?
   - Database accepting connections?
   - Disk space available?
   - Backup restore if needed

3. [ ] If database issue, failover to replica
   - Multi-AZ failover: [time = ~3 min]
   - Verify data consistency post-failover
   - Update DNS/LB if needed

4. [ ] If infrastructure issue, escalate to GCP
   - Open support ticket: Priority: 1
   - Contact: gcp-support@nexus-prod
   - Expected resolution time: 4-8h

**For Data Breach / Security Issue:**
1. [ ] Isolate affected systems
   - Disable the vulnerable API endpoint
   - Revoke credentials if compromised
   - Rotate secrets (database password, API keys, etc.)

2. [ ] Assess breach scope
   - How much data exposed?
   - Which users affected?
   - What data types? (PII, payment data, etc.)
   - Duration of exposure?

3. [ ] Preserve evidence
   - Don't delete logs
   - Save CloudLogging exports
   - Screenshot security events
   - Document timeline

4. [ ] Notify legal + compliance
   - Data breach = legal matter
   - LGPD/GDPR notification may be required
   - Insurance company (cyber liability)

**For Vulnerability Discovery:**
1. [ ] Validate vulnerability
   - Can it be reproduced?
   - What's the CVSS score?
   - Has it been exploited?

2. [ ] Implement workaround (if available)
   - Disable feature temporarily
   - Add WAF rule to block attack
   - Patch if available

3. [ ] Apply permanent fix
   - Develop patch
   - Test in staging
   - Deploy to production
   - Verify fix + regression testing

---

### 3.4 Communication Phase (Continuous)

**Internal Communication (Slack #incident-YYYY-MM-DD-HH-MM):**
- Post every 15 min (P1), 30 min (P2), 1h (P3+)
- Format:
  ```
  **Incident INC-XXXX Status Update**
  Time: [HH:MM UTC]
  Status: [INVESTIGATING | MITIGATING | MONITORING | RESOLVED]

  Summary:
  - Impact: [who/what affected]
  - Mitigation: [what we're doing]
  - ETA to resolution: [time]
  - Next update: [time]
  ```

**External Communication (Status Page):**
- Post to status.nexus.app every 15-30 min
- Format:
  ```
  🟡 INCIDENT: API Degradation
  We're currently investigating elevated response times on the API.
  Affected services: [list]
  Estimated resolution: [time]
  Last update: [time] UTC
  ```

**User Notification (Email/In-App Alert):**
- **Timing:** <30 min from incident start
- **Who:** All affected users (database query to find)
- **Template:** [see Section 3.5]
- **Approval:** Comms Lead + IC (before sending)

**Media/Press (if needed):**
- **Decision:** Made by CTO/CEO only
- **Spokesperson:** [name]
- **Statement:** [prepared in advance]
- **Timing:** <1h for high-visibility incidents

---

### 3.5 User Notification Template

```email
Subject: RESOLVED: API Service Incident on [DATE] [TIME UTC]

Dear NEXUS Users,

We experienced a service incident affecting API availability
on [DATE] from [START TIME] to [END TIME] UTC.

**What happened:**
[Technical explanation in user-friendly language]
[Example: "Our database had a connectivity issue for 23 minutes"]

**What was affected:**
[List specific features/services impacted]
[Example: "User authentication and data sync were temporarily unavailable"]

**Impact:**
[Number of affected users, duration, data loss if any]
[Example: "Approximately 1,200 users experienced service interruption"]

**Root cause:**
[Explanation of why it happened]
[Example: "A network configuration change caused database connection failures"]

**What we did:**
[Mitigation and resolution steps]
[Example: "We reverted the configuration change within 23 minutes"]

**What we're doing to prevent this:**
[Long-term fixes]
[Example: "We're implementing automated configuration validation before deployment"]

**Thank you for your patience.**
If you experienced any issues, please contact support@nexus.app

— NEXUS Team
```

---

## 🔧 SEÇÃO 4: SPECIFIC INCIDENT RUNBOOKS

### 4.1 API Latency Spike Runbook

**Trigger:** P95 latency >2s for 10 consecutive min
**Severity:** P2 (HIGH)

**Steps:**
1. [ ] Check Cloud Monitoring dashboard
   - Look at API latency chart (last 60 min)
   - Identify which endpoints are slow
   - Correlation with other metrics? (CPU, memory, database)

2. [ ] Check database performance
   ```
   SELECT query, calls, mean_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;
   ```
   - Are query times consistent or spiking?
   - New slow queries?
   - Index missing?

3. [ ] Check for resource contention
   - Cloud Run CPU: is it maxed out?
   - Cloud Run memory: is it approaching limit?
   - Database connections: are we hitting pool limit?

4. [ ] Potential mitigations (in order):
   - Increase Cloud Run instances (auto-scaling should kick in)
   - Increase Cloud Run memory (if memory pressure)
   - Kill long-running queries (if database locked)
   - Restart Cloud Run service (last resort)

5. [ ] Validate fix
   - Wait 5 min, check P95 latency
   - Should drop below 500ms
   - If not, escalate to database team

---

### 4.2 Database Connectivity Loss Runbook

**Trigger:** Application cannot connect to Cloud SQL
**Severity:** P1 (CRITICAL)

**Steps:**
1. [ ] Verify database status in GCP console
   - Is instance running? (check status)
   - Any recent changes? (automatic restarts?)
   - Storage quota exceeded? (check disk)

2. [ ] Check VPC Connector health
   - Is VPC Connector available?
   - Any recent configuration changes?
   - Subnet has available IPs?

3. [ ] Test database connectivity from Cloud Run
   ```bash
   gcloud cloud-shell ssh
   gcloud sql connect nexus-prod --user=app_user
   # If prompt for password, use: [SECRET from Secret Manager]
   ```

4. [ ] Check Cloud SQL proxy logs
   - Are there proxy errors?
   - Authentication issues?
   - Connection pool exhaustion?

5. [ ] If database is truly down:
   - [ ] Initiate failover to Multi-AZ standby
     - Automatic failover should trigger
     - Time to failover: ~1-3 min
     - Verify DNS/LB updated automatically

   - [ ] If automatic failover fails:
     - [ ] Open GCP support ticket (P1)
     - [ ] Prepare for manual restore from backup
     - [ ] Estimated recovery time: 30-60 min

6. [ ] Post-mitigation
   - [ ] Monitor database performance (5 min)
   - [ ] Verify application can connect
   - [ ] Run data integrity checks
   - [ ] Confirm no data loss

---

### 4.3 Data Breach Discovery Runbook

**Trigger:** Unauthorized data access detected OR credentials compromised
**Severity:** P1 (CRITICAL)

**Steps:**
1. [ ] **IMMEDIATE (First 5 minutes):**
   - [ ] Page all L3/L4 staff + Legal
   - [ ] Isolate affected system (disable API endpoint if needed)
   - [ ] Revoke compromised credentials
   - [ ] Enable CloudLogging (if not already)
   - [ ] Preserve evidence (don't delete logs)

2. [ ] **Investigation (First 30 minutes):**
   - [ ] Determine scope of breach
     - What data was accessed?
     - How many users affected?
     - Duration of exposure?
     - Was data exfiltrated? (check egress traffic logs)

   - [ ] Identify root cause
     - How were credentials compromised? (leaked secret? brute force?)
     - Was there an unpatched vulnerability?
     - Was access control bypassed?

   - [ ] Assess severity under LGPD/GDPR
     - Is this a "high-risk" breach? (GDPR Art. 34)
     - Notification required? (72h for GDPR, ASAP for LGPD)
     - Does it meet breach notification threshold?

3. [ ] **Notification (First 1-2 hours):**
   - [ ] Notify Legal counsel (email + phone)
   - [ ] Notify Compliance/DPO
   - [ ] Notify Insurance company (cyber liability claim)
   - [ ] Prepare breach notification letter (legal template)
   - [ ] Get approval from Legal before sending to users

4. [ ] **User notification (First 24-72 hours):**
   - [ ] Identify affected users (database query)
   - [ ] Send breach notification email (see template in Section 3.5)
   - [ ] Offer credit monitoring (if applicable)
   - [ ] Provide guidance on password reset
   - [ ] Update Privacy Policy/Terms (disclose breach)

5. [ ] **Remediation (Next 7 days):**
   - [ ] Patch root cause vulnerability
   - [ ] Rotate all credentials + API keys
   - [ ] Reset passwords for all users (or MFA reset)
   - [ ] Add monitoring/alerting to prevent recurrence
   - [ ] Update security controls

6. [ ] **Post-breach (Ongoing):**
   - [ ] File regulatory report (ANPD for LGPD, relevant DPA for GDPR)
   - [ ] Conduct internal audit to find other vulnerabilities
   - [ ] Update incident response plan based on lessons learned
   - [ ] Schedule post-mortem meeting (within 1 week)

---

### 4.4 Ransomware Detection Runbook

**Trigger:** Suspicious file encryption detected OR ransom note found
**Severity:** P1 (CRITICAL)

**Steps:**
1. [ ] **IMMEDIATE (First 2 minutes):**
   - [ ] **ISOLATE:** Disconnect affected server from network
     - Stop Cloud Run service (don't restart)
     - Revoke all IAM credentials
     - Don't touch encrypted files (preserve evidence)

   - [ ] **ALERT:** Page entire team + Legal + Cybersecurity insurance
   - [ ] **PRESERVE:** Take snapshot of disk (for forensics)

2. [ ] **Investigation (First 30 minutes):**
   - [ ] Do NOT pay ransom (likely ineffective + fund criminals)
   - [ ] Identify how ransomware entered
     - Unpatched vulnerability?
     - Compromised credentials?
     - Phishing attack?

   - [ ] Assess impact
     - What data encrypted?
     - Business impact? (can we operate without it?)
     - Can we restore from backup?

   - [ ] Contact FBI/Law Enforcement (if significant impact)
     - File report: ic3.gov (FBI)
     - Preserve logs for law enforcement

3. [ ] **Recovery (First 4-24 hours):**
   - [ ] If unencrypted backup available:
     - [ ] Restore from backup to new infrastructure
     - [ ] Verify data integrity
     - [ ] Deploy with updated security controls

   - [ ] If no backup:
     - [ ] Consult with cybersecurity forensics firm
     - [ ] Determine if decryption key available
     - [ ] Plan data recovery process (may be complex)

4. [ ] **Notification (First 24-48 hours):**
   - [ ] Notify users of data breach (if PII encrypted)
   - [ ] Regulatory notification (LGPD/GDPR)
   - [ ] Update status page (be honest about situation)

---

## 📋 SEÇÃO 5: POST-INCIDENT ACTIVITIES

### 5.1 Incident Closure Criteria

Incident is considered **RESOLVED** when:
- [ ] Root cause identified and documented
- [ ] Mitigation deployed and verified
- [ ] All systems back to normal state
- [ ] No customer-facing impact for >30 min
- [ ] All alerts cleared
- [ ] Incident Commander declares closure

---

### 5.2 Post-Mortem Template

**Schedule:** <24h after incident resolution

**Format:**
```markdown
# Post-Mortem: INC-2026-XXXX

## Summary
- **Incident ID:** INC-2026-XXXX
- **Duration:** [start time] - [end time] UTC ([X minutes])
- **Severity:** P1/P2/P3/P4
- **Affected users:** [number]
- **Root cause:** [brief description]

## Timeline
- **[HH:MM]** - Alert triggered
- **[HH:MM]** - Team paged
- **[HH:MM]** - Root cause identified
- **[HH:MM]** - Mitigation deployed
- **[HH:MM]** - Service recovered
- **[HH:MM]** - All-clear given

## Root Cause Analysis
[Detailed technical explanation of what went wrong]

## Contributing Factors
- Factor 1: [description]
- Factor 2: [description]

## Actions Taken During Incident
- Action 1: [who, what, when]
- Action 2: [who, what, when]

## What Went Well
- Positive 1: [specific action/process]
- Positive 2: [specific action/process]

## What Could Be Improved
- Improvement 1: [specific area for enhancement]
- Improvement 2: [specific area for enhancement]

## Follow-Up Actions (Action Items)
| Action | Owner | Due Date | Priority |
|--------|-------|----------|----------|
| [Action 1] | [Name] | [Date] | P0 |
| [Action 2] | [Name] | [Date] | P1 |

## Lessons Learned
[Key insights for the team]
```

---

### 5.3 Incident Metrics

Track these metrics per quarter:
- Total incidents: [X]
- By severity: P1: [X], P2: [X], P3: [X], P4: [X]
- Mean time to detect (MTTD): [X min]
- Mean time to mitigate (MTTM): [X min]
- Mean time to recovery (MTTR): [X min]
- Recurrence rate: [% of repeat incidents]
- Customer-facing impact: [% of incidents]

---

## ✅ SEÇÃO 6: SIGN-OFF & TRAINING

### 6.1 Playbook Approval

```
Approved by:

Incident Response Lead: _________________________ Date: __/__/__
CTO: _________________________ Date: __/__/__
Legal Counsel: _________________________ Date: __/__/__
Security Officer: _________________________ Date: __/__/__
```

### 6.2 Team Training

- [ ] All team members trained: [date]
- [ ] Annual refresher scheduled: [date]
- [ ] Tabletop exercise: [scheduled date]
- [ ] Last tabletop drill: [date, result]

**Training checklist:**
- [ ] Watched incident response video: [link]
- [ ] Read this playbook in full
- [ ] Knows their role + responsibilities
- [ ] Knows escalation procedure
- [ ] Can access war room (Slack + Zoom)
- [ ] Can access incident tools (Jira, PagerDuty, etc.)

---

## 📎 REFERÊNCIAS

- [PagerDuty Incident Response Best Practices](https://www.pagerduty.com/)
- [NIST Incident Response Guide](https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final)
- [AWS Security Incident Response](https://aws.amazon.com/blogs/security/)
- [GCP Security Best Practices](https://cloud.google.com/security/best-practices)

**Document Version:** 1.0
**Effective Date:** 2026-01-02
**Last Updated:** 2026-01-02
**Next Review:** 2026-04-02 (quarterly)
