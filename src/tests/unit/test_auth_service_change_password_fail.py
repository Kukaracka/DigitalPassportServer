import pytest
from fastapi import HTTPException
from services.auth_service import AuthService


class MockRepo:
    async def update_one(self, *args, **kwargs):
        return True


class MockUser:
    id = 1
    password = "hashed_password"


@pytest.mark.asyncio
async def test_change_password_fail(monkeypatch):
    auth = AuthService(MockRepo())
    user = MockUser()

    # МОК: делаем так, чтобы старый пароль считался неверным
    monkeypatch.setattr(auth, "verify_password", lambda a, b: False)

    with pytest.raises(HTTPException):
        await auth.change_password(
            user=user,
            old_password="wrong",
            new_password="newpass",
        )
