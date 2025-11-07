"""
Fiskaly Cloud-TSE Adapter
Handles TSE signature for transactions (KassenSichV compliance)
"""

from typing import Any, Dict, Optional

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class FiskalyAdapter:
    """
    Adapter for Fiskaly Cloud-TSE API.

    Handles:
    - TSE initialization
    - Transaction signing
    - Export data retrieval
    """

    def __init__(self, api_key: str, api_secret: str, tss_id: Optional[str] = None):
        self.api_url = settings.FISKALY_API_URL
        self.api_key = api_key
        self.api_secret = api_secret
        self.tss_id = tss_id
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def authenticate(self) -> str:
        """
        Authenticate with Fiskaly API and get access token.

        Returns access token for subsequent requests.
        """
        try:
            response = await self.client.post(
                "/auth",
                json={
                    "api_key": self.api_key,
                    "api_secret": self.api_secret,
                },
            )
            response.raise_for_status()
            data = response.json()

            logger.info("fiskaly_authenticated")
            return data.get("access_token")

        except Exception as e:
            logger.exception("fiskaly_auth_error", error=str(e))
            raise

    async def create_transaction(
        self, transaction_id: str, transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create and sign a transaction with TSE.

        Args:
            transaction_id: Unique transaction identifier
            transaction_data: Transaction details (amount, items, etc.)

        Returns:
            TSE signature data including:
            - transaction_number
            - signature_value
            - signature_counter
            - time_start
            - time_end
            - tss_serial_number
        """
        try:
            token = await self.authenticate()

            response = await self.client.put(
                f"/tss/{self.tss_id}/tx/{transaction_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "state": "FINISHED",
                    "client_id": transaction_data.get("client_id", "POS-1"),
                    "tx_data": transaction_data,
                },
            )
            response.raise_for_status()
            data = response.json()

            logger.info(
                "tse_transaction_signed",
                transaction_id=transaction_id,
                signature_counter=data.get("number"),
            )

            return {
                "transaction_number": data.get("number"),
                "signature_value": data.get("signature", {}).get("value"),
                "signature_counter": data.get("signature", {}).get("counter"),
                "time_start": data.get("time_start"),
                "time_end": data.get("time_end"),
                "tss_serial_number": data.get("tss_serial_number"),
            }

        except Exception as e:
            logger.exception(
                "tse_signing_error", transaction_id=transaction_id, error=str(e)
            )
            raise

    async def export_tar(self, start_date: str, end_date: str) -> bytes:
        """
        Export TSE data as TAR file (DSFinV-K format).

        Args:
            start_date: Start date (ISO 8601)
            end_date: End date (ISO 8601)

        Returns:
            TAR file content as bytes
        """
        try:
            token = await self.authenticate()

            response = await self.client.get(
                f"/tss/{self.tss_id}/export",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
            response.raise_for_status()

            logger.info(
                "tse_export_completed", start_date=start_date, end_date=end_date
            )
            return response.content

        except Exception as e:
            logger.exception("tse_export_error", error=str(e))
            raise

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
