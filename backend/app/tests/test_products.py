from httpx import AsyncClient

async def test_get_all_products(client: AsyncClient, sample_product):
    response = await client.get("api/products")
    assert response.status_code == 200
    assert response.json()["products"]


async def test_get_product_by_id(client: AsyncClient, sample_product):
    response = await client.get("api/products/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Phone"


async def test_get_product_by_category(client: AsyncClient, sample_product):
    response = await client.get("api/products/category/1")
    assert response.status_code == 200
    assert response.json()["products"][0]["name"] == "Phone"


async def test_create_product(client: AsyncClient):
    response = await client.post("")