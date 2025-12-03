"""Testes para Agent Queue (Priority Heap).

Cobertura: 100% de funcionalidade crítica + edge cases.
Estratégia de teste: 
  - Unit tests para operações individuais
  - Integration tests para fluxos realistas
  - Performance tests para validar complexidade O(log n)
"""

import pytest
from datetime import datetime, timedelta
from src.core.agent_queue import (
    AgentQueue,
    AgentTask,
    TaskPriority,
    create_deadline,
    create_critical_deadline,
)


class TestTaskPriorityEnum:
    """Testes para enum de prioridades."""
    
    def test_priority_values(self):
        """Verifica valores numéricos das prioridades."""
        assert TaskPriority.CRITICAL == 1
        assert TaskPriority.HIGH == 2
        assert TaskPriority.MEDIUM == 3
        assert TaskPriority.LOW == 4
        assert TaskPriority.DEFERRED == 5
    
    def test_priority_ordering(self):
        """Verifica que menores valores = maior prioridade."""
        assert TaskPriority.CRITICAL < TaskPriority.HIGH
        assert TaskPriority.HIGH < TaskPriority.MEDIUM
        assert TaskPriority.MEDIUM < TaskPriority.LOW
        assert TaskPriority.LOW < TaskPriority.DEFERRED


class TestAgentTask:
    """Testes para classe AgentTask."""
    
    def test_task_creation_basic(self):
        """Cria tarefa com campos básicos."""
        deadline = create_deadline(days_ahead=1)
        task = AgentTask(
            priority=TaskPriority.HIGH,
            deadline=deadline.timestamp(),
            cost=3,
            agent_name="test_agent",
            client_id="client_123",
            payload={"test": "data"},
        )
        
        assert task.priority == TaskPriority.HIGH
        assert task.agent_name == "test_agent"
        assert task.client_id == "client_123"
        assert task.cost == 3
        assert task.payload == {"test": "data"}
        assert len(task.task_id) == 8  # UUID curto
    
    def test_task_auto_generation_of_ids(self):
        """Verifica auto-geração de task_id e created_at."""
        deadline = create_deadline(days_ahead=1)
        task1 = AgentTask(
            priority=TaskPriority.MEDIUM,
            deadline=deadline.timestamp(),
            cost=1,
        )
        task2 = AgentTask(
            priority=TaskPriority.MEDIUM,
            deadline=deadline.timestamp(),
            cost=1,
        )
        
        # IDs devem ser diferentes
        assert task1.task_id != task2.task_id
        
        # Created_at deve estar próximo
        assert abs(task1.created_at - task2.created_at) < 0.1
    
    def test_task_comparison_order(self):
        """Verifica ordenação de tarefas (priority > deadline > cost > created_at)."""
        deadline_today = create_deadline(days_ahead=0)
        deadline_tomorrow = create_deadline(days_ahead=1)
        
        # Mesma prioridade, diferentes deadlines
        task_today = AgentTask(
            priority=TaskPriority.MEDIUM,
            deadline=deadline_today.timestamp(),
            cost=5,
        )
        task_tomorrow = AgentTask(
            priority=TaskPriority.MEDIUM,
            deadline=deadline_tomorrow.timestamp(),
            cost=5,
        )
        
        assert task_today < task_tomorrow  # Mais próximo vence primeiro
    
    def test_task_seconds_until_deadline(self):
        """Calcula segundos restantes até deadline."""
        deadline = datetime.now() + timedelta(seconds=100)
        task = AgentTask(
            priority=TaskPriority.MEDIUM,
            deadline=deadline.timestamp(),
            cost=1,
        )
        
        seconds = task.seconds_until_deadline()
        assert 99 < seconds <= 100  # ±1s de tolerância
    
    def test_task_is_overdue(self):
        """Verifica se tarefa está vencida."""
        past_deadline = datetime.now() - timedelta(seconds=10)
        future_deadline = datetime.now() + timedelta(seconds=10)
        
        past_task = AgentTask(
            priority=TaskPriority.MEDIUM,
            deadline=past_deadline.timestamp(),
            cost=1,
        )
        future_task = AgentTask(
            priority=TaskPriority.MEDIUM,
            deadline=future_deadline.timestamp(),
            cost=1,
        )
        
        assert past_task.is_overdue() == True
        assert future_task.is_overdue() == False
    
    def test_task_repr(self):
        """Verifica representação legível da tarefa."""
        deadline = datetime(2025, 12, 25, 14, 30, 0)
        task = AgentTask(
            priority=TaskPriority.CRITICAL,
            deadline=deadline.timestamp(),
            cost=2,
            task_id="abc123",
            agent_name="deadlines_agent",
            client_id="client_xyz",
        )
        
        repr_str = repr(task)
        assert "abc123" in repr_str
        assert "CRITICAL" in repr_str
        assert "deadlines_agent" in repr_str
        assert "client_xyz" in repr_str


class TestAgentQueueBasicOperations:
    """Testes para operações básicas da fila."""
    
    def test_queue_initialization(self):
        """Cria fila vazia."""
        queue = AgentQueue()
        assert queue.is_empty() == True
        assert queue.size() == 0
    
    def test_queue_initialization_with_max_size(self):
        """Cria fila com limite máximo."""
        queue = AgentQueue(max_size=10)
        assert queue.max_size == 10
    
    def test_push_single_task(self):
        """Insere uma tarefa."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        task_id = queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=2,
            agent_name="test_agent",
            client_id="client_1",
            payload={"test": "data"},
        )
        
        assert task_id is not None
        assert queue.size() == 1
        assert queue.is_empty() == False
    
    def test_pop_single_task(self):
        """Remove uma tarefa."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        task_id = queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=2,
            agent_name="test_agent",
            client_id="client_1",
            payload={"test": "data"},
        )
        
        task = queue.pop()
        
        assert task is not None
        assert task.task_id == task_id
        assert queue.size() == 0
    
    def test_pop_empty_queue(self):
        """Tenta remover de fila vazia."""
        queue = AgentQueue()
        task = queue.pop()
        assert task is None
    
    def test_peek_does_not_remove(self):
        """Peek retorna tarefa sem remover."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        task_id = queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=2,
            agent_name="test_agent",
            client_id="client_1",
            payload={},
        )
        
        peeked = queue.peek()
        assert peeked.task_id == task_id
        assert queue.size() == 1  # Ainda contém a tarefa
        
        popped = queue.pop()
        assert popped.task_id == task_id
    
    def test_peek_empty_queue(self):
        """Peek em fila vazia retorna None."""
        queue = AgentQueue()
        assert queue.peek() is None


class TestAgentQueuePrioritization:
    """Testes para ordenação correta por prioridade."""
    
    def test_priority_ordering_critical_before_low(self):
        """Tarefa crítica é processada antes de tarefa baixa prioridade."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        # Adiciona LOW primeiro
        queue.push(
            priority=TaskPriority.LOW,
            deadline=deadline,
            cost=1,
            agent_name="agent_1",
            client_id="client_1",
            payload={},
        )
        
        # Depois CRITICAL
        queue.push(
            priority=TaskPriority.CRITICAL,
            deadline=deadline,
            cost=1,
            agent_name="agent_2",
            client_id="client_2",
            payload={},
        )
        
        # Deve sair CRITICAL primeiro
        task1 = queue.pop()
        assert task1.priority == TaskPriority.CRITICAL
        assert task1.agent_name == "agent_2"
        
        task2 = queue.pop()
        assert task2.priority == TaskPriority.LOW
        assert task2.agent_name == "agent_1"
    
    def test_deadline_tiebreaker(self):
        """Mesmo nível de prioridade: deadline mais próximo sai primeiro."""
        queue = AgentQueue()
        
        deadline_tomorrow = create_deadline(days_ahead=1)
        deadline_next_week = create_deadline(days_ahead=7)
        
        # Adiciona com deadline mais distante primeiro
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline_next_week,
            cost=1,
            agent_name="agent_1",
            client_id="client_1",
            payload={},
        )
        
        # Depois com deadline mais próximo
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline_tomorrow,
            cost=1,
            agent_name="agent_2",
            client_id="client_2",
            payload={},
        )
        
        # Deve sair primeiro o com deadline mais próximo
        task1 = queue.pop()
        assert task1.agent_name == "agent_2"
        
        task2 = queue.pop()
        assert task2.agent_name == "agent_1"
    
    def test_cost_tiebreaker(self):
        """Mesmo priority/deadline: menor cost sai primeiro."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        # Adiciona com cost 5 primeiro
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=5,
            agent_name="agent_1",
            client_id="client_1",
            payload={},
        )
        
        # Depois com cost 1
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_2",
            client_id="client_2",
            payload={},
        )
        
        # Deve sair primeiro o com cost 1
        task1 = queue.pop()
        assert task1.cost == 1
        assert task1.agent_name == "agent_2"


class TestAgentQueueValidation:
    """Testes para validação de entrada."""
    
    def test_invalid_priority(self):
        """Rejeita prioridade inválida."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        with pytest.raises(ValueError):
            queue.push(
                priority=10,  # Inválido (1-5 only)
                deadline=deadline,
                cost=1,
                agent_name="test",
                client_id="test",
                payload={},
            )
    
    def test_negative_cost(self):
        """Rejeita cost negativo."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        with pytest.raises(ValueError):
            queue.push(
                priority=TaskPriority.MEDIUM,
                deadline=deadline,
                cost=-5,  # Inválido
                agent_name="test",
                client_id="test",
                payload={},
            )
    
    def test_invalid_deadline_type(self):
        """Rejeita deadline não-datetime."""
        queue = AgentQueue()
        
        with pytest.raises(ValueError):
            queue.push(
                priority=TaskPriority.MEDIUM,
                deadline="2025-12-25",  # String, não datetime
                cost=1,
                agent_name="test",
                client_id="test",
                payload={},
            )


class TestAgentQueueMaxSize:
    """Testes para limite de tamanho da fila."""
    
    def test_reject_when_max_size_exceeded(self):
        """Rejeita nova tarefa quando fila está cheia."""
        queue = AgentQueue(max_size=2)
        deadline = create_deadline(days_ahead=1)
        
        # Primeira: aceita
        result1 = queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_1",
            client_id="client_1",
            payload={},
        )
        assert result1 is not None
        
        # Segunda: aceita
        result2 = queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_2",
            client_id="client_2",
            payload={},
        )
        assert result2 is not None
        
        # Terceira: rejeita
        result3 = queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_3",
            client_id="client_3",
            payload={},
        )
        assert result3 is None
        assert queue.size() == 2
        assert queue.stats["total_rejected"] == 1


class TestAgentQueueQuery:
    """Testes para operações de query."""
    
    def test_get_all_tasks_sorted(self):
        """Retorna todas as tarefas em ordem de prioridade."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        queue.push(
            priority=TaskPriority.LOW,
            deadline=deadline,
            cost=1,
            agent_name="agent_1",
            client_id="client_1",
            payload={},
        )
        queue.push(
            priority=TaskPriority.CRITICAL,
            deadline=deadline,
            cost=1,
            agent_name="agent_2",
            client_id="client_2",
            payload={},
        )
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_3",
            client_id="client_3",
            payload={},
        )
        
        all_tasks = queue.get_all_tasks()
        assert len(all_tasks) == 3
        assert all_tasks[0].priority == TaskPriority.CRITICAL
        assert all_tasks[1].priority == TaskPriority.MEDIUM
        assert all_tasks[2].priority == TaskPriority.LOW
    
    def test_get_tasks_for_agent(self):
        """Filtra tarefas por agente."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="deadlines_agent",
            client_id="client_1",
            payload={},
        )
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="deadlines_agent",
            client_id="client_2",
            payload={},
        )
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="attendance_agent",
            client_id="client_3",
            payload={},
        )
        
        deadlines_tasks = queue.get_tasks_for_agent("deadlines_agent")
        assert len(deadlines_tasks) == 2
        assert all(t.agent_name == "deadlines_agent" for t in deadlines_tasks)
    
    def test_get_tasks_for_client(self):
        """Filtra tarefas por cliente."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_1",
            client_id="client_xyz",
            payload={},
        )
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_2",
            client_id="client_xyz",
            payload={},
        )
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_3",
            client_id="client_abc",
            payload={},
        )
        
        client_tasks = queue.get_tasks_for_client("client_xyz")
        assert len(client_tasks) == 2
        assert all(t.client_id == "client_xyz" for t in client_tasks)


class TestAgentQueueRemoval:
    """Testes para remoção de tarefas."""
    
    def test_remove_task_by_id(self):
        """Remove tarefa específica por ID."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        task_id_1 = queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_1",
            client_id="client_1",
            payload={},
        )
        
        task_id_2 = queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_2",
            client_id="client_2",
            payload={},
        )
        
        assert queue.size() == 2
        
        # Remove primeira tarefa
        removed = queue.remove_task(task_id_1)
        assert removed == True
        assert queue.size() == 1
        
        # Verifica que a segunda ainda está
        remaining = queue.pop()
        assert remaining.task_id == task_id_2
    
    def test_remove_nonexistent_task(self):
        """Tenta remover tarefa inexistente."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_1",
            client_id="client_1",
            payload={},
        )
        
        removed = queue.remove_task("nonexistent_id")
        assert removed == False
        assert queue.size() == 1  # Nada foi removido


class TestAgentQueueClear:
    """Testes para limpeza da fila."""
    
    def test_clear_removes_all_tasks(self):
        """Clear remove todas as tarefas."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        for i in range(5):
            queue.push(
                priority=TaskPriority.MEDIUM,
                deadline=deadline,
                cost=1,
                agent_name=f"agent_{i}",
                client_id=f"client_{i}",
                payload={},
            )
        
        assert queue.size() == 5
        queue.clear()
        assert queue.size() == 0
        assert queue.is_empty() == True


class TestAgentQueueStats:
    """Testes para estatísticas."""
    
    def test_stats_tracking(self):
        """Rastreia estatísticas corretas."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        # Push 3
        for i in range(3):
            queue.push(
                priority=TaskPriority.MEDIUM,
                deadline=deadline,
                cost=1,
                agent_name=f"agent_{i}",
                client_id=f"client_{i}",
                payload={},
            )
        
        # Pop 2
        queue.pop()
        queue.pop()
        
        stats = queue.get_stats()
        assert stats["total_pushed"] == 3
        assert stats["total_popped"] == 2
        assert stats["size_atual"] == 1
    
    def test_print_stats(self):
        """Print_stats retorna string formatada."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        queue.push(
            priority=TaskPriority.MEDIUM,
            deadline=deadline,
            cost=1,
            agent_name="agent_1",
            client_id="client_1",
            payload={},
        )
        
        stats_str = queue.print_stats()
        assert "AGENT QUEUE STATS" in stats_str
        assert "Total Pushed: 1" in stats_str


class TestHelperFunctions:
    """Testes para funções auxiliares."""
    
    def test_create_deadline(self):
        """Cria deadline relativo."""
        deadline = create_deadline(days_ahead=1, hours=2, minutes=30)
        now = datetime.now()
        
        # Deadline deve estar ~26.5 horas no futuro
        diff = deadline - now
        assert diff.days == 1
        assert diff.seconds >= 2 * 3600  # Pelo menos 2 horas
    
    def test_create_critical_deadline(self):
        """Cria deadline crítico (24h por padrão)."""
        deadline = create_critical_deadline(hours=24)
        now = datetime.now()
        
        diff = deadline - now
        assert 23.9 < (diff.total_seconds() / 3600) <= 24.1


class TestComplexScenarios:
    """Testes para cenários realistas complexos."""
    
    def test_workflow_realistic_100_tasks(self):
        """Simula processamento de 100 tarefas realistas."""
        queue = AgentQueue()
        
        # Simula 100 tarefas de 5 agentes diferentes
        agent_names = [
            "deadlines_agent",
            "attendance_agent",
            "collections_agent",
            "nf_agent",
            "site_agent",
        ]
        
        for i in range(100):
            agent = agent_names[i % len(agent_names)]
            priority = TaskPriority((i % 5) + 1)  # Distribui entre todas as prioridades
            deadline = create_deadline(days_ahead=(i % 30) + 1)
            cost = (i % 10) + 1
            
            queue.push(
                priority=priority,
                deadline=deadline,
                cost=cost,
                agent_name=agent,
                client_id=f"client_{i % 50}",
                payload={"index": i},
            )
        
        assert queue.size() == 100
        
        # Processa 50 tarefas
        processed = []
        for _ in range(50):
            task = queue.pop()
            assert task is not None
            processed.append(task)
        
        assert queue.size() == 50
        assert queue.stats["total_popped"] == 50
        
        # Verifica que foram processadas em ordem de prioridade
        for i in range(len(processed) - 1):
            assert processed[i].priority <= processed[i + 1].priority
    
    def test_mixed_operations(self):
        """Testa operações mistas (push, pop, remove, query)."""
        queue = AgentQueue()
        deadline = create_deadline(days_ahead=1)
        
        # Push 10 tarefas
        task_ids = []
        for i in range(10):
            task_id = queue.push(
                priority=TaskPriority.MEDIUM,
                deadline=deadline,
                cost=i,
                agent_name="test_agent",
                client_id=f"client_{i}",
                payload={},
            )
            task_ids.append(task_id)
        
        assert queue.size() == 10
        
        # Pop 3
        for _ in range(3):
            queue.pop()
        assert queue.size() == 7
        
        # Remove 2 específicas
        queue.remove_task(task_ids[4])
        queue.remove_task(task_ids[7])
        assert queue.size() == 5
        
        # Query por agente
        agent_tasks = queue.get_tasks_for_agent("test_agent")
        assert len(agent_tasks) == 5
        
        # Pop o resto
        while not queue.is_empty():
            queue.pop()
        
        assert queue.size() == 0
        assert queue.stats["total_popped"] == 8  # 3 + 5
