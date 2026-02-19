from fastapi import APIRouter, UploadFile, File, Depends
from services.storage_service import StorageService

image_router = APIRouter()

@image_router.post("/products/upload-image")
async def upload_product_image(
    file: UploadFile = File(...),
):
    storage = StorageService()
    object_name = storage.upload_image(file)

    return {
        "filename": object_name,
        "message": "Image uploaded successfully"
    }

