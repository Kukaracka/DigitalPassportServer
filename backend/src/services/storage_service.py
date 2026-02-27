# services/storage_service.py

from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException
import os
from datetime import timedelta
from typing import Optional, Union, BinaryIO
import logging

# Настраиваем логирование
logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        # Внутренний endpoint для подключения из контейнера
        self.internal_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        # Внешний endpoint для доступа из браузера
        self.public_endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", "http://localhost:9000")
        
        # Убираем протокол из internal_endpoint для MinIO клиента
        clean_endpoint = self.internal_endpoint.replace("http://", "").replace("https://", "")
        
        # Настройки безопасности
        self.secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.bucket = os.getenv("MINIO_BUCKET", "product-images")
        
        # Регион (если нужен)
        self.region = os.getenv("MINIO_REGION", "us-east-1")
        
        logger.info(f"Initializing MinIO client with endpoint: {clean_endpoint}, secure: {self.secure}")
        
        try:
            self.client = Minio(
                endpoint=clean_endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
                region=self.region
            )
            self._ensure_bucket_exists()
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise

    def _ensure_bucket_exists(self):
        """Проверяет существование бакета и создает его при необходимости"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Bucket '{self.bucket}' created successfully")
                
                # Устанавливаем публичную политику для чтения (опционально)
                self._set_public_read_policy()
            else:
                logger.info(f"Bucket '{self.bucket}' already exists")
        except Exception as e:
            logger.error(f"Error checking/creating bucket: {e}")
            raise

    def _set_public_read_policy(self):
        """Устанавливает политику публичного чтения для бакета"""
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket}/*"]
                    }
                ]
            }
            import json
            self.client.set_bucket_policy(self.bucket, json.dumps(policy))
            logger.info(f"Public read policy set for bucket '{self.bucket}'")
        except Exception as e:
            logger.warning(f"Could not set public read policy: {e}")


    def upload_file(self, file_data: bytes, file_name: str, content_type: str) -> bool:
        """
        Синхронная загрузка файла в MinIO
        """
        try:
            from io import BytesIO
            
            # Создаем поток из байтов
            data_stream = BytesIO(file_data)
            
            # Загружаем в MinIO
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=file_name,
                data=data_stream,
                length=len(file_data),
                content_type=content_type
            )
            
            logger.info(f"File uploaded successfully: {file_name}")
            return True
            
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return False

    def get_file_url(
        self, 
        file_name: str, 
        expires: int = 3600,
        method: str = "GET"
    ) -> Optional[str]:
        """
        Получает подписанный URL для доступа к файлу
        
        Args:
            file_name: Имя файла в хранилище
            expires: Время жизни URL в секундах
            method: HTTP метод (GET, PUT)
        
        Returns:
            Optional[str]: Подписанный URL или None
        """
        try:
            # Проверяем существование файла
            self.client.stat_object(self.bucket, file_name)
            
            # Генерируем подписанный URL
            url = self.client.get_presigned_url(
                method,
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires)
            )
            
            # Заменяем внутренний endpoint на публичный
            public_url = self._replace_endpoint(url)
            
            logger.debug(f"Generated {method} URL for {file_name}: {public_url}")
            return public_url
            
        except S3Error as e:
            if e.code == "NoSuchKey":
                logger.warning(f"File not found: {file_name}")
                return None
            else:
                logger.error(f"MinIO error creating presigned URL: {e}")
                return None
        except Exception as e:
            logger.error(f"Unexpected error creating presigned URL: {e}")
            return None

    def get_download_url(self, file_name: str, expires: int = 3600) -> Optional[str]:
        """
        Получение URL для скачивания файла
        """
        logger.info(f"=== get_download_url called for: {file_name} ===")
        logger.info(f"Bucket: {self.bucket}")
        
        try:
            # Проверяем существование файла через stat_object
            try:
                stat = self.client.stat_object(self.bucket, file_name)
                logger.info(f"File exists! Size: {stat.size}, ETag: {stat.etag}")
            except Exception as e:
                logger.error(f"File does NOT exist in MinIO: {e}")
                return None
            
            # Генерируем presigned URL
            logger.info("Generating presigned URL...")
            from datetime import timedelta
            
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires)
            )
            logger.info(f"Raw presigned URL: {url}")
            
            # Заменяем внутренний endpoint на публичный
            url = self._replace_endpoint(url)
            logger.info(f"Final URL after replace: {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"Error in get_download_url: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def get_upload_url(self, file_name: str, expires: int = 3600) -> Optional[str]:
        """
        Получение URL для загрузки файла
        """
        logger.info(f"=== get_upload_url ВЫЗВАН для: {file_name} ===")
        
        try:
            logger.info("Генерируем upload presigned URL...")
            from datetime import timedelta
            
            url = self.client.presigned_put_object(
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires)
            )
            logger.info(f"✅ Raw upload URL: {url}")
            
            # Заменяем внутренний endpoint на публичный
            url = self._replace_endpoint(url)
            logger.info(f"✅ Final upload URL: {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"❌ Ошибка в get_upload_url: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def get_public_url(self, file_name: str) -> Optional[str]:
        """
        Получает прямой публичный URL (без подписи)
        Работает только если бакет имеет публичный доступ на чтение
        """
        try:
            # Проверяем существование файла
            self.client.stat_object(self.bucket, file_name)
            
            # Формируем прямой URL
            url = f"{self.public_endpoint}/{self.bucket}/{file_name}"
            return url
            
        except S3Error as e:
            if e.code == "NoSuchKey":
                logger.warning(f"File not found for public URL: {file_name}")
                return None
            logger.error(f"Error checking file for public URL: {e}")
            return None

    def delete_file(self, file_name: str) -> bool:
        """Удаляет файл из хранилища"""
        try:
            self.client.remove_object(self.bucket, file_name)
            logger.info(f"File deleted: {file_name}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting file {file_name}: {e}")
            return False

    def file_exists(self, file_name: str) -> bool:
        """Проверяет существование файла"""
        try:
            self.client.stat_object(self.bucket, file_name)
            return True
        except S3Error:
            return False

    def get_file_info(self, file_name: str) -> Optional[dict]:
        """Получает информацию о файле"""
        try:
            obj = self.client.stat_object(self.bucket, file_name)
            return {
                "size": obj.size,
                "etag": obj.etag,
                "last_modified": obj.last_modified,
                "content_type": obj.content_type,
                "metadata": obj.metadata
            }
        except S3Error as e:
            logger.error(f"Error getting file info for {file_name}: {e}")
            return None

    def _replace_endpoint(self, url: str) -> str:
        """
        Заменяет внутренний endpoint MinIO на публичный
        """
        if not url:
            return url
        
        logger.info(f"Original URL: {url}")
        
        # Публичный endpoint из .env
        public_url = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000")
        logger.info(f"Public URL from env: {public_url}")
        
        # Внутренний endpoint
        internal = "minio:9000"
        
        # Заменяем внутренний endpoint на публичный
        if internal in url:
            new_url = url.replace(internal, public_url.replace("http://", "").replace("https://", ""))
            logger.info(f"Replaced URL: {new_url}")
            return new_url
        
        # Также проверяем наличие localhost:9000
        if "localhost:9000" in url:
            new_url = url.replace("localhost:9000", public_url.replace("http://", "").replace("https://", ""))
            logger.info(f"Replaced localhost URL: {new_url}")
            return new_url
        
        logger.info("No replacement needed")
        return url

    def generate_file_name(self, user_id: int, original_filename: str) -> str:
        """
        Генерирует уникальное имя файла для аватара
        """
        import time
        import hashlib
        
        # Получаем расширение файла
        ext = os.path.splitext(original_filename)[1]
        
        # Генерируем уникальное имя
        timestamp = int(time.time())
        hash_obj = hashlib.md5(f"{user_id}_{timestamp}".encode())
        file_hash = hash_obj.hexdigest()[:8]
        
        return f"avatars/{user_id}/avatar_{timestamp}_{file_hash}{ext}"
