from fastapi import APIRouter, Depends, status

from ..schemas.products import ProductCreate, ProductListResponse, ProductResponse
from ..services.dependencies import get_admin, get_seller, get_session
from ..services.products import ProductService as prod_service

router = APIRouter(prefix="/api/products", tags=["products"])


def get_prod_service(session=Depends(get_session)):  
    return prod_service(session)


@router.get("", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
async def get_all_products(service: prod_service = Depends(get_prod_service)):
    return await service.get_all()


@router.get(
    "/{product_id}/", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
async def get_product(product_id, service: prod_service = Depends(get_prod_service)):
    return await service.get_by_product_id(product_id)


@router.get(
    "/category/{category_id}/",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    category_id: int, service: prod_service = Depends(get_prod_service)
):
    return await service.get_by_category_id(category_id)


@router.post(
    "/add/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED
)
async def create_product(
    product_data: ProductCreate,
    service: prod_service = Depends(get_prod_service),
    current_seller=Depends(get_seller),
):
    return await service.create_product(product_data)


@router.get(
    "/admin/products/pending/",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_pending_products(
    service: prod_service = Depends(get_prod_service), current_admin=Depends(get_admin)
):
    return await service.get_pending_products()


@router.put(
    "/admin/products/{product_id}/approve/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def put_approve_status(
    product_id: int,
    service: prod_service = Depends(get_prod_service),
    current_admin=Depends(get_admin),
):
    return await service.put_approve_status(product_id)


@router.put(
    "/admin/products/{product_id}/reject/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def put_reject_status(
    product_id: int,
    service: prod_service = Depends(get_prod_service),
    current_admin=Depends(get_admin),
):
    return await service.put_reject_status(product_id)
