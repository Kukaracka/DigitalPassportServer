from sqlalchemy import Date, Float, String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime, Text, ForeignKey
import pytz

DATABASE_USL = (
    "postgresql+asyncpg://digitalpassport:digitalpassportpass@db:5432/digitalpassportdb"
)

engine = create_async_engine(DATABASE_USL, echo=True)
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
