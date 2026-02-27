# services/storage_service.py

import os
import logging
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from typing import Optional
import urllib3

# Отключаем предупреждения о самоподписанных сертификатах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        self.public_url = os.getenv("MINIO_PUBLIC_URL", "https://194.150.220.138:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "strongpassword")
        self.bucket = os.getenv("MINIO_BUCKET", "avatars")
        
        # Очищаем endpoint от протокола
        clean_endpoint = self.endpoint.replace("http://", "").replace("https://", "")
        
        logger.info(f"Подключение к MinIO: {clean_endpoint} (HTTPS, проверка сертификата отключена)")
        
        # Создаем HTTP client с отключенной проверкой сертификатов
        http_client = urllib3.PoolManager(
            cert_reqs='CERT_NONE',
            assert_hostname=False
        )
        
        self.client = Minio(
            endpoint=clean_endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=True,  # HTTPS
            http_client=http_client  # Используем наш HTTP client с отключенной проверкой
        )
        
        # Пробуем подключиться
        try:
            self._ensure_bucket_exists()
        except Exception as e:
            logger.error(f"Ошибка подключения к MinIO: {e}")
            # Пробуем с cert_check=False
            self.client = Minio(
                endpoint=clean_endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=True,
                cert_check=False  # Альтернативный способ отключения проверки
            )
            self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Проверяет существование бакета"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Бакет {self.bucket} создан")
            else:
                logger.info(f"Бакет {self.bucket} существует")
        except Exception as e:
            logger.error(f"Ошибка при проверке/создании бакета: {e}")
            raise
    
    def get_download_url(self, file_name: str, expires: int = 3600) -> Optional[str]:
        """Получение URL для скачивания файла"""
        try:
            # Проверяем существование файла
            self.client.stat_object(self.bucket, file_name)
            
            # Генерируем presigned URL
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires)
            )
            
            # Заменяем внутренний endpoint на публичный
            url = self._replace_endpoint(url)
            
            return url
            
        except S3Error as e:
            logger.error(f"Ошибка MinIO: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return None
    
    def get_upload_url(self, file_name: str, expires: int = 3600) -> Optional[str]:
        """Получение URL для загрузки файла"""
        try:
            url = self.client.presigned_put_object(
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires)
            )
            
            url = self._replace_endpoint(url)
            return url
            
        except Exception as e:
            logger.error(f"Ошибка генерации upload URL: {e}")
            return None
    
    def _replace_endpoint(self, url: str) -> str:
        """Заменяет внутренний endpoint на публичный"""
        if not url:
            return url
        
        # Заменяем minio:9000 на публичный IP
        url = url.replace("minio:9000", "194.150.220.138:9000")
        
        # Убеждаемся что URL начинается с https
        if url.startswith("http://"):
            url = url.replace("http://", "https://")
        elif not url.startswith("https://"):
            url = f"https://{url}"
        
        return url
