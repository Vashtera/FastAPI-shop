from httpx import AsyncClient

async def test_get_all_products(client: AsyncClient, sample_product):
    response = await client.get("api/products")
    assert response.status_code == 200
    assert response.json()["products"]