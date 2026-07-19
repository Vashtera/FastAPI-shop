import redis.asyncio as Redis


class RedisCache:
    """
    Обёртка над Redis для хранения корзины покупателя.

    Каждый пользователь имеет свой ключ вида "cart:{user_id}",
    под которым хранится Redis hash (аналог словаря):
    - поле (field) — id товара, приводится к строке, так как
      Redis hash хранит и ключи, и значения только как строки
    - значение (value) — количество этого товара в корзине

    В отличие от кэша поверх PostgreSQL (например для категорий),
    здесь нет инвалидации — Redis является единственным местом,
    где живут данные о корзине, а не временной копией чего-то
    из основной БД.
    """

    def __init__(self, redis_url: str, cache_ttl_seconds: int = 86400):
        """
        Args:
            redis_url: адрес подключения к Redis, например
                "redis://localhost:6379/0"
            cache_ttl_seconds: через сколько секунд неактивная
                корзина будет автоматически удалена Redis'ом
                (по умолчанию 86400 секунд = 24 часа)
        """
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.cache_ttl_seconds = cache_ttl_seconds

    async def add(self, user_id: int, product_id: int, quantity: int) -> None:
        """
        Добавить товар в корзину или увеличить его количество,
        если он там уже есть.

        HINCRBY атомарно прибавляет quantity к текущему значению поля.
        Если поля ещё нет — Redis сам создаёт его со значением quantity.

        После каждого добавления обновляется TTL ключа (EXPIRE) —
        это продлевает жизнь корзины при каждом взаимодействии
        с ней, чтобы активные корзины не удалялись раньше времени.

        Args:
            user_id: id пользователя
            product_id: id добавляемого товара
            quantity: на сколько увеличить количество
        """
        key = f"cart:{user_id}"
        await self.redis.hincrby(key, str(product_id), quantity)
        await self.redis.expire(key, self.cache_ttl_seconds)

    async def update(self, user_id: int, product_id: int, quantity: int) -> None:
        """
        Установить точное количество товара (перезаписать, а не
        прибавить — в отличие от add()).

        HSET просто заменяет значение поля, не важно было оно
        раньше или нет.

        Args:
            user_id: id пользователя
            product_id: id товара
            quantity: новое количество (полностью заменяет старое)
        """
        key = f"cart:{user_id}"
        await self.redis.hset(key, str(product_id), quantity)

    async def get(self, user_id: int) -> dict:
        """
        Получить всю корзину пользователя целиком.

        HGETALL возвращает словарь {field: value} — все товары
        и их количества в одном запросе. Если корзины не существует
        (ключ не найден) — возвращает пустой словарь, а не None
        или ошибку.

        Важно: и ключи, и значения возвращаются как строки —
        конвертация в int должна происходить на уровне вызывающего
        кода (сервиса), а не здесь.

        Args:
            user_id: id пользователя

        Returns:
            Словарь вида {"product_id_как_строка": "quantity_как_строка"}
        """
        key = f"cart:{user_id}"
        return await self.redis.hgetall(key)

    async def delete(self, user_id: int, product_id: int) -> None:
        """
        Удалить один товар из корзины (одно поле хэша),
        не затрагивая остальные товары.

        HDEL — в отличие от обычного DEL, удаляет конкретное поле
        внутри хэша, а не весь ключ целиком.

        Args:
            user_id: id пользователя
            product_id: id товара который нужно убрать
        """
        key = f"cart:{user_id}"
        await self.redis.hdel(key, str(product_id))

    async def clear(self, user_id: int) -> None:
        """
        Полностью очистить корзину — удаляет ключ "cart:{user_id}"
        целиком со всеми товарами внутри.

        Args:
            user_id: id пользователя
        """
        key = f"cart:{user_id}"
        await self.redis.delete(key)