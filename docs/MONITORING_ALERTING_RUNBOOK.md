# MONITORING_ALERTING_RUNBOOK.md

## Runbook de Monitoramento e Alertas - Plataforma NEXUS

### Versão: 1.0
### Data: Janeiro 2026
### Classificação: MÁXIMO RIGOR

---

## 1. Stack de Monitoramento

**Infraestrutura:**
- Prometheus (métricas)
- Grafana (dashboards)
- ELK Stack (logs)
- Jaeger (tracing distribuído)
- PagerDuty (alerting/on-call)

**Cobertura:**
- 100% dos endpoints críticos
- 100% dos workers/background jobs
- 100% dos serviços de terceiros
- 100% da infraestrutura (CPU, memória, disco)

---

## 2. Alertas Obrigatórios

### Camada de Aplicação
| Alerta | Threshold | Duraca | Acao |
|---|---|---|---|
| Taxa de Erro Alta | > 5% | 5 min | P1 - Slack + Page |
| Latência P99 | > 1000ms | 5 min | P2 - Slack |
| Taxa de Erro de Autenticação | > 10/min | 1 min | P1 - Page |
| Request Timeout | > 2% | 5 min | P2 - Slack |
| Memory Leak Detectão | Crescimento 50%/h | 1h | P1 - Page |

### Banco de Dados
| Alerta | Threshold | Acao |
|---|---|---|
| Conexões Critícas | > 90% do pool | P1 |
| Replica Lag | > 10s | P1 |
| Espaço em Disco | > 85% | P2 |
| Tempo de Query | > 5s (p99) | P2 |
| Falha de Backup | Não completou em 24h | P1 |

### Infraestrutura
| Alerta | Threshold | Acao |
|---|---|---|
| CPU | > 80% por 5min | P2 |
| Memória | > 85% | P2 |
| Disco | > 90% | P1 |
| Largura de Banda | > 80% | P2 |
| Node Down | Não responde | P0 |

### Segurança
| Alerta | Threshold | Acao |
|---|---|---|
| Falha de Autenticação | > 100/min | P1 |
| IP Suspeito | > 10 requisições/min | P1 |
| Acesso Não Autorizado | Qualquer | P0 |
| Execução de Query Suspeita | Detectada | P0 |
| Modificação Não Aprovada | Prod | P0 |

---

## 3. Dashboards Obrigatórios

### Dashboard Principal (SRE)
- Taxa de erro por serviço (realtime)
- Latência P50/P95/P99
- Taxa de requisições por segundo
- CPU/Memória/Disco utilização
- Health status de todas as dependências

### Dashboard de Segurança (Security)
- Taxa de falha de autenticação
- IPs Únicossugpeitos
- Tentativas de acesso não autorizado
- Modificações de sistema
- Logs de auditoria

### Dashboard de Banco de Dados (DBA)
- Conexões ativas
- Replica lag
- Tamanho do banco
- Top queries lentas
- Status de backup

---

## 4. SLOs (Service Level Objectives)

| Serviço | Disponibilidade | Latência P99 | Taxa de Erro |
|---|---|---|---|
| API Principal | 99.9% | < 500ms | < 0.1% |
| Autenticação | 99.95% | < 200ms | < 0.01% |
| Payment Gateway | 99.99% | < 1000ms | < 0.001% |
| Background Jobs | 99% | < 30s | < 1% |

---

## 5. Runbooks de Resposta

### Alta Taxa de Erro
1. Verificar Grafana -> Error Rate dashboard
2. Correlacionar com logs (ELK Stack)
3. Verificar versão deployé recentemente
4. Se sim -> Considere rollback
5. Se não -> Escale para Engineering

### Latência Elevada
1. Verificar query mais lenta (RDS Insights)
2. Verificar CPU/Memória do servidor
3. Verificar rede (bandwidth)
4. Escalar se necessário

### Falha de Replica
1. SSH para servidor de réplica
2. Verificar status: `SHOW SLAVE STATUS`
3. Se lag alto: resetar replica
4. Notificar DBA se manual fix needed
5. Escalar a P1 se primária down

---

## 6. Retention Policies

- Prometheus: 30 dias
- Grafana: Unlimited (historíco)
- Logs: 90 dias (quentes), 1 ano (archived)
- Audit logs: 2 anos
- Backup: 30 dias (incrmental), 1 ano (full)

---

## 7. Testes de Monitoramento

**Mensal:**
- Fire synthetic alerts
- Validar notificação via PagerDuty
- Verificar dashboards são atualizados

**Trimestral:**
- Teste de failover completo
- Validar RTO de recoveréncia
- Review de SLOs vs realidade

---

## 8. Approval

- [ ] SRE Lead: _________________________ Data: _________
- [ ] Security Lead: _____________________ Data: _________
- [ ] DBA: _____________________________ Data: _________

---

**Status**: ✅ IMPLEMENTADO E OPERACIONAL
