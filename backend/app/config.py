from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql://projects_user:projects_password@db:5432/projects_db"
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
