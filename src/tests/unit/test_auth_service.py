from services.auth_service import AuthService


def test_password_hashing():
    auth_service = AuthService(None)

    password = "123456"

    hashed = auth_service._get_password_hash(password)

    assert hashed != password
