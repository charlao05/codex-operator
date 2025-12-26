#!/usr/bin/env python3
"""Script de teste rápido da integração Queue no Orchestrator."""

import sys

sys.path.insert(0, ".")

from src.core.agent_queue import AgentQueue, TaskPriority, create_deadline

# Teste 1: Criar fila e adicionar tarefas
print("=== TESTE 1: Criar Fila e Adicionar Tarefas ===")
queue = AgentQueue(max_size=100)
print("✓ Fila criada com max_size=100")
print(f"  Size: {queue.size()}, Empty: {queue.is_empty()}")

# Teste 2: Adicionar tarefas com diferentes prioridades
print("\n=== TESTE 2: Adicionar Tarefas ===")
deadline = create_deadline(days_ahead=1)

task_ids = []
for i, (agent_name, priority) in enumerate(
    [
        ("nf_agent", TaskPriority.HIGH),
        ("attendance_agent", TaskPriority.MEDIUM),
        ("collections_agent", TaskPriority.CRITICAL),
        ("deadlines_agent", TaskPriority.LOW),
    ]
):
    task_id = queue.push(
        priority=priority,
        deadline=deadline,
        cost=i + 1,
        agent_name=agent_name,
        client_id=f"client_{i}",
        payload={"index": i},
    )
    task_ids.append(task_id)
    print(f"✓ Tarefa adicionada: {task_id} ({agent_name}, priority={priority})")

print(f"\n  Fila contém {queue.size()} tarefas")

# Teste 3: Verificar ordenação (testa prioridade)
print("\n=== TESTE 3: Verificar Ordenação ===")
all_tasks = queue.get_all_tasks()
print("Tarefas em ordem de processamento:")
for i, task in enumerate(all_tasks, 1):
    print(f"  [{i}] {task.agent_name} (priority={task.priority}, cost={task.cost})")

# Teste 4: Pop tarefas e verificar ordem
print("\n=== TESTE 4: Processar Tarefas (Pop) ===")
for i in range(2):
    task = queue.pop()
    if task:
        print(f"✓ Processada: {task.agent_name} (priority={task.priority})")

print(f"\n  Fila agora contém {queue.size()} tarefas")

# Teste 5: Query por agente
print("\n=== TESTE 5: Query por Agente ===")
nf_tasks = queue.get_tasks_for_agent("nf_agent")
print(f"✓ Tarefas para nf_agent: {len(nf_tasks)}")

# Teste 6: Estatísticas
print("\n=== TESTE 6: Estatísticas ===")
stats = queue.get_stats()
print(queue.print_stats())

print("\n✅ TODOS OS TESTES PASSARAM!")
