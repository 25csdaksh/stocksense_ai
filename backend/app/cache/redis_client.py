"""
Redis Cache Client with Graceful In-Memory Fallback.
Allows MarketMind AI to execute fully standalone without requiring an active Redis server.
"""
import json
import time
from typing import Any, Optional, Dict
from app.core.config import settings
from app.core.logging import logger

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None


class RedisCacheClient:
    """
    Asynchronous caching adapter with Redis connection pool
    and in-memory fallback store.
    """

    def __init__(self):
        self._client = None
        self._memory_cache: Dict[str, Any] = {}
        self._memory_ttl: Dict[str, float] = {}
        self.is_connected: bool = False

    async def connect(self):
        if not settings.CACHE_ENABLED:
            logger.info("Cache is disabled in settings.")
            return

        if aioredis is not None and settings.REDIS_URL:
            try:
                self._client = aioredis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=1.5
                )
                await self._client.ping()
                self.is_connected = True
                logger.info("Connected to Redis cache server.")
                return
            except Exception as err:
                logger.warning(f"Redis connection failed ({err}). Using in-memory fallback cache.")
                self._client = None
                self.is_connected = False
        else:
            logger.info("Using in-memory cache storage.")

    async def disconnect(self):
        if self._client:
            try:
                await self._client.close()
            except Exception:
                pass
            self.is_connected = False

    async def get(self, key: str) -> Optional[str]:
        if self._client and self.is_connected:
            try:
                return await self._client.get(key)
            except Exception:
                pass

        # In-memory retrieval with TTL expiration check
        if key in self._memory_cache:
            expire_at = self._memory_ttl.get(key, 0)
            if expire_at == 0 or time.time() < expire_at:
                return self._memory_cache[key]
            else:
                # Expired
                self._memory_cache.pop(key, None)
                self._memory_ttl.pop(key, None)
        return None

    async def set(self, key: str, value: str, expire: int = 300) -> bool:
        if self._client and self.is_connected:
            try:
                await self._client.set(key, value, ex=expire)
                return True
            except Exception:
                pass

        # In-memory storage
        self._memory_cache[key] = value
        self._memory_ttl[key] = time.time() + expire if expire > 0 else 0
        return True

    async def get_json(self, key: str) -> Optional[Any]:
        val = await self.get(key)
        if val is not None:
            try:
                return json.loads(val)
            except Exception:
                return None
        return None

    async def set_json(self, key: str, data: Any, expire: int = 300) -> bool:
        try:
            val_str = json.dumps(data)
            return await self.set(key, val_str, expire=expire)
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        if self._client and self.is_connected:
            try:
                await self._client.delete(key)
            except Exception:
                pass
        self._memory_cache.pop(key, None)
        self._memory_ttl.pop(key, None)
        return True


cache_client = RedisCacheClient()
redis_client = cache_client
