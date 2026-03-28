from typing import Optional
from sqlalchemy import select
from database.models import UserModel, Session
from utils.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[UserModel]):
    def __init__(self):
        super().__init__(UserModel)

    async def get_by_username(self, username: str) -> Optional[UserModel]:
        """Получить пользователя по username"""
        async with Session() as session:
            statement = select(UserModel).where(UserModel.username == username)
            result = await session.execute(statement=statement)
            return result.scalar_one_or_none()
