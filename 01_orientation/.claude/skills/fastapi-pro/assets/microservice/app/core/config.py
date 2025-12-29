from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Microservice"
    APP_VERSION: str = "1.0.0"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Celery (optional)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()
