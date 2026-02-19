from minio import Minio
from fastapi.responses import StreamingResponse
from fastapi import UploadFile
import os
import uuid

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
            part_size=10*1024*1024,
            content_type=file.content_type,
        )
        return object_name

    def get_presigned_url(self, object_name: str, expires=3600) -> str:
        return self.client.get_presigned_url(
            "GET",
            bucket_name=self.bucket,
            object_name=object_name,
            expires=expires
        )
