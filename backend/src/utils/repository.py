from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Any,
    Generic,
    Literal,
    Optional,
    Type,
    TypeVar,
)

from sqlalchemy import asc, delete, desc, insert, select, update
from sqlalchemy.sql import ColumnElement
from src.database.models import Session

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    """Базовый интерфейс репозитория."""

    @abstractmethod
    async def create_one(self, data: dict) -> T: ...

    @abstractmethod
    async def read_all(
        self,
        filter_clause: Optional[ColumnElement[bool]] = None,
        order: Optional[Literal["asc", "desc"]] = None,
        order_by: Optional[str] = None,
    ) -> list[T]: ...

    @abstractmethod
    async def read_one(self, obj_id: Any) -> T | None: ...

    @abstractmethod
    async def delete_one(self, obj_id: int) -> bool: ...

    @abstractmethod
    async def update_one(self, id: int, data: dict) -> Optional[T]: ...


class SQLAlchemyRepository(AbstractRepository[T]):
    """Реализация репозитория на SQLAlchemy."""

    model: Type[T]

    def __init__(self, model: Type[T]):
        self.model = model

    async def create_one(self, data: dict) -> T:
        """Создаёт одну запись и возвращает модель."""
        async with Session() as session:
            statement = insert(self.model).values(**data).returning(self.model)
            result = await session.execute(statement)
            await session.commit()
            return result.scalar_one()

    async def read_all(
        self,
        filter_clause: Optional[ColumnElement[bool]] = None,
        order: Optional[Literal["asc", "desc"]] = None,
        order_by: Optional[str] = None,
    ) -> list[T]:
        """Возвращает список всех записей с возможной фильтрацией и сортировкой."""
        async with Session() as session:
            statement = select(self.model)

            if filter_clause is not None:
                statement = statement.where(filter_clause)

            if order and order_by:
                column = getattr(self.model, order_by, None)
                if column is None:
                    raise ValueError(f"Invalid order_by column: {order_by}")

                if order == "asc":
                    statement = statement.order_by(asc(column))
                elif order == "desc":
                    statement = statement.order_by(desc(column))

            result = await session.execute(statement)
            return list(result.scalars().all())

    async def read_one(self, obj_id: Any) -> T | None:
        """Возвращает одну запись по идентификатору (если поле id существует)."""
        async with Session() as session:
            id_column = getattr(self.model, "id", None)
            if id_column is None:
                raise AttributeError(
                    f"Model {self.model.__name__} does not have an 'id' attribute."
                )

            statement = select(self.model).where(id_column == obj_id)
            result = await session.execute(statement)
            return result.scalar_one_or_none()

    async def delete_one(self, obj_id: int) -> bool:
        """Удаляет запись по id, если поле id существует у модели."""
        async with Session() as session:
            id_column = getattr(self.model, "id", None)
            if id_column is None:
                raise AttributeError(
                    f"Model {self.model.__name__} does not have an 'id' attribute."
                )

            statement = delete(self.model).where(id_column == obj_id)
            result = await session.execute(statement)
            await session.commit()
            return bool(getattr(result, "rowcount", 0))

    async def update_one(self, id: int, data: dict) -> Optional[T]:
        async with Session() as session:
            attribute = "id"
            id_column = getattr(self.model, attribute, None)
            if id_column is None:
                raise AttributeError(
                    f"Model {self.model.__name__} does not have an {attribute} attribute."
                )

            statement = (
                update(self.model)
                .where(id_column == id)
                .values(**data)
                .returning(self.model)
            )
            res = await session.execute(statement)
            await session.commit()
            return res.scalar_one_or_none()
