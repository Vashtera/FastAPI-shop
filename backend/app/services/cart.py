from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from ..cache.redis import RedisCache
from ..repositories.products_repo import ProductRepo
from ..schemas.cart import CartCreate, CartItem, CartResponse


class CartService:
    """
    Сервис для управления корзиной покупателя.
    Корзина хранится как словарь dict[int, int] где:
    - ключ: id продукта
    - значение: количество товара
    """
    def __init__(self, 
                 db: AsyncSession, 
                 cache_redis_url: str, 
                 cache_ttl_seconds: int,
                 cache_tasks_key: str
                 ):
        self.session = ProductRepo(db)
        self.cache = RedisCache(cache_redis_url, cache_ttl_seconds=86400)
        self.cache_tasks_key = cache_tasks_key

    async def add_to_cart(self, user_id: int, item: CartCreate) -> dict:
        """
        
        """
        product_cache = self.cache.get(self.cache_tasks_key) # Проверка наличия в кеше Redis
        if product_cache is not None:
            return await product_cache
        
        product = await self.session.get_by_id(item.product_id) # Взятие данных из БД если в кеше нету
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not founded"
            )

        await self.cache.add(user_id, item.product_id, item.quantity)
    

    def update_cart_item(self, cart_data: dict[int, int], item: CartCreate) -> dict[int, int]:
        """
        Обновить количество товара в корзине.

        Args:
            cart_data: текущее состояние корзины
            item: данные товара с новым количеством

        Returns:
            Обновлённая корзина

        Raises:
            HTTPException 404: если товар не найден в корзине
        """
        if item.product_id not in cart_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not founded"
            )
        cart_data[item.product_id] = item.quantity
        return cart_data
    
    def remove_from_cart(self, cart_data: dict[int, int], product_id: int) ->dict[int, int]:
        """
        Удалить товар из корзины.

        Args:
            cart_data: текущее состояние корзины
            product_id: id удаляемого товара

        Returns:
            Корзина без удалённого товара

        Raises:
            HTTPException 404: если товар не найден в корзине
        """
        if product_id not in cart_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not founded"
            )
        del cart_data[product_id]
        return cart_data
    
    async def get_cart_details(self, cart_data: dict[int, int]) -> CartResponse:
        """
        Получить детальную информацию о корзине с ценами и итогами.

        Args:
            cart_data: текущее состояние корзины

        Returns:
            CartResponse с полной информацией о товарах, общей суммой и количеством
        """
        if not cart_data:
            return CartResponse(items=[], total=0.0, items_count=0)
        
        product_ids = list(cart_data.keys())
        products = await self.session.get_multiple_by_ids(product_ids)
        products_dict = {product.id: product for product in products}

        cart_items = []
        total_price = 0.0
        total_items = 0

        for product_id, quantity in cart_data.items():
            if product_id in products_dict:
                product = products_dict[product_id]
                subtotal = product.price * quantity

                cart_item = CartItem(product_id=product.id, quantity=quantity, name=product.name,
                                     price=product.price, subtotal=subtotal, 
                                     image_url=product.image_url
                                    )
                
                cart_items.append(cart_item)
                total_price += subtotal
                total_items += quantity
        
        return CartResponse(items=cart_items, total=round(total_price), items_count=total_items)