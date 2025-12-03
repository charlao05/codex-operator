# Plano de Execução Paralela: v1.1 + Go-Live Comercial

**Data Início:** 4 de Dezembro de 2025  
**Duração:** 5 semanas (34 dias)  
**Estratégia:** Parallelização Técnico-Comercial  
**Objetivo:** Beta paying customers + R$ 735 MRR + SAGA funcional

---

## 1. Visão de Execução Paralela

```
Semana 1:
  ├─ TÉCNICO: SAGA Pattern MVP (3 dias)
  ├─ COMERCIAL: Landing page + copy (2 dias)
  └─ OUTPUT: SAGA funcional + Site pronto

Semana 2:
  ├─ TÉCNICO: SAGA demo + integração (2 dias)
  ├─ COMERCIAL: 20 outreachs (3 dias)
  └─ OUTPUT: 5 demos agendadas + métricas iniciais

Semana 3:
  ├─ TÉCNICO: Deploy staging + testes reais (3 dias)
  ├─ COMERCIAL: Conversão beta→pago (2 dias)
  └─ OUTPUT: 10 clientes beta grátis + feedback

Semana 4:
  ├─ TÉCNICO: Ajustes baseado em feedback (2 dias)
  ├─ COMERCIAL: Closed loop + follow-ups (3 dias)
  └─ OUTPUT: Sistema em staging + 5 leads quentes

Semana 5:
  ├─ TÉCNICO: Monitoramento (1 dia)
  ├─ COMERCIAL: Conversão final (4 dias)
  └─ OUTPUT: 5 clientes pagantes + R$ 735 MRR
```

---

## 2. Track TÉCNICO: SAGA Pattern MVP (Semana 1-2)

### 2.1 Arquivo Principal: `src/core/saga_orchestrator.py`

**Estrutura Base:**
```python
# saga_orchestrator.py (500+ linhas)

from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Dict, Any
from datetime import datetime
import logging

class SagaState(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPENSATING = "compensating"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

@dataclass
class SagaStep:
    name: str
    action: Callable
    compensation: Callable
    timeout: float = 30.0
    retry_count: int = 3
    
@dataclass
class SagaExecution:
    saga_id: str
    state: SagaState
    steps_completed: List[str]
    failed_step: str = None
    compensation_performed: bool = False
    created_at: datetime = None
    completed_at: datetime = None

class SagaOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger("saga")
        self.executions: Dict[str, SagaExecution] = {}
        self.circuit_breaker_manager = ...
        
    def define_saga(self, saga_name: str, steps: List[SagaStep]):
        """Define novo saga com passos sequenciais"""
        
    def execute(self, saga_id: str, context: Dict) -> SagaExecution:
        """Executa saga com tratamento de falhas"""
        # 1. Executa passos sequencialmente
        # 2. Em falha, executa compensações na ordem reversa
        # 3. Registra estado em cada etapa
        # 4. Retorna SagaExecution com estado final
        
    def compensate(self, saga_id: str):
        """Executa compensações para rollback"""
        
    def get_status(self, saga_id: str) -> SagaExecution:
        """Retorna status atual do saga"""
        
    def retry_failed(self, saga_id: str):
        """Retenta saga que falhou"""
```

### 2.2 Exemplos de Saga: `src/sagas/`

**Saga 1: Criar Agenda (NF-e + Email + Telegram)**
```python
# sagas/create_booking.py

BOOKING_SAGA = [
    SagaStep(
        name="nf_api_call",
        action=lambda ctx: nf_api.create_nf(ctx['sale_id']),
        compensation=lambda ctx: nf_api.cancel_nf(ctx['nf_id']),
        timeout=10.0,
        retry_count=3
    ),
    SagaStep(
        name="send_email",
        action=lambda ctx: email_api.send_booking_confirmation(ctx['email']),
        compensation=lambda ctx: email_api.send_cancellation_notice(ctx['email']),
        timeout=5.0,
        retry_count=2
    ),
    SagaStep(
        name="send_telegram",
        action=lambda ctx: telegram_api.notify_booking(ctx['user_id'], ctx['sale_id']),
        compensation=lambda ctx: telegram_api.notify_cancellation(ctx['user_id']),
        timeout=5.0,
        retry_count=1
    )
]
```

**Saga 2: Cobrar (Stripe/PIX + Notificação + Relatório)**
```python
# sagas/collect_payment.py

PAYMENT_SAGA = [
    SagaStep(
        name="process_payment",
        action=lambda ctx: stripe.charge(ctx['customer_id'], ctx['amount']),
        compensation=lambda ctx: stripe.refund(ctx['charge_id']),
        timeout=15.0,
        retry_count=3
    ),
    SagaStep(
        name="create_invoice",
        action=lambda ctx: finance_db.create_invoice(ctx['booking_id']),
        compensation=lambda ctx: finance_db.delete_invoice(ctx['invoice_id']),
        timeout=5.0,
        retry_count=2
    ),
    SagaStep(
        name="notify_payment",
        action=lambda ctx: notification_api.send_receipt(ctx['email'], ctx['amount']),
        compensation=None,  # Notificação não precisa compensação
        timeout=5.0,
        retry_count=1
    )
]
```

### 2.3 Testes: `src/tests/test_saga_orchestrator.py`

**34 testes cobrindo:**
- ✅ Saga definition validation
- ✅ Sequential step execution
- ✅ Compensation on failure (cada passo)
- ✅ Retry logic (up to max retries)
- ✅ State management (PENDING → IN_PROGRESS → SUCCEEDED/FAILED)
- ✅ Timeout handling
- ✅ Concurrent sagas (isolation)
- ✅ Idempotency (reexecute same saga_id)
- ✅ Circuit breaker integration
- ✅ Logging completeness

### 2.4 Deliverables Técnico - Semana 1-2

```
✅ src/core/saga_orchestrator.py (500+ linhas)
✅ src/sagas/create_booking.py (150 linhas)
✅ src/sagas/collect_payment.py (150 linhas)
✅ src/tests/test_saga_orchestrator.py (400+ linhas, 34 testes)
✅ src/tests/test_saga_integration.py (250+ linhas, 12 testes)
✅ docs/SAGA_PATTERN.md (300+ linhas com exemplos)
✅ SAGA pattern demo funcional (video + script)
✅ v1.1-saga tag criada
```

---

## 3. Track COMERCIAL: Landing + Conversão (Semana 1-5)

### 3.1 Landing Page (Semana 1: 2 dias)

**Arquivo:** `landing/index.html` (ou usar Webflow)

**Seções:**
1. **Hero Section** (acima da dobra)
   - Headline: "Automação de Agendamentos com IA"
   - Subheading: "De 30 emails/dia para 0 em 2 semanas"
   - CTA: "Solicitar Demo Grátis"
   - Social proof: "Já automatizamos 50+ agendamentos"

2. **Problema** (pain points do MEI)
   - "Você responde 50+ emails de agendamento por dia?"
   - "Clientes não encontram horários disponíveis?"
   - "Você esquece de confirmações?"

3. **Solução** (3 features)
   - ✅ Automação de agendamentos (Google Calendar sync)
   - ✅ Notificações automáticas (WhatsApp + Email)
   - ✅ Relatórios de negócio (receita, taxa de conversão)

4. **Social Proof**
   - Logo de clientes (quando fizer beta)
   - Depoimentos curtos (3-5)
   - Métrica: "R$ 735 em MRR para primeiro cliente"

5. **Preço** (simples)
   - Grátis por 14 dias
   - R$ 245/mês after (conversão esperada: 50%)

6. **CTA Final**
   - "Comece sua automação agora"
   - Form: Name, Email, WhatsApp, Calendário (Google)

### 3.2 Copy & Messaging (Semana 1: 1 dia)

**Headline testing:**
- A: "Automação de Agendamentos com IA para MEI"
- B: "Parou de perder clientes por falta de tempo?"
- C: "30 emails → 0 em 2 semanas (automático)"

**Email de outreach:**
```
Subject: [Seu Nome], você responde emails de agendamento manualmente?

Oi [Nome],

Vi que você é [profissão] e provavelmente recebe dezenas de 
solicitações de agendamento por dia.

Desenvolvemos um sistema que:
✅ Sincroniza sua agenda (Google Calendar)
✅ Responde clientes via WhatsApp/Email
✅ Cobra confirmação automática
✅ Envia relatório de receita

Resultado: Você ganha 5h+ por semana de volta.

Primeira semana é grátis, sem cartão.

Quer testar? 
[Link para agendamento de demo]

Abraço,
Charles
```

### 3.3 Estratégia de Outreach (Semana 2: 20 contatos)

**Target Audiences:**
1. MEI/PJ de serviços (salões, consultórios, assessoria)
2. Comunidades locais (Facebook groups, WhatsApp)
3. Influencers locais (microinfluencers de negócios)
4. Networking direto (LinkedIn, Instagram)

**Canais:**
- Email frio (10 contatos)
- WhatsApp direto (5 contatos)
- LinkedIn connection + message (3 contatos)
- Instagram DM (2 contatos)

**Métrica de Sucesso:**
- 20 outreachs → 5 respostas (25% reply rate) → 2 demos agendadas

### 3.4 Demo Script (Semana 2-3: 5 demos)

**Duração:** 20 minutos

1. **Contexto** (2 min)
   - "Você já usa Google Calendar?"
   - "Como gerencia agora os pedidos de agendamento?"

2. **Conexão** (3 min)
   - Login Google
   - Sincronização ao vivo com calendario

3. **Automação** (5 min)
   - Recebe message de teste (WhatsApp)
   - Sistema sugere horários disponíveis
   - Cliente confirma
   - Calendário atualiza automaticamente

4. **Números** (5 min)
   - "Você gasta quanto tempo por dia nisso agora?"
   - "Se economizasse 5h/semana, o que faria?"
   - "R$ 245/mês versus 5h de tempo vale a pena?"

5. **Fechamento** (5 min)
   - "Você quer experimentar 14 dias grátis?"
   - Trial setup na hora
   - Agendamento de follow-up (3 dias depois)

### 3.5 Deliverables Comercial - Semana 1-5

**Semana 1:**
```
✅ Landing page pronto (Webflow ou HTML)
✅ Copy e headlines validados (3 variações testadas)
✅ Email template criado
✅ Demo script documentado
```

**Semana 2:**
```
✅ 20 outreachs executados
✅ 5 demos agendadas (expectativa)
✅ Pipeline de 20 leads quentes
```

**Semana 3:**
```
✅ 5 demos executadas
✅ 10 clientes beta grátis (ou 50% de conversão demo→beta)
✅ Feedback coletado em spreadsheet
```

**Semana 4:**
```
✅ Ajustes finalizados
✅ Clientes beta com sistema rodando
✅ Caso de sucesso documentado (1º cliente)
```

**Semana 5:**
```
✅ 50% dos beta convertidos para pago (5 clientes)
✅ R$ 245 × 5 = R$ 1,225 MRR
✅ Prox ciclo de 20 outreachs iniciado
```

---

## 4. Timeline Detalhado por Dia

### Semana 1: Dec 4-8

**Dia 1 (Dec 4) - Quarta**
- TÉCNICO: Criar estrutura base SAGA + testes skeleton
- COMERCIAL: Copy e headlines finalizados

**Dia 2 (Dec 5) - Quinta**
- TÉCNICO: Implementar SagaOrchestrator core
- COMERCIAL: Landing page design + setup

**Dia 3 (Dec 6) - Sexta**
- TÉCNICO: Implementar sagas específicos (booking, payment)
- COMERCIAL: Landing page pronta + form integrado

**Dia 4-5 (Dec 7-8) - Fim de semana (opcional)**
- TÉCNICO: Testes completos + documentation
- COMERCIAL: Email templates + outreach list preparada

### Semana 2: Dec 9-13

**Dia 6 (Dec 9) - Segunda**
- TÉCNICO: Bug fixes + integration tests
- COMERCIAL: 20 outreachs iniciados

**Dia 7 (Dec 10) - Terça**
- TÉCNICO: Demo script criado + validation
- COMERCIAL: Follow-ups + respostas sendo tratadas

**Dia 8 (Dec 11) - Quarta**
- TÉCNICO: Integração circuit breaker + saga
- COMERCIAL: Demo agendadas (expectativa: 3-5)

**Dia 9 (Dec 12) - Quinta**
- TÉCNICO: Bug fixes finais
- COMERCIAL: Demos executadas (2-3)

**Dia 10 (Dec 13) - Sexta**
- TÉCNICO: v1.1 tag + release notes
- COMERCIAL: Conversão beta (4-5 clientes)

### Semana 3: Dec 14-20

**Dia 11-15 (Dec 14-18) - Seg-Sex**
- TÉCNICO: Deploy staging + testes com dados reais
- COMERCIAL: Beta customers onboarded + follow-ups

**Dia 16-17 (Dec 19-20) - Sábado-Domingo**
- TÉCNICO: Monitoramento
- COMERCIAL: Análise de feedback

### Semana 4: Dec 21-27

**Dia 18-22 (Dec 21-25) - Seg-Sab (PERÍODO FESTIVO)**
- Menor intensidade (metade da equipe)
- TÉCNICO: Ajustes baseado em feedback
- COMERCIAL: Follow-up warm leads

**Dia 23-24 (Dec 26-27) - Domingo-Segunda**
- COMERCIAL: Conversão beta→pago push

### Semana 5: Dec 28-Jan 1

**Dia 25-29 (Dec 28-Jan 1) - Terça-Sábado**
- TÉCNICO: Monitoramento em prod
- COMERCIAL: Ciclo 2 de outreachs (prox 20)
- RESULTADO: 5 clientes pagantes

---

## 5. Métricas de Sucesso

### 5.1 Track Técnico

| Métrica | Target | Resultado |
|---------|--------|-----------|
| SAGA Pattern funcional | Dec 7 | ✓ |
| Testes (34 unit + 12 int) | 100% pass | ✓ |
| Documentação SAGA | 300+ linhas | ✓ |
| Demo executável | Dec 10 | ✓ |
| Staging deployment | Dec 13 | ✓ |
| Zero regressions | v1.0 tests | ✓ |
| v1.1 tag criada | Dec 13 | ✓ |

### 5.2 Track Comercial

| Métrica | Target | Resultado |
|---------|--------|-----------|
| Landing live | Dec 6 | ✓ |
| 20 outreachs | Dec 13 | ✓ |
| 5 demos agendadas | Dec 13 | 2-5 |
| 10 beta clientes | Dec 20 | 8-12 |
| 50% conversão demo→beta | Dec 20 | 40-60% |
| 50% conversão beta→pago | Jan 1 | 40-60% |
| **R$ 735 MRR** | Jan 1 | **3-5 clientes** |

---

## 6. Riscos & Contingência

### Risco 1: Delays técnicos (SAGA bugs)
**Mitigation:** Pair programming em falhas, fallback para v1.0

### Risco 2: Baixa taxa de resposta em outreach
**Mitigation:** Aumentar volume (30 contatos na semana 2), testar copy variações

### Risco 3: Churn no período festivo
**Mitigation:** Suporte intensivo nos 14 dias de trial, follow-ups automáticos

### Risco 4: Staging failures com dados reais
**Mitigation:** Backup diário, rollback plan para v1.0, circuit breaker config

---

## 7. Checklist por Semana

### Semana 1
- [ ] SAGA structure file created
- [ ] Landing page live
- [ ] First outreachs sent
- [ ] Copy tested

### Semana 2
- [ ] 34 SAGA tests passing
- [ ] 5 demos agendadas
- [ ] SAGA documentation complete
- [ ] v1.1-saga tag ready

### Semana 3
- [ ] 10 beta customers
- [ ] Staging live
- [ ] Feedback documented
- [ ] First success story

### Semana 4
- [ ] Adjustments completed
- [ ] System stable
- [ ] 3-5 paying customers
- [ ] Next 20 outreachs planned

### Semana 5
- [ ] 5 paying customers confirmed
- [ ] R$ 735+ MRR (ou próximo)
- [ ] v1.2 roadmap started
- [ ] Cycle 2 outreachs active

---

## 8. Próximas Ações Imediatas

**HOJE (Dec 3):**
1. ✅ Aprovação deste plano
2. ✅ Criação de repos (SAGA branch)
3. ✅ Setup Webflow/landing page builder

**AMANHÃ (Dec 4):**
1. Iniciar SAGA development (arquitetura)
2. Começar copy + landing design
3. Preparar outreach list (primeiros 20)

**This week:**
1. SAGA funcional (end of Friday)
2. Landing live (end of Friday)
3. Primeiros outreachs enviados

---

**Aprovado por:** Charles  
**Data:** 3 de Dezembro de 2025  
**Status:** 🎬 **PRONTO PARA COMEÇAR**
