import os
os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///./test_shop.db"
)
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

import pytest
from fastapi.testclient import TestClient
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
Что делает: Создаёт один движок БД на всю сессию тестирования 
(scope="session" — не пересоздаётся для каждого теста).
NullPool: Отключает пул соединений. Для тестов это нужно — иначе SQLite может 
конфликтовать при параллельном доступе между тестами.
'''
@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool,
    )
    return engine


'''
Что делает:

До yield — создаёт все таблицы один раз в начале тестовой сессии
yield — здесь выполняются сами тесты
После yield — удаляет все таблицы и закрывает соединение когда все тесты закончились
'''
@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


'''
Что делает: Создаёт функцию-замену для get_session. 
Когда FastAPI внутри роутера попросит сессию через Depends(get_session) — вместо реальной 
подставится db_session из теста.
'''
@pytest.fixture
async def db_session(test_engine, setup_databse):
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



    
