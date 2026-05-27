from typing import Optional

from fastapi import HTTPException, status
from api.dependencies import get_auth_service
from database.models import UserModel
from schemas.user_schemas import UserCreateSchema, UserReadSchema, UserUpdateSchema
from services.auth_service import AuthService
from services.product_service import ProductService
from services.storage_service import StorageService
from utils.repository import SQLAlchemyRepository


import logging
import traceback

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        users_repo: SQLAlchemyRepository[UserModel],
        storage_service: StorageService,
        auth_service: AuthService | None = None,
        product_service: ProductService | None = None,
    ):
        self.users_repo = users_repo
        self.storage_service = storage_service
        self.auth_service = auth_service
        self.product_service = product_service

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
        """Получение пользователя по ID с URL для аватара"""
        logger.info(f"=== Чтение пользователя {user_id} ===")

        user_obj = await self.users_repo.read_one(user_id)
        if not user_obj:
            logger.warning(f"Пользователь {user_id} не найден")
            return None

        # Преобразуем SQLAlchemy объект в словарь
        user_dict = {
            "id": user_obj.id,
            "username": user_obj.username,
            "email": user_obj.email,
            "first_name": user_obj.first_name,
            "last_name": user_obj.last_name,
            "father_name": user_obj.father_name,
            "phone_number": user_obj.phone_number,
            "avatar": user_obj.avatar,
        }

        logger.info(f"Данные пользователя: {user_dict}")
        logger.info(f"Storage service: {self.storage_service}")

        # Генерируем URL для просмотра аватара
        avatar_url = None
        if user_obj.avatar:
            logger.info(f"Есть аватар в БД: {user_obj.avatar}")
            try:
                # Проверим, существует ли файл в MinIO
                logger.info("Проверяем существование файла в MinIO...")

                # Сначала проверим, есть ли метод get_download_url
                logger.info(f"Методы storage_service: {dir(self.storage_service)}")

                avatar_url = self.storage_service.get_download_url(
                    file_name=user_obj.avatar, expires=3600
                )
                logger.info(f"Сгенерированный avatar_url: {avatar_url}")

            except Exception as e:
                logger.error(f"ОШИБКА при генерации avatar_url: {e}")
                logger.error(traceback.format_exc())
        else:
            logger.info("Нет аватара в БД")

        # Генерируем URL для загрузки нового аватара
        try:
            logger.info("Генерируем upload URL...")
            new_avatar_name = f"avatars/{user_id}/avatar.jpg"
            logger.info(f"Новое имя файла: {new_avatar_name}")

            avatar_upload_url = self.storage_service.get_upload_url(
                file_name=new_avatar_name, expires=3600
            )
            logger.info(f"Сгенерированный avatar_upload_url: {avatar_upload_url}")

        except Exception as e:
            logger.error(f"ОШИБКА при генерации upload URL: {e}")
            logger.error(traceback.format_exc())
            avatar_upload_url = None

        # Добавляем URL в словарь
        user_dict["avatar_url"] = avatar_url
        user_dict["avatar_upload_url"] = avatar_upload_url

        logger.info(f"Финальный словарь: {user_dict}")

        print(f"\n\n\n{user_dict}")
        # Валидируем и возвращаем
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

    async def delete_user(self, user_id: int, password: str) -> bool:
        user = await self.users_repo.read_one(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not self.auth_service.verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Invalid password")

        files_to_delete = []

        # avatar
        if user.avatar:
            files_to_delete.append(user.avatar)

        # product images
        if self.product_service:
            product_files = (
                await self.product_service.get_all_product_file_names_by_owner(user_id)
            )
            files_to_delete.extend(product_files)

        # delete files from MinIO
        if files_to_delete:
            await self.storage_service.delete_files(files_to_delete)

        # delete user from DB
        deleted = await self.users_repo.delete_one(user_id)

        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete user")

        return True

    async def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
    ):
        user = await self.users_repo.read_one(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await self.auth_service.change_password(
            user=user,
            old_password=old_password,
            new_password=new_password,
        )

        return True
