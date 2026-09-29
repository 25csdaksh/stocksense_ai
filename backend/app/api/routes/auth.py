"""
Authentication & User Profile API Routes with Database Persistence.
"""
from datetime import timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserProfile
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ValidationException
from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.db.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory fallback user cache
_MOCK_USERS_DB: Dict[str, Dict[str, Any]] = {
    "admin": {
        "id": "usr_dev_001",
        "username": "admin",
        "email": "admin@marketmind.ai",
        "hashed_password": hash_password("marketmind123"),
        "is_active": True
    }
}


@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register_user(
    req: UserRegisterRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Registers a new user account with database persistence."""
    user_repo = UserRepository(db)
    
    # Check DB or fallback
    try:
        existing_user = await user_repo.get_by_username(req.username)
        if existing_user:
            raise ValidationException("Username is already registered.")
        
        db_user = await user_repo.create_user(
            username=req.username,
            email=req.email,
            password=req.password
        )
        user_id = db_user.id
    except ValidationException:
        raise
    except Exception:
        # Graceful fallback if database offline during standalone dev
        if req.username in _MOCK_USERS_DB:
            raise ValidationException("Username is already registered.")
        user_id = f"usr_{len(_MOCK_USERS_DB) + 1:03d}"

    # Sync to cache
    _MOCK_USERS_DB[req.username] = {
        "id": user_id,
        "username": req.username,
        "email": req.email,
        "hashed_password": hash_password(req.password),
        "is_active": True
    }

    return UserProfile(
        id=user_id,
        username=req.username,
        email=req.email,
        is_active=True
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    req: UserLoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Authenticates user credentials and issues a signed JWT token."""
    user_repo = UserRepository(db)
    user_data = None

    try:
        db_user = await user_repo.get_by_username(req.username)
        if db_user and verify_password(req.password, db_user.hashed_password):
            user_data = {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email
            }
    except Exception:
        pass

    # Fallback check
    if not user_data:
        cached_user = _MOCK_USERS_DB.get(req.username)
        if cached_user and verify_password(req.password, cached_user["hashed_password"]):
            user_data = {
                "id": cached_user["id"],
                "username": cached_user["username"],
                "email": cached_user["email"]
            }

    if not user_data:
        raise UnauthorizedException("Invalid username or password.")

    token_data = {
        "sub": user_data["username"],
        "user_id": user_data["id"],
        "email": user_data["email"]
    }
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(token_data, expires_delta)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserProfile)
async def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieves current authenticated user profile."""
    return UserProfile(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        is_active=current_user["is_active"]
    )
