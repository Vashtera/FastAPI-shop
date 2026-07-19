import redis.asyncio as Redis


class RedisCache:
    def __init__(self, redis_url: str, cache_ttl_seconds: int = 86400):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.cache_ttl_seconds = cache_ttl_seconds

    async def add(self, user_id: int, product_id: int, quantity: int) -> None:
        key = f"cart:{user_id}"
        await self.redis.hincrby(key, str(product_id), quantity)
        await self.redis.expire(key, self.cache_ttl_seconds)

    async def update(self, user_id: int, product_id: int, quantity: int) -> None:
        key = f"cart:{user_id}"
        await self.redis.hset(key, str(product_id), quantity)

    async def get(self, user_id: int) -> dict:
        key = f"cart:{user_id}"
        return await self.redis.hgetall(key)

    async def delete(self, user_id: int, product_id: int) -> None:
        key = f"cart:{user_id}"
        await self.redis.hdel(key, str(product_id))

    async def clear(self, user_id: int) -> None:
        key = f"cart:{user_id}"
        await self.redis.delete(key)