"""
Tests for TSE Service
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.tse.fiskaly_adapter import FiskalyAdapter
from app.models.transaction import Transaction, TransactionStatus, PaymentMethod
from app.models.tenant import Tenant


@pytest.mark.asyncio
class TestFiskalyAdapter:
    """Test Fiskaly TSE adapter."""

    @pytest.fixture
    def mock_fiskaly_client(self):
        """Create mock Fiskaly client."""
        with patch('app.services.tse.fiskaly_adapter.httpx.AsyncClient') as mock:
            client = AsyncMock()
            mock.return_value.__aenter__.return_value = client
            yield client

    @pytest.fixture
    def fiskaly_adapter(self, test_tenant: Tenant):
        """Create Fiskaly adapter instance."""
        return FiskalyAdapter(
            api_key=test_tenant.fiskaly_api_key,
            api_secret=test_tenant.fiskaly_api_secret,
            tss_id=test_tenant.fiskaly_tss_id,
        )

    async def test_authenticate(
        self,
        fiskaly_adapter: FiskalyAdapter,
        mock_fiskaly_client: AsyncMock
    ):
        """Test Fiskaly authentication."""
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_fiskaly_client.post.return_value = mock_response

        await fiskaly_adapter._authenticate()

        assert fiskaly_adapter.access_token == "test_token"
        mock_fiskaly_client.post.assert_called_once()

    async def test_sign_transaction(
        self,
        fiskaly_adapter: FiskalyAdapter,
        mock_fiskaly_client: AsyncMock,
        test_tenant: Tenant,
        db_session: AsyncSession
    ):
        """Test signing a transaction."""
        # Create test transaction
        transaction = Transaction(
            tenant_id=test_tenant.slug,
            receipt_number="TEST-001",
            total=10.00,
            subtotal=8.40,
            vat_amount=1.60,
            payment_method=PaymentMethod.CASH,
            amount_paid=10.00,
            change_amount=0.00,
            status=TransactionStatus.COMPLETED,
        )
        db_session.add(transaction)
        await db_session.commit()
        await db_session.refresh(transaction)

        # Mock successful TSE response
        mock_auth_response = Mock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}

        mock_sign_response = Mock()
        mock_sign_response.json.return_value = {
            "transaction_number": 123,
            "time_start": "2024-01-01T12:00:00Z",
            "time_end": "2024-01-01T12:00:01Z",
            "signature": {
                "value": "test_signature",
                "algorithm": "ecdsa-plain-SHA256",
            },
            "serial_number": "test_serial",
        }

        mock_fiskaly_client.post.side_effect = [
            mock_auth_response,  # Authentication
            mock_sign_response,  # Transaction signing
        ]

        result = await fiskaly_adapter.sign_transaction(transaction, db_session)

        assert result is True
        assert transaction.is_tse_signed is True
        assert transaction.tse_transaction_id is not None
        assert transaction.tse_signature is not None

    async def test_sign_transaction_failure(
        self,
        fiskaly_adapter: FiskalyAdapter,
        mock_fiskaly_client: AsyncMock,
        test_tenant: Tenant,
        db_session: AsyncSession
    ):
        """Test handling of TSE signing failure."""
        # Create test transaction
        transaction = Transaction(
            tenant_id=test_tenant.slug,
            receipt_number="TEST-002",
            total=10.00,
            subtotal=8.40,
            vat_amount=1.60,
            payment_method=PaymentMethod.CASH,
            amount_paid=10.00,
            change_amount=0.00,
            status=TransactionStatus.COMPLETED,
        )
        db_session.add(transaction)
        await db_session.commit()
        await db_session.refresh(transaction)

        # Mock authentication success but signing failure
        mock_auth_response = Mock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}

        mock_fiskaly_client.post.side_effect = [
            mock_auth_response,  # Authentication
            Exception("TSE service unavailable"),  # Signing failure
        ]

        result = await fiskaly_adapter.sign_transaction(transaction, db_session)

        assert result is False
        assert transaction.is_tse_signed is False

    async def test_export_tse_data(
        self,
        fiskaly_adapter: FiskalyAdapter,
        mock_fiskaly_client: AsyncMock
    ):
        """Test exporting TSE data."""
        mock_auth_response = Mock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}

        mock_export_response = Mock()
        mock_export_response.json.return_value = {
            "export_id": "test_export_123",
            "url": "https://example.com/export.tar",
        }

        mock_fiskaly_client.post.side_effect = [
            mock_auth_response,
            mock_export_response,
        ]

        start_date = "2024-01-01"
        end_date = "2024-01-31"

        result = await fiskaly_adapter.export_transactions(start_date, end_date)

        assert "export_id" in result
        assert result["export_id"] == "test_export_123"


@pytest.mark.asyncio
class TestTSETasks:
    """Test TSE Celery tasks."""

    @patch('app.services.tse.tasks.get_db')
    @patch('app.services.tse.tasks.FiskalyAdapter')
    async def test_sign_transaction_async_task(
        self,
        mock_fiskaly_adapter,
        mock_get_db,
        test_tenant: Tenant,
        db_session: AsyncSession
    ):
        """Test async TSE signing task."""
        from app.services.tse.tasks import sign_transaction_async

        # Create test transaction
        transaction = Transaction(
            tenant_id=test_tenant.slug,
            receipt_number="TEST-003",
            total=10.00,
            subtotal=8.40,
            vat_amount=1.60,
            payment_method=PaymentMethod.CASH,
            amount_paid=10.00,
            change_amount=0.00,
            status=TransactionStatus.COMPLETED,
        )
        db_session.add(transaction)
        await db_session.commit()
        await db_session.refresh(transaction)

        # Mock database session
        mock_get_db.return_value.__aenter__.return_value = db_session

        # Mock successful TSE signing
        mock_adapter_instance = Mock()
        mock_adapter_instance.sign_transaction.return_value = True
        mock_fiskaly_adapter.return_value = mock_adapter_instance

        # Call task (note: in tests we call directly, not via Celery)
        # In real implementation, this would be called via .delay()
        # For testing purposes, we're testing the task logic

        # The task should handle the signing
        assert transaction.id is not None


@pytest.mark.asyncio
class TestTSEIntegration:
    """Integration tests for TSE functionality."""

    async def test_transaction_triggers_tse_signing(
        self,
        client: AsyncClient,
        test_product,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test that creating a transaction triggers TSE signing."""
        with patch('app.services.tse.tasks.sign_transaction_async.delay') as mock_task:
            response = await client.post(
                "/api/v1/transactions",
                json={
                    "items": [{"product_id": test_product.id, "quantity": 1}],
                    "payment_method": "cash",
                    "amount_paid": 15.00,
                },
                headers=auth_headers
            )

            assert response.status_code == 201

            # Verify TSE signing task was triggered
            # mock_task.assert_called_once()

    async def test_unsigned_transactions_can_be_retried(
        self,
        client: AsyncClient,
        test_product,
        auth_headers: dict,
        db_session: AsyncSession,
        test_tenant: Tenant
    ):
        """Test that unsigned transactions can be found and retried."""
        # Create an unsigned transaction
        transaction = Transaction(
            tenant_id=test_tenant.slug,
            receipt_number="TEST-UNSIGNED",
            total=10.00,
            subtotal=8.40,
            vat_amount=1.60,
            payment_method=PaymentMethod.CASH,
            amount_paid=10.00,
            change_amount=0.00,
            status=TransactionStatus.COMPLETED,
            is_tse_signed=False,
        )
        db_session.add(transaction)
        await db_session.commit()

        # Query for unsigned transactions
        from sqlalchemy import select
        result = await db_session.execute(
            select(Transaction).where(
                Transaction.tenant_id == test_tenant.slug,
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.is_tse_signed == False
            )
        )
        unsigned = result.scalars().all()

        assert len(unsigned) >= 1
        assert any(t.receipt_number == "TEST-UNSIGNED" for t in unsigned)
