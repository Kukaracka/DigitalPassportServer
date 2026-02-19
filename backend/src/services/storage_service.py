from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import uuid
import os
from datetime import timedelta

class StorageService:
    def __init__(self):
        self.client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=False,
        )
        self.bucket = os.getenv("MINIO_BUCKET", "product-images")

    def upload_image(self, file: UploadFile, user_id: int) -> str:
        """Загрузка файла через бэкенд"""
        file_extension = file.filename.split(".")[-1]
        object_name = f"{user_id}.{file_extension}"

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=file.file,
            length=-1,  # Автоматическая длина, можно заменить на file_size
            part_size=10 * 1024 * 1024,
            content_type=file.content_type,
        )

        return object_name

    def get_upload_url(self, user_id: int, file_extension: str = "png", expires: int = 3600) -> str:
        """Создание pre-signed URL для прямой загрузки с фронтенда"""
        object_name = f"{user_id}.{file_extension}"
        try:
            url = self.client.presigned_put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires  # Время жизни ссылки в секундах
            )
            return url
        except S3Error as e:
            print("MinIO error:", e)
            return ""
