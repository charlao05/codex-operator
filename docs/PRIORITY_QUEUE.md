## Priority Queue (Min-Heap) - Documentação Técnica

**Versão:** v1.0  
**Autor:** Codex Operator  
**Data:** Dezembro 2025  

---

## 1. Visão Geral

A **Priority Queue** implementada com **Min-Heap** é uma estrutura de dados que permite processamento eficiente de tarefas baseado em prioridade, deadline e custo computacional.

### Problema que Resolve

```
Sem Priority Queue (Sequential):
  Task 1 (LOW, 30min deadline)  → 45s processamento
  Task 2 (CRITICAL, NOW!)      → Aguarda 45s ❌
  
Com Priority Queue (Min-Heap):
  Task 2 (CRITICAL, NOW!)      → 2s processamento ✓
  Task 1 (LOW, 30min deadline) → 45s processamento ✓
```

**Benefício:** Tarefas críticas processadas primeiro, respeitando SLAs (Service Level Agreements).

---

## 2. Arquitetura: Min-Heap

```
┌──────────────────────────────────────────────┐
│           PRIORITY QUEUE (Min-Heap)          │
└──────────────────────────────────────────────┘

Estrutura em memória (exemplo 4 tarefas):

                    ┌─────────────┐
                    │  Task A     │
                    │  (Priority: │
                    │   CRITICAL) │
                    └──────┬──────┘
                    /              \
            ┌──────┴─┐         ┌──┴────────┐
            │ Task B │         │  Task C   │
            │ (HIGH) │         │ (MEDIUM)  │
            └────────┘         └───┬───────┘
                                   │
                            ┌──────┴────┐
                            │  Task D   │
                            │  (LOW)    │
                            └───────────┘
```

### Propriedade Min-Heap

**Pai ≤ Filhos em ordem de prioridade**

```python
# Ordem de processamento (pop):
heap.pop()  # Task A (CRITICAL)
heap.pop()  # Task B (HIGH)
heap.pop()  # Task C (MEDIUM)
heap.pop()  # Task D (LOW)
```

---

## 3. Prioridades

```python
from src.core.agent_queue import TaskPriority

class TaskPriority(Enum):
    CRITICAL = 1    # Urgente (< 1h ou client paid)
    HIGH = 2        # Importante (< 4h)
    MEDIUM = 3      # Normal (< 1 dia)
    LOW = 4         # Background (< 1 semana)
    DEFERRED = 5    # Batch/archive (sem deadline)
```

### Exemplos de Mapeamento

| Tarefa | Prioridade | Motivo |
|--------|-----------|--------|
| Cobrança urgente (vencido hoje) | CRITICAL | Risco financeiro |
| NF-e com deadline amanhã | HIGH | SLA 24h |
| Agendamento com cliente | MEDIUM | Prioridade normal |
| Processamento em lote | LOW | Pode esperar |
| Limpeza de logs | DEFERRED | Sem deadline |

---

## 4. Ordenação: Tiebreaker

Quando duas tarefas têm mesma prioridade, usa-se ordem:

```
1. Priority (menor = mais urgente)
2. Deadline (mais próximo = primeiro)
3. Cost (menor = mais barato)
4. Created At (mais antigo = FIFO tiebreaker)
```

### Exemplo Prático

```python
# 3 tarefas com mesma prioridade (MEDIUM)
Task 1: priority=3, deadline=2025-12-25 14:00, cost=5
Task 2: priority=3, deadline=2025-12-25 16:00, cost=3  ← Deadline mais próximo
Task 3: priority=3, deadline=2025-12-25 14:00, cost=1  ← Mesmo deadline, menor cost

# Ordem de processamento:
1. Task 3 (deadline=14:00, cost=1)
2. Task 1 (deadline=14:00, cost=5)
3. Task 2 (deadline=16:00, cost=3)
```

---

## 5. Operações e Complexidade

```python
from src.core.agent_queue import AgentQueue, TaskPriority, create_deadline

# Criar fila
queue = AgentQueue(max_size=1000)

# PUSH: Adicionar tarefa - O(log n)
deadline = create_deadline(days_ahead=1)
task_id = queue.push(
    priority=TaskPriority.HIGH,
    deadline=deadline,
    cost=2,
    agent_name="nf_agent",
    client_id="client_123",
    payload={"sale_id": "456"}
)

# POP: Remover tarefa com maior prioridade - O(log n)
task = queue.pop()
# Retorna: AgentTask(
#   task_id="abc123",
#   priority=1,
#   deadline=timestamp,
#   agent_name="nf_agent",
#   ...
# )

# PEEK: Visualizar próxima sem remover - O(1)
next_task = queue.peek()

# GET: Operações de query
all_tasks = queue.get_all_tasks()               # O(n log n) - retorna sorted
agent_tasks = queue.get_tasks_for_agent("nf")   # O(n) - linear search
client_tasks = queue.get_tasks_for_client("c1") # O(n) - linear search

# REMOVE: Remover tarefa específica - O(n)
removed = queue.remove_task(task_id)

# INFO: Obter estatísticas - O(1)
stats = queue.get_stats()
size = queue.size()                             # O(1)
is_empty = queue.is_empty()                     # O(1)
```

### Tabela de Complexidade

| Operação | Complexidade | Quando Usar |
|----------|-------------|------------|
| `push()` | O(log n) | Adicionar tarefa |
| `pop()` | O(log n) | Processar próxima |
| `peek()` | O(1) | Verificar próxima |
| `size()` | O(1) | Monitorar fila |
| `get_all_tasks()` | O(n log n) | Dashboard/UI |
| `get_tasks_for_agent()` | O(n) | Query específica |
| `remove_task()` | O(n) | Cancelar tarefa |
| `clear()` | O(1) | Limpar tudo |

---

## 6. Validações

```python
# TaskPriority: Deve ser 1-5
queue.push(priority=10, ...)  # ❌ ValueError

# Cost: Deve ser ≥ 0
queue.push(cost=-5, ...)      # ❌ ValueError

# Deadline: Deve ser datetime
queue.push(deadline="2025-12-25", ...)  # ❌ ValueError

# Max Size: Rejeita se fila cheia
queue = AgentQueue(max_size=10)
for i in range(11):
    task_id = queue.push(...)
    if task_id is None:       # 11ª retorna None
        print("Fila cheia, rejeitada")
```

---

## 7. Uso Prático

### Caso 1: Processamento de NF-e

```python
from src.core.agent_queue import AgentQueue, TaskPriority, create_deadline

# Criar fila central
nf_queue = AgentQueue(max_size=5000)

# Receber vendas
sales = [
    {"id": "123", "client": "c1", "amount": 1000},
    {"id": "124", "client": "c2", "amount": 500},
    {"id": "125", "client": "c3", "amount": 10000},  # Valor alto
]

# Enfileirar com prioridades
for sale in sales:
    priority = TaskPriority.CRITICAL if sale["amount"] > 5000 else TaskPriority.MEDIUM
    deadline = create_deadline(days_ahead=1)
    
    task_id = nf_queue.push(
        priority=priority,
        deadline=deadline,
        cost=2,  # NF-e custa 2 "unidades computacionais"
        agent_name="nf_agent",
        client_id=sale["client"],
        payload=sale
    )

# Processar em ordem de prioridade
while not nf_queue.is_empty():
    task = nf_queue.pop()
    print(f"Processando NF #{task.payload['id']} (priority={task.priority})")
    # Executar nf_agent.prepare_invoice_steps()
```

### Caso 2: Agendamento de Confirmações

```python
# Sistema de agendamento de confirmações de cliente
booking_queue = AgentQueue(max_size=2000)

# Receber bookings
bookings = [
    {"booking_id": "b1", "datetime": "2025-12-25 14:00", "reminder_days": 7},
    {"booking_id": "b2", "datetime": "2025-12-25 10:00", "reminder_days": 1},
    {"booking_id": "b3", "datetime": "2025-12-25 16:00", "reminder_days": 3},
]

for booking in bookings:
    # Calcular prioridade por dias até evento
    days_until = booking["reminder_days"]
    if days_until < 1:
        priority = TaskPriority.CRITICAL
    elif days_until < 3:
        priority = TaskPriority.HIGH
    else:
        priority = TaskPriority.MEDIUM
    
    # Deadline: data do evento - dias de antecedência
    event_date = datetime.fromisoformat(booking["datetime"])
    deadline = event_date - timedelta(days=booking["reminder_days"])
    
    booking_queue.push(
        priority=priority,
        deadline=deadline,
        cost=1,  # SMS é barato
        agent_name="attendance_agent",
        client_id=booking["booking_id"],
        payload=booking
    )

# Monitor da fila
stats = booking_queue.get_stats()
print(f"Agendamentos na fila: {stats['size_atual']}")
print(f"Taxa de sucesso: {stats['success_rate']:.1f}%")
```

### Caso 3: Cobrança Inteligente

```python
# Sistema de cobranças com priorização por atraso
collection_queue = AgentQueue(max_size=10000)

invoices = [
    {"invoice": "nf001", "due_date": "2025-12-20", "amount": 1000},   # 5 dias atrasado
    {"invoice": "nf002", "due_date": "2025-12-23", "amount": 500},    # 2 dias atrasado
    {"invoice": "nf003", "due_date": "2025-12-25", "amount": 2000},   # Vence hoje
]

for inv in invoices:
    due = datetime.fromisoformat(inv["due_date"])
    days_overdue = (datetime.now() - due).days
    
    # Prioridade por dias de atraso
    if days_overdue >= 5:
        priority = TaskPriority.CRITICAL
    elif days_overdue >= 2:
        priority = TaskPriority.HIGH
    elif days_overdue >= 0:
        priority = TaskPriority.MEDIUM
    else:
        priority = TaskPriority.LOW
    
    # Cost: mais caro cobrar faturas maiores (human review)
    cost = min(10, int(inv["amount"] / 200))
    
    collection_queue.push(
        priority=priority,
        deadline=due,
        cost=cost,
        agent_name="collections_agent",
        client_id=inv["invoice"],
        payload=inv
    )

# Processar cobranças em ordem de urgência
for _ in range(collection_queue.size()):
    task = collection_queue.pop()
    days_overdue = (datetime.now() - datetime.fromisoformat(
        task.payload["due_date"]
    )).days
    
    print(f"Cobrando {task.payload['invoice']} (atrasado {days_overdue} dias, prioridade={task.priority})")
```

---

## 8. Monitoramento

```python
queue = AgentQueue()

# Estatísticas
stats = queue.get_stats()
print(f"Tasks enfileiradas: {stats['total_pushed']}")
print(f"Tasks processadas: {stats['total_popped']}")
print(f"Taxa de rejeição: {stats['total_rejected'] / stats['total_pushed'] * 100:.1f}%")
print(f"Tamanho atual: {stats['size_atual']}/{queue.max_size}")

# Visualizar tarefas
all_tasks = queue.get_all_tasks()
for task in all_tasks:
    print(f"- {task.agent_name}: {task.task_id} (priority={task.priority})")

# Obter tarefas de agente específico
nf_tasks = queue.get_tasks_for_agent("nf_agent")
print(f"NF-e pendentes: {len(nf_tasks)}")

# Obter tarefas de cliente
client_tasks = queue.get_tasks_for_client("client_xyz")
print(f"Tarefas do cliente: {len(client_tasks)}")
```

---

## 9. Análise Big O

```
Operação          │ Complexidade │ Operações por requisição
───────────────────────────────────────────────────────────
Push (enqueue)    │ O(log n)     │ ~20 ops para 1000 tarefas
Pop (dequeue)     │ O(log n)     │ ~20 ops para 1000 tarefas
Peek              │ O(1)         │ ~1 op (array access)
Size              │ O(1)         │ ~1 op (counter)
Get all sorted    │ O(n log n)   │ ~10000 ops para 1000 tarefas
Get by agent      │ O(n)         │ ~1000 ops para 1000 tarefas
Remove task       │ O(n)         │ ~1000 ops para 1000 tarefas (rare)
───────────────────────────────────────────────────────────

Memory:     O(n) onde n = número de tarefas na fila
Space:      ~200 bytes por tarefa (overhead minimal)

Exemplo com 1000 tarefas:
  Push = ~30μs (microsegundos)
  Pop  = ~30μs
  Peek = ~1μs
  Total = milissegundos por operação (fast)
```

---

## 10. Best Practices

### ✅ Fazer

- **Usar CRITICAL apenas para** casos reais (prazo vencido, cliente pagou extra)
- **Monitorar fila** regularmente (size, rejections, efficiency)
- **Respeitar max_size** e implementar fallback se cheio
- **Usar tiebreaker apropriado** (deadline, cost)
- **Logar operações** críticas (push de CRITICAL, rejections)

### ❌ Não Fazer

- **Não usar CRITICAL para tudo** (perde significado)
- **Não ignorar rejections** (indica gargalo)
- **Não usar fila como banco de dados** (dados persistem em memória)
- **Não modificar prioridade após enqueue** (não suportado, remove e re-add)

---

## 11. Conclusão

A **Priority Queue (Min-Heap)** em Codex Operator oferece:

- ✅ O(log n) push/pop operations
- ✅ Tiebreaker inteligente (priority > deadline > cost > created_at)
- ✅ Validações de entrada robustas
- ✅ Statistics & logging comprehensive
- ✅ 34 unit tests + 17 integration tests
- ✅ Production-ready com max_size limits

**Resultado:** Tarefas críticas processadas primeiro, SLAs respeitados, sistema sempre responsivo mesmo com fila cheia.
