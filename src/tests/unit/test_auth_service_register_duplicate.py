import pytest
from fastapi import HTTPException
from services.auth_service import AuthService


class MockRepo:
    async def get_by_username(self, username):
        return {"id": 1}

    async def create_one(self, data):
        pass


@pytest.mark.asyncio
async def test_register_duplicate():
    auth = AuthService(MockRepo())

    class UserData:
        username = "test"
        password = "123"

        def model_dump(self):
            return {"username": self.username, "password": self.password}

    with pytest.raises(HTTPException) as exc:
        await auth.registrate_user(UserData())

    assert exc.value.status_code == 409
