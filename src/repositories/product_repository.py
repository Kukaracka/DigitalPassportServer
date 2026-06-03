from typing import Optional, List, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import ProductModel
from utils.repository import SQLAlchemyRepository


class ProductRepository(SQLAlchemyRepository[ProductModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProductModel, session)

    async def get_by_serial_number(self, serial_number: str) -> Optional[ProductModel]:
        statement = select(self.model).where(
            self.model.serial_number == serial_number
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: int) -> Sequence[ProductModel]:
        statement = select(self.model).where(self.model.owner_id == owner_id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def search_by_name(self, name: str) -> List[ProductModel]:
        statement = select(self.model).where(
            self.model.name.ilike(f"%{name}%")
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_category(self, category: str) -> Sequence[ProductModel]:
        statement = select(self.model).where(self.model.category == category)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_file_names_by_owner(self, owner_id: int) -> list[str]:
        """Получить все имена файлов продуктов пользователя"""

        stmt = select(self.model.file_name).where(
            self.model.owner_id == owner_id
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
