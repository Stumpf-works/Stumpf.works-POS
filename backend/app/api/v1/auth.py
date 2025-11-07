"""
Authentication API Endpoints
Login, register, refresh token, etc.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.security import (create_token_pair, decode_token,
                               get_password_hash, verify_password,
                               verify_token_type)
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, Token
from app.schemas.user import UserCreate, UserLogin, UserPINLogin, UserResponse

logger = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    Creates a new user account in the current tenant.
    """
    tenant_id = getattr(request.state, "tenant_id", None)

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No tenant context"
        )

    # Check if user already exists
    result = await db.execute(
        select(User).where(
            or_(User.email == user_data.email, User.username == user_data.username),
            User.tenant_id == tenant_id,
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role,
        pin_code=user_data.pin_code,
        tenant_id=tenant_id,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(
        "user_registered",
        user_id=new_user.id,
        username=new_user.username,
        tenant_id=tenant_id,
    )

    return new_user


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with username/email and password.

    Returns access and refresh tokens.
    """
    tenant_id = getattr(request.state, "tenant_id", None)

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No tenant context"
        )

    # Find user by email or username
    result = await db.execute(
        select(User).where(
            or_(
                User.email == credentials.username_or_email,
                User.username == credentials.username_or_email,
            ),
            User.tenant_id == tenant_id,
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(
            "login_failed",
            identifier=credentials.username_or_email,
            tenant_id=tenant_id,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    # Create tokens
    tokens = create_token_pair(
        user_id=user.id,
        tenant_id=tenant_id,
        role=user.role.value,
    )

    logger.info(
        "user_logged_in",
        user_id=user.id,
        username=user.username,
        tenant_id=tenant_id,
    )

    return tokens


@router.post("/login/pin", response_model=Token)
async def login_with_pin(
    request: Request,
    credentials: UserPINLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Quick login with PIN code (for POS terminals).

    Returns access and refresh tokens.
    """
    tenant_id = getattr(request.state, "tenant_id", None)

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No tenant context"
        )

    # Find user by PIN
    result = await db.execute(
        select(User).where(
            User.pin_code == credentials.pin_code, User.tenant_id == tenant_id
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(
            "pin_login_failed",
            pin=credentials.pin_code[:2] + "***",  # Log partial PIN
            tenant_id=tenant_id,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid PIN code",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    if not user.can_access_pos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have POS access",
        )

    # Create tokens
    tokens = create_token_pair(
        user_id=user.id,
        tenant_id=tenant_id,
        role=user.role.value,
    )

    logger.info(
        "user_logged_in_with_pin",
        user_id=user.id,
        username=user.username,
        tenant_id=tenant_id,
    )

    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
):
    """
    Refresh access token using refresh token.

    Returns new access and refresh tokens.
    """
    # Verify refresh token
    if not verify_token_type(refresh_request.refresh_token, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode token to get user info
    payload = decode_token(refresh_request.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new token pair
    tokens = create_token_pair(
        user_id=int(payload["sub"]),
        tenant_id=payload["tenant_id"],
        role=payload.get("role"),
    )

    logger.info(
        "token_refreshed",
        user_id=payload["sub"],
        tenant_id=payload["tenant_id"],
    )

    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user information.
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
):
    """
    Logout current user.

    In a stateless JWT setup, logout is handled client-side by deleting the token.
    This endpoint is for logging purposes.
    """
    logger.info(
        "user_logged_out",
        user_id=current_user.id,
        username=current_user.username,
        tenant_id=current_user.tenant_id,
    )

    return {"message": "Successfully logged out"}
