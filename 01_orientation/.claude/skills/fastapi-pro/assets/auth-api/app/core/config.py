from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Auth API"
    APP_VERSION: str = "1.0.0"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
