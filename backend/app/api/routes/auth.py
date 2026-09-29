"""
Authentication & User Profile API Routes.
"""
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserProfile
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.core.exceptions import UnauthorizedException, ValidationException
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory user store for Phase 1 development
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
async def register_user(req: UserRegisterRequest):
    """Registers a new user account."""
    if req.username in _MOCK_USERS_DB:
        raise ValidationException("Username is already registered.")

    user_id = f"usr_{len(_MOCK_USERS_DB) + 1:03d}"
    user_entry = {
        "id": user_id,
        "username": req.username,
        "email": req.email,
        "hashed_password": hash_password(req.password),
        "is_active": True
    }
    _MOCK_USERS_DB[req.username] = user_entry
    return UserProfile(
        id=user_id,
        username=req.username,
        email=req.email,
        is_active=True
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(req: UserLoginRequest):
    """Authenticates user credentials and issues a signed JWT token."""
    user = _MOCK_USERS_DB.get(req.username)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise UnauthorizedException("Invalid username or password.")

    token_data = {
        "sub": user["username"],
        "user_id": user["id"],
        "email": user["email"]
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
