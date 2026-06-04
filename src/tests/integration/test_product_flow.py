import pytest


@pytest.mark.asyncio
async def test_create_product_flow(client):
    # 1. регистрация пользователя
    await client.post("/api/register", json={
        "username": "product_user",
        "password": "TestPass1",
        "email": "product@mail.com",
        "first_name": "Product",
        "last_name": "User",
        "father_name": ""
    })

    # 2. логин
    login = await client.post("/api/login", json={
        "username": "product_user",
        "password": "TestPass1"
    })

    assert login.status_code == 200
    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # 3. создаём продукт
    product_payload = {
        "name": "iPhone 15",
        "manufacturer": "Apple",
        "category": "smartphone",
        "model": "A3090",
        "serial_number": "SN123456789",
        "price": 999.99,
        "purchase_date": "2025-01-01",
        "warranty_until": "2026-01-01",
        "description": "Test product",
        "notes": "Integration test"
    }

    create = await client.post("/api/products/", json=product_payload, headers=headers)

    assert create.status_code in (200, 201)
    product_id = create.json().get("id")
    assert product_id is not None

    # 4. получаем список продуктов
    list_resp = await client.get("/api/products/", headers=headers)

    assert list_resp.status_code == 200
    data = list_resp.json()

    assert isinstance(data, list)
    assert any(p["serial_number"] == "SN123456789" for p in data)


@pytest.mark.asyncio
async def test_get_product_by_id(client):
    # регистрация + логин
    await client.post("/api/register", json={
        "username": "product_user2",
        "password": "TestPass1",
        "email": "product2@mail.com",
        "first_name": "Product",
        "last_name": "User",
        "father_name": ""
    })

    login = await client.post("/api/login", json={
        "username": "product_user2",
        "password": "TestPass1"
    })

    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # создаём продукт
    create = await client.post("/api/products/", json={
        "name": "MacBook Pro",
        "manufacturer": "Apple",
        "category": "laptop",
        "model": "M3",
        "serial_number": "MAC123456",
        "price": 1999.99,
        "purchase_date": "2025-02-01",
        "warranty_until": None,
        "description": None,
        "notes": None
    }, headers=headers)

    product_id = create.json()["id"]

    # получаем по id
    resp = await client.get(f"/api/products/{product_id}", headers=headers)

    assert resp.status_code == 200
    data = resp.json()

    assert data["serial_number"] == "MAC123456"
    assert data["name"] == "MacBook Pro"
