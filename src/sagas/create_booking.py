"""
SAGA Pattern: Create Booking

Exemplo de saga que:
1. Cria NF-e no sistema de faturamento
2. Envia email de confirmação
3. Notifica via WhatsApp
4. Registra no calendário

Se qualquer passo falhar, reverte os anteriores automaticamente.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from src.core.saga_orchestrator import SagaStep

# Imports das APIs (mock para desenvolvimento)
logger = logging.getLogger(__name__)


def nf_api_create(context: Dict[str, Any]) -> str:
    """
    Cria NF-e no sistema de faturamento.

    Args:
        context: {
            'sale_id': str,
            'customer_name': str,
            'amount': float,
            'service_description': str
        }

    Returns:
        nf_id (str)

    Raises:
        Exception: Se API falhar
    """
    logger.info(f"[NF-e API] Criando NF para venda {context['sale_id']}")

    # Simular chamada à API
    # Aqui entraria: nf_response = requests.post("https://nf.io/api/create", ...)

    nf_id = f"NF-{context['sale_id']}-{datetime.now(timezone.utc).timestamp()}"

    logger.info(f"[NF-e API] ✓ NF criada: {nf_id}")

    # Armazenar nf_id no contexto para compensação posterior
    context["nf_id"] = nf_id

    return nf_id


def nf_api_cancel(context: Dict[str, Any]) -> None:
    """Cancela NF-e criada (compensação)."""
    nf_id = context.get("nf_id")

    if not nf_id:
        logger.warning("[NF-e API] nf_id não encontrado no contexto")
        return

    logger.info(f"[NF-e API] Cancelando NF: {nf_id}")

    # Simular chamada à API
    # aqui entraria: requests.delete(f"https://nf.io/api/{nf_id}")

    logger.info(f"[NF-e API] ✓ NF cancelada: {nf_id}")


def email_api_send_confirmation(context: Dict[str, Any]) -> str:
    """
    Envia email de confirmação de agendamento.

    Args:
        context: {
            'customer_email': str,
            'customer_name': str,
            'booking_date': str,
            'service_description': str
        }

    Returns:
        email_message_id (str)
    """
    email = context.get("customer_email")

    logger.info(f"[Email API] Enviando confirmação para {email}")

    # Simular envio
    # requests.post("https://gmail.io/api/send", ...)

    message_id = f"MSG-{datetime.now(timezone.utc).timestamp()}"
    context["email_message_id"] = message_id

    logger.info(f"[Email API] ✓ Email enviado: {message_id}")

    return message_id


def email_api_send_cancellation(context: Dict[str, Any]) -> None:
    """Envia email de cancelamento (compensação)."""
    email = context.get("customer_email")

    if not email:
        logger.warning("[Email API] customer_email não encontrado")
        return

    logger.info(f"[Email API] Enviando cancelamento para {email}")

    # Simular envio

    logger.info("[Email API] ✓ Email de cancelamento enviado")


def whatsapp_api_notify(context: Dict[str, Any]) -> str:
    """
    Notifica cliente via WhatsApp.

    Args:
        context: {
            'customer_phone': str,
            'booking_id': str,
            'booking_date': str
        }

    Returns:
        whatsapp_message_id (str)
    """
    phone = context.get("customer_phone")

    logger.info(f"[WhatsApp API] Enviando notificação para {phone}")

    # Simular envio
    # requests.post("https://whatsapp.io/api/send", ...)

    message_id = f"WA-{datetime.now(timezone.utc).timestamp()}"
    context["whatsapp_message_id"] = message_id

    logger.info(f"[WhatsApp API] ✓ WhatsApp enviado: {message_id}")

    return message_id


def whatsapp_api_cancel_notification(context: Dict[str, Any]) -> None:
    """Envia notificação de cancelamento via WhatsApp (compensação)."""
    phone = context.get("customer_phone")

    if not phone:
        logger.warning("[WhatsApp API] customer_phone não encontrado")
        return

    logger.info(f"[WhatsApp API] Enviando notificação de cancelamento para {phone}")

    # Simular envio

    logger.info("[WhatsApp API] ✓ Notificação de cancelamento enviada")


def calendar_api_add_event(context: Dict[str, Any]) -> str:
    """
    Adiciona evento ao Google Calendar do atendente.

    Args:
        context: {
            'calendar_id': str,
            'booking_date': str,
            'customer_name': str,
            'service_description': str
        }

    Returns:
        calendar_event_id (str)
    """
    booking_date = context.get("booking_date")

    logger.info(f"[Calendar API] Adicionando evento em {booking_date}")

    # Simular chamada
    # google_calendar.events().insert(calendarId=calendar_id, body={...})

    event_id = f"EVENT-{datetime.now(timezone.utc).timestamp()}"
    context["calendar_event_id"] = event_id

    logger.info(f"[Calendar API] ✓ Evento adicionado: {event_id}")

    return event_id


def calendar_api_remove_event(context: Dict[str, Any]) -> None:
    """Remove evento do calendário (compensação)."""
    event_id = context.get("calendar_event_id")

    if not event_id:
        logger.warning("[Calendar API] calendar_event_id não encontrado")
        return

    logger.info(f"[Calendar API] Removendo evento: {event_id}")

    # Simular remoção

    logger.info("[Calendar API] ✓ Evento removido")


# ============================================================================
# DEFINIÇÃO DO SAGA: CREATE_BOOKING
# ============================================================================

CREATE_BOOKING_SAGA = [
    SagaStep(
        name="create_nf",
        action=nf_api_create,
        compensation=nf_api_cancel,
        timeout=10.0,
        retry_count=3,
        retry_delay=1.0,
        idempotent=True,
    ),
    SagaStep(
        name="send_email",
        action=email_api_send_confirmation,
        compensation=email_api_send_cancellation,
        timeout=5.0,
        retry_count=2,
        retry_delay=0.5,
        idempotent=True,
    ),
    SagaStep(
        name="send_whatsapp",
        action=whatsapp_api_notify,
        compensation=whatsapp_api_cancel_notification,
        timeout=5.0,
        retry_count=2,
        retry_delay=0.5,
        idempotent=True,
    ),
    SagaStep(
        name="add_calendar",
        action=calendar_api_add_event,
        compensation=calendar_api_remove_event,
        timeout=5.0,
        retry_count=1,
        retry_delay=0.5,
        idempotent=True,
    ),
]


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    from src.core.saga_orchestrator import get_saga_orchestrator

    logging.basicConfig(level=logging.INFO)

    orchestrator = get_saga_orchestrator()

    # Contexto de exemplo
    booking_context = {
        "sale_id": "SALE-001",
        "booking_id": "BOOKING-001",
        "customer_name": "João Silva",
        "customer_email": "joao@email.com",
        "customer_phone": "+5511999999999",
        "amount": 150.00,
        "service_description": "Corte de cabelo + barba",
        "booking_date": "2025-12-10T14:00:00",
        "calendar_id": "charles@gmail.com",
    }

    # Executar saga
    execution = orchestrator.execute(
        saga_id="booking_001",
        saga_name="create_booking",
        steps=CREATE_BOOKING_SAGA,
        context=booking_context,
    )

    # Verificar resultado
    print("\n" + "=" * 70)
    print(f"RESULTADO: {execution.state.value}")
    print(f"Passos completados: {len(execution.steps_completed)}")
    print(f"Duração: {execution.duration():.2f}s")
    print("=" * 70)

    if execution.state.value == "succeeded":
        print("✓ Booking criado com sucesso!")
    else:
        print(f"✗ Falha no passo: {execution.failed_step}")
        print(f"Mensagem: {execution.last_error}")
