from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Enmask SDM Platform"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    API_KEY: str = ""
    SECRET_KEY: str = "changemeplease"
    GOOGLE_CLIENT_ID: str = ""
    ADMIN_EMAILS: List[str] = []
    REPOSITORY_BACKEND: str = "memory"
    POSTGRES_META_DSN: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/enmask_meta"
    MONGODB_META_URI: str = "mongodb://mongodb:27017"
    METADATA_DATABASE: str = "enmask_meta"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")


settings = Settings()
