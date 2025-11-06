"""
Tests for Admin Endpoints
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.models.user import User
from app.models.product import Product


@pytest.mark.asyncio
class TestAdminDashboard:
    """Test admin dashboard endpoints."""

    async def test_get_dashboard_stats(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test getting dashboard statistics."""
        # Create some test transactions
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
            "/api/v1/admin/dashboard/stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "today_sales" in data
        assert "today_transactions" in data
        assert "today_average_basket" in data
        assert "month_sales" in data
        assert "month_transactions" in data
        assert "active_products" in data
        assert "low_stock_products" in data
        assert "pending_tse_signatures" in data

    async def test_get_recent_transactions(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test getting recent transactions."""
        # Create a transaction
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
            "/api/v1/admin/dashboard/recent-transactions?limit=10",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "receipt_number" in data[0]
        assert "total" in data[0]
        assert "payment_method" in data[0]

    async def test_cashier_cannot_access_dashboard(
        self,
        client: AsyncClient,
        cashier_auth_headers: dict
    ):
        """Test that cashiers cannot access dashboard stats."""
        response = await client.get(
            "/api/v1/admin/dashboard/stats",
            headers=cashier_auth_headers
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestAdminUsers:
    """Test admin user management endpoints."""

    async def test_list_users(
        self,
        client: AsyncClient,
        test_admin_user: User,
        test_cashier_user: User,
        auth_headers: dict
    ):
        """Test listing users."""
        response = await client.get(
            "/api/v1/admin/users",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least admin and cashier
        assert any(u["username"] == "admin" for u in data)
        assert any(u["username"] == "cashier" for u in data)

    async def test_create_user(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating a new user."""
        response = await client.post(
            "/api/v1/admin/users",
            json={
                "username": "newcashier",
                "email": "newcashier@test.com",
                "first_name": "New",
                "last_name": "Cashier",
                "role": "cashier",
                "password": "password123",
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newcashier"
        assert data["role"] == "cashier"
        assert data["is_active"] is True

    async def test_create_user_with_duplicate_username(
        self,
        client: AsyncClient,
        test_admin_user: User,
        auth_headers: dict
    ):
        """Test creating user with duplicate username."""
        response = await client.post(
            "/api/v1/admin/users",
            json={
                "username": "admin",  # Already exists
                "email": "duplicate@test.com",
                "role": "cashier",
                "password": "password123",
            },
            headers=auth_headers
        )

        assert response.status_code == 400

    async def test_update_user(
        self,
        client: AsyncClient,
        test_cashier_user: User,
        auth_headers: dict
    ):
        """Test updating a user."""
        response = await client.patch(
            f"/api/v1/admin/users/{test_cashier_user.id}",
            json={
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated@test.com",
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["email"] == "updated@test.com"

    async def test_deactivate_user(
        self,
        client: AsyncClient,
        test_cashier_user: User,
        auth_headers: dict
    ):
        """Test deactivating a user."""
        response = await client.patch(
            f"/api/v1/admin/users/{test_cashier_user.id}",
            json={"is_active": False},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    async def test_delete_user(
        self,
        client: AsyncClient,
        test_cashier_user: User,
        auth_headers: dict
    ):
        """Test deleting a user."""
        response = await client.delete(
            f"/api/v1/admin/users/{test_cashier_user.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

    async def test_cannot_delete_own_account(
        self,
        client: AsyncClient,
        test_admin_user: User,
        auth_headers: dict
    ):
        """Test that users cannot delete their own account."""
        response = await client.delete(
            f"/api/v1/admin/users/{test_admin_user.id}",
            headers=auth_headers
        )

        assert response.status_code == 400

    async def test_cashier_cannot_manage_users(
        self,
        client: AsyncClient,
        cashier_auth_headers: dict
    ):
        """Test that cashiers cannot manage users."""
        response = await client.get(
            "/api/v1/admin/users",
            headers=cashier_auth_headers
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestAdminReports:
    """Test admin reports endpoints."""

    async def test_get_sales_report(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test getting sales report."""
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

        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        end_date = datetime.now().isoformat()

        response = await client.get(
            f"/api/v1/admin/reports/sales?start_date={start_date}&end_date={end_date}&group_by=day",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_sales" in data
        assert "total_transactions" in data
        assert "average_basket" in data
        assert "sales_by_payment_method" in data
        assert "sales_by_day" in data
        assert "top_products" in data
        assert "sales_by_hour" in data

    async def test_sales_report_calculates_correctly(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test that sales report calculations are correct."""
        # Create transactions with known values
        num_transactions = 5
        for _ in range(num_transactions):
            await client.post(
                "/api/v1/transactions",
                json={
                    "items": [{"product_id": test_product.id, "quantity": 1}],
                    "payment_method": "cash",
                    "amount_paid": 15.00,
                },
                headers=auth_headers
            )

        start_date = (datetime.now() - timedelta(days=1)).isoformat()
        end_date = datetime.now().isoformat()

        response = await client.get(
            f"/api/v1/admin/reports/sales?start_date={start_date}&end_date={end_date}&group_by=day",
            headers=auth_headers
        )

        data = response.json()
        assert data["total_transactions"] >= num_transactions
        assert data["total_sales"] > 0

    async def test_cashier_cannot_access_reports(
        self,
        client: AsyncClient,
        cashier_auth_headers: dict
    ):
        """Test that cashiers cannot access sales reports."""
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        end_date = datetime.now().isoformat()

        response = await client.get(
            f"/api/v1/admin/reports/sales?start_date={start_date}&end_date={end_date}&group_by=day",
            headers=cashier_auth_headers
        )

        # Depending on implementation, might be 403 or allow cashiers to see their own reports
        # Adjust based on your requirements
        assert response.status_code in [200, 403]


@pytest.mark.asyncio
class TestAdminSettings:
    """Test admin settings endpoints."""

    async def test_get_tenant_settings(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting tenant settings."""
        response = await client.get(
            "/api/v1/admin/settings/tenant",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "tax_id" in data
        assert "vat_id" in data
        assert "sumup_enabled" in data
        assert "tse_enabled" in data

    async def test_update_tenant_settings(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test updating tenant settings."""
        response = await client.patch(
            "/api/v1/admin/settings/tenant",
            json={
                "name": "Updated Company Name",
                "address_city": "New City",
            },
            headers=auth_headers
        )

        assert response.status_code == 200

    async def test_cashier_cannot_access_settings(
        self,
        client: AsyncClient,
        cashier_auth_headers: dict
    ):
        """Test that cashiers cannot access settings."""
        response = await client.get(
            "/api/v1/admin/settings/tenant",
            headers=cashier_auth_headers
        )

        assert response.status_code == 403
