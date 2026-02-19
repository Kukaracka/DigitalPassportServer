from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import uuid
import os
from datetime import timedelta
from typing import Optional  # Добавлен недостающий импорт


class StorageService:
    def __init__(self):
        self.client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=False,
        )
        self.bucket = os.getenv("MINIO_BUCKET", "product-images")
        self.base_url = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000")
        
        # Убедимся, что бакет существует
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_image(self, file: UploadFile, user_id: int) -> str:
        """Загрузка файла через бэкенд"""
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "png"
        # Используем UUID для уникальности
        object_name = f"avatars/{user_id}/{uuid.uuid4()}.{file_extension}"

        # Получаем размер файла (опционально, но рекомендуется)
        file.file.seek(0, 2)  # Перемещаемся в конец файла
        file_size = file.file.tell()
        file.file.seek(0)  # Возвращаемся в начало

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=file.file,
            length=file_size,  # Лучше указать точный размер
            part_size=10 * 1024 * 1024,
            content_type=file.content_type,
        )

        return object_name

    def get_upload_url(self, user_id: int, filename: Optional[str] = None, expires: int = 3600) -> Optional[str]:
        """
        Создание pre-signed URL для прямой загрузки с фронтенда
        
        Args:
            user_id: ID пользователя
            filename: Имя файла (если не указано, генерируется автоматически)
            expires: Время жизни ссылки в секундах
        """
        # Если filename не указан, генерируем временное имя
        if filename:
            object_name = f"avatars/{user_id}/temp_{filename}"
        else:
            object_name = f"avatars/{user_id}/temp_{uuid.uuid4()}.jpg"
        
        try:
            url = self.client.presigned_put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print(f"MinIO error creating upload URL: {e}")
            return None
    
    def get_file_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """Получение pre-signed URL для просмотра файла"""
        if not object_name:
            return None
            
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print(f"MinIO error creating download URL: {e}")
            return None
    
    def get_public_url(self, object_name: str) -> Optional[str]:
        """Получение публичного URL (если бакет публичный)"""
        if not object_name:
            return None
        return f"{self.base_url}/{self.bucket}/{object_name}"
    
    def delete_image(self, object_name: str) -> bool:
        """Удаление файла"""
        try:
            self.client.remove_object(
                bucket_name=self.bucket,
                object_name=object_name
            )
            return True
        except S3Error as e:
            print(f"MinIO error deleting file: {e}")
            return False
    
    def move_temp_to_permanent(self, temp_object_name: str, user_id: int) -> Optional[str]:
        """
        Перемещение временного файла в постоянное хранилище
        (для случая, когда загрузка была через pre-signed URL)
        """
        try:
            # Генерируем постоянное имя
            file_extension = temp_object_name.split(".")[-1]
            permanent_name = f"avatars/{user_id}/{uuid.uuid4()}.{file_extension}"
            
            # Копируем объект
            self.client.copy_object(
                bucket_name=self.bucket,
                object_name=permanent_name,
                source=f"{self.bucket}/{temp_object_name}"
            )
            
            # Удаляем временный
            self.delete_image(temp_object_name)
            
            return permanent_name
        except S3Error as e:
            print(f"MinIO error moving file: {e}")
            return None
