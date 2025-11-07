"""
Celery Tasks for TSE Operations
Asynchronous TSE signature processing
"""

import structlog
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SyncSessionLocal, sync_engine
from app.models.tenant import Tenant
from app.models.transaction import Transaction, TransactionStatus
from app.services.tse.fiskaly_adapter import FiskalyAdapter

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sign_transaction_async(self, transaction_id: int, tenant_id: str):
    """
    Sign a transaction with TSE asynchronously.

    Args:
        transaction_id: Transaction ID to sign
        tenant_id: Tenant ID

    This task runs after a transaction is created and signs it with the TSE.
    If signing fails, it will retry up to 3 times.
    """
    logger.info(
        "tse_signing_task_started",
        transaction_id=transaction_id,
        tenant_id=tenant_id,
    )

    db = SyncSessionLocal()

    try:
        # Set search path to tenant schema
        db.execute(f'SET search_path TO "{tenant_id}", public')

        # Get transaction
        transaction = (
            db.query(Transaction).filter(Transaction.id == transaction_id).first()
        )

        if not transaction:
            logger.error("transaction_not_found", transaction_id=transaction_id)
            return {"success": False, "error": "Transaction not found"}

        # Check if already signed
        if transaction.is_tse_signed:
            logger.warning("transaction_already_signed", transaction_id=transaction_id)
            return {"success": True, "already_signed": True}

        # Get tenant configuration
        tenant = db.query(Tenant).filter(Tenant.slug == tenant_id).first()

        if not tenant:
            logger.error("tenant_not_found", tenant_id=tenant_id)
            return {"success": False, "error": "Tenant not found"}

        # Get Fiskaly credentials from tenant settings
        fiskaly_config = tenant.settings.get("fiskaly", {})
        api_key = fiskaly_config.get("api_key") or settings.FISKALY_API_KEY
        api_secret = fiskaly_config.get("api_secret") or settings.FISKALY_API_SECRET
        tss_id = fiskaly_config.get("tss_id")

        if not all([api_key, api_secret, tss_id]):
            logger.error("fiskaly_config_missing", tenant_id=tenant_id)
            return {"success": False, "error": "Fiskaly configuration missing"}

        # Initialize Fiskaly adapter
        fiskaly = FiskalyAdapter(api_key=api_key, api_secret=api_secret, tss_id=tss_id)

        # Prepare transaction data for TSE
        transaction_data = {
            "client_id": f"POS-{transaction.user_id}",
            "receipt_number": transaction.receipt_number,
            "total": float(transaction.total),
            "currency": "EUR",
            "items": [
                {
                    "name": item.product_name,
                    "quantity": item.quantity,
                    "price": float(item.unit_price),
                    "vat_rate": float(item.vat_rate),
                }
                for item in transaction.items
            ],
        }

        # Sign transaction with TSE
        import asyncio

        signature_data = asyncio.run(
            fiskaly.create_transaction(
                transaction_id=transaction.receipt_number,
                transaction_data=transaction_data,
            )
        )

        # Update transaction with signature data
        transaction.tse_transaction_id = str(signature_data.get("transaction_number"))
        transaction.tse_signature = signature_data.get("signature_value")
        transaction.tse_time_start = signature_data.get("time_start")
        transaction.tse_time_end = signature_data.get("time_end")
        transaction.tse_serial_number = signature_data.get("tss_serial_number")
        transaction.is_tse_signed = True

        db.commit()

        logger.info(
            "transaction_signed_successfully",
            transaction_id=transaction_id,
            receipt_number=transaction.receipt_number,
            signature_counter=signature_data.get("signature_counter"),
        )

        return {
            "success": True,
            "transaction_id": transaction_id,
            "receipt_number": transaction.receipt_number,
            "signature_data": signature_data,
        }

    except Exception as exc:
        logger.exception(
            "tse_signing_failed",
            transaction_id=transaction_id,
            error=str(exc),
        )

        # Retry the task
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(
                "tse_signing_max_retries_exceeded",
                transaction_id=transaction_id,
            )
            return {"success": False, "error": str(exc), "max_retries_exceeded": True}

    finally:
        db.close()


@shared_task
def sync_pending_signatures():
    """
    Periodic task to sync pending TSE signatures.

    This runs every minute (configured in celery_app.py)
    and attempts to sign any transactions that are completed but not yet signed.
    """
    logger.info("sync_pending_signatures_task_started")

    db = SyncSessionLocal()
    signed_count = 0

    try:
        # Get all tenants
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()

        for tenant in tenants:
            # Set search path to tenant schema
            db.execute(f'SET search_path TO "{tenant.schema_name}", public')

            # Get unsigned transactions
            unsigned_transactions = (
                db.query(Transaction)
                .filter(
                    Transaction.status == TransactionStatus.COMPLETED,
                    Transaction.is_tse_signed == False,
                )
                .limit(10)
                .all()
            )  # Process max 10 per tenant per run

            for transaction in unsigned_transactions:
                # Trigger signing task
                sign_transaction_async.delay(transaction.id, tenant.slug)
                signed_count += 1

                logger.info(
                    "unsigned_transaction_queued",
                    transaction_id=transaction.id,
                    tenant_id=tenant.slug,
                )

        logger.info("sync_pending_signatures_completed", signed_count=signed_count)
        return {"success": True, "queued_count": signed_count}

    except Exception as exc:
        logger.exception("sync_pending_signatures_error", error=str(exc))
        return {"success": False, "error": str(exc)}

    finally:
        db.close()
