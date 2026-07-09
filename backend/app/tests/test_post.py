import pytest
from httpx import AsyncClient

async def test_register(client: AsyncClient):
    response = await client.post("/users/registration/", json={
        "first_name": "Raul",
        "last_name": "Aitbayev",
        "email": "raul@test.com",
        "password": "12345678"
    })
    assert response.status_code == 200
    assert response.json()["first_name"] == "Raul"