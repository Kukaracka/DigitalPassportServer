from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserModel
from utils.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[UserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserModel, session)

    async def get_by_username(self, username: str) -> Optional[UserModel]:
        statement = select(self.model).where(self.model.username == username)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
