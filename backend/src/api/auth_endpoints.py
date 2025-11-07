from fastapi import APIRouter, Depends, Response

from api.dependencies import verify_token
from database.models import UserModel
from repositories.user_repository import UserRepository
from schemas.user_schemas import (
    TokenResponseSchema,
    UserCreateSchema,
    UserLoginSchema,
    UserReadSchema,
)
from api.dependencies import config, security
from services.auth_service import AuthService

auth_router = APIRouter(prefix="", tags=["Auth"])




@auth_router.post("/login", response_model=TokenResponseSchema)
async def login(credentials: UserLoginSchema, responce: Response):
    user_repo = UserRepository(UserModel)
    auth_service = AuthService(user_repo)
    token = await auth_service.authenticate_user(
        security=security, username=credentials.username, password=credentials.password
    )
    responce.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"access_token": token}


@auth_router.post("/register")
async def register(credentials: UserCreateSchema, responce: Response) -> UserReadSchema:
    user_repo = UserRepository(UserModel)
    service = AuthService(user_repo)
    user = await service.registrate_user(credentials)
    return user


@auth_router.get(
    "/login_check", response_description="Authentication status successfully received"
)
def check(current_user: UserModel = Depends(verify_token)):
    """
    Endpoint for authorization check
    """
    return {"Authentication successful"}
