"""
Redis Async Client and In-Memory Cache Fallback Manager.
"""
import json
from typing import Any, Optional
import redis.asyncio as aioredis
from config import settings
from core.logger import logger


class RedisManager:
    """
    Manages Redis connection with a graceful in-memory dictionary fallback
    if Redis server is unavailable.
    """

    def __init__(self):
        self.client: Optional[aioredis.Redis] = None
        self._memory_cache: dict = {}

    async def connect(self):
        try:
            self.client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2.0
            )
            await self.client.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning(f"Redis not reachable ({e}). Using in-memory fallback cache.")
            self.client = None

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        if self.client:
            try:
                return await self.client.get(key)
            except Exception:
                return self._memory_cache.get(key)
        return self._memory_cache.get(key)

    async def set(self, key: str, value: str, expire: int = 300) -> bool:
        if self.client:
            try:
                return await self.client.set(key, value, ex=expire)
            except Exception:
                self._memory_cache[key] = value
                return True
        self._memory_cache[key] = value
        return True

    async def get_json(self, key: str) -> Optional[Any]:
        val = await self.get(key)
        if val:
            try:
                return json.loads(val)
            except Exception:
                return None
        return None

    async def set_json(self, key: str, data: Any, expire: int = 300) -> bool:
        try:
            val = json.dumps(data)
            return await self.set(key, val, expire=expire)
        except Exception:
            return False


redis_client = RedisManager()
