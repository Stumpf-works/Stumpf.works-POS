"""
Loyalty Program Plugin

Features:
- Points earning on purchases
- Points redemption for discounts
- Tier system (Bronze, Silver, Gold, Platinum)
- Birthday bonus
- Welcome bonus
- Point expiry after X months
- QR code or card number
- SMS/Email on point changes
- Campaigns (double points on weekends)
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
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
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


class LoyaltyCustomer(SQLBase, TenantMixin):
    """Loyalty program customer."""

    __tablename__ = "plugin_loyalty_customers"

    customer_name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    card_number = Column(String(50), nullable=False, unique=True)
    qr_code = Column(String(200), nullable=True)
    points_balance = Column(Integer, default=0)
    lifetime_points = Column(Integer, default=0)
    tier = Column(String(20), default="bronze")  # bronze, silver, gold, platinum
    date_of_birth = Column(DateTime, nullable=True)
    enrollment_date = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(String(1000), nullable=True)


class LoyaltyTransaction(SQLBase, TenantMixin):
    """Loyalty point transactions."""

    __tablename__ = "plugin_loyalty_transactions"

    customer_id = Column(
        Integer, ForeignKey("plugin_loyalty_customers.id"), nullable=False
    )
    transaction_type = Column(String(20), nullable=False)  # earn, redeem, expire, bonus
    points = Column(Integer, nullable=False)
    points_before = Column(Integer, nullable=False)
    points_after = Column(Integer, nullable=False)
    reference_type = Column(
        String(50), nullable=True
    )  # sale, birthday, welcome, campaign
    reference_id = Column(Integer, nullable=True)
    amount_spent = Column(Numeric(10, 2), nullable=True)
    description = Column(String(500), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class LoyaltyTier(SQLBase, TenantMixin):
    """Loyalty tier definitions."""

    __tablename__ = "plugin_loyalty_tiers"

    tier_name = Column(String(50), nullable=False)  # bronze, silver, gold, platinum
    min_points = Column(Integer, nullable=False)
    points_multiplier = Column(Numeric(3, 2), default=1.0)  # 1.0x, 1.5x, 2.0x
    discount_percentage = Column(Numeric(5, 2), default=0)
    description = Column(String(500), nullable=True)
    color = Column(String(20), nullable=True)  # For UI
    is_active = Column(Boolean, default=True)


class LoyaltyReward(SQLBase, TenantMixin):
    """Redeemable rewards."""

    __tablename__ = "plugin_loyalty_rewards"

    reward_name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    points_required = Column(Integer, nullable=False)
    reward_type = Column(String(20), nullable=False)  # discount, product, service
    reward_value = Column(Numeric(10, 2), nullable=True)
    max_redemptions = Column(Integer, nullable=True)
    redemption_count = Column(Integer, default=0)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class LoyaltyCampaign(SQLBase, TenantMixin):
    """Marketing campaigns."""

    __tablename__ = "plugin_loyalty_campaigns"

    campaign_name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    campaign_type = Column(String(20), nullable=False)  # double_points, bonus_points
    points_multiplier = Column(Numeric(3, 2), nullable=True)
    bonus_points = Column(Integer, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    target_tier = Column(String(20), nullable=True)
    min_purchase_amount = Column(Numeric(10, 2), nullable=True)


# ============================================================================
# API Models (Pydantic)
# ============================================================================


class LoyaltyCustomerCreate(BaseModel):
    """Request to create a loyalty customer."""

    customer_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    notes: Optional[str] = None


class LoyaltyCustomerInfo(BaseModel):
    """Loyalty customer information."""

    id: int
    customer_name: str
    email: Optional[str]
    phone: Optional[str]
    card_number: str
    qr_code: Optional[str]
    points_balance: int
    lifetime_points: int
    tier: str
    date_of_birth: Optional[datetime]
    enrollment_date: datetime
    last_activity: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class EarnPointsRequest(BaseModel):
    """Request to earn points."""

    customer_id: int
    amount_spent: Decimal
    reference_id: Optional[int] = None


class RedeemPointsRequest(BaseModel):
    """Request to redeem points."""

    customer_id: int
    points: int
    reward_id: Optional[int] = None
    description: Optional[str] = None


class LoyaltyTransactionInfo(BaseModel):
    """Loyalty transaction information."""

    id: int
    customer_id: int
    transaction_type: str
    points: int
    points_before: int
    points_after: int
    reference_type: Optional[str]
    reference_id: Optional[int]
    amount_spent: Optional[Decimal]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RewardInfo(BaseModel):
    """Reward information."""

    id: int
    reward_name: str
    description: Optional[str]
    points_required: int
    reward_type: str
    reward_value: Optional[Decimal]
    is_active: bool

    class Config:
        from_attributes = True


class CampaignCreate(BaseModel):
    """Request to create a campaign."""

    campaign_name: str
    description: Optional[str] = None
    campaign_type: str = Field(..., pattern="^(double_points|bonus_points)$")
    points_multiplier: Optional[Decimal] = None
    bonus_points: Optional[int] = None
    start_date: datetime
    end_date: datetime
    target_tier: Optional[str] = None
    min_purchase_amount: Optional[Decimal] = None


# ============================================================================
# Plugin Class
# ============================================================================


class LoyaltyProgramPlugin(BasePlugin):
    """
    Loyalty Program Plugin.

    Provides comprehensive customer loyalty management.
    """

    def __init__(self):
        super().__init__()
        self.config = {
            "points_per_euro": 10,
            "enable_tiers": True,
            "birthday_bonus_points": 100,
            "points_expiry_months": 12,
            "redemption_rate": 100,  # 100 points = 1 EUR
        }

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="loyalty_program",
            version="1.0.0",
            description="Customer loyalty program with points and rewards",
            author="Stumpf.works",
            dependencies=[],
        )

    def get_name(self) -> str:
        """Get plugin name."""
        return "loyalty_program"

    def get_display_name(self) -> str:
        """Get plugin display name."""
        return "Treueprogramm"

    def get_description(self) -> str:
        """Get plugin description."""
        return "Kundenbindungsprogramm mit Punktesystem und Prämien"

    def get_version(self) -> str:
        """Get plugin version."""
        return self.metadata.version

    def get_author(self) -> str:
        """Get plugin author."""
        return self.metadata.author

    def get_category(self) -> str:
        """Get plugin category."""
        return "marketing"

    def get_requires(self) -> List[str]:
        """Get plugin dependencies."""
        return self.metadata.dependencies

    def get_config_schema(self) -> Optional[Dict]:
        """Get plugin configuration schema."""
        return {
            "type": "object",
            "properties": {
                "points_per_euro": {
                    "type": "integer",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 1000,
                    "description": "Punkte pro Euro Umsatz",
                },
                "enable_tiers": {
                    "type": "boolean",
                    "default": True,
                    "description": "Tier-System aktivieren",
                },
                "birthday_bonus_points": {
                    "type": "integer",
                    "default": 100,
                    "minimum": 0,
                    "maximum": 10000,
                    "description": "Geburtstags-Bonus Punkte",
                },
                "points_expiry_months": {
                    "type": "integer",
                    "default": 12,
                    "minimum": 0,
                    "maximum": 120,
                    "description": "Punkte verfallen nach (Monaten), 0 = nie",
                },
                "redemption_rate": {
                    "type": "integer",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 10000,
                    "description": "Punkte für 1€ Wert",
                },
            },
        }

    def configure(self, config: Dict):
        """Configure plugin with settings."""
        points_per_euro = config.get("points_per_euro", 10)
        if points_per_euro < 1 or points_per_euro > 1000:
            raise ValueError("points_per_euro must be between 1 and 1000")

        self.config.update(config)
        logger.info("loyalty_program_configured", config=self.config)

    def get_models(self) -> List[Any]:
        """Return database models."""
        return [
            LoyaltyCustomer,
            LoyaltyTransaction,
            LoyaltyTier,
            LoyaltyReward,
            LoyaltyCampaign,
        ]

    async def on_enable(self):
        """Called when plugin is enabled."""
        logger.info("loyalty_program_enabled")

    async def on_disable(self):
        """Called when plugin is disabled."""
        logger.info("loyalty_program_disabled")

    def _calculate_tier(self, lifetime_points: int) -> str:
        """Calculate customer tier based on lifetime points."""
        if not self.config["enable_tiers"]:
            return "bronze"

        if lifetime_points >= 10000:
            return "platinum"
        elif lifetime_points >= 5000:
            return "gold"
        elif lifetime_points >= 2000:
            return "silver"
        else:
            return "bronze"

    def _calculate_points(self, amount: Decimal, tier: str = "bronze") -> int:
        """Calculate points for a purchase amount."""
        base_points = int(amount * self.config["points_per_euro"])

        # Apply tier multiplier if enabled
        if self.config["enable_tiers"]:
            tier_multipliers = {
                "bronze": 1.0,
                "silver": 1.2,
                "gold": 1.5,
                "platinum": 2.0,
            }
            multiplier = tier_multipliers.get(tier, 1.0)
            return int(base_points * multiplier)

        return base_points

    def get_router(self) -> APIRouter:
        """Return API router with endpoints."""
        router = APIRouter(prefix="/loyalty", tags=["Marketing - Loyalty Program"])

        # ============================================================================
        # Customer Endpoints
        # ============================================================================

        @router.post("/customers", status_code=status.HTTP_201_CREATED)
        async def create_customer(
            request: LoyaltyCustomerCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Register a new loyalty customer."""
            # Generate card number
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            card_number = f"LC-{timestamp}"

            # Generate QR code data
            qr_code = f"LOYALTY:{current_user.tenant_id}:{card_number}"

            # Create customer
            customer = LoyaltyCustomer(
                tenant_id=current_user.tenant_id,
                customer_name=request.customer_name,
                email=request.email,
                phone=request.phone,
                card_number=card_number,
                qr_code=qr_code,
                date_of_birth=request.date_of_birth,
                enrollment_date=datetime.utcnow(),
                notes=request.notes,
            )
            db.add(customer)
            await db.flush()

            # Give welcome bonus
            welcome_points = 50
            transaction = LoyaltyTransaction(
                tenant_id=current_user.tenant_id,
                customer_id=customer.id,
                transaction_type="bonus",
                points=welcome_points,
                points_before=0,
                points_after=welcome_points,
                reference_type="welcome",
                description="Welcome bonus",
                created_by=current_user.id,
            )
            db.add(transaction)

            customer.points_balance = welcome_points
            customer.lifetime_points = welcome_points

            await db.commit()
            await db.refresh(customer)

            logger.info(
                "loyalty_customer_created",
                customer_id=customer.id,
                card_number=card_number,
            )

            return {
                "id": customer.id,
                "card_number": card_number,
                "qr_code": qr_code,
                "welcome_bonus": welcome_points,
            }

        @router.get("/customers/{customer_id}", response_model=LoyaltyCustomerInfo)
        async def get_customer(
            customer_id: int,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get customer information and points balance."""
            result = await db.execute(
                select(LoyaltyCustomer).where(
                    LoyaltyCustomer.id == customer_id,
                    LoyaltyCustomer.tenant_id == current_user.tenant_id,
                )
            )
            customer = result.scalar_one_or_none()

            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found",
                )

            return LoyaltyCustomerInfo(
                id=customer.id,
                customer_name=customer.customer_name,
                email=customer.email,
                phone=customer.phone,
                card_number=customer.card_number,
                qr_code=customer.qr_code,
                points_balance=customer.points_balance,
                lifetime_points=customer.lifetime_points,
                tier=customer.tier,
                date_of_birth=customer.date_of_birth,
                enrollment_date=customer.enrollment_date,
                last_activity=customer.last_activity,
                is_active=customer.is_active,
            )

        # ============================================================================
        # Points Endpoints
        # ============================================================================

        @router.post("/earn")
        async def earn_points(
            request: EarnPointsRequest,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Award points for a purchase."""
            # Get customer
            result = await db.execute(
                select(LoyaltyCustomer).where(
                    LoyaltyCustomer.id == request.customer_id,
                    LoyaltyCustomer.tenant_id == current_user.tenant_id,
                )
            )
            customer = result.scalar_one_or_none()

            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found",
                )

            # Calculate points
            points = self._calculate_points(request.amount_spent, customer.tier)

            # Check for active campaigns
            now = datetime.utcnow()
            campaigns_result = await db.execute(
                select(LoyaltyCampaign).where(
                    LoyaltyCampaign.tenant_id == current_user.tenant_id,
                    LoyaltyCampaign.is_active == True,  # noqa
                    LoyaltyCampaign.start_date <= now,
                    LoyaltyCampaign.end_date >= now,
                )
            )
            campaigns = campaigns_result.scalars().all()

            for campaign in campaigns:
                if (
                    campaign.campaign_type == "double_points"
                    and campaign.points_multiplier
                ):
                    points = int(points * float(campaign.points_multiplier))
                elif campaign.campaign_type == "bonus_points" and campaign.bonus_points:
                    points += campaign.bonus_points

            # Create transaction
            points_before = customer.points_balance
            points_after = points_before + points

            transaction = LoyaltyTransaction(
                tenant_id=current_user.tenant_id,
                customer_id=customer.id,
                transaction_type="earn",
                points=points,
                points_before=points_before,
                points_after=points_after,
                reference_type="sale",
                reference_id=request.reference_id,
                amount_spent=request.amount_spent,
                description=f"Purchase: {request.amount_spent}€",
                expires_at=(
                    datetime.utcnow()
                    + timedelta(days=self.config["points_expiry_months"] * 30)
                    if self.config["points_expiry_months"] > 0
                    else None
                ),
                created_by=current_user.id,
            )
            db.add(transaction)

            # Update customer
            customer.points_balance = points_after
            customer.lifetime_points += points
            customer.last_activity = datetime.utcnow()

            # Update tier
            new_tier = self._calculate_tier(customer.lifetime_points)
            if new_tier != customer.tier:
                customer.tier = new_tier
                logger.info(
                    "customer_tier_upgraded",
                    customer_id=customer.id,
                    old_tier=customer.tier,
                    new_tier=new_tier,
                )

            await db.commit()

            logger.info(
                "loyalty_points_earned",
                customer_id=customer.id,
                points=points,
                amount=float(request.amount_spent),
            )

            return {
                "customer_id": customer.id,
                "points_earned": points,
                "points_balance": points_after,
                "tier": customer.tier,
            }

        @router.post("/redeem")
        async def redeem_points(
            request: RedeemPointsRequest,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Redeem points for rewards."""
            # Get customer
            result = await db.execute(
                select(LoyaltyCustomer).where(
                    LoyaltyCustomer.id == request.customer_id,
                    LoyaltyCustomer.tenant_id == current_user.tenant_id,
                )
            )
            customer = result.scalar_one_or_none()

            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found",
                )

            # Check sufficient points
            if customer.points_balance < request.points:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient points",
                )

            # Get reward if specified
            reward = None
            if request.reward_id:
                reward_result = await db.execute(
                    select(LoyaltyReward).where(
                        LoyaltyReward.id == request.reward_id,
                        LoyaltyReward.tenant_id == current_user.tenant_id,
                    )
                )
                reward = reward_result.scalar_one_or_none()

                if not reward or not reward.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Reward not found or inactive",
                    )

                if reward.points_required != request.points:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Points mismatch",
                    )

                # Update reward redemption count
                reward.redemption_count += 1

            # Create transaction
            points_before = customer.points_balance
            points_after = points_before - request.points

            transaction = LoyaltyTransaction(
                tenant_id=current_user.tenant_id,
                customer_id=customer.id,
                transaction_type="redeem",
                points=-request.points,
                points_before=points_before,
                points_after=points_after,
                reference_type="reward",
                reference_id=request.reward_id,
                description=request.description
                or (reward.reward_name if reward else "Redemption"),
                created_by=current_user.id,
            )
            db.add(transaction)

            # Update customer
            customer.points_balance = points_after
            customer.last_activity = datetime.utcnow()

            await db.commit()

            logger.info(
                "loyalty_points_redeemed",
                customer_id=customer.id,
                points=request.points,
                reward_id=request.reward_id,
            )

            # Calculate discount value
            discount_value = float(request.points / self.config["redemption_rate"])

            return {
                "customer_id": customer.id,
                "points_redeemed": request.points,
                "points_balance": points_after,
                "discount_value": discount_value,
            }

        # ============================================================================
        # Transaction History
        # ============================================================================

        @router.get("/history", response_model=List[LoyaltyTransactionInfo])
        async def get_transaction_history(
            customer_id: int,
            limit: int = Query(50, le=500),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get customer's transaction history."""
            result = await db.execute(
                select(LoyaltyTransaction)
                .where(
                    LoyaltyTransaction.customer_id == customer_id,
                    LoyaltyTransaction.tenant_id == current_user.tenant_id,
                )
                .order_by(LoyaltyTransaction.created_at.desc())
                .limit(limit)
            )
            transactions = result.scalars().all()

            return [
                LoyaltyTransactionInfo(
                    id=t.id,
                    customer_id=t.customer_id,
                    transaction_type=t.transaction_type,
                    points=t.points,
                    points_before=t.points_before,
                    points_after=t.points_after,
                    reference_type=t.reference_type,
                    reference_id=t.reference_id,
                    amount_spent=t.amount_spent,
                    description=t.description,
                    created_at=t.created_at,
                )
                for t in transactions
            ]

        # ============================================================================
        # Rewards Endpoints
        # ============================================================================

        @router.get("/rewards", response_model=List[RewardInfo])
        async def list_rewards(
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """List available rewards."""
            result = await db.execute(
                select(LoyaltyReward).where(
                    LoyaltyReward.tenant_id == current_user.tenant_id,
                    LoyaltyReward.is_active == True,  # noqa
                )
            )
            rewards = result.scalars().all()

            return [
                RewardInfo(
                    id=r.id,
                    reward_name=r.reward_name,
                    description=r.description,
                    points_required=r.points_required,
                    reward_type=r.reward_type,
                    reward_value=r.reward_value,
                    is_active=r.is_active,
                )
                for r in rewards
            ]

        # ============================================================================
        # Campaign Endpoints
        # ============================================================================

        @router.post("/campaigns", status_code=status.HTTP_201_CREATED)
        async def create_campaign(
            request: CampaignCreate,
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Create a loyalty campaign."""
            campaign = LoyaltyCampaign(
                tenant_id=current_user.tenant_id,
                campaign_name=request.campaign_name,
                description=request.description,
                campaign_type=request.campaign_type,
                points_multiplier=request.points_multiplier,
                bonus_points=request.bonus_points,
                start_date=request.start_date,
                end_date=request.end_date,
                target_tier=request.target_tier,
                min_purchase_amount=request.min_purchase_amount,
            )
            db.add(campaign)
            await db.commit()
            await db.refresh(campaign)

            logger.info(
                "loyalty_campaign_created",
                campaign_id=campaign.id,
                name=request.campaign_name,
            )

            return {"id": campaign.id, "campaign_name": request.campaign_name}

        # ============================================================================
        # Tier Endpoints
        # ============================================================================

        @router.get("/tiers")
        async def get_tiers(
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db),
        ):
            """Get loyalty tier information."""
            result = await db.execute(
                select(LoyaltyTier).where(
                    LoyaltyTier.tenant_id == current_user.tenant_id,
                    LoyaltyTier.is_active == True,  # noqa
                )
            )
            tiers = result.scalars().all()

            if not tiers:
                # Return default tiers
                return [
                    {
                        "tier_name": "bronze",
                        "min_points": 0,
                        "points_multiplier": 1.0,
                        "discount_percentage": 0,
                    },
                    {
                        "tier_name": "silver",
                        "min_points": 2000,
                        "points_multiplier": 1.2,
                        "discount_percentage": 5,
                    },
                    {
                        "tier_name": "gold",
                        "min_points": 5000,
                        "points_multiplier": 1.5,
                        "discount_percentage": 10,
                    },
                    {
                        "tier_name": "platinum",
                        "min_points": 10000,
                        "points_multiplier": 2.0,
                        "discount_percentage": 15,
                    },
                ]

            return [
                {
                    "tier_name": t.tier_name,
                    "min_points": t.min_points,
                    "points_multiplier": float(t.points_multiplier),
                    "discount_percentage": float(t.discount_percentage),
                    "description": t.description,
                }
                for t in tiers
            ]

        return router


# ============================================================================
# Plugin Instance (for auto-discovery)
# ============================================================================

plugin = LoyaltyProgramPlugin()
