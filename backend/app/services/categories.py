from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.categories_repo import CategoryRepo
from ..schemas.categories import CategoryCreate, CategoryResponse
from fastapi import HTTPException, status


class CategoryService:
    """
    Сервис для управления категориями товаров.
    """
    def __init__(self, db: AsyncSession):
        self.session = CategoryRepo(db)

    async def get_all_categories(self) -> list[CategoryResponse]:
        """
        Получить список всех категорий.

        Returns:
            Список всех категорий
        """
        return await self.session.get_all()
    
    async def get_by_category_id(self, category_id: int) -> CategoryResponse:
        """
        Получить категорию по ID.

        Args:
            category_id: уникальный идентификатор категории

        Returns:
            Объект категории

        Raises:
            HTTPException 404: если категория не найдена
        """
        category = await self.session.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not founded"
            )
        return category 
    
    async def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        """
        Создать новую категорию.

        Args:
            category_data: данные новой категории

        Returns:
            Созданная категория
        """
        category = await self.session.create_category(category_data)
        return category 