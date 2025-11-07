"""
Product API Endpoints
CRUD operations for products and categories
"""

from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, require_admin
from app.core.database import get_db
from app.models.product import Product, ProductCategory
from app.models.user import User
from app.schemas.base import MessageResponse
from app.schemas.product import (ProductCategoryCreate,
                                 ProductCategoryResponse,
                                 ProductCategoryUpdate, ProductCreate,
                                 ProductResponse, ProductSearchParams,
                                 ProductUpdate, StockAdjustment)
from app.utils.helpers import slugify

logger = structlog.get_logger()
router = APIRouter(prefix="/products", tags=["Products"])


# ==========================================
# Product Categories
# ==========================================


@router.post(
    "/categories",
    response_model=ProductCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category_data: ProductCategoryCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new product category."""

    # Generate slug from name
    slug = slugify(category_data.name)

    # Check if slug already exists for this tenant
    result = await db.execute(
        select(ProductCategory).where(
            ProductCategory.slug == slug,
            ProductCategory.tenant_id == current_user.tenant_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with slug '{slug}' already exists",
        )

    # Create category
    category = ProductCategory(
        **category_data.model_dump(),
        slug=slug,
        tenant_id=current_user.tenant_id,
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    logger.info("category_created", category_id=category.id, name=category.name)

    return category


@router.get("/categories", response_model=List[ProductCategoryResponse])
async def list_categories(
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all product categories."""

    query = select(ProductCategory).where(
        ProductCategory.tenant_id == current_user.tenant_id
    )

    if is_active is not None:
        query = query.where(ProductCategory.is_active == is_active)

    query = query.order_by(ProductCategory.sort_order, ProductCategory.name)

    result = await db.execute(query)
    categories = result.scalars().all()

    return categories


@router.get("/categories/{category_id}", response_model=ProductCategoryResponse)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific category."""

    result = await db.execute(
        select(ProductCategory).where(
            ProductCategory.id == category_id,
            ProductCategory.tenant_id == current_user.tenant_id,
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return category


@router.patch("/categories/{category_id}", response_model=ProductCategoryResponse)
async def update_category(
    category_id: int,
    category_data: ProductCategoryUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a category."""

    result = await db.execute(
        select(ProductCategory).where(
            ProductCategory.id == category_id,
            ProductCategory.tenant_id == current_user.tenant_id,
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    # Update fields
    update_data = category_data.model_dump(exclude_unset=True)

    # Update slug if name changed
    if "name" in update_data:
        update_data["slug"] = slugify(update_data["name"])

    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    logger.info("category_updated", category_id=category.id)

    return category


@router.delete("/categories/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a category."""

    result = await db.execute(
        select(ProductCategory).where(
            ProductCategory.id == category_id,
            ProductCategory.tenant_id == current_user.tenant_id,
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    await db.delete(category)
    await db.commit()

    logger.info("category_deleted", category_id=category_id)

    return MessageResponse(message="Category deleted successfully")


# ==========================================
# Products
# ==========================================


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new product."""

    # Check if SKU or barcode already exists
    if product_data.sku or product_data.barcode:
        query = select(Product).where(Product.tenant_id == current_user.tenant_id)

        conditions = []
        if product_data.sku:
            conditions.append(Product.sku == product_data.sku)
        if product_data.barcode:
            conditions.append(Product.barcode == product_data.barcode)

        query = query.where(or_(*conditions))
        result = await db.execute(query)

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU or barcode already exists",
            )

    # Create product
    product = Product(
        **product_data.model_dump(),
        tenant_id=current_user.tenant_id,
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    logger.info("product_created", product_id=product.id, name=product.name)

    return product


@router.get("", response_model=List[ProductResponse])
async def list_products(
    q: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[int] = None,
    barcode: Optional[str] = None,
    sku: Optional[str] = None,
    is_available: Optional[bool] = None,
    is_active: Optional[bool] = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List products with search and filters."""

    query = select(Product).where(Product.tenant_id == current_user.tenant_id)

    # Filters
    if q:
        search_pattern = f"%{q}%"
        query = query.where(
            or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern),
                Product.sku.ilike(search_pattern),
                Product.barcode.ilike(search_pattern),
            )
        )

    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    if barcode:
        query = query.where(Product.barcode == barcode)

    if sku:
        query = query.where(Product.sku == sku)

    if is_available is not None:
        query = query.where(Product.is_available == is_available)

    if is_active is not None:
        query = query.where(Product.is_active == is_active)

    # Pagination
    query = query.offset(skip).limit(limit)
    query = query.order_by(Product.name)

    result = await db.execute(query)
    products = result.scalars().all()

    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific product."""

    result = await db.execute(
        select(Product).where(
            Product.id == product_id, Product.tenant_id == current_user.tenant_id
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a product."""

    result = await db.execute(
        select(Product).where(
            Product.id == product_id, Product.tenant_id == current_user.tenant_id
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    logger.info("product_updated", product_id=product.id)

    return product


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a product."""

    result = await db.execute(
        select(Product).where(
            Product.id == product_id, Product.tenant_id == current_user.tenant_id
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    await db.delete(product)
    await db.commit()

    logger.info("product_deleted", product_id=product_id)

    return MessageResponse(message="Product deleted successfully")


@router.post("/{product_id}/stock", response_model=ProductResponse)
async def adjust_stock(
    product_id: int,
    adjustment: StockAdjustment,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Adjust product stock quantity."""

    result = await db.execute(
        select(Product).where(
            Product.id == product_id, Product.tenant_id == current_user.tenant_id
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if not product.track_inventory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product does not track inventory",
        )

    # Adjust stock
    new_quantity = product.stock_quantity + adjustment.quantity

    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock quantity cannot be negative",
        )

    product.stock_quantity = new_quantity

    await db.commit()
    await db.refresh(product)

    logger.info(
        "stock_adjusted",
        product_id=product.id,
        adjustment=adjustment.quantity,
        new_quantity=new_quantity,
        reason=adjustment.reason,
    )

    return product
