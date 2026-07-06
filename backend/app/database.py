from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .core.config import settings

engine = create_async_engine(settings.database_url)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def init_db():
    from app.models.users import User 
    from app.models.categories import Category
    from app.models.products import Product

    # Проверяем в консоли, увидела ли SQLAlchemy твои таблицы перед созданием
    print("\n=== ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ===")
    print(f"Найденные таблицы для создания: {list(Base.metadata.tables.keys())}")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("=== СОЗДАНИЕ ТАБЛИЦ ЗАВЕРШЕНО ===\n")