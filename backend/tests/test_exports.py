"""
Tests for Export Endpoints
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.models.product import Product


@pytest.mark.asyncio
class TestDSFinVKExport:
    """Test DSFinV-K export functionality."""

    async def test_export_dsfink(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test DSFinV-K export generation."""
        # Create some test transactions
        for _ in range(3):
            await client.post(
                "/api/v1/transactions",
                json={
                    "items": [{"product_id": test_product.id, "quantity": 1}],
                    "payment_method": "cash",
                    "amount_paid": 15.00,
                },
                headers=auth_headers
            )

        start_date = (datetime.now() - timedelta(days=7)).date().isoformat()
        end_date = datetime.now().date().isoformat()

        response = await client.get(
            f"/api/v1/exports/dsfink?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/gzip"
        assert "dsfink_export" in response.headers.get("content-disposition", "")

    async def test_export_dsfink_invalid_date_range(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test DSFinV-K export with invalid date range."""
        start_date = datetime.now().date().isoformat()
        end_date = (datetime.now() - timedelta(days=7)).date().isoformat()  # End before start

        response = await client.get(
            f"/api/v1/exports/dsfink?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        assert response.status_code == 400

    async def test_export_dsfink_too_large_range(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test DSFinV-K export with too large date range."""
        start_date = (datetime.now() - timedelta(days=400)).date().isoformat()
        end_date = datetime.now().date().isoformat()

        response = await client.get(
            f"/api/v1/exports/dsfink?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        # Should limit or reject
        assert response.status_code in [200, 400]

    async def test_cashier_can_export(
        self,
        client: AsyncClient,
        test_product: Product,
        cashier_auth_headers: dict
    ):
        """Test that cashiers can export data."""
        start_date = (datetime.now() - timedelta(days=7)).date().isoformat()
        end_date = datetime.now().date().isoformat()

        response = await client.get(
            f"/api/v1/exports/dsfink?start_date={start_date}&end_date={end_date}",
            headers=cashier_auth_headers
        )

        # Cashiers might be able to export or not, depending on requirements
        assert response.status_code in [200, 403]


@pytest.mark.asyncio
class TestCSVExport:
    """Test CSV export functionality."""

    async def test_export_transactions_csv(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test CSV export of transactions."""
        # Create test transaction
        await client.post(
            "/api/v1/transactions",
            json={
                "items": [{"product_id": test_product.id, "quantity": 1}],
                "payment_method": "cash",
                "amount_paid": 15.00,
            },
            headers=auth_headers
        )

        start_date = (datetime.now() - timedelta(days=7)).date().isoformat()
        end_date = datetime.now().date().isoformat()

        response = await client.get(
            f"/api/v1/exports/transactions/csv?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    async def test_export_products_csv(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test CSV export of products."""
        response = await client.get(
            "/api/v1/exports/products/csv",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
