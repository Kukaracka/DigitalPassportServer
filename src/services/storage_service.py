import io
import os
import logging
from datetime import timedelta
from typing import Optional
import urllib3

from minio import Minio
from minio.error import S3Error

from core.config import get_settings

logger = logging.getLogger(__name__)


settings = get_settings()


class StorageService:
    def __init__(self):
        self.internal_endpoint = settings.MINIO_ENDPOINT
        self.public_endpoint = os.getenv(
            "MINIO_PUBLIC_ENDPOINT", "nl.tmpan.ru"
        )
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.bucket = settings.MINIO_BUCKET

        logger.info(f"MinIO internal endpoint: {self.internal_endpoint}")
        logger.info(f"MinIO public endpoint: {self.public_endpoint}")

        self.client = Minio(
            endpoint=self.internal_endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )

        http_client_for_https = urllib3.PoolManager(
            cert_reqs="CERT_NONE", 
            assert_hostname=False
        )

        self.public_client = Minio(
            endpoint=self.public_endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=True, # С SSL наружу
        )

        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Bucket {self.bucket} created")
            else:
                logger.info(f"Bucket {self.bucket} exists")
        except Exception as e:
            logger.error(f"Bucket check error: {e}")
            raise

    def upload_file(self, file_data: bytes, file_name: str, content_type: str) -> bool:
        """Загрузка файла через backend"""
        try:
            data = io.BytesIO(file_data)

            self.client.put_object(
                bucket_name=self.bucket,
                object_name=file_name,
                data=data,
                length=len(file_data),
                content_type=content_type,
            )

            return True

        except Exception as e:
            logger.error(f"Upload error: {e}")
            return False

    def get_download_url(self, file_name: str, expires: int = 3600) -> Optional[str]:
        """Presigned URL для скачивания"""

        try:
            return self.public_client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires),
            )

        except Exception as e:
            logger.error(f"Download URL error: {e}")
            return None

    async def delete_files(self, file_names: list[str]) -> bool:
        """
        Удаляет несколько файлов из MinIO.
        Возвращает True, если все удалены успешно.
        """
        success = True
        for file_name in file_names:
            try:
                self.client.remove_object(self.bucket, file_name)
            except Exception as e:
                logger.error(f"Failed to delete {file_name}: {e}")
                success = False
        return success

    def get_upload_url(self, file_name: str, expires: int = 3600) -> Optional[str]:
        """Presigned URL для загрузки"""

        try:
            return self.public_client.presigned_put_object(
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires),
            )

        except Exception as e:
            logger.error(f"Upload URL generation error: {e}")
            return None
