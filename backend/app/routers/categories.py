from fastapi import APIRouter, Depends, status

from ..schemas.categories import CategoryCreate, CategoryResponse
from ..schemas.users import UserResponse
from ..services.categories import CategoryService as ctg_service
from ..services.dependencies import get_admin, get_session

router = APIRouter(prefix="/categories", tags=["categories"])


def get_ctg_service(session=Depends(get_session)):
    return ctg_service(session)


@router.get("", response_model=list[CategoryResponse], status_code=status.HTTP_200_OK)
async def get_categories(service: ctg_service = Depends(get_ctg_service)):
    return await service.get_all_categories()


@router.get(
    "/{category_id}/", response_model=CategoryResponse, status_code=status.HTTP_200_OK
)
async def get_category(
    category_id: int, service: ctg_service = Depends(get_ctg_service)
):
    return await service.get_by_category_id(category_id)


@router.post(
    "/add/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_data: CategoryCreate,
    service: ctg_service = Depends(get_ctg_service),
    current_admin: UserResponse = Depends(get_admin),
):
    return await service.create_category(category_data)
