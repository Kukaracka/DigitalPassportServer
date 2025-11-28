from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
