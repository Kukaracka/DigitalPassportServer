import os
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

from api.dependencies import get_auth_service, get_user_repository, verify_token
from database.models import UserModel
from repositories.user_repository import UserRepository
from schemas.user_schemas import (
    TokenResponseSchema,
    UserCreateSchema,
    UserLoginSchema,
)
from api.dependencies import config, security
from services.auth_service import AuthService
from services.google_oauth import oauth

load_dotenv()

auth_router = APIRouter(prefix="", tags=["Auth"])


@auth_router.post("/login", response_model=TokenResponseSchema)
async def login(
    credentials: UserLoginSchema,
    responce: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    token = await auth_service.authenticate_user(
        security=security, username=credentials.username, password=credentials.password
    )
    responce.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"access_token": token}


@auth_router.post("/register")
async def register(
    credentials: UserCreateSchema,
    responce: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.registrate_user(credentials)
    return user


@auth_router.get(
    "/login_check", response_description="Authentication status successfully received"
)
def check(
    current_user: UserModel = Depends(verify_token),
):
    """
    Endpoint for authorization check
    """
    return {"Authentication successful"}


@auth_router.get("/google/login")
async def google_login(
    request: Request,
):
    """
    Начало авторизации через Google.
    Перенаправляет пользователя на Google login.
    """
    return await oauth.google.authorize_redirect(
        request, os.getenv("GOOGLE_REDIRECT_URI")
    )


@auth_router.get("/google/callback")
async def google_callback(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Callback после авторизации через Google.
    Создает пользователя, если его нет, и выдает JWT.
    """
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Google authentication failed")

    email = user_info["email"]
    name = user_info.get("name", email.split("@")[0])

    user = await user_repo.get_by_username(email)

    if not user:
        # Создаем нового пользователя
        user_data = UserCreateSchema(
            username=email,
            password="Oauth_google_dummy_password12345",
            email=email,
            first_name=name.split(" ")[0] if " " in name else name,
            last_name=name.split(" ")[1] if " " in name else " ",
            father_name="",
        )
        await auth_service.registrate_user(user_data)
        user = await user_repo.get_by_username(email)

    jwt_token = security.create_access_token(uid=str(user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, jwt_token)

    # Редирект на фронтенд с токеном
    return RedirectResponse(
        f"{os.getenv('FRONTEND_URL')}/auth/success?token={jwt_token}"
    )


# В auth_endpoints.py или debug_endpoints.py
@auth_router.post("/migrate-passwords", include_in_schema=False)
async def migrate_passwords_endpoint(
    auth_service: AuthService = Depends(get_auth_service),
    # Добавьте проверку админа для безопасности
):
    """Мигрирует пароли (только для разработки)"""
    await auth_service.migrate_passwords()
    return {"message": "Password migration completed"}
