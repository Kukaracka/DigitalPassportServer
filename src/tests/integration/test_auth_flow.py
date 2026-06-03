import pytest


@pytest.mark.asyncio
async def test_register_login_flow(client):

    register = await client.post(
        "/api/register",
        json={
            "username": "test_user",
            "password": "test_pass",
            "email": "test@mail.com",
            "first_name": "Test",
            "last_name": "User",
            "father_name": ""
        }
    )

    assert register.status_code in (200, 201)

    login = await client.post(
        "/api/login",
        json={
            "username": "test_user",
            "password": "test_pass"
        }
    )

    assert login.status_code == 200

    data = login.json()
    assert "access_token" in data
