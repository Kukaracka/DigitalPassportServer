from typing import Optional
from fastapi import HTTPException
from database.models import UserModel
from schemas.user_schemas import UserCreateSchema, UserReadSchema, UserUpdateSchema
from services.storage_service import StorageService
from utils.repository import SQLAlchemyRepository


class UserService:
    def __init__(
        self,
        users_repo: SQLAlchemyRepository[UserModel],
        storage_service: StorageService,
    ):
        self.users_repo: SQLAlchemyRepository = users_repo
        self.storage_service: StorageService = storage_service


    async def add_user(self, user: UserCreateSchema):
        """Добавить пользователя"""
        users_dict = user.model_dump()
        user_id = await self.users_repo.create_one(users_dict)
        return user_id

    async def read_all_users(self) -> list[UserReadSchema]:
        """Получить всех пользователей"""
        user_data: list[UserModel] | None = await self.users_repo.read_all()
        users_schema = [UserReadSchema.model_validate(user) for user in user_data]
        return users_schema

    async def read_one_user(self, user_id: int) -> dict:
        user_data = await self.users_repo.read_one(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        user_dict = user_data.model_dump()  # преобразуем модель в dict

        # добавляем avatar_url через presigned ссылку
        user_dict["avatar_url"] = self.storage_service.get_presigned_url(str(user_data.id))

        return user_dict

    async def update_user(
        self, id: int, user_update: UserUpdateSchema
    ) -> Optional[UserReadSchema]:
        """Обновить данные о пользователе"""
        existing_user = await self.users_repo.read_one(id)
        if not existing_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)

        updated_data = await self.users_repo.update_one(id, update_data)
        if updated_data:
            return await self.read_one_user(id)
        return None
