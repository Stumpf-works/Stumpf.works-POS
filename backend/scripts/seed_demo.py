#!/usr/bin/env python3
"""
Demo Data Seeding Script
Populates database with sample data for testing and demos
"""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import click

from app.core.config import settings
from app.models.product import Product, Category
from app.models.user import User, UserRole
from app.core.security import get_password_hash, get_pin_hash
import structlog

logger = structlog.get_logger()


DEMO_CATEGORIES = [
    {"name": "Getränke", "description": "Alkoholfrei und Alkoholisch", "color": "#3B82F6"},
    {"name": "Essen", "description": "Speisen und Snacks", "color": "#10B981"},
    {"name": "Süßwaren", "description": "Schokolade, Kekse, Süßigkeiten", "color": "#F59E0B"},
    {"name": "Tabakwaren", "description": "Zigaretten und Tabak", "color": "#EF4444"},
    {"name": "Sonstiges", "description": "Diverse Artikel", "color": "#8B5CF6"},
]

DEMO_PRODUCTS = [
    # Getränke
    {"name": "Coca Cola 0.5L", "sku": "DRINK-001", "price": 2.49, "vat_rate": 19.0, "category": "Getränke", "stock": 100, "barcode": "4006381333634"},
    {"name": "Wasser Still 1.5L", "sku": "DRINK-002", "price": 0.89, "vat_rate": 19.0, "category": "Getränke", "stock": 150, "barcode": "4006381333627"},
    {"name": "Bier Pilsner 0.5L", "sku": "DRINK-003", "price": 1.99, "vat_rate": 19.0, "category": "Getränke", "stock": 80, "barcode": "4006381333610"},
    {"name": "Kaffee To-Go", "sku": "DRINK-004", "price": 2.50, "vat_rate": 7.0, "category": "Getränke", "stock": 50, "barcode": "4006381333603"},

    # Essen
    {"name": "Sandwich Schinken", "sku": "FOOD-001", "price": 4.50, "vat_rate": 7.0, "category": "Essen", "stock": 30, "barcode": "4006381444634"},
    {"name": "Brezel", "sku": "FOOD-002", "price": 1.50, "vat_rate": 7.0, "category": "Essen", "stock": 40, "barcode": "4006381444627"},
    {"name": "Currywurst mit Pommes", "sku": "FOOD-003", "price": 6.90, "vat_rate": 19.0, "category": "Essen", "stock": 25, "barcode": "4006381444610"},

    # Süßwaren
    {"name": "Snickers", "sku": "CANDY-001", "price": 1.29, "vat_rate": 19.0, "category": "Süßwaren", "stock": 100, "barcode": "5000159461122"},
    {"name": "Haribo Goldbären", "sku": "CANDY-002", "price": 0.99, "vat_rate": 19.0, "category": "Süßwaren", "stock": 80, "barcode": "4001686334003"},
    {"name": "Milka Schokolade", "sku": "CANDY-003", "price": 1.79, "vat_rate": 19.0, "category": "Süßwaren", "stock": 60, "barcode": "7622210449283"},

    # Tabakwaren
    {"name": "Marlboro Red", "sku": "TOB-001", "price": 7.50, "vat_rate": 19.0, "category": "Tabakwaren", "stock": 40, "barcode": "4008400211825"},
    {"name": "Lucky Strike Blue", "sku": "TOB-002", "price": 7.20, "vat_rate": 19.0, "category": "Tabakwaren", "stock": 35, "barcode": "4008400211832"},

    # Sonstiges
    {"name": "Zeitung Tagesspiegel", "sku": "MISC-001", "price": 2.80, "vat_rate": 7.0, "category": "Sonstiges", "stock": 20, "barcode": "4193753001018"},
    {"name": "Feuerzeug", "sku": "MISC-002", "price": 1.50, "vat_rate": 19.0, "category": "Sonstiges", "stock": 50, "barcode": "4006381555634"},
    {"name": "Taschentücher", "sku": "MISC-003", "price": 0.79, "vat_rate": 19.0, "category": "Sonstiges", "stock": 100, "barcode": "4006381555627"},
]

DEMO_USERS = [
    {
        "username": "cashier1",
        "email": "cashier1@demo.com",
        "first_name": "Anna",
        "last_name": "Schmidt",
        "role": UserRole.CASHIER,
        "password": "cashier123",
        "pin": "1234",
    },
    {
        "username": "cashier2",
        "email": "cashier2@demo.com",
        "first_name": "Max",
        "last_name": "Müller",
        "role": UserRole.CASHIER,
        "password": "cashier123",
        "pin": "5678",
    },
    {
        "username": "manager",
        "email": "manager@demo.com",
        "first_name": "Lisa",
        "last_name": "Weber",
        "role": UserRole.ADMIN,
        "password": "manager123",
        "pin": "9999",
    },
]


async def seed_categories(session: AsyncSession, tenant_id: str):
    """Seed product categories."""
    logger.info("seeding_categories", tenant=tenant_id)

    await session.execute(text(f'SET search_path TO "{tenant_id}", public'))

    categories = {}
    for cat_data in DEMO_CATEGORIES:
        category = Category(
            tenant_id=tenant_id,
            **cat_data
        )
        session.add(category)
        await session.flush()
        categories[cat_data["name"]] = category.id

    await session.commit()
    logger.info("categories_seeded", count=len(DEMO_CATEGORIES))
    return categories


async def seed_products(session: AsyncSession, tenant_id: str, categories: dict):
    """Seed products."""
    logger.info("seeding_products", tenant=tenant_id)

    await session.execute(text(f'SET search_path TO "{tenant_id}", public'))

    for prod_data in DEMO_PRODUCTS:
        category_name = prod_data.pop("category")
        category_id = categories.get(category_name)

        product = Product(
            tenant_id=tenant_id,
            category_id=category_id,
            **prod_data
        )
        session.add(product)

    await session.commit()
    logger.info("products_seeded", count=len(DEMO_PRODUCTS))


async def seed_users(session: AsyncSession, tenant_id: str):
    """Seed demo users."""
    logger.info("seeding_users", tenant=tenant_id)

    await session.execute(text(f'SET search_path TO "{tenant_id}", public'))

    for user_data in DEMO_USERS:
        password = user_data.pop("password")
        pin = user_data.pop("pin")

        user = User(
            tenant_id=tenant_id,
            password_hash=get_password_hash(password),
            pin_hash=get_pin_hash(pin),
            is_active=True,
            **user_data
        )
        session.add(user)

    await session.commit()
    logger.info("users_seeded", count=len(DEMO_USERS))


@click.command()
@click.option('--tenant-slug', prompt='Tenant ID', help='Tenant to seed data for')
@click.option('--force', is_flag=True, help='Force seeding even if data exists')
def main(tenant_slug, force):
    """
    Seed database with demo data.

    Adds sample categories, products, and users for testing.
    """

    click.echo("\n🌱 Stumpf.works POS - Demo Data Seeding")
    click.echo("=" * 60)

    if not force:
        click.confirm(
            f"\nThis will add demo data to tenant '{tenant_slug}'.\nContinue?",
            abort=True
        )

    async def run():
        engine = create_async_engine(
            settings.database_url_async,
            echo=False,
        )

        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        try:
            async with AsyncSessionLocal() as session:
                # Verify tenant exists
                result = await session.execute(
                    text("SELECT slug FROM tenants WHERE slug = :slug"),
                    {"slug": tenant_slug}
                )
                if not result.first():
                    click.echo(f"❌ Tenant '{tenant_slug}' not found!", err=True)
                    sys.exit(1)

                # Seed categories
                click.echo("\n📁 Creating product categories...")
                categories = await seed_categories(session, tenant_slug)

                # Seed products
                click.echo(f"📦 Creating {len(DEMO_PRODUCTS)} products...")
                await seed_products(session, tenant_slug, categories)

                # Seed users
                click.echo(f"👥 Creating {len(DEMO_USERS)} demo users...")
                await seed_users(session, tenant_slug)

            click.echo("\n✅ Demo data seeded successfully!")
            click.echo("\n📝 Demo Users:")
            for user in DEMO_USERS:
                click.echo(f"   - {user['username']} / cashier123 (PIN: {user['pin']})")

            click.echo("\n💡 You can now test the POS with realistic data!")

        except Exception as e:
            click.echo(f"\n❌ Error during seeding: {e}", err=True)
            logger.error("seed_failed", error=str(e), exc_info=True)
            sys.exit(1)

        finally:
            await engine.dispose()

    asyncio.run(run())


if __name__ == "__main__":
    main()
