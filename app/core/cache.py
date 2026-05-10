import json
from typing import Any

from loguru import logger
from redis.asyncio import Redis


class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Any | None:
        value = await self.redis.get(key)
        if value is None:
            return None
        logger.debug(f"Cache HIT: {key}")
        return json.loads(value)

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        await self.redis.setex(key, ttl, json.dumps(value))
        logger.debug(f"Cache SET: {key} (ttl={ttl}s)")

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
        logger.debug(f"Cache DELETE: {key}")

    async def delete_pattern(self, pattern: str) -> None:
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
            logger.debug(f"Cache DELETE pattern: {pattern} ({len(keys)} keys)")
