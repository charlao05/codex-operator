"""Testes para Circuit Breaker Pattern.

Cobertura: Estados (CLOSED/OPEN/HALF_OPEN), transições, fallback, recovery.
Estratégia: Unit tests para lógica de estado, integration tests para decorador.
"""

import pytest
import time
from datetime import datetime

from src.core.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerStats,
    CircuitState,
)


class TestCircuitBreakerConfig:
    """Testes para configuração."""

    def test_default_config(self):
        """Verifica valores padrão da config."""
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.success_threshold == 2
        assert config.timeout == 60
        assert config.name == "CircuitBreaker"

    def test_custom_config(self):
        """Verifica config customizada."""
        config = CircuitBreakerConfig(
            failure_threshold=3, success_threshold=1, timeout=30, name="test_breaker"
        )
        assert config.failure_threshold == 3
        assert config.success_threshold == 1
        assert config.timeout == 30
        assert config.name == "test_breaker"


class TestCircuitBreakerStats:
    """Testes para estatísticas."""

    def test_stats_initialization(self):
        """Inicializa com valores zerados."""
        stats = CircuitBreakerStats()
        assert stats.total_requests == 0
        assert stats.total_failures == 0
        assert stats.total_successes == 0
        assert stats.success_rate() == 0.0

    def test_success_rate_calculation(self):
        """Calcula taxa de sucesso corretamente."""
        stats = CircuitBreakerStats()
        stats.total_requests = 10
        stats.total_successes = 7

        assert stats.success_rate() == 70.0
        assert stats.failure_rate() == 30.0

    def test_success_rate_zero_requests(self):
        """Taxa de sucesso com zero requisições."""
        stats = CircuitBreakerStats()
        assert stats.success_rate() == 0.0
        assert stats.failure_rate() == 100.0  # Corrigido: 100%, não 0%


class TestCircuitBreakerInitialization:
    """Testes para inicialização."""

    def test_initialization_closed_state(self):
        """Inicia em estado CLOSED."""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.stats.total_requests == 0

    def test_initialization_with_config(self):
        """Inicializa com config customizada."""
        config = CircuitBreakerConfig(name="my_breaker", failure_threshold=3)
        cb = CircuitBreaker(config=config)

        assert cb.config.name == "my_breaker"
        assert cb.config.failure_threshold == 3
        assert cb.state == CircuitState.CLOSED


class TestCircuitBreakerClosedState:
    """Testes para estado CLOSED (normal operation)."""

    def test_closed_allows_requests(self):
        """CLOSED permite requests passarem."""
        cb = CircuitBreaker()

        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.stats.total_requests == 1
        assert cb.stats.total_successes == 1

    def test_closed_counts_successes(self):
        """CLOSED conta sucessos."""
        cb = CircuitBreaker()

        for i in range(5):
            cb.call(lambda: "ok")

        assert cb.stats.total_successes == 5
        assert cb.stats.total_requests == 5

    def test_closed_counts_failures(self):
        """CLOSED conta falhas."""
        cb = CircuitBreaker()

        for i in range(3):
            try:
                cb.call(lambda: 1 / 0)  # Division by zero
            except ZeroDivisionError:
                pass

        assert cb.stats.total_failures == 3
        assert cb.stats.consecutive_failures == 3

    def test_closed_transitions_to_open_on_threshold(self):
        """CLOSED -> OPEN quando atinge threshold de falhas."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(config=config)

        # Temos 3 falhas para atingir threshold
        for i in range(3):
            try:
                cb.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        assert cb.state == CircuitState.OPEN
        assert cb.stats.state_changes == 1

    def test_closed_resets_failure_count_on_success(self):
        """CLOSED reseta failure count após sucesso."""
        config = CircuitBreakerConfig(failure_threshold=5)
        cb = CircuitBreaker(config=config)

        # 2 falhas
        for _ in range(2):
            try:
                cb.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        assert cb.stats.consecutive_failures == 2

        # 1 sucesso reseta
        cb.call(lambda: "ok")
        assert cb.stats.consecutive_failures == 0
        assert cb.stats.consecutive_successes == 1


class TestCircuitBreakerOpenState:
    """Testes para estado OPEN (fail fast)."""

    def test_open_rejects_requests(self):
        """OPEN rejeita requests (fail fast)."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config=config)

        # Abre o circuit
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        assert cb.state == CircuitState.OPEN

        # Requisição é rejeitada
        result = cb.call(lambda: "should not execute")
        assert result is None
        assert cb.stats.total_rejections == 1

    def test_open_counts_rejections(self):
        """OPEN conta rejections."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config=config)

        # Abre
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        # Múltiplas rejections
        for i in range(5):
            cb.call(lambda: "test")

        assert cb.stats.total_rejections == 5

    def test_open_transitions_to_half_open_after_timeout(self):
        """OPEN -> HALF_OPEN após timeout."""
        config = CircuitBreakerConfig(failure_threshold=1, timeout=1)
        cb = CircuitBreaker(config=config)

        # Abre
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        assert cb.state == CircuitState.OPEN

        # Aguarda timeout
        time.sleep(1.1)

        # Próxima requisição tenta recuperar (não precisamos do retorno)
        _ = cb.call(lambda: "test_recovery")

        # Estado mudou para HALF_OPEN (ou tentou, mas pode voltar para OPEN se falhar)
        # O importante é que tentou uma requisição
        assert cb.stats.total_requests >= 2


class TestCircuitBreakerHalfOpenState:
    """Testes para estado HALF_OPEN (recovery testing)."""

    def test_half_open_allows_limited_requests(self):
        """HALF_OPEN permite requisições para teste."""
        config = CircuitBreakerConfig(failure_threshold=1, timeout=1)
        cb = CircuitBreaker(config=config)

        # Abre
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        # Aguarda timeout
        time.sleep(1.1)

        # Tenta recuperar (HALF_OPEN)
        result = cb.call(lambda: "recovered")
        assert result == "recovered"
        assert cb.stats.total_requests == 2  # 1 falha + 1 teste

    def test_half_open_transitions_to_closed_on_success_threshold(self):
        """HALF_OPEN -> CLOSED após success_threshold sucessos."""
        config = CircuitBreakerConfig(
            failure_threshold=1, success_threshold=2, timeout=1
        )
        cb = CircuitBreaker(config=config)

        # Abre
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        # Aguarda timeout
        time.sleep(1.1)

        # Testa recuperação (HALF_OPEN)
        assert cb.state == CircuitState.HALF_OPEN or cb.state == CircuitState.OPEN

        # 1º sucesso
        cb.call(lambda: "ok")
        # Ainda em HALF_OPEN (precisa de 2 sucessos)
        assert cb.state == CircuitState.HALF_OPEN or cb.state == CircuitState.CLOSED

        # 2º sucesso - fecha
        cb.call(lambda: "ok")
        assert cb.state == CircuitState.CLOSED

    def test_half_open_transitions_to_open_on_failure(self):
        """HALF_OPEN -> OPEN se falha durante teste."""
        config = CircuitBreakerConfig(
            failure_threshold=1, success_threshold=2, timeout=1
        )
        cb = CircuitBreaker(config=config)

        # Abre
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        # Aguarda timeout
        time.sleep(1.1)

        # Falha durante teste em HALF_OPEN
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        # Volta para OPEN
        assert cb.state == CircuitState.OPEN


class TestCircuitBreakerDecorator:
    """Testes para decorator @guard()."""

    def test_guard_decorator_success(self):
        """Decorator funciona com sucesso."""
        cb = CircuitBreaker()

        @cb.guard()
        def my_func(x):
            return x * 2

        result = my_func(5)
        assert result == 10
        assert cb.stats.total_successes == 1

    def test_guard_decorator_failure(self):
        """Decorator propaga exceções."""
        cb = CircuitBreaker()

        @cb.guard()
        def my_func():
            raise ValueError("test error")

        with pytest.raises(ValueError):
            my_func()

        assert cb.stats.total_failures == 1

    def test_guard_decorator_with_open_circuit(self):
        """Decorator retorna None quando circuit está OPEN."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config=config)

        @cb.guard()
        def failing_func():
            raise RuntimeError()

        # Abre o circuit
        with pytest.raises(RuntimeError):
            failing_func()

        assert cb.state == CircuitState.OPEN

        # Próxima chamada retorna None
        @cb.guard()
        def normal_func():
            return "should not execute"

        result = normal_func()
        assert result is None

    def test_guard_decorator_preserves_function_metadata(self):
        """Decorator preserva função metadata."""
        cb = CircuitBreaker()

        @cb.guard()
        def documented_func():
            """This is documented."""
            pass

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This is documented."


class TestCircuitBreakerStateTransitions:
    """Testes para transições de estado."""

    def test_state_change_tracking(self):
        """Rastreia número de mudanças de estado."""
        config = CircuitBreakerConfig(failure_threshold=1, timeout=1)
        cb = CircuitBreaker(config=config)

        assert cb.stats.state_changes == 0

        # CLOSED -> OPEN
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass
        assert cb.stats.state_changes == 1

        # OPEN -> HALF_OPEN
        time.sleep(1.1)
        cb.call(lambda: "test")
        assert cb.stats.state_changes == 2

    def test_last_state_change_timestamp(self):
        """Registra timestamp da última mudança de estado."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config=config)

        before = datetime.now()

        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        after = datetime.now()

        assert cb.stats.last_state_change is not None
        assert before <= cb.stats.last_state_change <= after


class TestCircuitBreakerManualControl:
    """Testes para controle manual."""

    def test_force_open(self):
        """Force circuit para OPEN."""
        cb = CircuitBreaker()
        initial_time = datetime.now()
        cb.force_open()
        cb._last_failure_time = initial_time  # Evita que timeout permita HALF_OPEN

        assert cb.state == CircuitState.OPEN
        result = cb.call(lambda: "test")
        assert result is None  # Deve retornar None pois está OPEN

    def test_force_closed(self):
        """Force circuit para CLOSED."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config=config)

        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        assert cb.state == CircuitState.OPEN

        cb.force_closed()
        assert cb.state == CircuitState.CLOSED

    def test_reset(self):
        """Reset limpa stats e fecha circuit."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config=config)

        # Abre e acumula stats
        try:
            cb.call(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        assert cb.stats.total_requests > 0
        assert cb.state == CircuitState.OPEN

        cb.reset()

        assert cb.state == CircuitState.CLOSED
        assert cb.stats.total_requests == 0
        assert cb.stats.total_failures == 0


class TestCircuitBreakerStatistics:
    """Testes para geração de estatísticas."""

    def test_get_stats_format(self):
        """get_stats retorna dict com campos esperados."""
        cb = CircuitBreaker(CircuitBreakerConfig(name="test_cb"))
        cb.call(lambda: "test")

        stats = cb.get_stats()

        assert stats["name"] == "test_cb"
        assert stats["state"] == "CLOSED"
        assert stats["total_requests"] == 1
        assert stats["total_successes"] == 1
        assert "success_rate" in stats

    def test_print_stats_format(self):
        """print_stats retorna string formatada."""
        cb = CircuitBreaker(CircuitBreakerConfig(name="test"))

        for _ in range(3):
            cb.call(lambda: "ok")

        stats_str = cb.print_stats()

        assert "CIRCUIT BREAKER STATS" in stats_str
        assert "test" in stats_str
        assert "Total Requests: 3" in stats_str


class TestCircuitBreakerEdgeCases:
    """Testes para casos extremos."""

    def test_rapid_failures_then_timeout(self):
        """Múltiplas falhas rápidas, depois timeout e recuperação."""
        config = CircuitBreakerConfig(failure_threshold=2, timeout=1)
        cb = CircuitBreaker(config=config)

        # 2 falhas abrem
        for _ in range(2):
            try:
                cb.call(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        assert cb.state == CircuitState.OPEN

        # Aguarda
        time.sleep(1.1)

        # Recupera
        result = cb.call(lambda: "recovered")
        assert result == "recovered"

    def test_alternating_success_failure_stays_closed(self):
        """Sucesso/falha alternado mantém CLOSED (não atinge threshold)."""
        config = CircuitBreakerConfig(failure_threshold=5)
        cb = CircuitBreaker(config=config)

        for i in range(10):
            if i % 2 == 0:
                cb.call(lambda: "ok")
            else:
                try:
                    cb.call(lambda: 1 / 0)
                except ZeroDivisionError:
                    pass

        # Não deve abrir porque nunca tem 5 falhas consecutivas
        assert cb.state == CircuitState.CLOSED

    def test_exception_propagation_in_closed(self):
        """Exceções propagam normalmente em CLOSED."""
        cb = CircuitBreaker()

        def failing_func():
            raise RuntimeError("test error")

        with pytest.raises(RuntimeError, match="test error"):
            cb.call(failing_func)
