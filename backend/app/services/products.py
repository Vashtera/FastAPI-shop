from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from ..repositories.products_repo import ProductRepo
from ..repositories.categories_repo import CategoryRepo
from ..schemas.products import ProductCreate, ProductResponse, ProductListResponse

class Product:
    def __init__(self, db: AsyncSession):
        self.session = ProductRepo(db)
        self.category_session = CategoryRepo(db)

    async def get_all(self) -> ProductListResponse:
        products = await self.session.get_all()
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products, total=len(products_response))
    
    async def get_by_product_id(self, product_id: int) -> ProductResponse:
        product = await self.session.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not founded"
            )
        return product
    
    async def get_by_category_id(self, category_id: int) -> ProductListResponse:
        category = self.category_session.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not founded"
            )
        products = await self.session.get_by_category(category_id)
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products_response))
    
    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        category = self.category_session.get_by_id(product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {product_data.category_id} not founded"
            )

        product = await self.session.create_product(product_data)
        return product
    
