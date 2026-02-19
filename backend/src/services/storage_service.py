# src/services/storage_service.py

from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import uuid
import os
from datetime import timedelta
from typing import Optional


class StorageService:
    def __init__(self):  # Без параметров, использует os.getenv
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
        object_name = f"avatars/{user_id}/{uuid.uuid4()}.{file_extension}"

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=file.content_type,
        )

        return object_name

    def get_upload_url(self, user_id: int, expires: int = 3600) -> Optional[str]:
        """Создание pre-signed URL для прямой загрузки с фронтенда"""
        object_name = f"avatars/{user_id}/avatar.jpg"
        
        try:
            url = self.client.presigned_put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print("MinIO error:", e)
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
            print("MinIO error:", e)
            return None
