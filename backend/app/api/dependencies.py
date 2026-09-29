"""
FastAPI Dependency Injection Providers: Auth, Cache, and Context.
"""
from typing import Optional, Dict, Any
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.cache.redis_client import redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Validates Bearer token from request.
    In Phase 1 development mode, returns authenticated user claims.
    """
    if not token:
        raise UnauthorizedException("Authentication token required.")

    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Invalid or expired authentication token.")

    username = payload.get("sub")
    if not username:
        raise UnauthorizedException("Token payload missing subject.")

    return {
        "id": payload.get("user_id", "usr_dev_001"),
        "username": username,
        "email": payload.get("email", f"{username}@marketmind.ai"),
        "is_active": True
    }


async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[Dict[str, Any]]:
    """Optional authentication dependency for endpoints that allow anonymous access."""
    if not token:
        return None
    try:
        return await get_current_user(token)
    except UnauthorizedException:
        return None


async def get_cache():
    """Provides the async Redis / in-memory cache client."""
    return redis_client
