from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import uuid
import os

from starlette.responses import StreamingResponse


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
        file_extension = file.filename.split(".")[-1]
        object_name = f"{user_id}.{file_extension}"

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=file.content_type,
        )

        return object_name
    def get_image(self, object_name: str):
        """
        Возвращает StreamingResponse для файла из MinIO
        """
        try:
            obj = self.client.get_object(self.bucket, object_name)
            return StreamingResponse(
                obj,
                media_type="application/octet-stream"
            )
        except S3Error as e:
            raise RuntimeError(f"Error fetching object {object_name}: {e}")
