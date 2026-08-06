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
    """
    Управляет жизненным циклом приложения — код до `yield` выполняется
    ОДИН РАЗ при старте сервера, код после `yield` — один раз при
    остановке сервера.

    @asynccontextmanager превращает обычную функцию в объект который
    FastAPI понимает как "менеджер жизненного цикла": он сам вызовет
    код до yield при старте, дождётся пока приложение работает
    (это и есть момент yield), и вызовет код после yield при завершении.

    Здесь используется только для старта — создать таблицы в БД перед
    тем как приложение начнёт принимать запросы. Если бы после yield
    было что-то (например await engine.dispose()) — оно бы выполнилось
    при остановке сервера для аккуратного закрытия соединений.
    """
    # Этот код выполнится строго при старте сервера
    await init_db()
    yield
    # Если бы здесь был код — он выполнился бы при остановке сервера


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)
"""
Создаёт главный объект приложения — это ядро, вокруг которого
строится весь сервер.

title         — название проекта, отображается в Swagger UI
debug         — режим отладки (True/False), при True FastAPI
                показывает более подробные traceback при ошибках
docs_url      — по какому пути доступна Swagger UI документация
                (по умолчанию был бы "/docs", здесь переопределено
                на "/api/docs")
redoc_url     — альтернативная документация ReDoc, по другому пути
lifespan      — передаём функцию управления жизненным циклом,
                описанную выше, чтобы init_db() вызвался при старте
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""
Middleware — это код, который выполняется для КАЖДОГО запроса
до того как он дойдёт до конкретного роутера (и после того как
роутер отдаст ответ).

CORSMiddleware конкретно решает проблему CORS (Cross-Origin
Resource Sharing) — браузер по умолчанию блокирует запросы с одного
домена (например фронтенд на localhost:5173) к другому домену
(бэкенд на localhost:8000), если сервер явно не разрешил это.

allow_origins     — список доменов, которым разрешено делать запросы
                    к этому API (берётся из settings — там прописаны
                    адреса Vue.js фронтенда)
allow_credentials — разрешить отправку cookies/токенов авторизации
                    вместе с запросом
allow_methods     — какие HTTP методы разрешены (GET, POST, PUT,
                    DELETE...); "*" значит разрешены все
allow_headers     — какие заголовки запроса разрешены; "*" значит
                    разрешены любые (включая Authorization для JWT)

Без этого middleware браузер бы блокировал все запросы
фронтенда к бэкенду с ошибкой CORS policy.
"""

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
"""
Подключает раздачу статических файлов (изображений, например) —
всё что лежит в папке settings.static_dir будет
доступно по URL начинающемуся с "/static".

Например файл static/images/phone.jpg будет доступен браузеру
по адресу http://localhost:8000/static/images/phone.jpg — это
нужно если ты хранишь картинки товаров локально на сервере,
а не на внешнем хостинге вроде Unsplash.

name="static" — внутреннее имя этого маршрута внутри FastAPI,
используется если понадобится сослаться на него программно.
"""

app.include_router(users_router)
app.include_router(categories_router)
app.include_router(product_router)
app.include_router(cart_router)
"""
Подключает отдельные файлы роутеров к главному приложению.

Каждый роутер (users_router, categories_router и т.д.) — это
набор эндпоинтов, описанных в соответствующем файле
routers/users.py, routers/categories.py и т.д., со своим prefix
(например "/users" или "/api/cart") и своими тегами для
группировки в Swagger UI.

Без include_router FastAPI не будет знать что эти эндпоинты
вообще существуют — просто написать @router.get(...) в другом
файле недостаточно, главное приложение должно явно подключить
этот роутер к себе.
"""


@app.get("/")
def read_root():
    """
    Корневой эндпоинт — просто проверка что сервер вообще работает
    и подсказка где искать документацию API.

    Не помечен как async — потому что внутри нет никаких
    асинхронных операций (нет обращений к БД, Redis, внешним
    сервисам), функция просто мгновенно возвращает словарь.
    FastAPI одинаково хорошо работает и с sync, и с async
    функциями.

    Returns:
        Простой словарь с приветственным сообщением и
        подсказкой на путь к документации
    """
    return {
        "message": "Welcome to FastAPI-Shop",
        "docs": "api/docs",
    }
