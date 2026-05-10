from fastapi import HTTPException, Request, status
from loguru import logger

from app.core.redis import get_redis


async def rate_limit(
    request: Request,
    key_prefix: str,
    max_requests: int,
    window_seconds: int,
) -> None:
    redis = await get_redis()

    # Ключ по IP адресу
    client_ip = request.client.host
    key = f"rate_limit:{key_prefix}:{client_ip}"

    # Атомарно увеличиваем счётчик
    count = await redis.incr(key)

    # При первом запросе устанавливаем TTL
    if count == 1:
        await redis.expire(key, window_seconds)

    logger.debug(f"Rate limit: {key} = {count}/{max_requests}")

    if count > max_requests:
        retry_after = await redis.ttl(key)
        logger.warning(f"Rate limit exceeded: {key}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )
