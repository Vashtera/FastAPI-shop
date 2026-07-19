import redis.asyncio as Redis
import json


class RedisCache:
    def __init__(self, redis_url: str, cache_ttl_seconds: int | None = 86400):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.cache_ttl_seconds = cache_ttl_seconds


    async def add(self, user_id: int, product_id: int, quantity: int) -> None:
        await self.redis.hincrby(f"cart: {user_id}", product_id, quantity)


    async def set(self, key: str, value: dict) -> None:
        await self.redis.set(key, json.dumps(value), ex=self.cache_ttl_seconds) 


    async def get(self, key: str) -> dict:
        return await json.loads(self.redis.get(key)) # type: ignore[call-arg]


    async def delete(self, key: str) -> None:
        await self.redis.delete(key)