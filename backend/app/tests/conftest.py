import os
os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///./test_shop.db"
)
os.environ["REDIS_URL"] = (
    "redis://localhost:6379/0"
)
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base
from app.services.dependencies import get_session
'''
import os
os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///./test_shop.db"
)
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

    Что делает: Устанавливает переменные окружения ДО импорта твоего приложения. 
    Это подменяет настройки — теперь app/config.py 
    при чтении DATABASE_URL увидит тестовую БД, а не рабочую.
    Почему это важно: Если бы app импортировался раньше — он бы уже прочитал 
    рабочий DATABASE_URL из .env и подключился к реальной базе. Порядок здесь критичен.
'''

'''
    ASGITransport — это способ сказать AsyncClient: "не делай реальный сетевой запрос через интернет, 
    а вызови FastAPI приложение напрямую в памяти, как будто оно уже запущено". 
    Без него AsyncClient пытался бы реально стучаться на http://test через сеть, что бы не сработало.
'''


@pytest.fixture(scope="session")
def test_engine():
    '''
    Что делает: Создаёт один движок БД на всю сессию тестирования 
    (scope="session" — не пересоздаётся для каждого теста).

    NullPool: на самом деле не убирает, а отключает пул соединений. 
    Обычно SQLAlchemy держит несколько открытых соединений про запас (пул) для скорости. 
    Для тестов с SQLite это не нужно и может создавать конфликты между тестами — поэтому NullPool
    говорит "открывай новое соединение каждый раз, не кэшируй".
    '''
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool,
    )
    return engine


@pytest.fixture(scope="session")
async def setup_database(test_engine):
    '''
    Что делает:

    До yield — создаёт все таблицы один раз в начале тестовой сессии
    yield — здесь выполняются сами тесты
    После yield — удаляет все таблицы и закрывает соединение когда все тесты закончились
    '''
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def db_session(test_engine, setup_database):
    '''
    Что делает: Создаёт функцию-замену для get_session. 
    Когда FastAPI внутри роутера попросит сессию через Depends(get_session) — вместо реальной 
    подставится db_session из теста.
    '''
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession):
    '''
    Что делает: Создаёт функцию-замену для get_session. 
    Когда FastAPI внутри роутера попросит сессию через Depends(get_session) — вместо реальной 
    подставится db_session из теста.
    app.dependency_overrides — это словарь FastAPI специально для тестов, 
    позволяет подменять любые зависимости.
    '''
    async def override_get_db():
        yield db_session
    

    '''
    app.dependency_overrides — это словарь FastAPI специально для тестов, 
    позволяет подменять любые зависимости.
    '''
    app.dependency_overrides[get_session] = override_get_db


    '''
    Что делает: Создаёт HTTP клиент который обращается к твоему app напрямую в памяти, 
    без реального сервера.
    '''
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


    '''
    Что делает: После теста удаляет подмену — возвращает get_session к нормальному поведению. 
    Важно чтобы тесты не влияли друг на друга.
    '''
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def clean_database(db_session):
    """
    Автоматически очищает тестовую базу данных после каждого теста.

    Фикстура выполняется для каждого теста благодаря `autouse=True`.
    После завершения теста удаляет все записи из таблиц товаров,
    категорий и пользователей, чтобы каждый тест начинался с
    чистого состояния базы данных.

    Args:
        db_session: асинхронная сессия SQLAlchemy,
        используемая для выполнения SQL-запросов.

    Yields:
        Управление передаётся тесту. После его выполнения
        производится очистка базы данных.
    """
    from sqlalchemy import delete
    from app.models.products import Product
    from app.models.categories import Category
    from app.models.users import User
    yield

    await db_session.execute(delete(Product))
    await db_session.execute(delete(Category))
    await db_session.execute(delete(User))
    await db_session.commit()


@pytest.fixture(scope="function")
async def sample_product(db_session):
    from app.models.categories import Category
    from app.models.products import Product

    category = Category(name="Electronics", slug="electronics")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    product = Product(name="Phone", price=999, category_id=category.id, description="Test phone description" )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    return product
    
