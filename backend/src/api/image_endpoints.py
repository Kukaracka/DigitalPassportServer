from fastapi import APIRouter, UploadFile, File, Depends
from api.dependencies import get_current_authorised_user
from database.models import UserModel
from services.storage_service import StorageService

image_router = APIRouter()

@image_router.post("/users/avatar")
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_authorised_user),
):
    storage = StorageService()
    object_name = storage.upload_image(file, current_user.id)

    return {
        "filename": object_name,
        "message": "Image uploaded successfully"
    }



