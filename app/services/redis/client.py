from functools import lru_cache

import redis.asyncio as redis

from app.core.config import get_settings


@lru_cache
def get_redis_client() -> redis.Redis:
    settings = get_settings()
    return redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)