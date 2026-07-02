from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.categories import Category
from ..schemas.categories import CategoryCreate


class CategoryRepo():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Category]:
        result = await self.session.execute(
            select(Category)
        )
        return result.scalars().all() 
    
    async def get_by_id(self, id: int) -> Optional[Category]:
        result = await self.session.execute(
            select(Category).where(Category.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Optional[Category]:
        result = await self.session.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def create_category(self, category_data: CategoryCreate) -> Category:
        try:
            db_category = Category(**category_data.model_dump())
            self.session.add(db_category)
            await self.session.commit()
            await self.session.refresh(db_category)
            return db_category
        except Exception as e:
            await self.session.rollback()
            raise e