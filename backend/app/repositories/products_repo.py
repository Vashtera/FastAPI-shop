from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.products import Product
from ..schemas.products import ProductCreate


class ProductRepo():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Product]:
        result = await self.session.execute(
            select(Product)
        )
        return result.scalars().all()
    
    async def get_by_id(self, id: int) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(Product.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(func.lower(Product.name) == name.lower())
        )
        return result.scalar_one_or_none()
    
    async def get_by_category_id(self, category_id: int) -> List[Product]:
        result = await self.session.execute(
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.category_id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        try:
            db_product = Product(**product_data.model_dump())
            self.session.add(db_product)
            await self.session.commit()
            await self.session.refresh(db_product)
            return db_product
        except Exception as e:
            await self.session.rollback()
            raise e