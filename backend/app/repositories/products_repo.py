from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.products import Product
from ..schemas.products import ProductCreate


class ProductRepo():
    """
    Репозиторий для работы с таблицей product.
    Содержит все запросы к БД связанные с товарами.
    """

    def __init__(self, session: AsyncSession):
        """
        Args:
            session: асинхронная сессия SQLAlchemy
        """
        self.session = session

    async def get_all(self) -> List[Product]:
        """
        Получить список всех товаров вместе с их категориями.

        joinedload(Product.category) — загружает связанную категорию
        одним JOIN-запросом. Без этого обращение к product.category
        в Pydantic-схеме вызовет ошибку MissingGreenlet, так как
        async SQLAlchemy не может делать ленивую подгрузку "на лету".

        Returns:
            Список всех товаров
        """
        result = await self.session.execute(
            select(Product)
            .options(joinedload(Product.category))
        )
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Optional[Product]:
        """
        Получить товар по ID.

        Args:
            id: уникальный идентификатор товара

        Returns:
            Объект Product или None если не найден
        """
        result = await self.session.execute(
            select(Product).where(Product.id == id)
            .options(joinedload(Product.category))
        )
        return result.scalar_one_or_none()

    async def get_multiple_by_ids(self, product_ids: list[int]) -> list[Product]:
        """
        Получить несколько товаров по списку ID (используется в корзине).

        .in_(product_ids) — SQL-эквивалент "WHERE id IN (1, 2, 3)",
        возвращает все товары чьи id есть в переданном списке.

        Args:
            product_ids: список id товаров

        Returns:
            Список найденных товаров
        """
        result = await self.session.execute(
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.id.in_(product_ids))
        )
        return result.scalars().all()

    async def get_by_category_id(self, category_id: int) -> List[Product]:
        """
        Получить все товары определённой категории.

        Args:
            category_id: id категории

        Returns:
            Список товаров категории
        """
        result = await self.session.execute(
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.category_id == category_id)
        )
        return result.scalar_one_or_none()

    async def create_product(self, product_data: ProductCreate) -> Product:
        """
        Создать новый товар в БД.

        Args:
            product_data: валидированные данные товара

        Returns:
            Созданный объект Product с присвоенным id

        Raises:
            Exception: при ошибке создания откатывает транзакцию
        """
        try:
            db_product = Product(**product_data.model_dump())
            self.session.add(db_product)
            await self.session.commit()
            await self.session.refresh(db_product)
            return db_product
        except Exception as e:
            await self.session.rollback()
            raise e