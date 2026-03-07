import os
import time
import asyncio
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
    
    # БЕЗОПАСНО получаем расширение файла
    # file.filename может быть None, поэтому проверяем
    filename = file.filename or f"avatar_{int(time.time())}.jpg"
    
    # Получаем расширение и приводим к нижнему регистру
    # os.path.splitext может вернуть ('filename', '.ext') или ('filename', '')
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Если расширения нет или оно не поддерживается, используем .jpg
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if not file_extension or file_extension not in allowed_extensions:
        file_extension = '.jpg'
    
    # ВАЖНО: Используем фиксированное имя без временной метки!
    # Так проще обновлять и не плодить файлы
    object_name = f"{current_user.id}/avatar{file_extension}"
    
    # Определяем content_type для MinIO
    content_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    
    # Получаем content_type из маппинга или используем исходный
    content_type = content_type_map.get(file_extension, file.content_type or 'image/jpeg')
    
    # Загружаем файл (синхронный вызов в потоке)
    try:
        # Проверяем, какой метод использует storage_service
        if hasattr(storage, 'upload_file') and callable(storage.upload_file):
            # Если метод асинхронный
            if asyncio.iscoroutinefunction(storage.upload_file):
                success = await storage.upload_file(
                    file_data=contents,
                    file_name=object_name,
                    content_type=content_type
                )
            else:
                # Если метод синхронный
                success = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: storage.upload_file(contents, object_name, content_type)
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage service not properly configured"
            )
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )
    
    # Обновляем запись пользователя в БД
    try:
        await user_service.users_repo.update_one(
            current_user.id,
            {"avatar": object_name}
        )
    except Exception as e:
        print(f"Database update error: {e}")
        # Пробуем удалить загруженный файл, если не удалось обновить БД
        try:
            storage.delete_file(object_name)
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user record: {str(e)}"
        )
    
    # Получаем URL для загруженного аватара
    avatar_url = None
    try:
        avatar_url = storage.get_download_url(object_name, expires=3600)
    except Exception as e:
        print(f"Error getting avatar URL: {e}")
        # Не падаем, если не удалось получить URL
    
    return {
        "filename": object_name,
        "avatar_url": avatar_url,
        "message": "Avatar uploaded successfully"
    }
