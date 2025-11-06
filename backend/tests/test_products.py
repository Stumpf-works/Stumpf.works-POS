"""
Tests for Product Management Endpoints
"""

import pytest
from httpx import AsyncClient

from app.models.tenant import Tenant
from app.models.product import Product, Category


@pytest.mark.asyncio
class TestProducts:
    """Test product management endpoints."""

    async def test_create_product(
        self,
        client: AsyncClient,
        test_tenant: Tenant,
        test_category: Category,
        auth_headers: dict
    ):
        """Test creating a new product."""
        response = await client.post(
            "/api/v1/products",
            json={
                "name": "New Product",
                "description": "A new test product",
                "sku": "NEW-001",
                "barcode": "9876543210123",
                "price": 19.99,
                "vat_rate": 19.0,
                "category_id": test_category.id,
                "stock_quantity": 50,
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Product"
        assert data["sku"] == "NEW-001"
        assert data["price"] == 19.99
        assert data["stock_quantity"] == 50

    async def test_create_product_duplicate_sku(
        self,
        client: AsyncClient,
        test_product: Product,
        test_category: Category,
        auth_headers: dict
    ):
        """Test creating product with duplicate SKU."""
        response = await client.post(
            "/api/v1/products",
            json={
                "name": "Duplicate Product",
                "sku": test_product.sku,  # Duplicate
                "price": 9.99,
                "vat_rate": 19.0,
                "category_id": test_category.id,
            },
            headers=auth_headers
        )

        assert response.status_code == 400

    async def test_list_products(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test listing products."""
        response = await client.get(
            "/api/v1/products",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(p["id"] == test_product.id for p in data)

    async def test_get_product_by_id(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test getting product by ID."""
        response = await client.get(
            f"/api/v1/products/{test_product.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == test_product.name

    async def test_get_nonexistent_product(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting non-existent product."""
        response = await client.get(
            "/api/v1/products/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_update_product(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test updating a product."""
        response = await client.patch(
            f"/api/v1/products/{test_product.id}",
            json={
                "name": "Updated Product Name",
                "price": 14.99,
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product Name"
        assert data["price"] == 14.99

    async def test_delete_product(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test deleting a product."""
        response = await client.delete(
            f"/api/v1/products/{test_product.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = await client.get(
            f"/api/v1/products/{test_product.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    async def test_search_products(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test searching products."""
        response = await client.get(
            f"/api/v1/products?search={test_product.name[:4]}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(p["id"] == test_product.id for p in data)

    async def test_filter_products_by_category(
        self,
        client: AsyncClient,
        test_product: Product,
        test_category: Category,
        auth_headers: dict
    ):
        """Test filtering products by category."""
        response = await client.get(
            f"/api/v1/products?category_id={test_category.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(p["category_id"] == test_category.id for p in data)

    async def test_adjust_stock(
        self,
        client: AsyncClient,
        test_product: Product,
        auth_headers: dict
    ):
        """Test adjusting product stock."""
        initial_stock = test_product.stock_quantity

        response = await client.post(
            f"/api/v1/products/{test_product.id}/adjust-stock",
            json={
                "adjustment": 10,
                "reason": "Restock",
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stock_quantity"] == initial_stock + 10


@pytest.mark.asyncio
class TestCategories:
    """Test category management endpoints."""

    async def test_create_category(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating a new category."""
        response = await client.post(
            "/api/v1/categories",
            json={
                "name": "New Category",
                "description": "A new test category",
                "color": "#00FF00",
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Category"
        assert data["color"] == "#00FF00"

    async def test_list_categories(
        self,
        client: AsyncClient,
        test_category: Category,
        auth_headers: dict
    ):
        """Test listing categories."""
        response = await client.get(
            "/api/v1/categories",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(c["id"] == test_category.id for c in data)

    async def test_update_category(
        self,
        client: AsyncClient,
        test_category: Category,
        auth_headers: dict
    ):
        """Test updating a category."""
        response = await client.patch(
            f"/api/v1/categories/{test_category.id}",
            json={
                "name": "Updated Category",
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Category"

    async def test_delete_category(
        self,
        client: AsyncClient,
        test_category: Category,
        auth_headers: dict
    ):
        """Test deleting a category."""
        # First remove products from category
        response = await client.delete(
            f"/api/v1/categories/{test_category.id}",
            headers=auth_headers
        )

        # Should succeed if no products are linked
        assert response.status_code in [204, 400]
