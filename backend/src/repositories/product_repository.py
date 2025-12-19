from typing import Optional, List
from sqlalchemy import select

from database.models import ProductModel, Session
from utils.repository import SQLAlchemyRepository


class ProductRepository(SQLAlchemyRepository[ProductModel]):
    def __init__(self):
        super().__init__(ProductModel)

    async def get_by_serial_number(self, serial_number: str) -> Optional[ProductModel]:
        """Получить продукт по серийному номеру"""
        async with Session() as session:
            statement = select(ProductModel).where(
                ProductModel.serial_number == serial_number
            )
            result = await session.execute(statement)
            return result.scalar_one_or_none()

    async def get_by_owner(self, owner_id: int) -> List[ProductModel]:
        """Получить все продукты владельца"""
        async with Session() as session:
            statement = select(ProductModel).where(ProductModel.owner_id == owner_id)
            result = await session.execute(statement)
            return list(result.scalars().all())

    async def search_by_name(self, name: str) -> List[ProductModel]:
        """Поиск продуктов по названию"""
        async with Session() as session:
            statement = select(ProductModel).where(ProductModel.name.ilike(f"%{name}%"))
            result = await session.execute(statement)
            return list(result.scalars().all())

    async def get_by_category(self, category: str) -> List[ProductModel]:
        """Получить продукты по категории"""
        async with Session() as session:
            statement = select(ProductModel).where(ProductModel.category == category)
            result = await session.execute(statement)
            return list(result.scalars().all())
