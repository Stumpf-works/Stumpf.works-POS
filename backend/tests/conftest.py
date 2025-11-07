"""
Pytest Configuration and Fixtures
Provides test database, clients, and common fixtures
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.product import Product, Category
from app.core.security import get_password_hash


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/pos_test"


# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create test schema
    async with test_engine.begin() as conn:
        await conn.execute("CREATE SCHEMA IF NOT EXISTS test_tenant")

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_tenant(db_session: AsyncSession) -> Tenant:
    """Create test tenant."""
    tenant = Tenant(
        name="Test Company",
        slug="test_tenant",
        address_street="Test Street 1",
        address_postal_code="12345",
        address_city="Test City",
        address_country="DE",
        tax_id="DE123456789",
        vat_id="DE987654321",
        sumup_enabled=True,
        sumup_api_key="test_sumup_key",
        sumup_merchant_code="TEST123",
        tse_enabled=True,
        fiskaly_api_key="test_fiskaly_key",
        fiskaly_api_secret="test_fiskaly_secret",
        fiskaly_tss_id="test_tss_id",
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest.fixture
async def test_admin_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create test admin user."""
    user = User(
        tenant_id=test_tenant.slug,
        username="admin",
        email="admin@test.com",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        password_hash=get_password_hash("admin123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_cashier_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create test cashier user."""
    user = User(
        tenant_id=test_tenant.slug,
        username="cashier",
        email="cashier@test.com",
        first_name="Cashier",
        last_name="User",
        role=UserRole.CASHIER,
        password_hash=get_password_hash("cashier123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_token(client: AsyncClient, test_tenant: Tenant, test_admin_user: User) -> str:
    """Get admin authentication token."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
        headers={"X-Tenant-ID": test_tenant.slug}
    )
    return response.json()["access_token"]


@pytest.fixture
async def cashier_token(client: AsyncClient, test_tenant: Tenant, test_cashier_user: User) -> str:
    """Get cashier authentication token."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "cashier", "password": "cashier123"},
        headers={"X-Tenant-ID": test_tenant.slug}
    )
    return response.json()["access_token"]


@pytest.fixture
async def test_category(db_session: AsyncSession, test_tenant: Tenant) -> Category:
    """Create test category."""
    category = Category(
        tenant_id=test_tenant.slug,
        name="Test Category",
        slug="test-category",
        description="A test category",
        color="#FF5733",
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture
async def test_product(
    db_session: AsyncSession,
    test_tenant: Tenant,
    test_category: Category
) -> Product:
    """Create test product."""
    product = Product(
        tenant_id=test_tenant.slug,
        name="Test Product",
        description="A test product",
        sku="TEST-001",
        barcode="1234567890123",
        price=9.99,
        vat_rate=19.0,
        category_id=test_category.id,
        stock_quantity=100,
        is_active=True,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


@pytest.fixture
def auth_headers(admin_token: str, test_tenant: Tenant) -> dict:
    """Create authentication headers."""
    return {
        "Authorization": f"Bearer {admin_token}",
        "X-Tenant-ID": test_tenant.slug,
    }


@pytest.fixture
def cashier_auth_headers(cashier_token: str, test_tenant: Tenant) -> dict:
    """Create cashier authentication headers."""
    return {
        "Authorization": f"Bearer {cashier_token}",
        "X-Tenant-ID": test_tenant.slug,
    }
