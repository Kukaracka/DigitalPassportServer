import pytest
from services.auth_service import AuthService


class MockRepo:
    async def get_by_username(self, username):
        return None

    async def create_one(self, data):
        return {"id": 1, **data}


@pytest.mark.asyncio
async def test_register_success():
    auth = AuthService(MockRepo())

    class UserData:
        username = "test"
        password = "123456"

        def model_dump(self):
            return {
                "username": self.username,
                "password": self.password,
            }

    result = await auth.registrate_user(UserData())

    assert result["username"] == "test"
