from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from database.models import engine

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_session():
    async with SessionLocal() as session:
        yield session
