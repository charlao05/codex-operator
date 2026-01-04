# GO_LIVE_CHECKLIST.md

## Lista de Verificação para Go-Live da Plataforma NEXUS

### Versão: 1.0
### Data de Criação: Janeiro 2026
### Classificação: MÁXIMO RIGOR

---

## Pre-Go-Live Checks (T-7 dias)

### Infraestrutura e Segurança
- [ ] VPC isolada criada e validada
- [ ] Security groups configurados com regras restritivas
- [ ] WAF (Web Application Firewall) ativado
- [ ] DDoS protection ativado
- [ ] Load balancer testado com 1000 req/s
- [ ] Auto-scaling policies configuradas e testadas
- [ ] Certificados SSL/TLS válidos (não vencidos por 1 ano)
- [ ] DNSSEC habilitado
- [ ] Backup automatizado e validado com criação de dados de teste

### Banco de Dados
- [ ] Replicação primária/secundária configurada
- [ ] Testes de failover executados com sucesso
- [ ] Tempo de failover < 2 minutos
- [ ] Backup eà cada 6 horas habilitado
- [ ] Retenção de backup = 30 dias mínimo
- [ ] Testes de restauração de backup executados (RTO < 4h)
- [ ] Plano de execução para escalabilidade criado

### APIs e Integratos
- [ ] Todos os endpoints testados com Postman/Insomnia
- [ ] Rate limiting configurado (100 req/min por chave de API)
- [ ] Throttling implementado e testado
- [ ] Error handling robusto para timeout > 5 segundos
- [ ] OAuth 2.0 flow testado end-to-end
- [ ] Token refresh automatizado validado
- [ ] API versioning habilitado (v1)
- [ ] Documentação API atualizada no Swagger/OpenAPI

### Monitoramento e Logging
- [ ] Prometheus/Grafana configurado
- [ ] Alertas para CPU > 80% habilitados
- [ ] Alertas para memória > 85% habilitados
- [ ] Alertas para taxa de erro > 1% habilitados
- [ ] Alertas para latencia > 1000ms habilitados
- [ ] Logs estruturados com JSON habilitados
- [ ] Log retention policy = 90 dias
- [ ] ELK Stack ou Cloud Logging centralizado
- [ ] Audit logs habilitados para alterações críticas

### Testing
- [ ] Teste de carga: 500 usuários simultâneos
- [ ] Teste de estresse: 1000 usuários
- [ ] Teste de resistencia: 48 horas de execução
- [ ] Teste de segurança: Pentesting realizado
- [ ] Teste de compliance: LGPD validado
- [ ] Teste de acessibilidade: WCAG 2.1 AA validado
- [ ] Teste de performance: Lighthouse score > 85
- [ ] Cobertura de testes unitários > 85%
- [ ] Cobertura de testes integração > 80%

### Conformidade Legal
- [ ] Termos de Serviço atualizados e publicados
- [ ] Política de Privacidade LGPD-compliant publicada
- [ ] Consentimento de cookies habilitado
- [ ] Data Processing Agreement (DPA) assinado (se aplicável)
- [ ] Notificação de incidente de dados preparada

### Equipe e Operações
- [ ] 2+ DevOps engineers em standby
- [ ] On-call rotation ativado 24/7
- [ ] Runbook de incidentes criado e revisado
- [ ] Escalation procedures documentadas
- [ ] Plano de comunicação com stakeholders criado
- [ ] Treinamento da equipe de suporte completado

---

## Go-Live Checks (T-24 horas)

### Pre-Go-Live
- [ ] Todos os checks T-7 revalidados (Green status)
- [ ] Rollback plan simulado com sucesso
- [ ] Database backup fresco (< 1 hora)
- [ ] Load balancers em perfeito estado
- [ ] Cache (Redis) aquecido e validado
- [ ] DNS propagado (dig/nslookup)

### Go-Live Execution
- [ ] Blue/green deployment iniciado
- [ ] Health checks passando 100%
- [ ] Tracing distribuído habilitado (Jaeger/Zipkin)
- [ ] Tela de status operacional exibindo green
- [ ] Monitoramento em tempo real ativado
- [ ] Suporte técnico monitorando logs

---

## Post-Go-Live Checks (T+24 horas)

- [ ] Taxa de erro < 0.1%
- [ ] P99 latencia < 500ms
- [ ] Taxa de sucesso de API >= 99.9%
- [ ] Zero alertas críticos não resolvidos
- [ ] Feedback positivo de usuários beta
- [ ] Não há escalada de incidentes

---

## Rollback Triggers

**Rollback será acionado automaticamente se:**
- Taxa de erro > 5% por 5 minutos
- Latencia P99 > 2000ms
- Falha de banco de dados
- Consumo de memória > 95%
- Taxa de requisições rejeitadas > 1%

**Tempo de execução de rollback**: < 15 minutos

---

## Sign-Off

- [ ] Tech Lead: _________________________ Data: _________
- [ ] DevOps Lead: _______________________ Data: _________
- [ ] Product Manager: ___________________ Data: _________
- [ ] Security Officer: __________________ Data: _________

---

**Status Final**: ✅ APROVADO PARA GO-LIVE
