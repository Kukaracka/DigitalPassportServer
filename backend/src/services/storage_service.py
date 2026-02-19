# src/services/storage_service.py

from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import uuid
import os
from datetime import timedelta
from typing import Optional


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
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except Exception as e:
            print(f"Error checking/creating bucket: {e}")

    def upload_image(self, file: UploadFile, user_id: int) -> str:
        """Загрузка файла через бэкенд"""
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "png"
        object_name = f"avatars/{user_id}/{uuid.uuid4()}.{file_extension}"

        try:
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=file.file,
                length=-1,
                part_size=10 * 1024 * 1024,
                content_type=file.content_type,
            )
            return object_name
        except S3Error as e:
            print(f"MinIO upload error: {e}")
            raise

    def get_upload_url(self, user_id: int, expires_seconds: int = 3600) -> Optional[str]:
        """
        Создание pre-signed URL для прямой загрузки с фронтенда
        
        Args:
            user_id: ID пользователя
            expires_seconds: Время жизни ссылки в секундах (по умолчанию 1 час)
        """
        object_name = f"avatars/{user_id}/avatar.jpg"
        
        try:
            # MinIO ожидает timedelta, а не int
            expires_delta = timedelta(seconds=expires_seconds)
            
            url = self.client.presigned_put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires_delta  # Теперь передаем timedelta
            )
            return url
        except S3Error as e:
            print(f"MinIO error creating upload URL: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error creating upload URL: {e}")
            return None
    
    def get_file_url(self, object_name: str, expires_seconds: int = 3600) -> Optional[str]:
        """
        Получение pre-signed URL для просмотра файла
        
        Args:
            object_name: Имя объекта в MinIO
            expires_seconds: Время жизни ссылки в секундах
        """
        if not object_name:
            return None
            
        try:
            expires_delta = timedelta(seconds=expires_seconds)
            
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires_delta  # Исправлено: передаем timedelta
            )
            return url
        except S3Error as e:
            print(f"MinIO error creating download URL: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error creating download URL: {e}")
            return None
