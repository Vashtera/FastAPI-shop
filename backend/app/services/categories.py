from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.categories_repo import CategoryRepo
from ..schemas.categories import CategoryCreate, CategoryResponse
from fastapi import HTTPException, status


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.session = CategoryRepo(db)

    async def get_all_categories(self) -> list[CategoryResponse]:
        return await self.session.get_all()
    
    async def get_by_category_id(self, category_id: int) -> CategoryResponse:
        category = await self.session.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not founded"
            )
        return category 
    
    async def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        category = await self.session.create_category(category_data)
        return category 