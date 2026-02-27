from typing import Optional
from fastapi import HTTPException
from database.models import UserModel
from schemas.user_schemas import UserCreateSchema, UserReadSchema, UserUpdateSchema
from utils.repository import SQLAlchemyRepository


from typing import Optional
from fastapi import HTTPException
from database.models import UserModel
from schemas.user_schemas import UserCreateSchema, UserReadSchema, UserUpdateSchema
from utils.repository import SQLAlchemyRepository


class UserService:
    def __init__(self, users_repo: SQLAlchemyRepository[UserModel]):
        self.users_repo: SQLAlchemyRepository = users_repo

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

    async def read_one_user(self, user_id: int):
        user_obj = await self.users_repo.read_one(user_id)
        if not user_obj:
            return None

        # Преобразуем SQLAlchemy объект в словарь
        user_dict = {
            c.name: getattr(user_obj, c.name) for c in user_obj.__table__.columns
        }

        # Добавляем URL аватара, если он есть
        if user_dict.get("avatar"):
            # Для просмотра аватара используем get_file_url
            avatar_url = self.storage_service.get_file_url(user_dict["avatar"])
            user_dict["avatar_url"] = avatar_url
            
            # Для загрузки нового аватара (если нужно)
            user_dict["avatar_upload_url"] = self.storage_service.get_upload_url(user_dict["avatar"])
        else:
            # Можно добавить URL для дефолтного аватара
            user_dict["avatar_url"] = "/static/default-avatar.png"

        return UserReadSchema.model_validate(user_dict)

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
