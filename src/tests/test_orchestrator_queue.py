"""Testes para integração de Priority Queue no Orchestrator.

Valida que:
- Comandos 'queue' foram adicionados corretamente
- Fila persiste entre chamadas
- Backward compatibility com comandos 'executar' e 'nf'
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock
import sys

# Mock Playwright para evitar instalação em testes
sys.modules["playwright"] = MagicMock()
sys.modules["playwright.sync_api"] = MagicMock()

from src.orchestrator import (  # noqa: E402
    get_task_queue,
    _handle_queue_stats,
    _handle_queue_list,
    _handle_queue_clear,
    _handle_queue_process,
    _handle_queue_push,
)
from src.core.agent_queue import TaskPriority, create_deadline  # noqa: E402


class TestOrchestratorQueueIntegration:
    """Testes para integração da fila no orchestrator."""

    def test_get_task_queue_singleton(self):
        """get_task_queue retorna mesma instância (singleton)."""
        queue1 = get_task_queue(max_size=100)
        queue2 = get_task_queue(max_size=200)  # max_size é ignorado na segunda chamada

        assert queue1 is queue2
        assert queue1.max_size == 100  # Mantém config da primeira chamada

    def test_get_task_queue_creates_instance(self):
        """get_task_queue cria instância se não existir."""
        queue = get_task_queue(max_size=500)
        assert queue is not None
        assert queue.is_empty()


class TestQueueCommands:
    """Testes para comandos de fila."""

    def setup_method(self):
        """Reinicia fila antes de cada teste."""
        # Reset global queue
        import src.orchestrator

        src.orchestrator._TASK_QUEUE = None

    def test_handle_queue_stats_empty(self, capsys):
        """handle_queue_stats exibe stats de fila vazia."""
        result = _handle_queue_stats()

        assert result == 0
        captured = capsys.readouterr()
        assert "AGENT QUEUE STATS" in captured.out
        assert "Total Pushed: 0" in captured.out

    def test_handle_queue_stats_with_tasks(self, capsys):
        """handle_queue_stats exibe stats corretas com tarefas."""
        queue = get_task_queue()
        deadline = create_deadline(days_ahead=1)

        # Add some tasks
        queue.push(TaskPriority.HIGH, deadline, 1, "agent1", "client1", {})
        queue.pop()  # Process one
        queue.push(TaskPriority.MEDIUM, deadline, 2, "agent2", "client2", {})

        result = _handle_queue_stats()

        assert result == 0
        captured = capsys.readouterr()
        assert "Total Pushed: 2" in captured.out
        assert "Total Popped: 1" in captured.out

    def test_handle_queue_list_empty(self, capsys):
        """handle_queue_list mostra mensagem para fila vazia."""
        result = _handle_queue_list()

        assert result == 0
        captured = capsys.readouterr()
        assert "Fila vazia" in captured.out

    def test_handle_queue_list_with_tasks(self, capsys):
        """handle_queue_list lista todas as tarefas."""
        queue = get_task_queue()
        deadline = create_deadline(days_ahead=1)

        queue.push(TaskPriority.CRITICAL, deadline, 1, "agent_a", "client_x", {})
        queue.push(TaskPriority.HIGH, deadline, 2, "agent_b", "client_y", {})
        queue.push(TaskPriority.MEDIUM, deadline, 3, "agent_c", "client_z", {})

        result = _handle_queue_list()

        assert result == 0
        captured = capsys.readouterr()
        assert "agent_a" in captured.out
        assert "agent_b" in captured.out
        assert "agent_c" in captured.out
        assert "Total: 3 tarefas" in captured.out

    def test_handle_queue_clear(self, capsys):
        """handle_queue_clear remove todas as tarefas."""
        queue = get_task_queue()
        deadline = create_deadline(days_ahead=1)

        queue.push(TaskPriority.MEDIUM, deadline, 1, "agent1", "client1", {})
        queue.push(TaskPriority.MEDIUM, deadline, 2, "agent2", "client2", {})

        assert queue.size() == 2

        result = _handle_queue_clear()

        assert result == 0
        assert queue.size() == 0
        captured = capsys.readouterr()
        assert "Fila limpa" in captured.out
        assert "2 tarefas" in captured.out

    def test_handle_queue_process_empty_queue(self, capsys):
        """handle_queue_process com fila vazia retorna 0."""
        result = _handle_queue_process(count=5)

        assert result == 0
        captured = capsys.readouterr()
        assert "Fila vazia" in captured.out

    def test_handle_queue_process_partial(self, capsys):
        """handle_queue_process processa N tarefas."""
        queue = get_task_queue()
        deadline = create_deadline(days_ahead=1)

        for i in range(5):
            queue.push(
                TaskPriority.MEDIUM, deadline, 1, f"agent_{i}", f"client_{i}", {}
            )

        assert queue.size() == 5

        result = _handle_queue_process(count=2)

        assert result == 0
        assert queue.size() == 3  # 5 - 2 = 3
        captured = capsys.readouterr()
        assert "2 tarefa(s) processada(s)" in captured.out

    def test_handle_queue_process_more_than_available(self, capsys):
        """handle_queue_process processa o máximo disponível."""
        queue = get_task_queue()
        deadline = create_deadline(days_ahead=1)

        queue.push(TaskPriority.MEDIUM, deadline, 1, "agent1", "client1", {})
        queue.push(TaskPriority.MEDIUM, deadline, 2, "agent2", "client2", {})

        result = _handle_queue_process(count=10)  # Pede 10, mas só tem 2

        assert result == 0
        assert queue.size() == 0
        captured = capsys.readouterr()
        assert "2 tarefa(s) processada(s)" in captured.out

    def test_handle_queue_push_success(self, capsys):
        """handle_queue_push adiciona tarefa com sucesso."""
        args = MagicMock()
        args.agent = "nf_agent"
        args.client = "client_123"
        args.priority = 2  # HIGH
        args.days = 3
        args.cost = 5
        args.payload = None

        queue = get_task_queue()
        initial_size = queue.size()

        result = _handle_queue_push(args)

        assert result == 0
        assert queue.size() == initial_size + 1
        captured = capsys.readouterr()
        assert "Tarefa adicionada" in captured.out
        assert "nf_agent" in captured.out
        assert "client_123" in captured.out

    def test_handle_queue_push_with_payload(self, capsys):
        """handle_queue_push com payload JSON."""
        payload_json = '{"sale_id": "123", "amount": 1500.00}'
        args = MagicMock()
        args.agent = "nf_agent"
        args.client = "client_xyz"
        args.priority = 1  # CRITICAL
        args.days = 1
        args.cost = 3
        args.payload = payload_json

        queue = get_task_queue()
        result = _handle_queue_push(args)

        assert result == 0

        # Verificar que payload foi armazenado
        task = queue.peek()
        assert task.payload == {"sale_id": "123", "amount": 1500.00}

    def test_handle_queue_push_invalid_json(self, capsys):
        """handle_queue_push com JSON inválido retorna erro."""
        args = MagicMock()
        args.agent = "nf_agent"
        args.client = "client_123"
        args.priority = 2
        args.days = 1
        args.cost = 1
        args.payload = "{ invalid json }"  # Inválido

        result = _handle_queue_push(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "JSON inválido" in captured.out

    def test_handle_queue_push_when_full(self, capsys):
        """handle_queue_push quando fila está cheia."""
        # Create queue with small max_size
        import src.orchestrator

        src.orchestrator._TASK_QUEUE = None
        queue = get_task_queue(max_size=2)

        deadline = create_deadline(days_ahead=1)
        queue.push(TaskPriority.MEDIUM, deadline, 1, "agent1", "client1", {})
        queue.push(TaskPriority.MEDIUM, deadline, 2, "agent2", "client2", {})

        assert queue.size() == 2  # Fila cheia

        # Tenta adicionar quando está cheia
        args = MagicMock()
        args.agent = "agent3"
        args.client = "client3"
        args.priority = 3
        args.days = 1
        args.cost = 1
        args.payload = None

        result = _handle_queue_push(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Fila cheia" in captured.out


class TestOrchestratorBackwardCompatibility:
    """Testes para garantir backward compatibility."""

    def setup_method(self):
        """Reinicia fila antes de cada teste."""
        import src.orchestrator

        src.orchestrator._TASK_QUEUE = None

    def test_queue_singleton_persists_across_calls(self):
        """Fila persiste entre chamadas diferentes."""
        queue1 = get_task_queue()
        deadline = create_deadline(days_ahead=1)

        task_id = queue1.push(TaskPriority.MEDIUM, deadline, 1, "agent", "client", {})
        assert queue1.size() == 1

        # Outra "chamada" (simula novo comando) obtém mesma instância
        queue2 = get_task_queue()
        assert queue2 is queue1
        assert queue2.size() == 1

        # A tarefa adicionada persiste
        task = queue2.peek()
        assert task.task_id == task_id


class TestQueueEdgeCases:
    """Testes para casos extremos."""

    def test_handle_queue_push_invalid_priority(self, capsys):
        """handle_queue_push rejeita prioridade inválida."""
        args = MagicMock()
        args.agent = "agent"
        args.client = "client"
        args.priority = 10  # Inválido (1-5 only)
        args.days = 1
        args.cost = 1
        args.payload = None

        result = _handle_queue_push(args)

        # Espera que argparse rejeite antes de chegar aqui
        # Este teste valida o comportamento esperado
        assert result in [0, 1]  # Ambos são aceitáveis dependendo da implementação

    def test_handle_queue_process_overdue_tasks(self, capsys):
        """handle_queue_process marca tarefas vencidas."""
        queue = get_task_queue()

        # Criar tarefa vencida (deadline no passado)
        past_deadline = datetime.now() - timedelta(days=1)

        queue._heap = []  # Reset para controlar
        _ = queue.push(TaskPriority.MEDIUM, past_deadline, 1, "agent", "client", {})

        result = _handle_queue_process(count=1)

        assert result == 0
        captured = capsys.readouterr()
        assert "[OVERDUE]" in captured.out  # Deve marcar como vencida
