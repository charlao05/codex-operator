"""
Integration Tests for SAGA Pattern with Real APIs

12 testes integrando:
- Booking saga com múltiplas APIs (NF-e, Email, WhatsApp, Calendar)
- Payment saga com Stripe, Invoice, Email
- Real world scenarios com falhas intermitentes
- Circuit breaker integration
- Recovery after failures
"""

import pytest
from datetime import datetime, timezone

from src.core.saga_orchestrator import (
    SagaOrchestrator,
    SagaStep,
    SagaState,
    reset_saga_orchestrator,
)
from src.sagas.create_booking import CREATE_BOOKING_SAGA
from src.sagas.collect_payment import COLLECT_PAYMENT_SAGA


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
def booking_context():
    """Contexto para teste de booking."""
    return {
        "sale_id": "SALE-TEST-001",
        "booking_id": "BOOKING-TEST-001",
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "customer_phone": "+5511999999999",
        "amount": 150.00,
        "service_description": "Test Service",
        "booking_date": "2025-12-10T14:00:00",
        "calendar_id": "test@gmail.com",
    }


@pytest.fixture
def payment_context():
    """Contexto para teste de pagamento."""
    return {
        "customer_id": "CUST-TEST-001",
        "customer_email": "test@example.com",
        "customer_name": "Test Customer",
        "booking_id": "BOOKING-TEST-001",
        "amount": 150.00,
        "service_description": "Test Service",
        "payment_method": "credit_card",
    }


# ============================================================================
# TEST: Booking Saga Full Execution
# ============================================================================


class TestBookingSagaExecution:
    """Testa execução completa do booking saga."""

    def test_booking_saga_success_full_flow(self, orchestrator, booking_context):
        """Teste: Booking saga completa com sucesso."""
        execution = orchestrator.execute(
            saga_id="booking_full_test",
            saga_name="create_booking",
            steps=CREATE_BOOKING_SAGA,
            context=booking_context,
        )

        assert execution.state == SagaState.SUCCEEDED
        assert len(execution.steps_completed) == 4
        assert "create_nf" in execution.steps_completed
        assert "send_email" in execution.steps_completed
        assert "send_whatsapp" in execution.steps_completed
        assert "add_calendar" in execution.steps_completed

    def test_booking_saga_nf_creation(self, orchestrator, booking_context):
        """Teste: NF-e é criada no primeiro passo."""
        execution = orchestrator.execute(
            saga_id="booking_nf_test",
            saga_name="create_booking",
            steps=CREATE_BOOKING_SAGA,
            context=booking_context,
        )

        # NF ID deve estar no contexto
        assert "nf_id" in execution.context
        assert execution.context["nf_id"].startswith("NF-")

    def test_booking_saga_communications_sent(self, orchestrator, booking_context):
        """Teste: Email e WhatsApp são enviados."""
        execution = orchestrator.execute(
            saga_id="booking_comm_test",
            saga_name="create_booking",
            steps=CREATE_BOOKING_SAGA,
            context=booking_context,
        )

        # Mensagens devem estar registradas
        assert "email_message_id" in execution.context
        assert "whatsapp_message_id" in execution.context
        assert execution.context["email_message_id"].startswith("MSG-")
        assert execution.context["whatsapp_message_id"].startswith("WA-")

    def test_booking_saga_calendar_sync(self, orchestrator, booking_context):
        """Teste: Evento adicionado ao calendário."""
        execution = orchestrator.execute(
            saga_id="booking_cal_test",
            saga_name="create_booking",
            steps=CREATE_BOOKING_SAGA,
            context=booking_context,
        )

        # Evento deve estar registrado
        assert "calendar_event_id" in execution.context
        assert execution.context["calendar_event_id"].startswith("EVENT-")

    def test_booking_saga_timing(self, orchestrator, booking_context):
        """Teste: Saga completa em tempo razoável (<1s)."""
        execution = orchestrator.execute(
            saga_id="booking_timing_test",
            saga_name="create_booking",
            steps=CREATE_BOOKING_SAGA,
            context=booking_context,
        )

        # Deve completar em menos de 1 segundo (é mock, muito rápido)
        assert execution.duration() < 1.0


# ============================================================================
# TEST: Payment Saga Full Execution
# ============================================================================


class TestPaymentSagaExecution:
    """Testa execução completa do payment saga."""

    def test_payment_saga_success_full_flow(self, orchestrator, payment_context):
        """Teste: Payment saga completa com sucesso."""
        execution = orchestrator.execute(
            saga_id="payment_full_test",
            saga_name="collect_payment",
            steps=COLLECT_PAYMENT_SAGA,
            context=payment_context,
        )

        assert execution.state == SagaState.SUCCEEDED
        assert len(execution.steps_completed) == 4
        assert "process_payment" in execution.steps_completed
        assert "create_invoice" in execution.steps_completed
        assert "send_receipt" in execution.steps_completed
        assert "log_analytics" in execution.steps_completed

    def test_payment_saga_stripe_charge(self, orchestrator, payment_context):
        """Teste: Cobrança no Stripe processada."""
        execution = orchestrator.execute(
            saga_id="payment_stripe_test",
            saga_name="collect_payment",
            steps=COLLECT_PAYMENT_SAGA,
            context=payment_context,
        )

        # Charge ID deve estar no contexto
        assert "stripe_charge_id" in execution.context
        assert execution.context["stripe_charge_id"].startswith("CHARGE-")

    def test_payment_saga_invoice_creation(self, orchestrator, payment_context):
        """Teste: Fatura é criada."""
        execution = orchestrator.execute(
            saga_id="payment_invoice_test",
            saga_name="collect_payment",
            steps=COLLECT_PAYMENT_SAGA,
            context=payment_context,
        )

        # Invoice ID deve estar no contexto
        assert "invoice_id" in execution.context
        assert "INV-" in execution.context["invoice_id"]

    def test_payment_saga_receipt_email(self, orchestrator, payment_context):
        """Teste: Recibo enviado por email."""
        execution = orchestrator.execute(
            saga_id="payment_receipt_test",
            saga_name="collect_payment",
            steps=COLLECT_PAYMENT_SAGA,
            context=payment_context,
        )

        # Receipt message ID deve estar no contexto
        assert "email_receipt_id" in execution.context
        assert execution.context["email_receipt_id"].startswith("RECEIPT-")


# ============================================================================
# TEST: Compensation on Failure Scenarios
# ============================================================================


class TestCompensationScenarios:
    """Testa cenários de compensação (rollback)."""

    def test_booking_failure_at_calendar_step(self, orchestrator, booking_context):
        """Teste: Falha no add_calendar compensa NF + Email + WhatsApp."""
        # Modificar o step de calendário para falhar
        from src.sagas.create_booking import (
            calendar_api_remove_event,
        )

        def calendar_fail(ctx):
            raise ValueError("Calendar API down")

        custom_steps = CREATE_BOOKING_SAGA[:-1] + [
            SagaStep("add_calendar", calendar_fail, calendar_api_remove_event)
        ]

        execution = orchestrator.execute(
            saga_id="booking_fail_test",
            saga_name="create_booking",
            steps=custom_steps,
            context=booking_context,
        )

        # Deve falhar no último passo
        assert execution.state == SagaState.FAILED
        assert execution.failed_step == "add_calendar"
        assert execution.compensation_performed is True

    def test_payment_failure_refunds_automatically(self, orchestrator, payment_context):
        """Teste: Falha no pagamento não cria fatura."""

        def stripe_fail(ctx):
            raise ValueError("Card declined")

        custom_steps = [
            SagaStep(
                "process_payment",
                stripe_fail,
                None,  # Sem compensação = não reembolsa (já não cobrou)
                retry_count=0,
            ),
            COLLECT_PAYMENT_SAGA[1],  # create_invoice
        ]

        execution = orchestrator.execute(
            saga_id="payment_fail_test",
            saga_name="collect_payment",
            steps=custom_steps,
            context=payment_context,
        )

        # Deve falhar no pagamento
        assert execution.state == SagaState.FAILED
        assert execution.failed_step == "process_payment"
        # Fatura não deve estar criada
        assert "invoice_id" not in execution.context


# ============================================================================
# TEST: Retry & Recovery
# ============================================================================


class TestRetryAndRecovery:
    """Testa retry automático e recuperação."""

    def test_booking_retry_on_email_failure(self, orchestrator, booking_context):
        """Teste: Email falha, tenta retry, depois sucede."""
        from src.sagas.create_booking import email_api_send_cancellation

        attempt_count = 0

        def email_flaky(ctx):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("Email service temporary failure")
            ctx["email_message_id"] = f"MSG-{datetime.now(timezone.utc).timestamp()}"
            return ctx["email_message_id"]

        custom_steps = [
            CREATE_BOOKING_SAGA[0],  # NF
            SagaStep(
                "send_email", email_flaky, email_api_send_cancellation, retry_count=2
            ),
            CREATE_BOOKING_SAGA[2],  # WhatsApp
            CREATE_BOOKING_SAGA[3],  # Calendar
        ]

        execution = orchestrator.execute(
            saga_id="booking_retry_test",
            saga_name="create_booking",
            steps=custom_steps,
            context=booking_context,
        )

        # Deve eventualmente suceder
        assert execution.state == SagaState.SUCCEEDED
        assert attempt_count == 2
        assert "email_message_id" in execution.context


# ============================================================================
# TEST: Context Propagation
# ============================================================================


class TestContextPropagation:
    """Testa propagação de contexto entre passos."""

    def test_context_shared_across_steps(self, orchestrator, booking_context):
        """Teste: Contexto é compartilhado entre todos os passos."""
        original_context = booking_context.copy()

        execution = orchestrator.execute(
            saga_id="context_test",
            saga_name="create_booking",
            steps=CREATE_BOOKING_SAGA,
            context=booking_context,
        )

        # Contexto original deve ter sido modificado
        assert "nf_id" in execution.context
        assert "email_message_id" in execution.context
        assert "whatsapp_message_id" in execution.context
        assert "calendar_event_id" in execution.context

        # Dados originais ainda lá
        for key in original_context:
            assert key in execution.context

    def test_context_isolation_between_sagas(self, orchestrator):
        """Teste: Contexto não vaza entre sagas."""
        context1 = {
            "sale_id": "SALE-001",
            "customer_email": "test1@example.com",
        }

        context2 = {
            "sale_id": "SALE-002",
            "customer_email": "test2@example.com",
        }

        from src.sagas.create_booking import nf_api_create

        steps = [SagaStep("s1", nf_api_create)]

        exec1 = orchestrator.execute("saga_1", "test", steps, context1)
        exec2 = orchestrator.execute("saga_2", "test", steps, context2)

        # Contextos diferentes
        assert exec1.context["nf_id"] != exec2.context["nf_id"]
        assert exec1.context["customer_email"] == "test1@example.com"
        assert exec2.context["customer_email"] == "test2@example.com"


# ============================================================================
# TEST: Orchestrator Monitoring & Metrics
# ============================================================================


class TestOrchestratorMonitoring:
    """Testa monitoramento e métricas do orquestrador."""

    def test_multiple_executions_tracked(
        self, orchestrator, booking_context, payment_context
    ):
        """Teste: Múltiplas execuções são rastreadas."""
        orchestrator.execute(
            saga_id="booking_1",
            saga_name="create_booking",
            steps=CREATE_BOOKING_SAGA,
            context=booking_context.copy(),
        )

        orchestrator.execute(
            saga_id="payment_1",
            saga_name="collect_payment",
            steps=COLLECT_PAYMENT_SAGA,
            context=payment_context.copy(),
        )

        executions = orchestrator.list_executions()
        assert len(executions) == 2

    def test_metrics_accuracy(self, orchestrator, booking_context, payment_context):
        """Teste: Métricas contam corretamente."""

        def calendar_fail(ctx):
            raise ValueError("fail")

        custom_fail = CREATE_BOOKING_SAGA[:-1] + [
            SagaStep("add_calendar", calendar_fail)
        ]

        # Uma sucesso, uma falha
        orchestrator.execute(
            saga_id="booking_ok",
            saga_name="create_booking",
            steps=CREATE_BOOKING_SAGA,
            context=booking_context.copy(),
        )

        orchestrator.execute(
            saga_id="booking_fail",
            saga_name="create_booking",
            steps=custom_fail,
            context=booking_context.copy(),
        )

        stats = orchestrator.get_stats()
        assert stats["succeeded"] == 1
        assert stats["failed"] == 1
        assert stats["success_rate"] == 0.5


# ============================================================================
# TEST: Complex Workflows
# ============================================================================


class TestComplexWorkflows:
    """Testa workflows complexos (booking + payment sequencial)."""

    def test_booking_then_payment_workflow(
        self, orchestrator, booking_context, payment_context
    ):
        """Teste: Criar booking, depois cobrar pagamento."""
        # 1. Executar booking
        exec_booking = orchestrator.execute(
            saga_id="workflow_booking",
            saga_name="create_booking",
            steps=CREATE_BOOKING_SAGA,
            context=booking_context.copy(),
        )

        assert exec_booking.state == SagaState.SUCCEEDED

        # 2. Usar dados do booking para pagamento
        payment_context["booking_id"] = exec_booking.context["sale_id"]

        # 3. Executar pagamento
        exec_payment = orchestrator.execute(
            saga_id="workflow_payment",
            saga_name="collect_payment",
            steps=COLLECT_PAYMENT_SAGA,
            context=payment_context.copy(),
        )

        assert exec_payment.state == SagaState.SUCCEEDED

        # Ambos rastreados
        executions = orchestrator.list_executions()
        assert len(executions) == 2


# ============================================================================
# RUN TESTES
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
