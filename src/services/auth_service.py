from authx import AuthX
from fastapi import HTTPException
from passlib.context import CryptContext

from database.models import UserModel
from repositories.user_repository import UserRepository
from schemas.user_schemas import UserCreateSchema


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, users_repo: UserRepository):
        self.users_repo = users_repo
        self.pwd_context = pwd_context

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def _get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def authenticate_user(
        self,
        security: AuthX,
        username: str,
        password: str
    ) -> str:
        user = await self.users_repo.get_by_username(username)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid username")

        if not self.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password")

        return security.create_access_token(uid=str(user.id))

    async def registrate_user(self, user_data: UserCreateSchema) -> UserModel:
        existing_user = await self.users_repo.get_by_username(user_data.username)

        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="User with this username already exists"
            )

        user_dict = user_data.model_dump()
        user_dict["password"] = self._get_password_hash(user_dict["password"])

        return await self.users_repo.create_one(user_dict)

    async def change_password(
        self,
        user: UserModel,
        old_password: str,
        new_password: str,
    ) -> None:

        if not self.verify_password(old_password, user.password):
            raise HTTPException(status_code=400, detail="Invalid old password")

        new_hash = self._get_password_hash(new_password)

        await self.users_repo.update_one(
            user.id,
            {"password": new_hash}
        )

    async def migrate_passwords(self) -> None:
        users = await self.users_repo.read_all()

        for user in users:
            if not user.password.startswith("$2b$"):
                hashed = self._get_password_hash(user.password)
                await self.users_repo.update_one(
                    user.id,
                    {"password": hashed}
                )
