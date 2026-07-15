from httpx import AsyncClient


async def test_add_to_cart(client: AsyncClient, sample_product):
    response = await client.post("/api/cart/add", json={
        "product_id": sample_product.id,
        "quantity": 2
    })
    assert response.status_code == 200

# нужно проверить после добавления redis  
async def test_get_cart(client: AsyncClient):
    response = await client.get("/api/cart", json={})
    assert response.status_code == 200


async def test_update_cart(client: AsyncClient)