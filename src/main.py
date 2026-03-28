from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from api.api_router import api_router
import uvicorn
from database.models import Base, engine
from core.config import get_settings

settings = get_settings()

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()
app.add_event_handler("startup", create_tables)

secret = settings.SECRET_KEY
if secret is None:
    raise Exception("You have no secret auth key in .env file")

app.add_middleware(
    SessionMiddleware,
    secret_key=secret,
    same_site="lax",
    https_only=False,
)

app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
