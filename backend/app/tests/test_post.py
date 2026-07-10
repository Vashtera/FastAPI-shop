from httpx import AsyncClient

# Правильные данные
async def test_register(client: AsyncClient):
    response = await client.post("/users/registration/", json={
        "first_name": "Raul",
        "last_name": "Aitbayev",
        "email": "raul@test.com",
        "password": "12345678"
    })
    assert response.status_code == 200
    assert response.json()["first_name"] == "Raul"


# Правильные данные
async def test_login(client: AsyncClient):
    # Сначала нужно зарегистрировать пользователя
    await client.post("/users/registration/", json={
        "first_name": "Raul",
        "last_name": "Aitbayev",
        "email": "raul2@test.com",
        "password": "12345678"
    })
    
    response = await client.post("/users/login/", data={ # OAuth2 использует data, не json
        "username": "raul2@test.com",  # OAuth2 использует username, не email
        "password": "12345678"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()