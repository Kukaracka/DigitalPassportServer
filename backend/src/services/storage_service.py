import os
import logging
from datetime import timedelta
from typing import Optional
import urllib3

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)



class StorageService:

    def __init__(self):
        # Внутренний endpoint (для backend -> MinIO)
        self.internal_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")

        # Публичный endpoint (для presigned URL)
        self.public_endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", "194.150.220.138:9000")

        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "strongpassword")
        self.bucket = os.getenv("MINIO_BUCKET", "avatars")



        http_client = urllib3.PoolManager(
            cert_reqs="CERT_NONE",
            assert_hostname=False
        )

        self.secure = os.getenv("MINIO_SECURE", "true").lower() == "true"

        logger.info(f"MinIO internal endpoint: {self.internal_endpoint}")
        logger.info(f"MinIO public endpoint: {self.public_endpoint}")

        # клиент для работы backend -> minio
        self.client = Minio(
            endpoint=self.internal_endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=True,
            http_client=http_client
        )

        # клиент только для генерации presigned URL
        self.public_client = Minio(
            endpoint=self.public_endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
            http_client=http_client
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

    def get_download_url(self, file_name: str, expires: int = 3600) -> Optional[str]:
        """Presigned URL для скачивания файла"""

        try:
            self.client.stat_object(self.bucket, file_name)

            url = self.public_client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires)
            )

            return url

        except S3Error as e:
            logger.error(f"MinIO error: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def get_upload_url(self, file_name: str, expires: int = 3600) -> Optional[str]:
        """Presigned URL для загрузки файла"""

        try:
            url = self.public_client.presigned_put_object(
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires),
            )

            return url

        except Exception as e:
            logger.error(f"Upload URL generation error: {e}")
            return None
