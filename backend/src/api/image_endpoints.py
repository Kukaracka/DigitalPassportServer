import os
import time
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
    storage: StorageService = Depends(get_storage_service),
):
    """
    Загрузка аватара пользователя
    """
    # Проверяем, что файл - изображение
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Читаем файл
    contents = await file.read()
    
    # Проверяем размер (макс 5MB)
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Max size: 5MB"
        )
    
    # ОПРЕДЕЛЯЕМ РАСШИРЕНИЕ ИЗ ЗАГРУЖАЕМОГО ФАЙЛА
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    # Разрешенные расширения
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    
    if file_extension not in allowed_extensions:
        # Если расширение не разрешено, используем .jpg по умолчанию
        file_extension = '.jpg'
    
    # Всегда используем avatar + расширение загруженного файла
    object_name = f"avatars/{current_user.id}/avatar{file_extension}"
    
    # Загружаем файл
    success = await storage.upload_file(
        file_data=contents,
        file_name=object_name,
        content_type=file.content_type
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )
    
    # Обновляем запись пользователя в БД
    await user_service.users_repo.update_one(
        current_user.id,
        {"avatar": object_name}
    )
    
    # Получаем URL для просмотра
    avatar_url = storage.get_download_url(object_name, expires=3600)
    
    return {
        "filename": object_name,
        "avatar_url": avatar_url,
        "message": "Avatar uploaded successfully"
    }
