from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException
import os
from datetime import timedelta

class StorageService:
    def __init__(self):
        self.client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=False,  # True, если https
        )
        self.bucket = os.getenv("MINIO_BUCKET", "product-images")

        # Проверяем, что бакет существует
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

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

    def get_presigned_url(self, file_name: str, expires: int = 3600) -> str:
        try:
            return self.client.get_presigned_url(
                "GET",
                bucket_name=self.bucket,
                object_name=file_name,
                expires=timedelta(seconds=expires)
            )
        except S3Error:
            return None
