from fastapi import HTTPException
from database.models import UserModel
from schemas.user_schemas import UserCreateSchema, UserReadSchema
from utils.repository import SQLAlchemyRepository


class UserService:
    def __init__(self, users_repo: SQLAlchemyRepository[UserModel]):
        self.users_repo: SQLAlchemyRepository = users_repo

    async def add_user(self, user: UserCreateSchema):
        users_dict = user.model_dump()
        user_id = await self.users_repo.create_one(users_dict)
        return user_id

    async def read_all_users(self) -> list[UserReadSchema]:
        user_data: list[UserModel] | None = await self.users_repo.read_all()
        users_schema = [UserReadSchema.model_validate(user) for user in user_data]
        return users_schema
    
    async def read_one_user(self, user_id: int):
        user_data: UserModel | None = await self.users_repo.read_one(user_id)
        if user_data is None:
            raise HTTPException(status_code=404, detail="User npt found")
        user_schema = UserReadSchema.model_validate(user_data)
        return user_schema
