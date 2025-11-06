"""
Webhook API Endpoints
Handle webhooks from external services (SumUp, etc.)
"""

from fastapi import APIRouter, Request, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.models.transaction import Transaction, PaymentMethod
from app.services.payment.sumup_service import SumUpService
from app.services.tse.tasks import sign_transaction_async
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/sumup")
async def sumup_webhook(
    request: Request,
    x_sumup_signature: str = Header(None),
):
    """
    SumUp payment webhook endpoint.

    Receives notifications from SumUp when payments are completed.

    Flow:
    1. Verify webhook signature
    2. Find transaction by payment_reference
    3. Update transaction status
    4. Trigger TSE signature
    5. Return 200 OK

    SumUp requires a 200 OK response within 10 seconds.
    """
    # Get raw body for signature verification
    body = await request.body()
    body_str = body.decode('utf-8')

    # Verify signature
    if not x_sumup_signature or not settings.SUMUP_WEBHOOK_SECRET:
        logger.warning("sumup_webhook_missing_signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid signature"
        )

    # TODO: Get tenant-specific SumUp service
    # For now, use global config
    sumup = SumUpService(
        merchant_code="MERCHANT",  # Should come from tenant config
        api_key=settings.SUMUP_CLIENT_ID or ""
    )

    if not sumup.verify_webhook_signature(body_str, x_sumup_signature):
        logger.error("sumup_webhook_invalid_signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )

    # Parse webhook payload
    import json
    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError:
        logger.error("sumup_webhook_invalid_json")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )

    # Extract event data
    event_type = payload.get('event_type')
    event_data = payload.get('data', {})

    logger.info(
        "sumup_webhook_received",
        event_type=event_type,
        checkout_id=event_data.get('id'),
    )

    # Handle different event types
    if event_type == 'PAYMENT_SUCCESSFUL':
        await handle_successful_payment(event_data)
    elif event_type == 'PAYMENT_FAILED':
        await handle_failed_payment(event_data)
    elif event_type == 'REFUND_SUCCESSFUL':
        await handle_successful_refund(event_data)
    else:
        logger.warning("sumup_webhook_unknown_event", event_type=event_type)

    return {"status": "ok"}


async def handle_successful_payment(event_data: dict):
    """Handle successful payment webhook."""
    checkout_id = event_data.get('id')
    checkout_reference = event_data.get('checkout_reference')
    amount = event_data.get('amount')
    status_val = event_data.get('status')

    logger.info(
        "sumup_payment_successful",
        checkout_id=checkout_id,
        reference=checkout_reference,
        amount=amount,
    )

    # Find transaction by payment_reference
    # TODO: Get database session and find transaction
    # Update transaction with SumUp payment ID
    # Trigger TSE signature if not already signed

    # This is a placeholder - needs proper database integration
    logger.info("sumup_payment_processed", checkout_id=checkout_id)


async def handle_failed_payment(event_data: dict):
    """Handle failed payment webhook."""
    checkout_id = event_data.get('id')
    checkout_reference = event_data.get('checkout_reference')

    logger.warning(
        "sumup_payment_failed",
        checkout_id=checkout_id,
        reference=checkout_reference,
    )

    # Find transaction and mark as failed
    # Restore inventory if needed


async def handle_successful_refund(event_data: dict):
    """Handle successful refund webhook."""
    transaction_id = event_data.get('transaction_id')
    amount = event_data.get('amount')

    logger.info(
        "sumup_refund_successful",
        transaction_id=transaction_id,
        amount=amount,
    )

    # Find transaction and create refund record
    # Update transaction status
    # Restore inventory if applicable


@router.get("/sumup/test")
async def test_sumup_webhook():
    """
    Test endpoint to verify webhook setup.

    Returns basic information about webhook configuration.
    """
    return {
        "status": "ok",
        "webhook_url": "/api/v1/webhooks/sumup",
        "configured": settings.SUMUP_WEBHOOK_SECRET is not None,
    }
