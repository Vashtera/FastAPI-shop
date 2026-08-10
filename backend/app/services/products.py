from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.categories_repo import CategoryRepo
from ..repositories.products_repo import ProductRepo
from ..schemas.products import ProductCreate, ProductListResponse, ProductResponse


class ProductService:
    """
    Сервис для управления товарами магазина.
    """

    def __init__(self, db: AsyncSession):
        self.session = ProductRepo(db)
        self.category_session = CategoryRepo(db)

    async def get_all(self) -> ProductListResponse:
        """
        Получить список всех товаров.

        Returns:
            ProductListResponse со списком товаров и их количеством
        """
        products = await self.session.get_all()
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products, total=len(products_response))

    async def get_by_product_id(self, product_id: int) -> ProductResponse:
        """
        Получить товар по ID.

        Args:
            product_id: уникальный идентификатор товара

        Returns:
            Объект товара

        Raises:
            HTTPException 404: если товар не найден
        """
        product = await self.session.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not founded",
            )
        return product

    async def get_by_category_id(self, category_id: int) -> ProductListResponse:
        """
        Получить все товары определённой категории.

        Args:
            category_id: уникальный идентификатор категории

        Returns:
            ProductListResponse со списком товаров категории

        Raises:
            HTTPException 404: если категория не найдена
        """
        category = await self.category_session.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not founded",
            )
        products = await self.session.get_by_category_id(category_id)
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(
            products=products_response, total=len(products_response)
        )

    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """
        Создать новый товар.

        Args:
            product_data: данные нового товара

        Returns:
            Созданный товар

        Raises:
            HTTPException 404: если указанная категория не существует
        """
        category = await self.category_session.get_by_id(product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {product_data.category_id} not founded",
            )

        product = await self.session.create_product(product_data)
        return product

    async def get_pending_products(self) -> ProductListResponse:
        products = await self.session.get_pending_products()
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(
            products=products_response, total=len(products_response)
        )

    async def put_approve_status(self, product_id: int) -> ProductResponse:
        product = await self.session.put_approve_status(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not founded",
            )
        return ProductResponse.model_validate(product)

    async def put_reject_status(self, product_id: int) -> ProductResponse:
        product = await self.session.put_reject_status(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not founded",
            )
        return ProductResponse.model_validate(product)
