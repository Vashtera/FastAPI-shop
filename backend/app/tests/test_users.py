from httpx import AsyncClient


async def test_register(client: AsyncClient):
    """
    Тест регистрации нового пользователя.

    client: AsyncClient — не создаётся вручную, а приходит из фикстуры
    client() в conftest.py. Pytest видит имя параметра "client",
    ищет фикстуру с таким же именем, вызывает её и подставляет результат.
    """

    # Отправляем POST запрос на тот же путь, что обрабатывает
    # @router.post("/registration/") в routers/users.py.
    # json={...} — тело запроса, автоматически сериализуется в JSON
    # и отправляется с заголовком Content-Type: application/json.
    # await обязателен — .post() асинхронная операция, ждём ответ сервера.
    response = await client.post("/users/registration/", json={
        "first_name": "Raul",
        "last_name": "Aitbayev",
        "email": "raul@test.com",
        "password": "12345678"
    })

    # response.status_code — числовой HTTP-код ответа.
    # 200 значит запрос обработан без ошибок на уровне сервера.
    # assert — если условие False, тест немедленно падает с AssertionError.
    assert response.status_code == 200

    # response.json() превращает тело ответа (JSON-строку) в Python-словарь,
    # например {"first_name": "Raul", "last_name": "Aitbayev", "id": 1}.
    # Проверяем не только что запрос прошёл (статус 200),
    # но и что сервер вернул именно те данные, что мы отправили —
    # то есть пользователь реально создался с правильным именем.
    assert response.json()["first_name"] == "Raul"


async def test_login(client: AsyncClient):
    """
    Тест авторизации существующего пользователя.
    """

    # Подготовительный шаг: чтобы залогиниться, пользователь должен
    # уже существовать в базе. Тестовая БД пустая перед каждым запуском
    # (создаётся/удаляется фикстурой setup_database), поэтому сначала
    # регистрируем его вручную — так же, как в test_register.
    #
    # Тут нет "response = ..." и нет assert после этого запроса,
    # потому что регистрация здесь не то, что мы тестируем —
    # это просто подготовка данных для следующего шага.
    #
    # email отличается от того что в test_register (raul2 вместо raul),
    # чтобы не столкнуться с ошибкой "email уже занят" —
    # тестовая БД общая в рамках одной сессии pytest.
    await client.post("/users/registration/", json={
        "first_name": "Raul",
        "last_name": "Aitbayev",
        "email": "raul2@test.com",
        "password": "12345678"
    })

    # Роут /users/login/ использует OAuth2PasswordRequestForm — это
    # стандарт OAuth2, он ожидает данные в формате form-data
    # (application/x-www-form-urlencoded), а НЕ json.
    # Поэтому здесь data=, а не json=, как в регистрации.
    
    # Поле называется именно "username", а не "email" —
    # это фиксированное требование OAuth2PasswordRequestForm,
    # даже если по факту логинимся через email.
    response = await client.post("/users/login/", data={
        "username": "raul2@test.com",
        "password": "12345678"
    })

    # Проверяем что вход прошёл успешно.
    assert response.status_code == 200

    # JWT токен — подписанная строка, включает время истечения (exp),
    # генерируется заново при каждом запросе. Он никогда не будет
    # одинаковым между запусками, поэтому сравнивать с конкретным
    # значением бессмысленно (assert response.json()["access_token"] == "..."
    # никогда бы не сработал).
    
    # Вместо этого проверяем сам факт наличия ключа в ответе —
    # оператор "in" для словаря проверяет присутствие ключа,
    # не заглядывая в его значение.
    assert "access_token" in response.json()


async def test_registration_exist_user(client: AsyncClient):
    await client.post("/users/registration/", json={
        "first_name": "Raul",
        "last_name": "Aitbayev",
        "email": "raul2@test.com",
        "password": "12345678"
    })

    response = await client.post("/users/registration/", json={
        "first_name": "aul",
        "last_name": "itbayev",
        "email": "raul2@test.com",
        "password": "123456780"
    })
    assert response.status_code == 400


async def test_login_with_wrong_password(client: AsyncClient):
    await client.post("/users/registration/", json={
        "first_name": "Raul",
        "last_name": "Aitbayev",
        "email": "raul2@test.com",
        "password": "12345678"
    })

    response = await client.post("/users/login/", data={
        "username": "raul2@test.com",
        "password": "12345679"
    })
    assert response.status_code == 401


async def test_login_with_unexist_email(client: AsyncClient):
    await client.post("/users/registration/", json={
        "first_name": "Raul",
        "last_name": "Aitbayev",
        "email": "raul2@test.com",
        "password": "12345678"
    })

    response = await client.post("/users/login/", data={
        "username": "raul3@test.com",
        "password": "12345678"
    })
    assert response.status_code == 401


async def test_registration_with_small_password(client: AsyncClient):
    response = await client.post("/users/registration/", json={
        "first_name": "Raul",
        "last_name": "Aitbayev",
        "email": "raul2@test.com",
        "password": "1234567"
    })
    assert response.status_code == 422


async def test_login_success(client: AsyncClient):
    await client.post("/users/registration/", json={
        "first_name": "Test",
        "last_name": "User",
        "email": "login_test@test.com",
        "password": "12345678"
    })
    response = await client.post("/users/login/", data={
        "username": "login_test@test.com",
        "password": "12345678"
    })
    assert response.status_code == 200


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/users/registration/", json={
        "first_name": "Test",
        "last_name": "User",
        "email": "wrongpass@test.com",
        "password": "12345678"
    })
    response = await client.post("/users/login/", data={
        "username": "wrongpass@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post("/users/login/", data={
        "username": "doesnotexist@test.com",
        "password": "12345678"
    })
    assert response.status_code == 401