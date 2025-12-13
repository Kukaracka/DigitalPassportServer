import os
from authx import AuthX, AuthXConfig
from authx.exceptions import JWTDecodeError
from fastapi import Depends, HTTPException, Request, status

from database.models import UserModel
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository
from dotenv import load_dotenv

from services.auth_service import AuthService
from services.product_service import ProductService
from services.user_service import UserService

load_dotenv()


secret = os.getenv("SECRET_KEY")
if secret is None:
    raise Exception
config = AuthXConfig()
config.JWT_SECRET_KEY = secret
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False


security = AuthX(config=config)


async def verify_token(request: Request):
    try:
        result = await security.access_token_required(request)
        return result
    except JWTDecodeError as e:
        if "expired" in str(e).lower():
            raise HTTPException(status_code=401, detail="Token has expired")
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Other auth error: {e}")  # Отладочная информация
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_current_authorised_user(
    payload: dict = Depends(verify_token),
) -> UserModel:
    """Проверяет токен, достаёт user_id и возвращает объект пользователя."""

    sub = getattr(payload, "sub", None)

    # Проверка наличия поля sub в payload
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing 'sub' claim",
        )

    # Безопасно конвертируем в int
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: 'sub' must be an integer",
        )

    # Создаём экземпляр репозитория
    user_repo = UserRepository()
    user = await user_repo.read_one(user_id)

    # Проверяем, что пользователь найден
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


async def get_user_repository() -> UserRepository:
    return UserRepository()


async def get_product_repository() -> ProductRepository:
    return ProductRepository()



async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
):
    return AuthService(user_repo)

async def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository)):
    return ProductService(product_repo)
