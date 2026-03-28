from fastapi import APIRouter, Depends

from api.dependencies import verify_token
from database.models import UserModel

debug_router = APIRouter(prefix="/debug", tags=["Debug"])


@debug_router.get(
    "/",
    response_description="Just test for protected endpoint",
)
async def get_users(current_user: UserModel = Depends(verify_token)) -> dict:
    """
    This endpoint created to test protect dependency
    """
    return {"Auth": True}
