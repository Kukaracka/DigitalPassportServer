# src/services/storage_service.py
import os
from minio import Minio
from datetime import timedelta
from typing import Optional

class StorageService:
    def __init__(self):
        # Внутренний endpoint для подключения к MinIO (всегда используется внутри Docker)
        self.internal_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        
        # Публичный endpoint для доступа из браузера/клиента
        # В продакшене это будет ваш домен, в разработке - localhost
        self.public_endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", "http://localhost:9000")
        
        # Для MinIO клиента всегда используем internal_endpoint
        self.client = Minio(
            endpoint=self.internal_endpoint,  # всегда minio:9000 внутри Docker
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=False,  # в продакшене с HTTPS будет True
        )
        self.bucket = os.getenv("MINIO_BUCKET", "product-images")
        
        # Убедимся, что бакет существует
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except Exception as e:
            print(f"Error checking/creating bucket: {e}")

    def get_file_url(self, object_name: str, expires_seconds: int = 3600) -> Optional[str]:
        """
        Получение pre-signed URL для просмотра файла с правильным публичным endpoint
        """
        if not object_name:
            return None
            
        try:
            expires_delta = timedelta(seconds=expires_seconds)
            
            # Получаем pre-signed URL от MinIO (с internal_endpoint)
            internal_url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires_delta
            )
            
            # Заменяем внутренний endpoint на публичный
            if internal_url:
                # Извлекаем хост из internal_url (minio:9000)
                # и заменяем на публичный endpoint
                public_url = internal_url.replace(
                    self.internal_endpoint,
                    self.public_endpoint.replace("http://", "").replace("https://", "")
                )
                return public_url
            
            return None
            
        except Exception as e:
            print(f"Error creating download URL: {e}")
            return None
