from httpx import AsyncClient


async def test_add_to_cart(client: AsyncClient, sample_product):
    response = await client.post("/api/cart/add", json={
        "product_id": sample_product.id,
        "quantity": 2
    })
    assert response.status_code == 200