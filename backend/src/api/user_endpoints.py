from fastapi import APIRouter, Depends

from api.dependencies import verify_token
from database.models import UserModel
from repositories.user_repository import UserRepository
from schemas.user_schemas import UserCreateSchema, UserReadSchema
from services.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])



@user_router.post(
    "/",
    response_description="New user has been created",
    tags=["Users"],
)
async def create_user(
    user: UserCreateSchema,
    # current_user: UserModel = Depends(get_current_authorised_user),
):
    user_repo = UserRepository(UserModel)
    user_service = UserService(user_repo)
    user_id = await user_service.add_user(user)
    return {"created": True, "user_id": user_id}

@user_router.get(
    "/me",
    response_description="One user retrieved successfully",
    response_model=UserReadSchema
)
async def get_user(current_user: UserModel = Depends(verify_token)):
    user_repo = UserRepository(UserModel)
    user_service = UserService(user_repo)
    user_data = await user_service.read_one_user(current_user.id)
    return user_data

@user_router.get(
    "/",
    response_description="List of users retrieved successfully",
    response_model=list[UserReadSchema],
)
async def get_users() -> list[UserReadSchema]:
    """
    This endpoint is used to get a list of users
    """
    user_repo = UserRepository(UserModel)
    user_service = UserService(user_repo)
    user_data = await user_service.read_all_users()
    return user_data


@user_router.delete("/", response_description="User has been deleted")
async def detele_user(user_id):
    # TODO: delete logic
    return {"user_id": user_id, "deleted": True}


@user_router.patch("/", response_description="User has been updated")
async def update_user(user_id):
    # TODO: update logic
    return {"user_id": user_id, "updated": True}
