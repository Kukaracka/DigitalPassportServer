from services.auth_service import AuthService


def test_wrong_password():
    auth = AuthService(None)

    password = "123456"
    hashed = auth._get_password_hash(password)

    assert not auth.verify_password("wrong", hashed)
