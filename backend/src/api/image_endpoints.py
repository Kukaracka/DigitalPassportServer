from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from services.user_service import UserService
from services.storage_service import StorageService
from database.models import UserModel
from schemas.user_schemas import UserReadSchema

from api.dependencies import get_current_authorised_user, get_user_service

image_router = APIRouter(prefix="/users", tags=["Users"])
storage_service = StorageService()


@image_router.post("/me/avatar", response_description="Upload user avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_authorised_user),
    user_service: UserService = Depends(get_user_service),
):
    # загружаем файл в MinIO
    object_name = storage_service.upload_image(file, current_user.id)

    # сохраняем имя файла в БД
    current_user.avatar_filename = object_name
    await user_service.update_user(current_user.id, {"avatar_filename": object_name})

    # генерируем presigned URL
    avatar_url = storage_service.get_presigned_url(object_name)

    return {"message": "Avatar uploaded", "avatar_filename": object_name, "avatar_url": avatar_url}


@image_router.get("/me", response_model=UserReadSchema)
async def get_current_user(
    current_user: UserModel = Depends(get_current_authorised_user),
    user_service: UserService = Depends(get_user_service),
):
    user_data = await user_service.read_one_user(current_user.id)

    # добавляем presigned URL если есть avatar
    avatar_url = None
    if user_data.avatar_filename:
        try:
            avatar_url = storage_service.get_presigned_url(user_data.avatar_filename)
        except Exception:
            avatar_url = None

    return UserReadSchema(
        id=user_data.id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        father_name=user_data.father_name,
        phone_number=user_data.phone_number,
        username=user_data.username,
        email=user_data.email,
        avatar_filename=user_data.avatar_filename,
        avatar_url=avatar_url
    )
