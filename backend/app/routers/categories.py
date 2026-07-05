from fastapi import APIRouter, Depends, status

from ..services.categories import CategoryService as ctg_service
from ..services.dependencies import get_session
from ..schemas.categories import CategoryResponse 

router = APIRouter(
    prefix='/api/categories',
    tags=['categories']
)


def get_ctg_service(session=Depends(get_session)):
    return ctg_service(session)


@router.get("", response_model=list[CategoryResponse], status_code=status.HTTP_200_OK)
async def get_categories(service: ctg_service = Depends(get_ctg_service)):
    return await service.get_all_categories()


@router.get("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
async def get_category(category_id: int, service: ctg_service = Depends(get_ctg_service)):
    return await service.get_by_category_id(category_id)





