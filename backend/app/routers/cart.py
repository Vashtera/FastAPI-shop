from fastapi import APIRouter, Depends, status

from ..core.config import settings
from ..services.cart import CartService 
from ..services.dependencies import get_session, get_current_user
from ..schemas.cart import CartResponse, CartCreate, CartItemUpdate

router = APIRouter(
    prefix='/api/cart',
    tags=['cart']
)

def get_cart_service(session = Depends(get_session)):
    return CartService(session, settings.redis_url, settings.cache_ttl_seconds)


@router.get("", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def get_cart(
    user_id = Depends(get_current_user), 
    service: CartService = Depends(get_cart_service)
    ):
    return await service.get_cart_details(user_id.id)


@router.post("/add", status_code=status.HTTP_200_OK)
async def add_to_cart(
    product_id: int, 
    quantity: int,
    user_id = Depends(get_current_user), 
    service: CartService = Depends(get_cart_service)
    ):
    item = CartCreate(product_id=product_id, quantity=quantity)
    updated_cart = await service.add_to_cart(user_id.id, item)
    return {'cart': updated_cart}


@router.put("/update", status_code=status.HTTP_200_OK)
async def update_cart(
    product_id: int, 
    quantity: int,
    user_id = Depends(get_current_user), 
    service: CartService = Depends(get_cart_service)
    ):
    item = CartItemUpdate(product_id=product_id, quantity=quantity)
    updated_cart = await service.update_cart_item(user_id.id, item)
    return {'cart': updated_cart}


@router.delete("/remove/{product_id}", status_code=status.HTTP_200_OK)
async def remove_from_cart(
    product_id: int,
    user_id = Depends(get_current_user), 
    service: CartService = Depends(get_cart_service)
    ):
    updated_cart = await service.delete_from_cart(user_id.id, product_id)
    return {'cart': updated_cart}