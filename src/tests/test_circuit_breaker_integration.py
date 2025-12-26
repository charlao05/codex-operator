"""Testes de Integração: Circuit Breaker + APIs.

Valida que Circuit Breaker protege chamadas a APIs externas:
- Gmail, Email, WhatsApp, Telegram
- Simula falhas e testa automatic fallback
- Verifica recuperação após timeout
- Valida que não há cascata de falhas
"""

import pytest
import time

from src.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState


class TestCircuitBreakerWithAPIs:
    """Testes de integração CB com APIs."""

    def test_gmail_api_with_circuit_breaker(self):
        """Circuit Breaker protege chamadas a Gmail API."""
        # Simular Gmail API com Circuit Breaker
        config = CircuitBreakerConfig(
            name="gmail_api", failure_threshold=2, success_threshold=1, timeout=1
        )
        cb = CircuitBreaker(config=config)

        # Simular falha da API
        def gmail_send(to, subject, body):
            raise ConnectionError("Gmail API timeout")

        # protected_send was unused; call CircuitBreaker directly in tests

        # Primeira falha
        with pytest.raises(ConnectionError):
            cb.call(gmail_send, to="test@test.com", subject="Test", body="Body")

        assert cb.stats.total_failures == 1
        assert cb.state == CircuitState.CLOSED

        # Segunda falha abre o circuit
        with pytest.raises(ConnectionError):
            cb.call(gmail_send, to="test@test.com", subject="Test", body="Body")

        assert cb.stats.total_failures == 2
        assert cb.state == CircuitState.OPEN

        # Terceira tentativa falha rápido (sem chamar API)
        result = cb.call(gmail_send, to="test@test.com", subject="Test", body="Body")
        assert result is None
        assert cb.stats.total_rejections == 1

    def test_email_api_with_circuit_breaker(self):
        """Circuit Breaker protege Email SMTP."""
        config = CircuitBreakerConfig(
            name="email_smtp", failure_threshold=1, success_threshold=1, timeout=1
        )
        cb = CircuitBreaker(config=config)

        # Simular SMTP failure
        def send_smtp(recipients, subject, body):
            raise TimeoutError("SMTP timeout")

        # Abre circuit rapidamente (threshold=1)
        with pytest.raises(TimeoutError):
            cb.call(
                send_smtp, recipients=["test@test.com"], subject="Test", body="Body"
            )

        assert cb.state == CircuitState.OPEN

        # Agora rejeita fast (não chama SMTP)
        result = cb.call(
            send_smtp, recipients=["test@test.com"], subject="Test", body="Body"
        )
        assert result is None

    def test_whatsapp_api_with_circuit_breaker(self):
        """Circuit Breaker protege WhatsApp Business API."""
        config = CircuitBreakerConfig(
            name="whatsapp_api", failure_threshold=3, success_threshold=1, timeout=1
        )
        cb = CircuitBreaker(config=config)

        call_count = [0]

        def whatsapp_send(phone, message):
            call_count[0] += 1
            if call_count[0] <= 3:
                raise RuntimeError("WhatsApp API rate limited")
            return {"status": "sent", "message_id": "123"}

        # Acumula 3 falhas
        for i in range(3):
            with pytest.raises(RuntimeError):
                cb.call(whatsapp_send, phone="+5511999999999", message="Test")

        assert cb.state == CircuitState.OPEN

        # Aguarda timeout
        time.sleep(1.1)

        # Tenta recuperar (HALF_OPEN)
        result = cb.call(whatsapp_send, phone="+5511999999999", message="Test")
        assert result is not None
        assert cb.state == CircuitState.CLOSED

    def test_telegram_api_with_circuit_breaker(self):
        """Circuit Breaker protege Telegram Bot API."""
        config = CircuitBreakerConfig(
            name="telegram_bot", failure_threshold=2, success_threshold=2, timeout=1
        )
        cb = CircuitBreaker(config=config)

        failures = [0]

        def telegram_send(chat_id, text):
            failures[0] += 1
            if failures[0] <= 2:
                raise ConnectionError("Telegram API unreachable")
            return {"ok": True, "result": {"message_id": 123}}

        # 2 falhas abrem
        for _ in range(2):
            with pytest.raises(ConnectionError):
                cb.call(telegram_send, chat_id="123456", text="Test")

        assert cb.state == CircuitState.OPEN

        # Aguarda e tenta recuperar
        time.sleep(1.1)

        # Precisa de 2 sucessos para fechar
        for i in range(2):
            _ = cb.call(telegram_send, chat_id="123456", text="Test")
            if i == 1:
                # Após 2º sucesso, deve estar CLOSED
                assert cb.state == CircuitState.CLOSED

    def test_cascading_failure_prevention(self):
        """CB previne cascata de falhas entre APIs."""
        # Simular duas APIs em cascata
        gmail_cb = CircuitBreaker(
            CircuitBreakerConfig(name="gmail", failure_threshold=2)
        )

        fallback_email_cb = CircuitBreaker(
            CircuitBreakerConfig(name="email_fallback", failure_threshold=2)
        )

        def gmail_send():
            raise ConnectionError("Gmail down")

        def email_fallback():
            raise ConnectionError("Email SMTP also down")

        # Gmail falha e abre
        for _ in range(2):
            with pytest.raises(ConnectionError):
                gmail_cb.call(gmail_send)

        assert gmail_cb.state == CircuitState.OPEN

        # Sistema tenta fallback (email)
        for _ in range(2):
            with pytest.raises(ConnectionError):
                fallback_email_cb.call(email_fallback)

        assert fallback_email_cb.state == CircuitState.OPEN

        # Agora ambos estão abertos
        result1 = gmail_cb.call(lambda: "send email")
        result2 = fallback_email_cb.call(lambda: "send sms")

        assert result1 is None
        assert result2 is None

    def test_circuit_breaker_statistics_accuracy(self):
        """Estatísticas refletem uso real com APIs."""
        cb = CircuitBreaker(CircuitBreakerConfig(name="test_api", failure_threshold=5))

        # Simular 20 requisições: 15 sucesso, 5 falha
        for i in range(15):
            cb.call(lambda: f"success_{i}")

        for i in range(5):
            try:
                cb.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        stats = cb.get_stats()
        assert stats["total_requests"] == 20
        assert stats["total_successes"] == 15
        assert stats["total_failures"] == 5
        assert stats["success_rate"] == "75.0%"
        assert stats["failure_rate"] == "25.0%"

    def test_decorator_with_api_function(self):
        """Decorator @guard() funciona com funções reais de API."""
        cb = CircuitBreaker(
            CircuitBreakerConfig(name="api_decorator", failure_threshold=2)
        )

        call_count = [0]

        @cb.guard()
        def api_call(param1, param2):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise ValueError("API Error")
            return {"result": param1 + param2}

        # Primeira 2 chamadas falham
        with pytest.raises(ValueError):
            api_call(1, 2)

        with pytest.raises(ValueError):
            api_call(3, 4)

        # Agora circuit está OPEN
        result = api_call(5, 6)
        assert result is None  # Rejected

    def test_circuit_breaker_with_http_exception(self):
        """CB captura exceções HTTP de APIs."""
        cb = CircuitBreaker(CircuitBreakerConfig(name="http_api", failure_threshold=1))

        def api_with_http_error():
            # Simular HTTP 500
            class HTTPError(Exception):
                def __init__(self, status):
                    self.status = status

            raise HTTPError(500)

        # Falha abre o circuit
        with pytest.raises(Exception):
            cb.call(api_with_http_error)

        assert cb.state == CircuitState.OPEN

        # Próxima requisição é rejeitada
        result = cb.call(api_with_http_error)
        assert result is None


class TestCircuitBreakerRecoveryScenarios:
    """Testes para cenários de recuperação realistas."""

    def test_intermittent_failures_recovery(self):
        """CB recupera de falhas intermitentes."""
        config = CircuitBreakerConfig(
            name="intermittent_api", failure_threshold=3, success_threshold=2, timeout=1
        )
        cb = CircuitBreaker(config=config)

        # API que falha 3x, depois recupera
        call_sequence = ["fail", "fail", "fail", "success", "success"]
        index = [0]

        def flaky_api():
            result = call_sequence[index[0]]
            index[0] = min(index[0] + 1, len(call_sequence) - 1)

            if result == "fail":
                raise RuntimeError("Temporary failure")
            return {"status": "ok"}

        # 3 falhas abrem
        for _ in range(3):
            with pytest.raises(RuntimeError):
                cb.call(flaky_api)

        assert cb.state == CircuitState.OPEN

        # Aguarda recovery timeout
        time.sleep(1.1)

        # 2 sucessos fecham
        for _ in range(2):
            result = cb.call(flaky_api)
            assert result is not None

        assert cb.state == CircuitState.CLOSED

    def test_graceful_degradation_with_fallback(self):
        """Sistema degrada graciosamente quando API falha."""
        main_api_cb = CircuitBreaker(
            CircuitBreakerConfig(name="main_api", failure_threshold=1)
        )

        def main_api():
            raise RuntimeError("Main API down")

        def fallback_response():
            return {"status": "degraded", "message": "Using cached data"}

        # Main API falha e abre
        with pytest.raises(RuntimeError):
            main_api_cb.call(main_api)

        # Circuit está OPEN
        result = main_api_cb.call(main_api)
        assert result is None

        # Sistema pode usar fallback
        fallback = fallback_response()
        assert fallback["status"] == "degraded"

    def test_partial_failure_doesnt_cascade(self):
        """Falha em uma API não causa cascata em outras."""
        gmail_cb = CircuitBreaker(
            CircuitBreakerConfig(name="gmail", failure_threshold=1)
        )

        whatsapp_cb = CircuitBreaker(
            CircuitBreakerConfig(name="whatsapp", failure_threshold=1)
        )

        # Gmail falha
        with pytest.raises(ConnectionError):
            gmail_cb.call(lambda: (_ for _ in ()).throw(ConnectionError("Gmail down")))

        # Mas WhatsApp continua operando
        result = whatsapp_cb.call(lambda: {"status": "sent"})
        assert result["status"] == "sent"

        # Gmail está aberto, WhatsApp está fechado
        assert gmail_cb.state == CircuitState.OPEN
        assert whatsapp_cb.state == CircuitState.CLOSED


class TestCircuitBreakerMonitoring:
    """Testes para monitoramento e alerting."""

    def test_state_change_visibility(self):
        """Mudanças de estado são visíveis para monitoring."""
        cb = CircuitBreaker(
            CircuitBreakerConfig(name="monitored_api", failure_threshold=2)
        )

        # Registra mudança CLOSED -> OPEN
        state_changes = []

        # Gera 2 falhas para OPEN
        for _ in range(2):
            try:
                cb.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass
            state_changes.append(cb.state.value)

        # Último deve ser OPEN
        assert state_changes[-1] == "OPEN"
        assert cb.stats.state_changes == 1

    def test_metrics_for_alerting(self):
        """Métricas disponíveis para alerting."""
        cb = CircuitBreaker(
            CircuitBreakerConfig(name="alertable_api", failure_threshold=3)
        )

        # Gera falhas
        for _ in range(3):
            try:
                cb.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        stats = cb.get_stats()

        # Pode usar para alertas
        if stats["state"] == "OPEN":
            alert = f"ALERT: {stats['name']} circuit opened. Failure rate: {stats['failure_rate']}"
            assert "ALERT" in alert
            assert stats["name"] == "alertable_api"

    def test_last_failure_information(self):
        """Informações sobre última falha disponíveis."""
        cb = CircuitBreaker(
            CircuitBreakerConfig(name="trackable_api", failure_threshold=1)
        )

        try:
            cb.call(lambda: (_ for _ in ()).throw(ValueError("Connection timeout")))
        except ValueError:
            pass

        stats = cb.get_stats()
        assert stats["last_failure_reason"] == "Connection timeout"
        assert stats["last_state_change"] is not None
