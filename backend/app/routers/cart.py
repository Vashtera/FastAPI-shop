from fastapi import APIRouter, Depends, status

from ..services.cart import CartService 
from ..services.dependencies import get_session
from ..schemas.cart import AddToCartRequest, UpdateCartRequest, RemoveFromCartRequest, CartResponse, CartCreate, CartItemUpdate

router = APIRouter(
    prefix='/api/cart',
    tags=['cart']
)

def get_cart_service(session = Depends(get_session)):
    return CartService(session)


@router.post("/add", status_code=status.HTTP_200_OK)
async def add_to_cart(request: AddToCartRequest, service: CartService = Depends(get_cart_service)):
    item = CartCreate(product_id=request.product_id, quantity=request.quantity)
    updated_cart = await service.add_to_cart(request.cart, item)
    return {'cart': updated_cart}


@router.get("", response_model=CartResponse, status_code=status.HTTP_200_OK)
async def get_cart(cart_data: dict[int, int], service: CartService = Depends(get_cart_service)):
    return await service.get_cart_details(cart_data)


@router.put("/update", status_code=status.HTTP_200_OK)
def update_cart(request: UpdateCartRequest, service: CartService = Depends(get_cart_service)):
    item = CartItemUpdate(product_id=request.product_id, quantity=request.quantity)
    updated_cart = service.update_cart_item(request.cart, item)
    return {'cart': updated_cart}


@router.delete("/remove/{product_id}", status_code=status.HTTP_200_OK)
def remove_from_cart(
    product_id: int,
    request: RemoveFromCartRequest, 
    service: CartService = Depends(get_cart_service)
    ):
    updated_cart = service.remove_from_cart(request.cart, product_id)
    return {'cart': updated_cart}