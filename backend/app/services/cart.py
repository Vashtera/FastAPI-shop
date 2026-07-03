from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from ..repositories.products_repo import ProductRepo
from ..schemas.cart import CartCreate, CartItem, CartItemUpdate, CartResponse


class CartService:
    def __init__(self, db: AsyncSession):
        self.session = ProductRepo(db)

#тут dict[int, int] - означаем первое - id продукта, а второй int это количество товара
    async def add_to_cart(self, cart_data: dict[int, int], item: CartCreate) -> dict[int, int]:
        product = await self.session.get_by_id(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not founded"
            )

        if item.product_id in cart_data:
            cart_data[item.product_id] += item.quantity
        else:
            cart_data[item.product_id] = item.quantity

        return cart_data
    
    def update_cart_item(self, cart_data: dict[int, int], item: CartCreate) -> dict[int, int]:
        if item.product_id not in cart_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not founded"
            )
        cart_data[item.product_id] = item.quantity
        return cart_data
    
    def remove_from_cart(self, cart_data: dict[int, int], product_id: int) ->dict[int, int]:
        if product_id not in cart_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not founded"
            )
        del cart_data[product_id]
        return cart_data
    
    async def get_cart_details(self, cart_data: dict[int, int]) -> CartResponse:
        if not cart_data:
            return CartResponse(items=[], total=0,0, items_count=0)
        
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