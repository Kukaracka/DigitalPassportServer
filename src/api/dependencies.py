from minio import Minio
from authx import AuthX, AuthXConfig
from authx.exceptions import JWTDecodeError
from fastapi import Depends, HTTPException, Request, status
from functools import lru_cache

from core.config import get_settings
from database.models import UserModel
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository

from services.auth_service import AuthService
from services.product_service import ProductService
from services.user_service import UserService
from services.storage_service import StorageService

from repositories.product_image_repository import ProductImageRepository
from services.product_image_service import ProductImageService

settings = get_settings()

secret = settings.SECRET_KEY
if secret is None:
    raise Exception("SECRET_KEY environment variable is not set")

config = AuthXConfig()
config.JWT_SECRET_KEY = secret
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False

security = AuthX(config=config)


# MinIO Client Dependency
@lru_cache
def get_minio_client() -> Minio:
    """
    Dependency для получения MinIO клиента
    """
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


# Storage Service Dependency
async def get_storage_service() -> StorageService:
    """
    Dependency для получения StorageService
    """
    return StorageService()


# Auth Dependencies
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
        print(f"Other auth error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_current_authorised_user(
    payload: dict = Depends(verify_token),
) -> UserModel:
    """Проверяет токен, достаёт user_id и возвращает объект пользователя."""

    sub = getattr(payload, "sub", None)

    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing 'sub' claim",
        )

    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: 'sub' must be an integer",
        )

    user_repo = UserRepository()
    user = await user_repo.read_one(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


# Repository Dependencies
async def get_user_repository() -> UserRepository:
    return UserRepository()


async def get_product_repository() -> ProductRepository:
    return ProductRepository()


async def get_product_image_repository() -> ProductImageRepository:
    return ProductImageRepository()


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)


async def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ProductService:
    return ProductService(product_repo)


async def get_product_image_service(
    image_repo: ProductImageRepository = Depends(get_product_image_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    storage_service: StorageService = Depends(get_storage_service),
) -> ProductImageService:
    return ProductImageService(
        image_repo=image_repo,
        product_repo=product_repo,
        storage_service=storage_service,
    )


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    storage_service: StorageService = Depends(get_storage_service),
    auth_service: AuthService = Depends(get_auth_service),
    product_service: ProductService = Depends(get_product_service),
) -> UserService:
    return UserService(
        users_repo=user_repo,
        storage_service=storage_service,
        auth_service=auth_service,
        product_service=product_service,
    )
