import pytest
from services.auth_service import AuthService


class MockRepo:
    async def update_one(self, user_id, data):
        self.updated = (user_id, data)


class MockUser:
    def __init__(self):
        self.id = 1
        self.password = None


@pytest.mark.asyncio
async def test_change_password_success():
    repo = MockRepo()
    auth = AuthService(repo)

    user = MockUser()

    old = "123456"
    new = "654321"

    user.password = auth._get_password_hash(old)

    await auth.change_password(user, old, new)

    assert repo.updated is not None
