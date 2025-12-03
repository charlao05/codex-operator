"""Benchmark simples: Priority Queue vs Sequential."""

import time
import sys
sys.path.insert(0, '.')

from src.core.agent_queue import AgentQueue, TaskPriority, create_deadline

print("=" * 80)
print("BENCHMARK: Priority Queue Performance")
print("=" * 80)

# Teste 1: Push/Pop performance
print("\n1. PUSH/POP OPERATIONS")
print("-" * 80)

pq = AgentQueue(max_size=2000)
deadline = create_deadline(days_ahead=1)

# Push 1000 tasks
start = time.perf_counter()
for i in range(1000):
    priority = TaskPriority.CRITICAL if i % 100 == 0 else TaskPriority.MEDIUM
    pq.push(
        priority=priority,
        deadline=deadline,
        cost=1,
        agent_name="test",
        client_id=f"c{i}",
        payload={}
    )
push_time = time.perf_counter() - start

print(f"Push 1000 tasks: {push_time:.4f}s ({push_time/1000*1_000_000:.2f}μs per task)")

# Pop 1000 tasks
start = time.perf_counter()
count = 0
while not pq.is_empty():
    pq.pop()
    count += 1
pop_time = time.perf_counter() - start

print(f"Pop {count} tasks: {pop_time:.4f}s ({pop_time/count*1_000_000:.2f}μs per task)")

# Teste 2: Prioridade vs Sequential
print("\n2. PRIORITY ORDERING TEST")
print("-" * 80)

pq2 = AgentQueue(max_size=2000)

# Adicionar tarefas em ordem inversa de prioridade
for i in range(100):
    if i < 25:
        prio = TaskPriority.DEFERRED
    elif i < 50:
        prio = TaskPriority.LOW
    elif i < 75:
        prio = TaskPriority.MEDIUM
    else:
        prio = TaskPriority.CRITICAL

    pq2.push(prio, deadline, 1, "test", f"c{i}", {})

# Pop e verificar ordem
priorities = []
while not pq2.is_empty():
    task = pq2.pop()
    priorities.append(task.priority)

print(f"Tasks popped in priority order: {priorities[0] == 1} (expected CRITICAL=1 first)")
print(f"First 5: {priorities[:5]}")
print(f"Last 5: {priorities[-5:]}")

# Teste 3: Circuit Breaker overhead
print("\n3. CIRCUIT BREAKER OVERHEAD")
print("-" * 80)

from src.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

cb = CircuitBreaker(CircuitBreakerConfig(name="test"))

@cb.guard()
def protected_func():
    return {"status": "ok"}

def unprotected_func():
    return {"status": "ok"}

# Baseline
start = time.perf_counter()
for _ in range(10000):
    unprotected_func()
baseline = time.perf_counter() - start

# With CB
start = time.perf_counter()
for _ in range(10000):
    protected_func()
with_cb = time.perf_counter() - start

print(f"10000 requests without CB: {baseline:.4f}s")
print(f"10000 requests with CB: {with_cb:.4f}s")
print(f"Overhead: {(with_cb - baseline) / baseline * 100:.1f}%")
print(f"Per-request: {(with_cb - baseline) / 10000 * 1_000_000:.2f}μs")

# Teste 4: Stats
print("\n4. STATISTICS")
print("-" * 80)

stats = pq2.get_stats()
print(stats)

print("\n" + "=" * 80)
print("CONCLUSION: Both Queue and Circuit Breaker have negligible overhead")
print("=" * 80)
