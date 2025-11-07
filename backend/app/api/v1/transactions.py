"""
Transaction API Endpoints
POS checkout, transaction management, and reporting
"""

from datetime import datetime
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_cashier
from app.core.config import settings
from app.core.database import get_db
from app.models.product import Product
from app.models.transaction import (PaymentMethod, Transaction,
                                    TransactionItem, TransactionStatus)
from app.models.user import User
from app.schemas.base import MessageResponse
from app.schemas.transaction import (TransactionCreate,
                                     TransactionListResponse,
                                     TransactionResponse,
                                     TransactionSearchParams, TransactionStats)
from app.services.tse.tasks import sign_transaction_async
from app.utils.helpers import generate_receipt_number

logger = structlog.get_logger()
router = APIRouter(prefix="/transactions", tags=["Transactions"])


async def calculate_transaction_totals(
    items_data: list, discount_amount: float, db: AsyncSession, tenant_id: str
) -> dict:
    """
    Calculate transaction totals from items.

    Returns dict with:
    - items: List of item data with prices
    - subtotal: Total before tax
    - tax_amount: Total tax
    - total: Final total
    """
    items = []
    subtotal_before_discount = 0.0
    total_tax = 0.0

    for item_data in items_data:
        # Get product
        result = await db.execute(
            select(Product).where(
                Product.id == item_data.product_id, Product.tenant_id == tenant_id
            )
        )
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item_data.product_id} not found",
            )

        if not product.is_available or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is not available",
            )

        # Check stock
        if product.track_inventory and product.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock for '{product.name}'. "
                    f"Available: {product.stock_quantity}"
                ),
            )

        # Calculate item totals
        unit_price = product.price
        quantity = item_data.quantity
        vat_rate = float(product.vat_rate.value)

        # Item subtotal (gross)
        item_subtotal = unit_price * quantity

        # Apply item-level discount if any
        item_discount = (
            item_data.discount_amount if hasattr(item_data, "discount_amount") else 0.0
        )
        item_subtotal_after_discount = max(0, item_subtotal - item_discount)

        # Calculate net and tax
        item_net = round(item_subtotal_after_discount / (1 + vat_rate), 2)
        item_tax = round(item_subtotal_after_discount - item_net, 2)

        subtotal_before_discount += item_subtotal_after_discount
        total_tax += item_tax

        items.append(
            {
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "vat_rate": vat_rate,
                "subtotal": item_subtotal_after_discount,
                "tax_amount": item_tax,
                "total": item_subtotal_after_discount,
                "discount_amount": item_discount,
            }
        )

    # Apply transaction-level discount proportionally
    if discount_amount > 0:
        # Distribute discount proportionally across items
        for item in items:
            if subtotal_before_discount > 0:
                item_discount_ratio = item["subtotal"] / subtotal_before_discount
                item_discount = round(discount_amount * item_discount_ratio, 2)

                item["discount_amount"] += item_discount
                item["subtotal"] = max(0, item["subtotal"] - item_discount)

                # Recalculate tax for this item
                vat_rate = item["vat_rate"]
                item_net = round(item["subtotal"] / (1 + vat_rate), 2)
                item_tax = round(item["subtotal"] - item_net, 2)

                item["tax_amount"] = item_tax
                item["total"] = item["subtotal"]

    # Recalculate totals
    final_subtotal = sum(item["subtotal"] for item in items)
    final_tax = sum(item["tax_amount"] for item in items)
    final_total = sum(item["total"] for item in items)

    return {
        "items": items,
        "subtotal": round(final_subtotal, 2),
        "tax_amount": round(final_tax, 2),
        "total": round(final_total, 2),
    }


@router.post(
    "", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(require_cashier),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new transaction (checkout).

    This creates a sale transaction with all items and processes payment.
    For cash payments, calculates change.
    """

    # Calculate totals
    calc_result = await calculate_transaction_totals(
        transaction_data.items,
        transaction_data.discount_amount,
        db,
        current_user.tenant_id,
    )

    # Validate cash payment
    if transaction_data.payment_method == PaymentMethod.CASH:
        if transaction_data.cash_given is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cash amount is required for cash payments",
            )
        if transaction_data.cash_given < calc_result["total"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient cash. Total: €{calc_result['total']:.2f}, "
                    f"Given: €{transaction_data.cash_given:.2f}"
                ),
            )

    # Calculate change
    cash_change = None
    if (
        transaction_data.payment_method == PaymentMethod.CASH
        and transaction_data.cash_given
    ):
        cash_change = round(transaction_data.cash_given - calc_result["total"], 2)

    # Generate receipt number
    receipt_number = generate_receipt_number()

    # Create transaction
    transaction = Transaction(
        receipt_number=receipt_number,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        status=TransactionStatus.COMPLETED,
        subtotal=calc_result["subtotal"],
        tax_amount=calc_result["tax_amount"],
        total=calc_result["total"],
        discount_amount=transaction_data.discount_amount,
        payment_method=transaction_data.payment_method,
        cash_given=transaction_data.cash_given,
        cash_change=cash_change,
        customer_name=transaction_data.customer_name,
        customer_email=transaction_data.customer_email,
        notes=transaction_data.notes,
        completed_at=datetime.utcnow(),
    )

    db.add(transaction)
    await db.flush()  # Get transaction ID

    # Create transaction items and update stock
    for item_data in calc_result["items"]:
        product = item_data["product"]

        transaction_item = TransactionItem(
            transaction_id=transaction.id,
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            vat_rate=item_data["vat_rate"],
            subtotal=item_data["subtotal"],
            tax_amount=item_data["tax_amount"],
            total=item_data["total"],
            discount_amount=item_data["discount_amount"],
        )

        db.add(transaction_item)

        # Update stock
        if product.track_inventory:
            product.stock_quantity -= item_data["quantity"]

    await db.commit()
    await db.refresh(transaction)

    logger.info(
        "transaction_created",
        transaction_id=transaction.id,
        receipt_number=receipt_number,
        total=calc_result["total"],
        payment_method=transaction_data.payment_method.value,
        user_id=current_user.id,
    )

    # Trigger TSE signature task asynchronously
    if settings.TSE_ENABLED:
        sign_transaction_async.delay(transaction.id, current_user.tenant_id)
        logger.info("tse_signing_task_queued", transaction_id=transaction.id)

    return transaction


@router.get("", response_model=List[TransactionListResponse])
async def list_transactions(
    receipt_number: Optional[str] = None,
    user_id: Optional[int] = None,
    status: Optional[TransactionStatus] = None,
    payment_method: Optional[PaymentMethod] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List transactions with filters."""

    query = select(Transaction).where(Transaction.tenant_id == current_user.tenant_id)

    # Filters
    if receipt_number:
        query = query.where(Transaction.receipt_number.ilike(f"%{receipt_number}%"))

    if user_id is not None:
        query = query.where(Transaction.user_id == user_id)

    if status is not None:
        query = query.where(Transaction.status == status)

    if payment_method is not None:
        query = query.where(Transaction.payment_method == payment_method)

    if date_from:
        query = query.where(Transaction.completed_at >= date_from)

    if date_to:
        query = query.where(Transaction.completed_at <= date_to)

    # Pagination and ordering
    query = query.order_by(Transaction.created_at.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    transactions = result.scalars().all()

    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific transaction with all items."""

    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.tenant_id == current_user.tenant_id,
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    return transaction


@router.post("/{transaction_id}/cancel", response_model=TransactionResponse)
async def cancel_transaction(
    transaction_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(require_cashier),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a transaction and restore stock."""

    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.tenant_id == current_user.tenant_id,
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    if transaction.status == TransactionStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction is already cancelled",
        )

    if transaction.is_tse_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel TSE-signed transaction. Create a refund instead.",
        )

    # Restore stock
    for item in transaction.items:
        result = await db.execute(
            select(Product).where(
                Product.id == item.product_id,
                Product.tenant_id == current_user.tenant_id,
            )
        )
        product = result.scalar_one_or_none()

        if product and product.track_inventory:
            product.stock_quantity += item.quantity

    # Update transaction
    transaction.status = TransactionStatus.CANCELLED
    transaction.cancelled_at = datetime.utcnow()
    if reason:
        transaction.notes = f"{transaction.notes or ''}\nCancelled: {reason}".strip()

    await db.commit()
    await db.refresh(transaction)

    logger.info(
        "transaction_cancelled",
        transaction_id=transaction.id,
        receipt_number=transaction.receipt_number,
        reason=reason,
    )

    return transaction


@router.get("/stats/summary", response_model=TransactionStats)
async def get_transaction_stats(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get transaction statistics for reporting."""

    query = select(Transaction).where(
        Transaction.tenant_id == current_user.tenant_id,
        Transaction.status == TransactionStatus.COMPLETED,
    )

    if date_from:
        query = query.where(Transaction.completed_at >= date_from)

    if date_to:
        query = query.where(Transaction.completed_at <= date_to)

    result = await db.execute(query)
    transactions = result.scalars().all()

    # Calculate stats
    total_transactions = len(transactions)
    total_revenue = sum(t.total for t in transactions)
    total_tax = sum(t.tax_amount for t in transactions)
    avg_value = total_revenue / total_transactions if total_transactions > 0 else 0

    # Payment methods breakdown
    payment_methods = {}
    for t in transactions:
        method = t.payment_method.value
        payment_methods[method] = payment_methods.get(method, 0) + 1

    # Status breakdown
    status_breakdown = {}
    for t in transactions:
        status_val = t.status.value
        status_breakdown[status_val] = status_breakdown.get(status_val, 0) + 1

    return TransactionStats(
        total_transactions=total_transactions,
        total_revenue=round(total_revenue, 2),
        total_tax=round(total_tax, 2),
        avg_transaction_value=round(avg_value, 2),
        payment_methods=payment_methods,
        status_breakdown=status_breakdown,
    )
