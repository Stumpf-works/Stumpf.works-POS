"""
Tests for Transaction Endpoints
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.product import Product


@pytest.mark.asyncio
class TestTransactions:
    """Test transaction management endpoints."""

    async def test_create_transaction(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test creating a new transaction."""
        response = await client.post(
            "/api/v1/transactions",
            json={
                "items": [
                    {
                        "product_id": test_product.id,
                        "quantity": 2,
                    }
                ],
                "payment_method": "cash",
                "amount_paid": 25.00,
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert "receipt_number" in data
        assert data["status"] == "completed"
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == test_product.id
        assert data["items"][0]["quantity"] == 2
        assert data["payment_method"] == "cash"
        assert data["total"] > 0

    async def test_create_transaction_insufficient_stock(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test creating transaction with insufficient stock."""
        response = await client.post(
            "/api/v1/transactions",
            json={
                "items": [
                    {
                        "product_id": test_product.id,
                        "quantity": 999999,  # More than available
                    }
                ],
                "payment_method": "cash",
                "amount_paid": 100.00,
            },
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "insufficient" in response.json()["detail"].lower()

    async def test_create_transaction_nonexistent_product(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating transaction with non-existent product."""
        response = await client.post(
            "/api/v1/transactions",
            json={
                "items": [
                    {
                        "product_id": 99999,
                        "quantity": 1,
                    }
                ],
                "payment_method": "cash",
                "amount_paid": 10.00,
            },
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_create_transaction_multiple_items(
        self,
        client: AsyncClient,
        test_product: Product,
        db_session: AsyncSession,
        test_tenant: Tenant,
        test_category,
        auth_headers: dict
    ):
        """Test creating transaction with multiple items."""
        # Create another product
        from app.models.product import Product as ProductModel
        product2 = ProductModel(
            tenant_id=test_tenant.slug,
            name="Product 2",
            sku="TEST-002",
            price=15.99,
            vat_rate=19.0,
            category_id=test_category.id,
            stock_quantity=50,
            is_active=True,
        )
        db_session.add(product2)
        await db_session.commit()
        await db_session.refresh(product2)

        response = await client.post(
            "/api/v1/transactions",
            json={
                "items": [
                    {
                        "product_id": test_product.id,
                        "quantity": 2,
                    },
                    {
                        "product_id": product2.id,
                        "quantity": 1,
                    },
                ],
                "payment_method": "card",
                "amount_paid": 50.00,
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["items"]) == 2
        assert data["payment_method"] == "card"

    async def test_list_transactions(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test listing transactions."""
        # Create a transaction first
        await client.post(
            "/api/v1/transactions",
            json={
                "items": [{"product_id": test_product.id, "quantity": 1}],
                "payment_method": "cash",
                "amount_paid": 15.00,
            },
            headers=auth_headers
        )

        response = await client.get(
            "/api/v1/transactions",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_transaction_by_id(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test getting transaction by ID."""
        # Create a transaction
        create_response = await client.post(
            "/api/v1/transactions",
            json={
                "items": [{"product_id": test_product.id, "quantity": 1}],
                "payment_method": "cash",
                "amount_paid": 15.00,
            },
            headers=auth_headers
        )
        transaction_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/transactions/{transaction_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction_id

    async def test_get_transaction_receipt(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test getting transaction receipt."""
        # Create a transaction
        create_response = await client.post(
            "/api/v1/transactions",
            json={
                "items": [{"product_id": test_product.id, "quantity": 1}],
                "payment_method": "cash",
                "amount_paid": 15.00,
            },
            headers=auth_headers
        )
        receipt_number = create_response.json()["receipt_number"]

        response = await client.get(
            f"/api/v1/transactions/receipt/{receipt_number}",
            headers=auth_headers
        )

        assert response.status_code == 200
        # Receipt endpoint should return formatted receipt

    async def test_transaction_updates_stock(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test that transaction reduces stock quantity."""
        initial_stock = test_product.stock_quantity

        await client.post(
            "/api/v1/transactions",
            json={
                "items": [{"product_id": test_product.id, "quantity": 5}],
                "payment_method": "cash",
                "amount_paid": 100.00,
            },
            headers=auth_headers
        )

        # Refresh product to get updated stock
        await db_session.refresh(test_product)
        assert test_product.stock_quantity == initial_stock - 5

    async def test_transaction_calculates_vat_correctly(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test that VAT is calculated correctly."""
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
        data = response.json()

        # Check VAT calculation
        item = data["items"][0]
        expected_vat = item["unit_price"] * item["quantity"] * (test_product.vat_rate / 100)
        assert abs(item["vat_amount"] - expected_vat) < 0.01

    async def test_cashier_can_create_transaction(
        self,
        client: AsyncClient,
        test_product: Product,
        cashier_auth_headers: dict
    ):
        """Test that cashier can create transactions."""
        response = await client.post(
            "/api/v1/transactions",
            json={
                "items": [{"product_id": test_product.id, "quantity": 1}],
                "payment_method": "cash",
                "amount_paid": 15.00,
            },
            headers=cashier_auth_headers
        )

        assert response.status_code == 201

    async def test_transaction_with_sumup_payment(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test creating transaction with SumUp payment."""
        response = await client.post(
            "/api/v1/transactions",
            json={
                "items": [{"product_id": test_product.id, "quantity": 1}],
                "payment_method": "sumup",
                "sumup_checkout_id": "test-checkout-id",
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["payment_method"] == "sumup"
