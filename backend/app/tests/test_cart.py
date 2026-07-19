from httpx import AsyncClient


async def test_add_to_cart(client: AsyncClient, sample_product):
    response = await client.post("/api/cart/add", json={
        "product_id": sample_product.id,
        "quantity": 2
    })
    assert response.status_code == 200

 
async def test_get_cart(client: AsyncClient, sample_product):
    await client.post("/users/registration/", json={
        "first_name": "Test",
        "last_name": "User",
        "email": "login_test@test.com",
        "password": "12345678"
    })

    login_response = await client.post("/users/login/", data={
        "username": "login_test@test.com",
        "password": "12345678"
    })
    token = login_response.json()["access_token"]
    print(f"TOKEN: {token}")

    response = await client.get(
        "/api/cart", 
        headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Phone"

