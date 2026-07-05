from fastapi import FastAPI 
from app.routers.users import router as users_router
from app.routers.categories import router as categories_router
from app.routers.products import router as product_router
from app.routers.cart import router as cart_router

app = FastAPI()

app.include_router(users_router)
app.include_router(categories_router)
app.include_router(product_router)
app.include_router(cart_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI-Shop"}