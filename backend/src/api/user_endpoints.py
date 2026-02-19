from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_current_authorised_user, get_user_service
from database.models import UserModel
from schemas.user_schemas import UserCreateSchema, UserReadSchema, UserUpdateSchema
from services.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post(
    "/",
    response_description="New user has been created",
    tags=["Users"],
)
async def create_user(
    user: UserCreateSchema,
    user_service: UserService = Depends(get_user_service),
):
    user_id = await user_service.add_user(user)
    return {"created": True, "user_id": user_id}


@user_router.get(
    "/me",
    response_model=UserReadSchema,
    response_description="Get current user with avatar URL"
)
async def get_user(
    current_user: UserModel = Depends(get_current_authorised_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.read_one_user(current_user.id)


@user_router.get(
    "/",
    response_description="List of users retrieved successfully",
    response_model=list[UserReadSchema],
)
async def get_users(
    user_service: UserService = Depends(get_user_service),
) -> list[UserReadSchema]:
    """
    Получить список всех пользователей
    """
    user_data = await user_service.read_all_users()
    return user_data


@user_router.delete("/", response_description="User has been deleted")
async def detele_user(user_id):
    """
    Тут нихуя нет если чо
    """
    # TODO: delete logic
    return {"user_id": user_id, "deleted": True}


@user_router.put(
    "/",
    response_description="User has been updated",
    response_model=UserReadSchema,
)
async def update_user(
    user_update: UserUpdateSchema,
    user: UserModel = Depends(get_current_authorised_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Частичное обновление информации о пользователе
    """
    try:
        updated_user = await user_service.update_user(user.id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
