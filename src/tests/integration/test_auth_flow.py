import pytest


@pytest.mark.asyncio
async def test_register_login_flow(client):
    payload = {
        "username": "test_user",
        "password": "TestPass1",
        "email": "test@mail.com",
        "first_name": "Test",
        "last_name": "User",
        "father_name": ""
    }

    register = await client.post("/api/register", json=payload)
    assert register.status_code in (200, 201)

    login = await client.post("/api/login", json={
        "username": "test_user",
        "password": "TestPass1"
    })

    assert login.status_code == 200
    assert "access_token" in login.json()


@pytest.mark.asyncio
async def test_login_and_access_me(client):
    await client.post("/api/register", json={
        "username": "test_user2",
        "password": "TestPass1",
        "email": "test2@mail.com",
        "first_name": "Test",
        "last_name": "User",
        "father_name": ""
    })

    login = await client.post("/api/login", json={
        "username": "test_user2",
        "password": "TestPass1"
    })

    token = login.json()["access_token"]

    me = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert me.status_code == 200
