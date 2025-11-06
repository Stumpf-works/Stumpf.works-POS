"""
Bakery Management Plugin

Features:
- Recipe management with ingredients
- Daily production planning
- Freshness tracking (best-before dates)
- Baking sheets generation
- Ingredient inventory
- Waste tracking (spoilage, returns)
- Production batch tracking
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.base import BaseModel as SQLBase
from app.models.base import TenantMixin
from app.models.user import User
from app.plugins.base import BasePlugin, PluginMetadata

logger = structlog.get_logger()


# ============================================================================
# Database Models
# ============================================================================


class Recipe(SQLBase, TenantMixin):
    """Recipes for bakery products."""

    __tablename__ = "plugin_bakery_recipes"

    product_id = Column(Integer, nullable=False)
    recipe_name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=True)  # bread, rolls, cake, pastry
    preparation_time = Column(Integer, nullable=True)  # minutes
    baking_time = Column(Integer, nullable=True)  # minutes
    baking_temperature = Column(Integer, nullable=True)  # celsius
    yield_quantity = Column(Numeric(10, 2), nullable=False)  # how many items
    instructions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)


class RecipeIngredient(SQLBase, TenantMixin):
    """Ingredients for recipes."""

    __tablename__ = "plugin_bakery_recipe_ingredients"

    recipe_id = Column(Integer, ForeignKey("plugin_bakery_recipes.id"), nullable=False)
    ingredient_name = Column(String(200), nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False)
    unit = Column(String(20), nullable=False)  # kg, g, l, ml, pieces
    ingredient_type = Column(String(50), nullable=True)  # flour, yeast, sugar, etc.
    notes = Column(String(500), nullable=True)


class ProductionPlan(SQLBase, TenantMixin):
    """Daily production plans."""

    __tablename__ = "plugin_bakery_production_plans"

    plan_date = Column(Date, nullable=False)
    recipe_id = Column(Integer, ForeignKey("plugin_bakery_recipes.id"), nullable=False)
    planned_quantity = Column(Numeric(10, 2), nullable=False)
    produced_quantity = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="planned")  # planned, in_progress, completed
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    notes = Column(String(1000), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class ProductionBatch(SQLBase, TenantMixin):
    """Production batch tracking."""

    __tablename__ = "plugin_bakery_production_batches"

    plan_id = Column(
        Integer, ForeignKey("plugin_bakery_production_plans.id"), nullable=True
    )
    recipe_id = Column(Integer, ForeignKey("plugin_bakery_recipes.id"), nullable=False)
    batch_number = Column(String(50), nullable=False, unique=True)
    production_date = Column(DateTime, nullable=False)
    quantity_produced = Column(Numeric(10, 2), nullable=False)
    best_before_date = Column(Date, nullable=True)
    batch_status = Column(String(20), default="fresh")  # fresh, expiring_soon, expired
    notes = Column(String(500), nullable=True)
    produced_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class FreshnessTracking(SQLBase, TenantMixin):
    """Track freshness of bakery products."""

    __tablename__ = "plugin_bakery_freshness_tracking"

    product_id = Column(Integer, nullable=False)
    batch_id = Column(
        Integer, ForeignKey("plugin_bakery_production_batches.id"), nullable=True
    )
    production_date = Column(Date, nullable=False)
    best_before_date = Column(Date, nullable=False)
    current_quantity = Column(Numeric(10, 2), nullable=False)
    status = Column(
        String(20), default="fresh"
    )  # fresh, expiring_soon, expired, sold_out
    location = Column(String(100), nullable=True)  # display, storage, etc.


class WasteTracking(SQLBase, TenantMixin):
    """Track waste and returns."""

    __tablename__ = "plugin_bakery_waste_tracking"

    product_id = Column(Integer, nullable=False)
    batch_id = Column(
        Integer, ForeignKey("plugin_bakery_production_batches.id"), nullable=True
    )
    waste_type = Column(String(20), nullable=False)  # spoilage, return, broken, other
    quantity = Column(Numeric(10, 2), nullable=False)
    waste_date = Column(DateTime, nullable=False)
    reason = Column(String(500), nullable=True)
    cost_impact = Column(Numeric(10, 2), nullable=True)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class BakingSheet(SQLBase, TenantMixin):
    """Generated baking sheets for production."""

    __tablename__ = "plugin_bakery_baking_sheets"

    sheet_number = Column(String(50), nullable=False, unique=True)
    plan_date = Column(Date, nullable=False)
    generated_at = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    notes = Column(String(1000), nullable=True)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=True)


# ============================================================================
# API Models (Pydantic)
# ============================================================================


class RecipeCreate(BaseModel):
    """Request to create a recipe."""

    product_id: int
    recipe_name: str
    category: Optional[str] = None
    preparation_time: Optional[int] = None
    baking_time: Optional[int] = None
    baking_temperature: Optional[int] = None
    yield_quantity: Decimal
    instructions: Optional[str] = None
    notes: Optional[str] = None
    ingredients: List[Dict[str, Any]]  # [{ingredient_name, quantity, unit}]


class RecipeInfo(BaseModel):
    """Recipe information."""

    id: int
    product_id: int
    recipe_name: str
    category: Optional[str]
    preparation_time: Optional[int]
    baking_time: Optional[int]
    baking_temperature: Optional[int]
    yield_quantity: Decimal
    instructions: Optional[str]
    notes: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class ProductionPlanCreate(BaseModel):
    """Request to create production plan."""

    plan_date: datetime
    recipe_id: int
    planned_quantity: Decimal
    notes: Optional[str] = None


class ProductionPlanInfo(BaseModel):
    """Production plan information."""

    id: int
    plan_date: datetime
    recipe_id: int
    recipe_name: str
    planned_quantity: Decimal
    produced_quantity: Decimal
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


class ProductionBatchCreate(BaseModel):
    """Request to create production batch."""

    plan_id: Optional[int] = None
    recipe_id: int
    production_date: datetime
    quantity_produced: Decimal
    best_before_date: Optional[datetime] = None
    notes: Optional[str] = None


class WasteTrackingCreate(BaseModel):
    """Request to track waste."""

    product_id: int
    batch_id: Optional[int] = None
    waste_type: str = Field(..., pattern="^(spoilage|return|broken|other)$")
    quantity: Decimal
    reason: Optional[str] = None
    cost_impact: Optional[Decimal] = None


# ============================================================================
# Plugin Class
# ============================================================================


class BakeryManagementPlugin(BasePlugin):
    """
    Bakery Management Plugin.

    Provides comprehensive bakery production and freshness management.
    """

    def __init__(self):
        super().__init__()
        self.config = {
            "default_bread_shelf_life_days": 2,
            "default_cake_shelf_life_days": 5,
            "expiring_soon_threshold_hours": 6,
            "auto_generate_baking_sheets": True,
            "waste_cost_tracking": True,
        }

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="bakery_management",
            version="1.0.0",
            description="Bakery production planning and freshness management",
            author="Stumpf.works",
            dependencies=[],
        )

    def get_name(self) -> str:
        """Get plugin name."""
        return "bakery_management"

    def get_display_name(self) -> str:
        """Get plugin display name."""
        return "Bäckerei-Verwaltung"

    def get_description(self) -> str:
        """Get plugin description."""
        return (
            "Produktionsplanung, Rezeptverwaltung und Frische-Tracking für Bäckereien"
        )

    def get_version(self) -> str:
        """Get plugin version."""
        return self.metadata.version

    def get_author(self) -> str:
        """Get plugin author."""
        return self.metadata.author

    def get_category(self) -> str:
        """Get plugin category."""
        return "bakery"

    def get_requires(self) -> List[str]:
        """Get plugin dependencies."""
        return self.metadata.dependencies

    def get_config_schema(self) -> Optional[Dict]:
        """Get plugin configuration schema."""
        return {
            "type": "object",
            "properties": {
                "default_bread_shelf_life_days": {
                    "type": "integer",
                    "default": 2,
                    "minimum": 1,
                    "maximum": 30,
                    "description": "Standard-Haltbarkeit Brot (Tage)",
                },
                "default_cake_shelf_life_days": {
                    "type": "integer",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 30,
                    "description": "Standard-Haltbarkeit Kuchen (Tage)",
                },
                "expiring_soon_threshold_hours": {
                    "type": "integer",
                    "default": 6,
                    "minimum": 1,
                    "maximum": 48,
                    "description": "Warnung vor Ablauf (Stunden)",
                },
                "auto_generate_baking_sheets": {
                    "type": "boolean",
                    "default": True,
                    "description": "Backzettel automatisch generieren",
                },
                "waste_cost_tracking": {
                    "type": "boolean",
                    "default": True,
                    "description": "Verlustkosten tracken",
                },
            },
        }

    def configure(self, config: Dict):
        """Configure plugin with settings."""
        shelf_life = config.get("default_bread_shelf_life_days", 2)
        if shelf_life < 1 or shelf_life > 30:
            raise ValueError("Shelf life must be between 1 and 30 days")

        self.config.update(config)
        logger.info("bakery_management_configured", config=self.config)

    def get_models(self) -> List[Any]:
        """Return database models."""
        return [
            Recipe,
            RecipeIngredient,
            ProductionPlan,
            ProductionBatch,
            FreshnessTracking,
            WasteTracking,
            BakingSheet,
        ]

    async def on_enable(self):
        """Called when plugin is enabled."""
        logger.info("bakery_management_enabled")

    async def on_disable(self):
        """Called when plugin is disabled."""
        logger.info("bakery_management_disabled")

    def get_router(self) -> APIRouter:
        """Return API router with endpoints."""
        router = APIRouter(prefix="/bakery", tags=["Bakery - Production Management"])

        # ============================================================================
        # Recipe Endpoints
        # ============================================================================

        @router.get("/recipes", response_model=List[RecipeInfo])
        async def list_recipes(
            category: Optional[str] = Query(None),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """List all recipes."""
            query = select(Recipe).where(
                Recipe.tenant_id == current_user.tenant_id,
                Recipe.is_active == True,  # noqa
            )

            if category:
                query = query.where(Recipe.category == category)

            result = await db.execute(query)
            recipes = result.scalars().all()

            return [
                RecipeInfo(
                    id=r.id,
                    product_id=r.product_id,
                    recipe_name=r.recipe_name,
                    category=r.category,
                    preparation_time=r.preparation_time,
                    baking_time=r.baking_time,
                    baking_temperature=r.baking_temperature,
                    yield_quantity=r.yield_quantity,
                    instructions=r.instructions,
                    notes=r.notes,
                    is_active=r.is_active,
                )
                for r in recipes
            ]

        @router.post("/recipes", status_code=status.HTTP_201_CREATED)
        async def create_recipe(
            request: RecipeCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Create a new recipe."""
            # Create recipe
            recipe = Recipe(
                tenant_id=current_user.tenant_id,
                product_id=request.product_id,
                recipe_name=request.recipe_name,
                category=request.category,
                preparation_time=request.preparation_time,
                baking_time=request.baking_time,
                baking_temperature=request.baking_temperature,
                yield_quantity=request.yield_quantity,
                instructions=request.instructions,
                notes=request.notes,
            )
            db.add(recipe)
            await db.flush()

            # Add ingredients
            for ing_data in request.ingredients:
                ingredient = RecipeIngredient(
                    tenant_id=current_user.tenant_id,
                    recipe_id=recipe.id,
                    ingredient_name=ing_data["ingredient_name"],
                    quantity=Decimal(str(ing_data["quantity"])),
                    unit=ing_data["unit"],
                    ingredient_type=ing_data.get("ingredient_type"),
                    notes=ing_data.get("notes"),
                )
                db.add(ingredient)

            await db.commit()
            await db.refresh(recipe)

            logger.info(
                "recipe_created",
                recipe_id=recipe.id,
                name=request.recipe_name,
            )

            return {"id": recipe.id, "recipe_name": request.recipe_name}

        @router.get("/recipes/{recipe_id}/ingredients")
        async def get_recipe_ingredients(
            recipe_id: int,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get ingredients for a recipe."""
            result = await db.execute(
                select(RecipeIngredient).where(
                    RecipeIngredient.recipe_id == recipe_id,
                    RecipeIngredient.tenant_id == current_user.tenant_id,
                )
            )
            ingredients = result.scalars().all()

            return [
                {
                    "id": i.id,
                    "ingredient_name": i.ingredient_name,
                    "quantity": float(i.quantity),
                    "unit": i.unit,
                    "ingredient_type": i.ingredient_type,
                    "notes": i.notes,
                }
                for i in ingredients
            ]

        # ============================================================================
        # Production Plan Endpoints
        # ============================================================================

        @router.get("/production-plans", response_model=List[ProductionPlanInfo])
        async def list_production_plans(
            plan_date: Optional[datetime] = Query(None),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """List production plans."""
            query = select(ProductionPlan).where(
                ProductionPlan.tenant_id == current_user.tenant_id
            )

            if plan_date:
                target_date = plan_date.date()
                query = query.where(ProductionPlan.plan_date == target_date)

            result = await db.execute(query.order_by(ProductionPlan.plan_date.desc()))
            plans = result.scalars().all()

            plans_info = []
            for plan in plans:
                # Get recipe name
                recipe_result = await db.execute(
                    select(Recipe).where(Recipe.id == plan.recipe_id)
                )
                recipe = recipe_result.scalar_one_or_none()

                plans_info.append(
                    ProductionPlanInfo(
                        id=plan.id,
                        plan_date=datetime.combine(plan.plan_date, datetime.min.time()),
                        recipe_id=plan.recipe_id,
                        recipe_name=recipe.recipe_name if recipe else "Unknown",
                        planned_quantity=plan.planned_quantity,
                        produced_quantity=plan.produced_quantity,
                        status=plan.status,
                        start_time=plan.start_time,
                        end_time=plan.end_time,
                        notes=plan.notes,
                    )
                )

            return plans_info

        @router.post("/production-plans", status_code=status.HTTP_201_CREATED)
        async def create_production_plan(
            request: ProductionPlanCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Create a production plan."""
            plan = ProductionPlan(
                tenant_id=current_user.tenant_id,
                plan_date=request.plan_date.date(),
                recipe_id=request.recipe_id,
                planned_quantity=request.planned_quantity,
                notes=request.notes,
                created_by=current_user.id,
            )
            db.add(plan)
            await db.commit()
            await db.refresh(plan)

            logger.info(
                "production_plan_created",
                plan_id=plan.id,
                date=plan.plan_date,
            )

            return {
                "id": plan.id,
                "plan_date": plan.plan_date.isoformat(),
                "planned_quantity": float(request.planned_quantity),
            }

        @router.patch("/production-plans/{plan_id}/status")
        async def update_production_status(
            plan_id: int,
            new_status: str = Query(..., pattern="^(planned|in_progress|completed)$"),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Update production plan status."""
            result = await db.execute(
                select(ProductionPlan).where(
                    ProductionPlan.id == plan_id,
                    ProductionPlan.tenant_id == current_user.tenant_id,
                )
            )
            plan = result.scalar_one_or_none()

            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Production plan not found",
                )

            old_status = plan.status
            plan.status = new_status

            if new_status == "in_progress" and not plan.start_time:
                plan.start_time = datetime.utcnow()

            if new_status == "completed" and not plan.end_time:
                plan.end_time = datetime.utcnow()

            await db.commit()

            logger.info(
                "production_status_updated",
                plan_id=plan_id,
                old_status=old_status,
                new_status=new_status,
            )

            return {"plan_id": plan_id, "status": new_status}

        # ============================================================================
        # Production Batch Endpoints
        # ============================================================================

        @router.post("/production-batches", status_code=status.HTTP_201_CREATED)
        async def create_production_batch(
            request: ProductionBatchCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Create a production batch."""
            # Generate batch number
            batch_number = f"BATCH-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

            # Calculate best before date if not provided
            best_before = request.best_before_date
            if not best_before:
                # Get recipe to determine shelf life
                recipe_result = await db.execute(
                    select(Recipe).where(Recipe.id == request.recipe_id)
                )
                recipe = recipe_result.scalar_one_or_none()

                if recipe:
                    # Determine shelf life based on category
                    if recipe.category in ["bread", "rolls"]:
                        days = self.config["default_bread_shelf_life_days"]
                    else:
                        days = self.config["default_cake_shelf_life_days"]

                    best_before = request.production_date + timedelta(days=days)

            batch = ProductionBatch(
                tenant_id=current_user.tenant_id,
                plan_id=request.plan_id,
                recipe_id=request.recipe_id,
                batch_number=batch_number,
                production_date=request.production_date,
                quantity_produced=request.quantity_produced,
                best_before_date=best_before.date() if best_before else None,
                notes=request.notes,
                produced_by=current_user.id,
            )
            db.add(batch)
            await db.commit()
            await db.refresh(batch)

            logger.info(
                "production_batch_created",
                batch_id=batch.id,
                batch_number=batch_number,
            )

            return {
                "id": batch.id,
                "batch_number": batch_number,
                "quantity_produced": float(request.quantity_produced),
                "best_before_date": (
                    batch.best_before_date.isoformat()
                    if batch.best_before_date
                    else None
                ),
            }

        # ============================================================================
        # Freshness Tracking Endpoints
        # ============================================================================

        @router.get("/freshness/expiring-soon")
        async def get_expiring_products(
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get products expiring soon."""
            threshold_hours = self.config["expiring_soon_threshold_hours"]
            threshold_date = datetime.utcnow() + timedelta(hours=threshold_hours)

            result = await db.execute(
                select(ProductionBatch).where(
                    ProductionBatch.tenant_id == current_user.tenant_id,
                    ProductionBatch.best_before_date <= threshold_date.date(),
                    ProductionBatch.batch_status == "fresh",
                )
            )
            batches = result.scalars().all()

            return {
                "count": len(batches),
                "threshold_hours": threshold_hours,
                "batches": [
                    {
                        "batch_id": b.id,
                        "batch_number": b.batch_number,
                        "recipe_id": b.recipe_id,
                        "production_date": b.production_date.isoformat(),
                        "best_before_date": (
                            b.best_before_date.isoformat()
                            if b.best_before_date
                            else None
                        ),
                        "quantity": float(b.quantity_produced),
                    }
                    for b in batches
                ],
            }

        # ============================================================================
        # Waste Tracking Endpoints
        # ============================================================================

        @router.post("/waste", status_code=status.HTTP_201_CREATED)
        async def track_waste(
            request: WasteTrackingCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Track waste."""
            waste = WasteTracking(
                tenant_id=current_user.tenant_id,
                product_id=request.product_id,
                batch_id=request.batch_id,
                waste_type=request.waste_type,
                quantity=request.quantity,
                waste_date=datetime.utcnow(),
                reason=request.reason,
                cost_impact=request.cost_impact,
                recorded_by=current_user.id,
            )
            db.add(waste)
            await db.commit()
            await db.refresh(waste)

            logger.info(
                "waste_tracked",
                waste_id=waste.id,
                type=request.waste_type,
                quantity=float(request.quantity),
            )

            return {
                "id": waste.id,
                "waste_type": request.waste_type,
                "quantity": float(request.quantity),
            }

        @router.get("/waste/summary")
        async def get_waste_summary(
            start_date: Optional[datetime] = Query(None),
            end_date: Optional[datetime] = Query(None),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get waste summary."""
            query = select(WasteTracking).where(
                WasteTracking.tenant_id == current_user.tenant_id
            )

            if start_date:
                query = query.where(WasteTracking.waste_date >= start_date)

            if end_date:
                query = query.where(WasteTracking.waste_date <= end_date)

            result = await db.execute(query)
            waste_records = result.scalars().all()

            # Summarize by type
            summary = {}
            total_cost = Decimal("0")

            for record in waste_records:
                waste_type = record.waste_type
                if waste_type not in summary:
                    summary[waste_type] = {
                        "count": 0,
                        "total_quantity": 0.0,
                        "total_cost": 0.0,
                    }

                summary[waste_type]["count"] += 1
                summary[waste_type]["total_quantity"] += float(record.quantity)

                if record.cost_impact:
                    summary[waste_type]["total_cost"] += float(record.cost_impact)
                    total_cost += record.cost_impact

            return {
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None,
                },
                "total_records": len(waste_records),
                "total_cost_impact": float(total_cost),
                "by_type": summary,
            }

        # ============================================================================
        # Baking Sheet Endpoints
        # ============================================================================

        @router.post("/baking-sheets/generate")
        async def generate_baking_sheet(
            plan_date: datetime,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Generate baking sheet for a date."""
            sheet_number = f"BS-{plan_date.strftime('%Y%m%d')}"

            # Get all production plans for the date
            result = await db.execute(
                select(ProductionPlan).where(
                    ProductionPlan.tenant_id == current_user.tenant_id,
                    ProductionPlan.plan_date == plan_date.date(),
                )
            )
            plans = result.scalars().all()

            if not plans:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No production plans found for this date",
                )

            # Create baking sheet
            sheet = BakingSheet(
                tenant_id=current_user.tenant_id,
                sheet_number=sheet_number,
                plan_date=plan_date.date(),
                generated_at=datetime.utcnow(),
                generated_by=current_user.id,
            )
            db.add(sheet)
            await db.commit()
            await db.refresh(sheet)

            # Compile sheet data
            sheet_data = []
            for plan in plans:
                # Get recipe
                recipe_result = await db.execute(
                    select(Recipe).where(Recipe.id == plan.recipe_id)
                )
                recipe = recipe_result.scalar_one_or_none()

                if recipe:
                    # Get ingredients
                    ing_result = await db.execute(
                        select(RecipeIngredient).where(
                            RecipeIngredient.recipe_id == recipe.id
                        )
                    )
                    ingredients = ing_result.scalars().all()

                    # Calculate ingredient amounts for planned quantity
                    multiplier = float(plan.planned_quantity) / float(
                        recipe.yield_quantity
                    )

                    sheet_data.append(
                        {
                            "recipe_name": recipe.recipe_name,
                            "planned_quantity": float(plan.planned_quantity),
                            "baking_temp": recipe.baking_temperature,
                            "baking_time": recipe.baking_time,
                            "ingredients": [
                                {
                                    "name": i.ingredient_name,
                                    "quantity": float(i.quantity) * multiplier,
                                    "unit": i.unit,
                                }
                                for i in ingredients
                            ],
                            "instructions": recipe.instructions,
                        }
                    )

            logger.info(
                "baking_sheet_generated",
                sheet_id=sheet.id,
                date=plan_date.date(),
            )

            return {
                "sheet_id": sheet.id,
                "sheet_number": sheet_number,
                "plan_date": plan_date.date().isoformat(),
                "items": sheet_data,
            }

        return router


# ============================================================================
# Plugin Instance (for auto-discovery)
# ============================================================================

plugin = BakeryManagementPlugin()
