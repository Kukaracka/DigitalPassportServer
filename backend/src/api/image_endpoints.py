from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, status
from api.dependencies import get_current_authorised_user, get_storage_service, get_user_service
from database.models import UserModel
from services.storage_service import StorageService
from services.user_service import UserService

image_router = APIRouter()

@image_router.post("/users/me/avatar")
async def upload_user_avatar(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_authorised_user),
    user_service: UserService = Depends(get_user_service),
    storage: StorageService = Depends(get_storage_service),  # Инъекция зависимости
):
    """
    Загрузка аватара пользователя
    """
    # Проверяем файл
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Читаем и проверяем размер
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Max size: 5MB"
        )
    
    # Генерируем имя файла
    import time
    import os
    file_extension = os.path.splitext(file.filename)[1]
    object_name = f"avatars/{current_user.id}/avatar_{int(time.time())}{file_extension}"
    
    # Загружаем файл
    await storage.upload_file(
        file_data=contents,
        file_name=object_name,
        content_type=file.content_type
    )
    
    # Обновляем БД
    await user_service.users_repo.update(
        current_user.id,
        {"avatar": object_name}
    )
    
    # Получаем URL
    avatar_url = storage.get_download_url(object_name, expires=3600)
    
    return {
        "filename": object_name,
        "avatar_url": avatar_url,
        "message": "Avatar uploaded successfully"
    }
