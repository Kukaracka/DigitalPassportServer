import pytest
from services.user_service import UserService


class MockUser:
    id = 1
    password = "hashed"
    avatar = "avatar.jpg"


class MockRepo:
    async def read_one(self, user_id):
        return MockUser()

    async def delete_one(self, user_id):
        return True


class MockStorage:
    async def delete_files(self, files):
        return True


class MockAuth:
    def verify_password(self, a, b):
        return True


class MockProductRepository:
    async def get_file_names_by_owner(self, owner_id: int):
        return ["file1.jpg", "file2.jpg"]


@pytest.mark.asyncio
async def test_delete_user():
    service = UserService(
        users_repo=MockRepo(),
        storage_service=MockStorage(),
        auth_service=MockAuth(),
        product_repo=MockProductRepository()
    )

    result = await service.delete_user(1, "123")

    assert result is True
