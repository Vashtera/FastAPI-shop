from httpx import AsyncClient

async def test_get_categories(client: AsyncClient, sample_product):
    response = await client.get("/api/categories")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Electronics"


async def test_create_category(client: AsyncClient):
    response = await client.post("/api/categories/add", json={
        "name": "Test1",
        "slug": "test1"
    })
    assert response.status_code == 201
    print(response.json())
    assert response.json()["name"] == "Test1"