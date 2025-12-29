from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "FastAPI Structured App"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "A well-structured FastAPI application"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
