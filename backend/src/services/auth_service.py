from authx import AuthX
from fastapi import HTTPException, security
from passlib.context import CryptContext

from database.models import UserModel
from repositories.user_repository import UserRepository
from schemas.user_schemas import UserCreateSchema


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, users_repo_cls: UserRepository):
        self.users_repo: UserRepository = users_repo_cls
        self.security = security
        self.pwd_context = pwd_context

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def _get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def authenticate_user(
        self, security: AuthX, username: str, password: str
    ) -> str:
        user = await self.users_repo.get_by_username(username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username")

        if not self._verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password")

        token = security.create_access_token(uid=str(user.id))
        return token

    async def registrate_user(self, user_data: UserCreateSchema) -> UserModel:
        """
        Создает пользователя в БД. Возвращает объект UserModel.
        """
        existing_user = await self.users_repo.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=409, detail="User with this username already exist"
            )

        user_dict = user_data.model_dump()
        user_dict["password"] = self._get_password_hash(user_dict["password"])

        new_user = await self.users_repo.create_one(user_dict)  # <- сразу объект модели
        return new_user

    async def migrate_passwords(self):
        """Мигрирует все незашифрованные пароли"""
        users = await self.users_repo.read_all()

        for user in users:
            # Проверяем, не хэширован ли уже пароль
            if not user.password.startswith("$2b$"):
                hashed_password = self._get_password_hash(user.password)
                await self.users_repo.update_one(user.id, {"password": hashed_password})
                print(f"Migrated password for user: {user.username}")
