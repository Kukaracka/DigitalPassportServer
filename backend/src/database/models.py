from enum import Enum
from sqlalchemy import Boolean, Date, Float, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config import get_settings
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime, Text, ForeignKey
import pytz
from sqlalchemy import (
    Enum as SQLEnum,
)

settings = get_settings()

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, echo=True)
Session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]
    email: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    father_name: Mapped[str] = mapped_column(default="")
    phone_number: Mapped[str] = mapped_column(default="")
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    products: Mapped[list["ProductModel"]] = relationship(
        "ProductModel", back_populates="owner", cascade="all, delete-orphan"
    )


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255))
    manufacturer: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    serial_number: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    price: Mapped[float] = mapped_column(Float)
    purchase_date: Mapped[date] = mapped_column(Date)
    warranty_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="products")

    # Добавляем связь с изображениями
    images: Mapped[List["ProductImageModel"]] = relationship(
        "ProductImageModel",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImageModel.sort_order",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(pytz.timezone("Europe/Moscow"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(pytz.timezone("Europe/Moscow")),
        onupdate=lambda: datetime.now(pytz.timezone("Europe/Moscow")),
    )

    def __repr__(self) -> str:
        return f"Product(id={self.id}, name={self.name}, serial={self.serial_number})"


# /home/kukaracka/Projects/DigitalPassport/backend/src/database/models.py


class ImageType(str, Enum):
    RECEIPT = "RECEIPT"  # Теперь значение совпадает с БД
    WARRANTY = "WARRANTY"
    PRODUCT = "PRODUCT"
    DOCUMENT = "DOCUMENT"
    CERTIFICATE = "CERTIFICATE"
    OTHER = "OTHER"


class ProductImageModel(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )

    file_name: Mapped[str] = mapped_column(String(255))
    original_name: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    image_type: Mapped[ImageType] = mapped_column(
        SQLEnum(ImageType), default=ImageType.OTHER, nullable=False
    )

    is_main: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # ВАЖНО: Используем DateTime без часового пояса
    created_at: Mapped[datetime] = mapped_column(
        DateTime,  # Убрали timezone=True
        default=lambda: datetime.now(pytz.timezone("Europe/Moscow")).replace(
            tzinfo=None
        ),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,  # Убрали timezone=True
        default=lambda: datetime.now(pytz.timezone("Europe/Moscow")).replace(
            tzinfo=None
        ),
        onupdate=lambda: datetime.now(pytz.timezone("Europe/Moscow")).replace(
            tzinfo=None
        ),
    )

    product: Mapped["ProductModel"] = relationship(
        "ProductModel", back_populates="images"
    )

    def __repr__(self) -> str:
        return f"ProductImage(id={self.id}, product_id={self.product_id}, type={self.image_type})"
