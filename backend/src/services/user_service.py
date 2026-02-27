from typing import Optional
from fastapi import HTTPException
from database.models import UserModel
from schemas.user_schemas import UserCreateSchema, UserReadSchema, UserUpdateSchema
from services.storage_service import StorageService
from utils.repository import SQLAlchemyRepository


from typing import Optional
from fastapi import HTTPException
from database.models import UserModel
from schemas.user_schemas import UserCreateSchema, UserReadSchema, UserUpdateSchema
from utils.repository import SQLAlchemyRepository


class UserService:
    def __init__(self, users_repo: SQLAlchemyRepository[UserModel], storage_service: StorageService):
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

    async def read_one_user(self, user_id: int):
        user_obj = await self.users_repo.read_one(user_id)
        if not user_obj:
            return None

        # Преобразуем SQLAlchemy объект в словарь
        user_dict = {
            c.name: getattr(user_obj, c.name) for c in user_obj.__table__.columns
        }
        
        # Генерируем URL'ы для аватара
        if user_dict.get("avatar"):
            # Если аватар есть - даем ссылку на существующий файл
            avatar_url = self.storage_service.get_presigned_url(
                file_name=user_dict["avatar"],
                expires=3600  # 1 час
            )
        else:
            # Если аватара нет - даем ссылку на дефолтный
            avatar_url = "/static/default-avatar.png"
        
        # URL для загрузки нового аватара (всегда доступен)
        # Формируем путь с уникальным именем, чтобы избежать кэширования
        import time
        upload_file_name = f"avatars/{user_id}/avatar_{int(time.time())}.jpg"
        avatar_upload_url = self.storage_service.get_upload_presigned_url(
            file_name=upload_file_name,
            expires=3600  # 1 час
        )
        
        # Добавляем URL'ы в словарь
        user_dict.update({
            "avatar_url": avatar_url,
            "avatar_upload_url": avatar_upload_url
        })

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
