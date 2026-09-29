"""
Security utilities, Rate Limiting & Header configurations.
"""
from fastapi import Request, HTTPException, status
from core.redis import redis_client


async def rate_limiter(request: Request, max_requests: int = 120, window_seconds: int = 60):
    """
    Sliding window IP-based rate limiter using Redis / in-memory cache.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    key = f"ratelimit:{client_ip}"
    
    current = await redis_client.get(key)
    if current is not None:
        count = int(current)
        if count >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please wait before making more requests."
            )
        await redis_client.set(key, str(count + 1), expire=window_seconds)
    else:
        await redis_client.set(key, "1", expire=window_seconds)
