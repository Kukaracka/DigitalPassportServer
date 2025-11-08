import os
from fastapi import FastAPI
from api.api_router import api_router
import uvicorn
from starlette.middleware.sessions import SessionMiddleware

from database.models import Base, engine
from dotenv import load_dotenv

load_dotenv()

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()
app.add_event_handler("startup", create_tables)

# Мидлвар для работы сессий (обязательно для Google OAuth)
secret = os.getenv("SECRET_KEY")
if secret is None:
    raise Exception
app.add_middleware(
    SessionMiddleware,
    secret_key=secret,
    same_site="lax",     # cookie работают при редиректе с Google
    https_only=False     # локальная разработка на http
)

app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
