from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .core.config import settings

engine = create_async_engine(settings.database_url)
SessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def init_db():
    from app.models.categories import Category
    from app.models.products import Product
    from app.models.users import User

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
