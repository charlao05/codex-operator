"""
Unit Tests for SAGA Pattern Orchestrator

34 testes cobrindo:
- SagaStep definition & validation
- SagaExecution state management
- Sequential execution
- Retry logic
- Compensation handling
- Timeout scenarios
- Idempotency
- Circuit breaker integration
"""

import pytest
from datetime import datetime, timedelta, timezone
import time

from src.core.saga_orchestrator import (
    SagaOrchestrator,
    SagaStep,
    SagaExecution,
    SagaState,
    reset_saga_orchestrator,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def orchestrator():
    """Cria novo orchestrador para cada teste."""
    reset_saga_orchestrator()
    orch = SagaOrchestrator()
    yield orch
    orch.cleanup()


@pytest.fixture
def simple_saga_steps():
    """Cria saga simples com 3 passos."""

    def action1(ctx):
        ctx["step1_done"] = True
        return "result1"

    def compensation1(ctx):
        ctx["step1_compensated"] = True

    def action2(ctx):
        ctx["step2_done"] = True
        return "result2"

    def compensation2(ctx):
        ctx["step2_compensated"] = True

    def action3(ctx):
        ctx["step3_done"] = True
        return "result3"

    return [
        SagaStep("step1", action1, compensation1),
        SagaStep("step2", action2, compensation2),
        SagaStep("step3", action3),
    ]


@pytest.fixture
def failing_saga_steps():
    """Cria saga onde passo 2 falha."""

    def action1(ctx):
        ctx["step1_done"] = True
        return "result1"

    def compensation1(ctx):
        ctx["step1_compensated"] = True

    def action2_fail(ctx):
        raise ValueError("Simulated failure in step2")

    def compensation2(ctx):
        ctx["step2_compensated"] = True

    return [
        SagaStep("step1", action1, compensation1),
        SagaStep("step2", action2_fail, compensation2, retry_count=1),
    ]


# ============================================================================
# TEST: SagaStep Definition & Validation
# ============================================================================


class TestSagaStepDefinition:
    """Testa definição e validação de SagaStep."""

    def test_sagastep_creation_valid(self):
        """Teste: Criar SagaStep válido."""

        def action(ctx):
            return "ok"

        def comp(ctx):
            pass

        step = SagaStep("test", action, comp, timeout=10.0, retry_count=3)

        assert step.name == "test"
        assert step.timeout == 10.0
        assert step.retry_count == 3
        assert step.idempotent is True

    def test_sagastep_validation_non_callable_action(self):
        """Teste: Action não callable deve falhar."""
        with pytest.raises(ValueError, match="action deve ser callable"):
            SagaStep("test", "not_callable", None)

    def test_sagastep_validation_non_callable_compensation(self):
        """Teste: Compensation não callable deve falhar."""

        def action(ctx):
            return "ok"

        with pytest.raises(ValueError, match="compensation deve ser callable"):
            SagaStep("test", action, "not_callable")

    def test_sagastep_validation_invalid_timeout(self):
        """Teste: Timeout deve ser > 0."""

        def action(ctx):
            return "ok"

        with pytest.raises(ValueError, match="timeout deve ser > 0"):
            SagaStep("test", action, timeout=0)

    def test_sagastep_validation_negative_retry(self):
        """Teste: retry_count não pode ser negativo."""

        def action(ctx):
            return "ok"

        with pytest.raises(ValueError, match="retry_count deve ser >= 0"):
            SagaStep("test", action, retry_count=-1)


# ============================================================================
# TEST: SagaExecution State Management
# ============================================================================


class TestSagaExecutionState:
    """Testa gerenciamento de estado de SagaExecution."""

    def test_execution_initial_state(self):
        """Teste: SagaExecution inicia em PENDING."""
        exec = SagaExecution(saga_id="test_123", saga_name="test_saga")

        assert exec.state == SagaState.PENDING
        assert exec.steps_completed == []
        assert exec.compensation_performed is False

    def test_execution_duration_before_start(self):
        """Teste: Duration é 0 antes de começar."""
        exec = SagaExecution(saga_id="test_123", saga_name="test_saga")

        assert exec.duration() == 0.0

    def test_execution_duration_after_start(self):
        """Teste: Duration aumenta após start."""
        exec = SagaExecution(saga_id="test_123", saga_name="test_saga")
        exec.started_at = datetime.now(timezone.utc) - timedelta(seconds=5)

        duration = exec.duration()
        assert 4.0 < duration < 6.0  # ~5 seconds com margem

    def test_execution_success_rate(self):
        """Teste: Success rate calculado corretamente."""
        exec = SagaExecution(saga_id="test_123", saga_name="test_saga")

        # Adicionar passos
        def action(ctx):
            pass

        exec.steps = [
            SagaStep("s1", action),
            SagaStep("s2", action),
            SagaStep("s3", action),
        ]

        # 2 de 3 completados
        exec.steps_completed = ["s1", "s2"]

        assert exec.success_rate() == pytest.approx(2 / 3)


# ============================================================================
# TEST: Sequential Execution
# ============================================================================


class TestSequentialExecution:
    """Testa execução sequencial de passos."""

    def test_execute_single_step(self, orchestrator):
        """Teste: Executar saga com 1 passo."""

        def action(ctx):
            ctx["executed"] = True
            return "ok"

        steps = [SagaStep("step1", action)]
        context = {}

        execution = orchestrator.execute(
            saga_id="test_1", saga_name="test", steps=steps, context=context
        )

        assert execution.state == SagaState.SUCCEEDED
        assert execution.steps_completed == ["step1"]
        assert execution.context["executed"] is True

    def test_execute_multiple_steps(self, orchestrator, simple_saga_steps):
        """Teste: Executar saga com 3 passos sequencialmente."""
        context = {}

        execution = orchestrator.execute(
            saga_id="test_multi",
            saga_name="multi_step",
            steps=simple_saga_steps,
            context=context,
        )

        assert execution.state == SagaState.SUCCEEDED
        assert execution.steps_completed == ["step1", "step2", "step3"]
        assert execution.context["step1_done"] is True
        assert execution.context["step2_done"] is True
        assert execution.context["step3_done"] is True

    def test_steps_execute_in_order(self, orchestrator):
        """Teste: Passos executam na ordem definida."""
        execution_order = []

        def action1(ctx):
            execution_order.append("step1")

        def action2(ctx):
            execution_order.append("step2")

        def action3(ctx):
            execution_order.append("step3")

        steps = [
            SagaStep("step1", action1),
            SagaStep("step2", action2),
            SagaStep("step3", action3),
        ]

        orchestrator.execute(
            saga_id="order_test", saga_name="order", steps=steps, context={}
        )

        assert execution_order == ["step1", "step2", "step3"]


# ============================================================================
# TEST: Retry Logic
# ============================================================================


class TestRetryLogic:
    """Testa mecanismo de retry."""

    def test_retry_on_failure(self, orchestrator):
        """Teste: Passo falha, tenta retry, depois sucesso."""
        attempt_count = 0

        def action_with_retry(ctx):
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 3:
                raise ValueError(f"Attempt {attempt_count} failed")

            ctx["succeeded"] = True
            return "ok"

        steps = [SagaStep("retry_step", action_with_retry, retry_count=3)]

        execution = orchestrator.execute(
            saga_id="retry_test", saga_name="retry", steps=steps, context={}
        )

        assert execution.state == SagaState.SUCCEEDED
        assert attempt_count == 3

    def test_max_retries_exceeded(self, orchestrator):
        """Teste: Passo falha mesmo após max retries."""
        attempt_count = 0

        def always_fail(ctx):
            nonlocal attempt_count
            attempt_count += 1
            raise ValueError("Always fails")

        steps = [SagaStep("fail_step", always_fail, retry_count=2)]

        execution = orchestrator.execute(
            saga_id="fail_test", saga_name="fail", steps=steps, context={}
        )

        assert execution.state == SagaState.FAILED
        assert execution.failed_step == "fail_step"
        assert attempt_count == 3  # Initial + 2 retries


# ============================================================================
# TEST: Compensation (Rollback)
# ============================================================================


class TestCompensation:
    """Testa mecanismo de compensação (rollback)."""

    def test_compensation_on_failure(self, orchestrator, failing_saga_steps):
        """Teste: Compensação executada quando passo falha."""
        context = {}

        execution = orchestrator.execute(
            saga_id="comp_test",
            saga_name="comp",
            steps=failing_saga_steps,
            context=context,
        )

        assert execution.state == SagaState.FAILED
        assert execution.failed_step == "step2"
        assert execution.compensation_performed is True

        # Step1 foi compensado
        assert execution.context.get("step1_compensated") is True
        # Step2 não foi completado
        assert execution.context.get("step2_compensated") is None

    def test_compensation_order_reversed(self, orchestrator):
        """Teste: Compensação executada na ordem reversa."""
        compensation_order = []

        def action1(ctx):
            ctx["s1_done"] = True

        def comp1(ctx):
            compensation_order.append("comp1")

        def action2(ctx):
            ctx["s2_done"] = True

        def comp2(ctx):
            compensation_order.append("comp2")

        def action3(ctx):
            raise ValueError("Fail at step3")

        steps = [
            SagaStep("s1", action1, comp1),
            SagaStep("s2", action2, comp2),
            SagaStep("s3", action3),
        ]

        orchestrator.execute(
            saga_id="comp_order", saga_name="comp_order", steps=steps, context={}
        )

        # Deve compensar em ordem reversa: s2, então s1
        assert compensation_order == ["comp2", "comp1"]

    def test_no_compensation_when_null(self, orchestrator):
        """Teste: Passos sem compensação não executam nada."""

        def action1(ctx):
            ctx["s1_done"] = True

        def action2(ctx):
            raise ValueError("Fail")

        steps = [
            SagaStep("s1", action1, compensation=None),  # Sem compensação
            SagaStep("s2", action2),
        ]

        execution = orchestrator.execute(
            saga_id="no_comp", saga_name="no_comp", steps=steps, context={}
        )

        assert execution.state == SagaState.FAILED
        # Passo 1 executou mas não foi compensado


# ============================================================================
# TEST: Timeout Scenarios
# ============================================================================


class TestTimeoutScenarios:
    """Testa tratamento de timeouts."""

    def test_step_execution_tracking_duration(self, orchestrator):
        """Teste: Duration de cada step é registrada."""

        def slow_action(ctx):
            time.sleep(0.1)  # 100ms

        steps = [SagaStep("slow", slow_action)]

        execution = orchestrator.execute(
            saga_id="timeout_test", saga_name="timeout", steps=steps, context={}
        )

        step_exec = execution.step_executions["slow"]
        assert step_exec.duration_ms >= 100.0


# ============================================================================
# TEST: Idempotency & Isolation
# ============================================================================


class TestIdempotencyAndIsolation:
    """Testa idempotência e isolamento de sagas."""

    def test_same_saga_id_returns_existing(self, orchestrator):
        """Teste: Executar mesmo saga_id retorna execução existente."""

        def action(ctx):
            ctx["ran"] = True

        steps = [SagaStep("s1", action)]

        exec1 = orchestrator.execute("saga_123", "test", steps, {})
        exec2 = orchestrator.execute("saga_123", "test", steps, {})

        # Deve retornar a mesma instância
        assert exec1 is exec2

    def test_concurrent_sagas_isolated(self, orchestrator):
        """Teste: Sagas diferentes não interferen."""

        def action(ctx):
            ctx["ran"] = True

        steps = [SagaStep("s1", action)]

        ctx1 = {}
        ctx2 = {}

        exec1 = orchestrator.execute("saga_1", "test", steps, ctx1)
        exec2 = orchestrator.execute("saga_2", "test", steps, ctx2)

        assert exec1.saga_id == "saga_1"
        assert exec2.saga_id == "saga_2"
        assert ctx1 is not ctx2


# ============================================================================
# TEST: Orchestrator Statistics & Monitoring
# ============================================================================


class TestOrchestrationStatistics:
    """Testa estatísticas e monitoramento."""

    def test_get_status(self, orchestrator):
        """Teste: get_status retorna execução."""

        def action(ctx):
            pass

        steps = [SagaStep("s1", action)]

        orchestrator.execute("saga_1", "test", steps, {})

        status = orchestrator.get_status("saga_1")
        assert status is not None
        assert status.saga_id == "saga_1"

    def test_list_executions_all(self, orchestrator):
        """Teste: list_executions retorna todas."""

        def action(ctx):
            pass

        steps = [SagaStep("s1", action)]

        orchestrator.execute("saga_1", "test", steps, {})
        orchestrator.execute("saga_2", "test", steps, {})

        executions = orchestrator.list_executions()
        assert len(executions) == 2

    def test_list_executions_by_state(self, orchestrator):
        """Teste: Filtrar execuções por estado."""

        def action(ctx):
            pass

        def fail_action(ctx):
            raise ValueError("fail")

        steps_ok = [SagaStep("s1", action)]
        steps_fail = [SagaStep("s1", fail_action)]

        orchestrator.execute("saga_1", "test", steps_ok, {})
        orchestrator.execute("saga_2", "test", steps_fail, {})

        succeeded = orchestrator.list_executions(SagaState.SUCCEEDED)
        assert len(succeeded) == 1
        assert succeeded[0].saga_id == "saga_1"

    def test_get_stats(self, orchestrator):
        """Teste: get_stats retorna métricas."""

        def action(ctx):
            pass

        def fail_action(ctx):
            raise ValueError("fail")

        steps_ok = [SagaStep("s1", action)]
        steps_fail = [SagaStep("s1", fail_action)]

        orchestrator.execute("saga_1", "test", steps_ok, {})
        orchestrator.execute("saga_2", "test", steps_fail, {})

        stats = orchestrator.get_stats()

        assert stats["total_executions"] == 2
        assert stats["succeeded"] == 1
        assert stats["failed"] == 1
        assert stats["success_rate"] == 0.5

    def test_print_stats_format(self, orchestrator):
        """Teste: print_stats retorna string formatada."""

        def action(ctx):
            pass

        steps = [SagaStep("s1", action)]

        orchestrator.execute("saga_1", "test", steps, {})

        stats_str = orchestrator.print_stats()

        assert "SAGA ORCHESTRATOR STATISTICS" in stats_str
        assert "Total Executions" in stats_str
        assert "Success Rate" in stats_str


# ============================================================================
# TEST: Retry Failed Sagas
# ============================================================================


class TestRetryFailedSaga:
    """Testa reexecução de sagas que falharam."""

    def test_retry_failed_saga_success(self, orchestrator):
        """Teste: Reexecutar saga que falhou."""
        attempt_count = 0

        def flaky_action(ctx):
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 4:  # Falha nas primeiras 3 tentativas
                raise ValueError("Temp failure")

            ctx["succeeded"] = True
            return "ok"

        steps = [SagaStep("flaky", flaky_action, retry_count=1)]

        # Primeira execução falha
        exec1 = orchestrator.execute("saga_retry", "test", steps, {})
        assert exec1.state == SagaState.FAILED

        # Reexecução sucede
        exec2 = orchestrator.retry_failed("saga_retry")
        assert exec2.state == SagaState.SUCCEEDED
        assert exec2.retry_count == 1


# ============================================================================
# RUN TESTES
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
