from services.auth_service import AuthService


def test_password_hashing():
    auth = AuthService(None)

    password = "123456"
    hashed = auth._get_password_hash(password)

    assert hashed != password
    assert auth.verify_password(password, hashed)
