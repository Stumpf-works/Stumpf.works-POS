"""
Database Configuration
SQLAlchemy 2.0 setup with multi-tenant support
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Base class for SQLAlchemy models
Base = declarative_base()

# Synchronous engine (for Alembic migrations)
sync_engine = create_engine(
    settings.database_url_sync,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
)

# Asynchronous engine (for FastAPI)
async_engine = create_async_engine(
    settings.database_url_async,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
)

# Session factories
SyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=sync_engine, class_=Session
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class TenantContext:
    """Thread-local context for current tenant schema."""

    _schema: Optional[str] = None

    @classmethod
    def set_schema(cls, schema: str) -> None:
        """Set current tenant schema."""
        cls._schema = schema

    @classmethod
    def get_schema(cls) -> Optional[str]:
        """Get current tenant schema."""
        return cls._schema

    @classmethod
    def clear(cls) -> None:
        """Clear tenant context."""
        cls._schema = None


def set_search_path(dbapi_conn, connection_record, schema: Optional[str] = None):
    """
    Set PostgreSQL search_path for schema isolation.
    This ensures queries use the correct tenant schema.
    """
    schema = schema or TenantContext.get_schema() or settings.DEFAULT_TENANT_SCHEMA

    with dbapi_conn.cursor() as cursor:
        cursor.execute(f'SET search_path TO "{schema}", public')


# Attach search_path setter to connection events
@event.listens_for(sync_engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Set search_path on sync connection."""
    set_search_path(dbapi_conn, connection_record)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            # Set search path for multi-tenant isolation
            schema = TenantContext.get_schema() or settings.DEFAULT_TENANT_SCHEMA
            await session.execute(text(f'SET search_path TO "{schema}", public'))

            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Session:
    """
    Get synchronous database session (for migrations, CLI, etc.).
    """
    db = SyncSessionLocal()
    try:
        # Set search path
        schema = TenantContext.get_schema() or settings.DEFAULT_TENANT_SCHEMA
        db.execute(text(f'SET search_path TO "{schema}", public'))

        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def create_tenant_schema(schema_name: str) -> None:
    """
    Create a new schema for a tenant.
    This is called when onboarding a new tenant.
    """
    async with async_engine.begin() as conn:
        # Check if schema exists
        result = await conn.execute(
            text(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name = :schema_name"
            ),
            {"schema_name": schema_name},
        )
        exists = result.fetchone()

        if not exists:
            # Create schema
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))

            # Run migrations for this schema (to be implemented with Alembic)
            # This will be handled by the tenant onboarding service


async def drop_tenant_schema(schema_name: str) -> None:
    """
    Drop a tenant schema (use with caution!).
    Only for tenant offboarding or testing.
    """
    if schema_name == settings.DEFAULT_TENANT_SCHEMA:
        raise ValueError("Cannot drop default schema")

    async with async_engine.begin() as conn:
        await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))


async def init_db() -> None:
    """
    Initialize database (create all tables in default schema).
    Should be run on first deployment.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await async_engine.dispose()
