from fastapi import APIRouter, Depends, status

from ..services.products import ProductService as prod_service
from ..services.dependencies import get_session
from ..schemas.products import ProductListResponse, ProductResponse, ProductCreate

router = APIRouter(
    prefix='/api/products',
    tags=['products']
)


def get_prod_service(session = Depends(get_session)):
    return prod_service(session)


@router.get("", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
async def get_all_products(service: prod_service = Depends(get_prod_service)):
    return await service.get_all()


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product(product_id, service: prod_service = Depends(get_prod_service)):
    return await service.get_by_product_id(product_id)


@router.get("/category/{category_id}", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, service: prod_service = Depends(get_prod_service)):
    return await service.get_by_category_id(category_id)


@router.post("/add", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    service: prod_service = Depends(get_prod_service)
    ):
    return await service.create_product(product_data)