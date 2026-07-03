from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from ..repositories.products_repo import ProductRepo
from ..schemas.cart import CartCreate, CartItem, CartItemUpdate, CartResponse


class CartService:
    def __init__(self, db: AsyncSession):
        self.session = ProductRepo(db)

    async def 