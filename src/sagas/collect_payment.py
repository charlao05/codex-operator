"""
SAGA Pattern: Collect Payment

Exemplo de saga de cobrança que:
1. Processa pagamento (Stripe/PIX)
2. Cria fatura (Finance DB)
3. Envia recibo por email
4. Registra no relatório de negócios

Se falhar, reverte a cobrança automaticamente.
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


def stripe_charge_customer(context: Dict[str, Any]) -> str:
    """
    Processa cobrança via Stripe.
    
    Args:
        context: {
            'customer_id': str,
            'amount': float,  # em reais
            'description': str,
            'booking_id': str
        }
    
    Returns:
        charge_id (str)
    
    Raises:
        Exception: Se cobrança falhar
    """
    customer_id = context.get('customer_id')
    amount = context.get('amount', 0.0)
    
    logger.info(f"[Stripe API] Cobrando R$ {amount:.2f} do cliente {customer_id}")
    
    # Simular chamada à Stripe
    # stripe.Charge.create(
    #     amount=int(amount * 100),
    #     currency="brl",
    #     customer=customer_id,
    #     description=context.get('description')
    # )
    
    charge_id = f"CHARGE-{datetime.utcnow().timestamp()}"
    context['stripe_charge_id'] = charge_id
    
    logger.info(f"[Stripe API] ✓ Cobrança processada: {charge_id}")
    
    return charge_id


def stripe_refund_charge(context: Dict[str, Any]) -> None:
    """Reembolsa cobrança (compensação)."""
    charge_id = context.get('stripe_charge_id')
    
    if not charge_id:
        logger.warning("[Stripe API] stripe_charge_id não encontrado")
        return
    
    logger.info(f"[Stripe API] Reembolsando cobrança: {charge_id}")
    
    # Simular reembolso
    # stripe.Charge.retrieve(charge_id).refund()
    
    logger.info(f"[Stripe API] ✓ Cobrança reembolsada")


def finance_db_create_invoice(context: Dict[str, Any]) -> str:
    """
    Cria fatura no sistema financeiro.
    
    Args:
        context: {
            'customer_id': str,
            'booking_id': str,
            'amount': float,
            'service_description': str,
            'charge_id': str (do passo anterior)
        }
    
    Returns:
        invoice_id (str)
    """
    booking_id = context.get('booking_id')
    amount = context.get('amount')
    
    logger.info(f"[Finance DB] Criando fatura para booking {booking_id}")
    
    # Simular inserção em DB
    # INSERT INTO invoices (booking_id, amount, status, created_at) VALUES (...)
    
    invoice_id = f"INV-{booking_id}-{datetime.utcnow().timestamp()}"
    context['invoice_id'] = invoice_id
    
    logger.info(f"[Finance DB] ✓ Fatura criada: {invoice_id}")
    
    return invoice_id


def finance_db_delete_invoice(context: Dict[str, Any]) -> None:
    """Deleta fatura (compensação)."""
    invoice_id = context.get('invoice_id')
    
    if not invoice_id:
        logger.warning("[Finance DB] invoice_id não encontrado")
        return
    
    logger.info(f"[Finance DB] Deletando fatura: {invoice_id}")
    
    # Simular delete
    # DELETE FROM invoices WHERE id = invoice_id
    
    logger.info(f"[Finance DB] ✓ Fatura deletada")


def email_api_send_receipt(context: Dict[str, Any]) -> str:
    """
    Envia recibo de pagamento por email.
    
    Args:
        context: {
            'customer_email': str,
            'customer_name': str,
            'amount': float,
            'invoice_id': str,
            'payment_method': str
        }
    
    Returns:
        email_message_id (str)
    """
    email = context.get('customer_email')
    amount = context.get('amount')
    
    logger.info(f"[Email API] Enviando recibo para {email}")
    
    # Simular envio
    # requests.post("https://gmail.io/api/send", ...)
    
    message_id = f"RECEIPT-{datetime.utcnow().timestamp()}"
    context['email_receipt_id'] = message_id
    
    logger.info(f"[Email API] ✓ Recibo enviado: {message_id}")
    
    return message_id


def analytics_log_transaction(context: Dict[str, Any]) -> None:
    """
    Registra transação no analytics/relatório.
    
    Nota: Não tem compensação (é apenas log).
    
    Args:
        context: Contexto da transação
    """
    booking_id = context.get('booking_id')
    amount = context.get('amount')
    
    logger.info(f"[Analytics] Registrando transação de R$ {amount:.2f}")
    
    # Simular log/analytics
    # analytics.log_event("payment_received", {...})
    
    logger.info(f"[Analytics] ✓ Transação registrada")


# ============================================================================
# DEFINIÇÃO DO SAGA: COLLECT_PAYMENT
# ============================================================================

from src.core.saga_orchestrator import SagaStep

COLLECT_PAYMENT_SAGA = [
    SagaStep(
        name="process_payment",
        action=stripe_charge_customer,
        compensation=stripe_refund_charge,
        timeout=15.0,
        retry_count=3,
        retry_delay=2.0,
        idempotent=True
    ),
    
    SagaStep(
        name="create_invoice",
        action=finance_db_create_invoice,
        compensation=finance_db_delete_invoice,
        timeout=5.0,
        retry_count=2,
        retry_delay=1.0,
        idempotent=True
    ),
    
    SagaStep(
        name="send_receipt",
        action=email_api_send_receipt,
        compensation=None,  # Email não precisa de compensação
        timeout=5.0,
        retry_count=2,
        retry_delay=0.5,
        idempotent=True
    ),
    
    SagaStep(
        name="log_analytics",
        action=analytics_log_transaction,
        compensation=None,  # Log não precisa de compensação
        timeout=2.0,
        retry_count=1,
        retry_delay=0.5,
        idempotent=True
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
    payment_context = {
        "customer_id": "CUST-001",
        "customer_email": "joao@email.com",
        "customer_name": "João Silva",
        "booking_id": "BOOKING-001",
        "amount": 150.00,
        "service_description": "Corte de cabelo + barba",
        "payment_method": "credit_card",
    }
    
    # Executar saga de cobrança
    execution = orchestrator.execute(
        saga_id="payment_001",
        saga_name="collect_payment",
        steps=COLLECT_PAYMENT_SAGA,
        context=payment_context
    )
    
    # Verificar resultado
    print("\n" + "=" * 70)
    print(f"RESULTADO COBRANÇA: {execution.state.value}")
    print(f"Passos completados: {len(execution.steps_completed)}")
    print(f"Duração: {execution.duration():.2f}s")
    print("=" * 70)
    
    if execution.state.value == "succeeded":
        print("✓ Pagamento processado com sucesso!")
        print(f"Fatura: {execution.context.get('invoice_id')}")
        print(f"Recibo enviado para: {payment_context['customer_email']}")
    else:
        print(f"✗ Falha no passo: {execution.failed_step}")
        print(f"Reembolso processado: {execution.compensation_performed}")
