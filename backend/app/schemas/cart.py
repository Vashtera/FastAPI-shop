from pydantic import BaseModel, Field
from typing import Optional


class CartBase(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Количество(должно быть больше 0)")


class CartCreate(CartBase):
    pass


class CartItemUpdate(CartBase):
    pass


class CartItem(CartBase):
    name: str = Field(..., description="Имя товара в корзине")
    price: float = Field(..., description="Цена товара в корзине")
    subtotal: float = Field(
        ..., description="Цена за этот товар(цена * количество)"
        )
    image_url: Optional[str] = Field(None, description="URL изображения товара")


class CartResponse(BaseModel):
    items: list[CartItem] = Field(..., description="Лист товаров в корзине")
    total: float = Field(..., description="Итоговая стоимость корзины")
    items_count: int = Field(..., description="Общее количество товара в корзине")