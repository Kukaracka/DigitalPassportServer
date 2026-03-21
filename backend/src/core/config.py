# src/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class Settings(BaseSettings):
    # MinIO settings
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "avatars"
    MINIO_PUBLIC_URL: str = "http://localhost:9000"
    
    # Google settings
    CID: str = "id_client"
    CSCR: str = "google_secret"
    GOOGLE_REDIRECT_URI: str = "https://example.com"
    FRONTEND_URL: str = "https://example.com"
    
    # Database settings
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_NAME: str = ""
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"

@lru_cache
def get_settings() -> Settings:
    return Settings()
