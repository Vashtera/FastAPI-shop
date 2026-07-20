from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from ..cache.redis import RedisCache
from ..repositories.products_repo import ProductRepo
from ..schemas.cart import CartCreate, CartItem, CartResponse, CartItemUpdate


class CartService:
    """
    Сервис для управления корзиной покупателя.

    В отличие от товаров/категорий, корзина НЕ хранится в PostgreSQL —
    Redis здесь является единственным источником данных, а не кэшем
    поверх основной БД. Поэтому в этом сервисе нет логики "инвалидации
    кэша" — все операции напрямую читают/пишут в Redis.

    Данные в Redis хранятся как hash по ключу "cart:{user_id}", где:
    - поле (field) — id товара (product_id), приводится к строке
    - значение (value) — количество этого товара (quantity)
    """

    def __init__(
        self,
        db: AsyncSession,
        cache_redis_url: str,
        cache_ttl_seconds: int,
    ):
        """
        Args:
            db: асинхронная сессия SQLAlchemy — нужна только чтобы
                проверять существование товаров и получать их данные
                (цену, название) из PostgreSQL
            cache_redis_url: строка подключения к Redis
            cache_ttl_seconds: время жизни корзины в секундах
                (после этого Redis сам удалит ключ)
        """
        self.session = ProductRepo(db)
        self.cache = RedisCache(cache_redis_url, cache_ttl_seconds=cache_ttl_seconds)

    async def add_to_cart(self, user_id: int, item: CartCreate) -> None:
        """
        Добавить товар в корзину пользователя.

        Сначала проверяет что товар реально существует в PostgreSQL —
        нет смысла класть в корзину несуществующий товар. Если товар
        уже был в корзине, RedisCache.add() увеличивает количество
        (через HINCRBY), а не перезаписывает его.

        Args:
            user_id: id пользователя, которому принадлежит корзина
            item: данные добавляемого товара (product_id и quantity)

        Raises:
            HTTPException 404: если товара с таким id не существует в БД
        """
        product = await self.session.get_by_id(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not founded",
            )

        await self.cache.add(user_id, item.product_id, item.quantity)

    async def update_cart_item(self, user_id: int, item: CartItemUpdate) -> None:
        """
        Обновить количество конкретного товара в корзине (перезаписать,
        а не прибавить — в отличие от add_to_cart).

        Args:
            user_id: id пользователя
            item: данные товара с новым количеством

        Raises:
            HTTPException 404: если product_id не передан
        """
        if not item.product_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not founded",
            )
        await self.cache.update(user_id, item.product_id, item.quantity)

    async def delete_from_cart(self, user_id: int, product_id: int) -> None:
        """
        Удалить один товар из корзины (одно поле хэша в Redis).

        Args:
            user_id: id пользователя
            product_id: id товара который нужно убрать из корзины

        Raises:
            HTTPException 404: если product_id не передан
        """
        if not product_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not founded",
            )
        await self.cache.delete(user_id, product_id)

    async def clear_all_cart(self, user_id: int) -> None:
        """
        Полностью очистить корзину пользователя — удаляет весь ключ
        "cart:{user_id}" из Redis целиком

        Args:
            user_id: id пользователя
        """
        await self.cache.clear(user_id)

    async def get_cart_details(self, user_id: int) -> CartResponse:
        """
        Получить полную информацию о корзине: список товаров с их
        актуальными названиями/ценами, общую сумму и количество.

        Redis хранит только product_id и quantity — название, цену
        и картинку товара нужно каждый раз подтягивать из PostgreSQL,
        потому что в Redis эти данные не дублируются (иначе при
        изменении цены товара в БД корзина показывала бы старую цену).

        Args:
            user_id: id пользователя

        Returns:
            CartResponse с товарами, итоговой суммой и количеством.
            Если корзина пустая — возвращает пустой CartResponse,
            а не ошибку.
        """
        cart_data = await self.cache.get(user_id)

        if not cart_data:
            return CartResponse(items=[], total=0.0, items_count=0)

        # Redis хранит ключи и значения хэша как строки, даже если
        # изначально передавались int — здесь конвертируем обратно,
        # иначе product_id не совпадёт с id из PostgreSQL (int).
        cart_data = {
            int(product_id): int(quantity)
            for product_id, quantity in cart_data.items()
        }

        product_ids = list(cart_data.keys())
        products = await self.session.get_multiple_by_ids(product_ids)
        products_dict = {product.id: product for product in products}

        cart_items = []
        total_price = 0.0
        total_items = 0

        for product_id, quantity in cart_data.items():
            # Если товар был удалён из БД продавцом после того как
            # его положили в корзину — он просто не попадёт в вывод.
            if product_id in products_dict:
                product = products_dict[product_id]
                subtotal = product.price * quantity

                cart_item = CartItem(
                    product_id=product.id,
                    quantity=quantity,
                    name=product.name,
                    price=product.price,
                    subtotal=subtotal,
                    image_url=product.image_url,
                )

                cart_items.append(cart_item)
                total_price += float(subtotal)
                total_items += quantity

        return CartResponse(
            items=cart_items,
            total=round(total_price),
            items_count=total_items,
        )