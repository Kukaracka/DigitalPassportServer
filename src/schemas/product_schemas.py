from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProductSchema(BaseModel):
    """Базовая схема продукта"""

    model_config = ConfigDict(from_attributes=True)


class ProductCreateSchema(ProductSchema):
    """Схема для создания продукта"""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Название продукта"
    )
    manufacturer: str = Field(
        ..., min_length=1, max_length=255, description="Производитель"
    )
    category: str = Field(..., min_length=1, max_length=100, description="Категория")
    model: str = Field(..., min_length=1, max_length=100, description="Модель")
    serial_number: str = Field(
        ..., min_length=1, max_length=100, description="Серийный номер"
    )
    price: float = Field(..., gt=0, description="Цена")
    purchase_date: date = Field(..., description="Дата покупки")
    warranty_until: Optional[date] = Field(None, description="Гарантия до")
    description: Optional[str] = Field(None, max_length=2000, description="Описание")
    notes: Optional[str] = Field(None, max_length=2000, description="Заметки")


class ProductUpdateSchema(ProductSchema):
    """Схема для обновления продукта"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    manufacturer: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    serial_number: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    purchase_date: Optional[date] = Field(None)
    warranty_until: Optional[date] = Field(None)
    description: Optional[str] = Field(None, max_length=2000)
    notes: Optional[str] = Field(None, max_length=2000)


class ProductReadSchema(ProductCreateSchema):
    """Схема для чтения продукта"""

    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: int  # Кто добавил продукт


class ProductListSchema(ProductSchema):
    """Схема для списка продуктов (сокращенная)"""

    id: int
    name: str
    manufacturer: str
    category: str
    model: str
    serial_number: str
    price: float
    purchase_date: date
    warranty_until: Optional[date]
    created_at: datetime
    owner_id: int
