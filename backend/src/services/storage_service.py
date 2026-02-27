from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException
import os
from datetime import timedelta

class StorageService:
    def __init__(self):
        # Внутренний endpoint для подключения из контейнера
        self.internal_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        # Внешний endpoint для доступа из браузера
        self.public_endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", "http://localhost:9000")
        
        self.client = Minio(
            endpoint=self.internal_endpoint,
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=False,  # True, если https
        )
        self.bucket = os.getenv("MINIO_BUCKET", "product-images")

        # Проверяем, что бакет существует
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except Exception as e:
            print(f"Error checking/creating bucket: {e}")

    async def upload_file(self, file_bytes: bytes, file_name: str, content_type: str):
        try:
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=file_name,
                data=file_bytes,
                length=len(file_bytes),
                content_type=content_type,
            )
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"MinIO upload error: {e}")

    def get_presigned_url(self, file_name: str, expires: int = 3600) -> str | None:
        try:
            # Получаем pre-signed URL от MinIO
            url = self.client.get_presigned_url(
                "GET",
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires)
            )
            
            # Заменяем внутренний endpoint на внешний
            url = self._replace_endpoint(url)
            
            return url
        except S3Error as e:
            print(f"MinIO error creating presigned URL: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def get_upload_presigned_url(self, file_name: str, expires: int = 3600) -> str | None:
        """
        Получение pre-signed URL для загрузки файла
        """
        try:
            url = self.client.get_presigned_url(
                "PUT",
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires)
            )
            
            # Заменяем внутренний endpoint на внешний
            url = self._replace_endpoint(url)
            
            return url
        except S3Error as e:
            print(f"MinIO error creating upload presigned URL: {e}")
            return None
    
    def _replace_endpoint(self, url: str) -> str:
        """
        Заменяет внутренний endpoint MinIO на публичный
        """
        if not url:
            return url
            
        # Формируем внутренний хост для замены
        internal_host = self.internal_endpoint.replace("http://", "").replace("https://", "")
        
        # Заменяем в URL
        if internal_host in url:
            # Если URL начинается с http://internal_host
            url = url.replace(f"http://{internal_host}", self.public_endpoint)
            url = url.replace(f"https://{internal_host}", self.public_endpoint)
        
        return url
    
    def get_public_url(self, file_name: str) -> str:
        """
        Получение прямого публичного URL (без подписи)
        """
        return f"{self.public_endpoint}/{self.bucket}/{file_name}"
