"""
SAGA Pattern implementations for Codex Operator

Includes:
- CREATE_BOOKING_SAGA: NF-e + Email + WhatsApp + Calendar
- COLLECT_PAYMENT_SAGA: Stripe + Invoice + Receipt + Analytics
"""

from src.sagas.create_booking import (
    CREATE_BOOKING_SAGA,
    nf_api_create,
    nf_api_cancel,
    email_api_send_confirmation,
    email_api_send_cancellation,
    whatsapp_api_notify,
    whatsapp_api_cancel_notification,
    calendar_api_add_event,
    calendar_api_remove_event,
)

from src.sagas.collect_payment import (
    COLLECT_PAYMENT_SAGA,
    stripe_charge_customer,
    stripe_refund_charge,
    finance_db_create_invoice,
    finance_db_delete_invoice,
    email_api_send_receipt,
    analytics_log_transaction,
)

__all__ = [
    "CREATE_BOOKING_SAGA",
    "COLLECT_PAYMENT_SAGA",
    # Booking functions
    "nf_api_create",
    "nf_api_cancel",
    "email_api_send_confirmation",
    "email_api_send_cancellation",
    "whatsapp_api_notify",
    "whatsapp_api_cancel_notification",
    "calendar_api_add_event",
    "calendar_api_remove_event",
    # Payment functions
    "stripe_charge_customer",
    "stripe_refund_charge",
    "finance_db_create_invoice",
    "finance_db_delete_invoice",
    "email_api_send_receipt",
    "analytics_log_transaction",
]
