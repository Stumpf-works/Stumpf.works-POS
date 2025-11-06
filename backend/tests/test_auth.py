"""
Tests for Authentication Endpoints
"""

import pytest
from httpx import AsyncClient

from app.models.tenant import Tenant
from app.models.user import User


@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication endpoints."""

    async def test_register_new_user(
        self,
        client: AsyncClient,
        test_tenant: Tenant
    ):
        """Test user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "password123",
                "first_name": "New",
                "last_name": "User",
            },
            headers={"X-Tenant-ID": test_tenant.slug}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@test.com"
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_register_duplicate_username(
        self,
        client: AsyncClient,
        test_tenant: Tenant,
        test_admin_user: User
    ):
        """Test registration with duplicate username."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "admin",  # Already exists
                "email": "another@test.com",
                "password": "password123",
            },
            headers={"X-Tenant-ID": test_tenant.slug}
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    async def test_login_with_password(
        self,
        client: AsyncClient,
        test_tenant: Tenant,
        test_admin_user: User
    ):
        """Test login with username and password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "admin123",
            },
            headers={"X-Tenant-ID": test_tenant.slug}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "admin"

    async def test_login_invalid_password(
        self,
        client: AsyncClient,
        test_tenant: Tenant,
        test_admin_user: User
    ):
        """Test login with invalid password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "wrongpassword",
            },
            headers={"X-Tenant-ID": test_tenant.slug}
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_login_nonexistent_user(
        self,
        client: AsyncClient,
        test_tenant: Tenant
    ):
        """Test login with non-existent user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123",
            },
            headers={"X-Tenant-ID": test_tenant.slug}
        )

        assert response.status_code == 401

    async def test_get_current_user(
        self,
        client: AsyncClient,
        test_tenant: Tenant,
        test_admin_user: User,
        admin_token: str
    ):
        """Test getting current user info."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Tenant-ID": test_tenant.slug,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"

    async def test_unauthorized_access(
        self,
        client: AsyncClient,
        test_tenant: Tenant
    ):
        """Test accessing protected endpoint without token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"X-Tenant-ID": test_tenant.slug}
        )

        assert response.status_code == 401

    async def test_invalid_token(
        self,
        client: AsyncClient,
        test_tenant: Tenant
    ):
        """Test accessing protected endpoint with invalid token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": "Bearer invalid_token",
                "X-Tenant-ID": test_tenant.slug,
            }
        )

        assert response.status_code == 401

    async def test_missing_tenant_header(
        self,
        client: AsyncClient,
        test_admin_user: User
    ):
        """Test request without tenant header."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "admin123",
            }
        )

        # Should fail without tenant header
        assert response.status_code in [400, 401, 403]
