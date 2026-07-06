from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.routers.users import router as users_router
from app.routers.categories import router as categories_router
from app.routers.products import router as product_router
from app.routers.cart import router as cart_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Этот код выполнится строго при старте сервера
    await init_db()
    yield

app = FastAPI(
    title = settings.app_name,
    debug = settings.debug,
    docs_url = "/api/docs",
    redoc_url = "/api/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.cors_origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.mount(
    "/static", StaticFiles(directory=settings.static_dir), name = "static"
)

app.include_router(users_router)
app.include_router(categories_router)
app.include_router(product_router)
app.include_router(cart_router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to FastAPI-Shop",
        "docs": "api/docs"
        }