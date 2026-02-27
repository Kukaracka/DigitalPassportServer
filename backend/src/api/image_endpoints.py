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
    
    # Проверяем размер файла (не больше 5MB)
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Max size: 5MB"
        )
    
    # Генерируем имя файла
    import time
    import os
    file_extension = os.path.splitext(file.filename)[1]
    if not file_extension:
        file_extension = '.png'
    
    object_name = f"avatars/{current_user.id}/avatar_{int(time.time())}{file_extension}"
    
    # Загружаем файл (синхронный вызов в потоке)
    import asyncio
    success = await asyncio.get_event_loop().run_in_executor(
        None,  # используем пул потоков по умолчанию
        lambda: storage.upload_file(contents, object_name, file.content_type)
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
    
    # Получаем URL для загруженного аватара
    avatar_url = storage.get_download_url(object_name, expires=3600)
    
    return {
        "filename": object_name,
        "avatar_url": avatar_url,
        "message": "Avatar uploaded successfully"
    }
