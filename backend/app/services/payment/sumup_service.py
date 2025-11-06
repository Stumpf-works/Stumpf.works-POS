"""
SumUp Payment Integration
Handles payment processing via SumUp API
"""

import httpx
from typing import Optional, Dict, Any
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class SumUpService:
    """
    Service for SumUp payment processing.

    Handles:
    - Payment checkout creation
    - Payment status checking
    - Webhook verification
    - Refunds
    """

    def __init__(self, merchant_code: str, api_key: str):
        self.api_url = settings.SUMUP_API_URL
        self.merchant_code = merchant_code
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def create_checkout(
        self,
        amount: float,
        currency: str = "EUR",
        reference: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a payment checkout.

        Args:
            amount: Payment amount
            currency: Currency code (default: EUR)
            reference: Internal reference (e.g., receipt number)
            description: Payment description

        Returns:
            Checkout data including checkout_id and payment URL
        """
        try:
            response = await self.client.post(
                "/checkouts",
                json={
                    "checkout_reference": reference,
                    "amount": amount,
                    "currency": currency,
                    "merchant_code": self.merchant_code,
                    "description": description,
                }
            )
            response.raise_for_status()
            data = response.json()

            logger.info(
                "sumup_checkout_created",
                checkout_id=data.get("id"),
                amount=amount,
                reference=reference,
            )

            return data

        except Exception as e:
            logger.exception("sumup_checkout_error", error=str(e))
            raise

    async def get_checkout_status(self, checkout_id: str) -> Dict[str, Any]:
        """
        Get checkout status.

        Args:
            checkout_id: Checkout ID

        Returns:
            Checkout status data
        """
        try:
            response = await self.client.get(f"/checkouts/{checkout_id}")
            response.raise_for_status()
            data = response.json()

            logger.info("sumup_checkout_status", checkout_id=checkout_id, status=data.get("status"))
            return data

        except Exception as e:
            logger.exception("sumup_status_error", checkout_id=checkout_id, error=str(e))
            raise

    async def create_refund(
        self,
        transaction_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create a refund for a transaction.

        Args:
            transaction_id: SumUp transaction ID
            amount: Refund amount (None for full refund)

        Returns:
            Refund data
        """
        try:
            payload = {}
            if amount is not None:
                payload["amount"] = amount

            response = await self.client.post(
                f"/transactions/{transaction_id}/refund",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            logger.info("sumup_refund_created", transaction_id=transaction_id, amount=amount)
            return data

        except Exception as e:
            logger.exception("sumup_refund_error", transaction_id=transaction_id, error=str(e))
            raise

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify SumUp webhook signature.

        Args:
            payload: Webhook payload as string
            signature: Signature from X-Sumup-Signature header

        Returns:
            True if signature is valid
        """
        import hmac
        import hashlib

        expected_signature = hmac.new(
            settings.SUMUP_WEBHOOK_SECRET.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
