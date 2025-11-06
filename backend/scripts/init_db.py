#!/usr/bin/env python3
"""
Database Initialization Script
Creates first tenant and admin user for fresh installation
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import click
from getpass import getpass

from app.core.config import settings
from app.core.database import Base
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.core.security import get_password_hash
import structlog

logger = structlog.get_logger()


async def create_tables(engine):
    """Create all database tables."""
    async with engine.begin() as conn:
        logger.info("creating_database_tables")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("database_tables_created")


async def create_default_tenant(session: AsyncSession, tenant_slug: str, tenant_name: str):
    """Create default tenant."""
    logger.info("creating_default_tenant", slug=tenant_slug)

    # Check if tenant already exists
    result = await session.execute(
        text("SELECT slug FROM tenants WHERE slug = :slug"),
        {"slug": tenant_slug}
    )
    if result.first():
        logger.warning("tenant_already_exists", slug=tenant_slug)
        return tenant_slug

    # Create tenant
    tenant = Tenant(
        slug=tenant_slug,
        name=tenant_name,
        address_country="DE",
        tse_enabled=False,  # Will be configured later
        sumup_enabled=False,
    )

    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)

    # Create tenant schema
    await session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{tenant_slug}"'))
    await session.commit()

    # Create tables in tenant schema
    await session.execute(text(f'SET search_path TO "{tenant_slug}", public'))

    # Create tenant-specific tables
    # Note: In production, use Alembic migrations
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(100) NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            role VARCHAR(20) NOT NULL,
            password_hash VARCHAR(255),
            pin_hash VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

    await session.commit()

    logger.info("tenant_created", slug=tenant_slug)
    return tenant_slug


async def create_admin_user(
    session: AsyncSession,
    tenant_id: str,
    username: str,
    email: str,
    password: str,
    first_name: str = None,
    last_name: str = None
):
    """Create admin user."""
    logger.info("creating_admin_user", username=username, tenant=tenant_id)

    # Set search path to tenant schema
    await session.execute(text(f'SET search_path TO "{tenant_id}", public'))

    # Check if user already exists
    result = await session.execute(
        text("SELECT username FROM users WHERE username = :username"),
        {"username": username}
    )
    if result.first():
        logger.warning("user_already_exists", username=username)
        return

    # Create admin user
    user = User(
        tenant_id=tenant_id,
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=UserRole.ADMIN,
        password_hash=get_password_hash(password),
        is_active=True,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.info("admin_user_created", username=username, user_id=user.id)
    return user


@click.command()
@click.option('--tenant-slug', prompt='Tenant ID (slug)', help='Unique tenant identifier')
@click.option('--tenant-name', prompt='Tenant Name', help='Tenant display name')
@click.option('--admin-username', prompt='Admin Username', default='admin', help='Admin username')
@click.option('--admin-email', prompt='Admin Email', help='Admin email address')
@click.option('--admin-password', prompt='Admin Password', hide_input=True, confirmation_prompt=True, help='Admin password')
@click.option('--first-name', default='', help='Admin first name')
@click.option('--last-name', default='', help='Admin last name')
def main(tenant_slug, tenant_name, admin_username, admin_email, admin_password, first_name, last_name):
    """
    Initialize database with first tenant and admin user.

    This script should be run once after deploying the application
    to create the initial setup.
    """

    click.echo("\n🚀 Stumpf.works POS - Database Initialization")
    click.echo("=" * 60)

    async def run():
        # Create engine
        engine = create_async_engine(
            settings.database_url_async,
            echo=False,
        )

        # Create session
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        try:
            # Create tables
            click.echo("\n📋 Creating database tables...")
            await create_tables(engine)

            async with AsyncSessionLocal() as session:
                # Create tenant
                click.echo(f"\n🏢 Creating tenant '{tenant_name}' ({tenant_slug})...")
                await create_default_tenant(session, tenant_slug, tenant_name)

                # Create admin user
                click.echo(f"\n👤 Creating admin user '{admin_username}'...")
                await create_admin_user(
                    session,
                    tenant_slug,
                    admin_username,
                    admin_email,
                    admin_password,
                    first_name or None,
                    last_name or None
                )

            click.echo("\n✅ Database initialization complete!")
            click.echo("\n📝 Next steps:")
            click.echo(f"   1. Login with: {admin_username} / {admin_password}")
            click.echo("   2. Configure TSE settings in admin dashboard")
            click.echo("   3. Configure SumUp integration (if needed)")
            click.echo("   4. Create product categories and products")
            click.echo("\n💡 Access the API at: http://localhost:8000/api/docs")

        except Exception as e:
            click.echo(f"\n❌ Error during initialization: {e}", err=True)
            logger.error("init_failed", error=str(e), exc_info=True)
            sys.exit(1)

        finally:
            await engine.dispose()

    # Run async function
    asyncio.run(run())


if __name__ == "__main__":
    main()
