from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
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

@image_router.get("/users/me/avatar")
def get_my_avatar(
    current_user: UserModel = Depends(get_current_authorised_user),
):
    storage = StorageService()
    if not current_user.avatar_filename:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    try:
        return storage.get_image(current_user.avatar_filename)
    except Exception:
        raise HTTPException(status_code=404, detail="Avatar not found")



