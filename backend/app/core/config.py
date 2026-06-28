from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    APP_NAME: str = "ZeroTrust Hub"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/zerotrust"
    DATABASE_URL_ASYNC: Optional[str] = None

    SECRET_KEY: str = "change-this-to-a-very-long-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"

    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "openai/gpt-4o"
    NVD_API_KEY: Optional[str] = None
    VIRUSTOTAL_API_KEY: Optional[str] = None

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024

    RATE_LIMIT_PER_MINUTE: int = 60

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
