"""Configuration module."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    database_url: str = "postgresql+asyncpg://grants_user:grants_password@localhost:5432/grants_svc"
    database_echo: bool = False
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
