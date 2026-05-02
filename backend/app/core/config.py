import json
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_str_list(raw: str) -> List[str]:
    """Comma-separated list, or JSON array (pydantic-settings cannot use List[str] from .env without JSON)."""
    if raw is None or not str(raw).strip():
        return []
    s = str(raw).strip()
    if s.startswith("["):
        return [str(x).strip() for x in json.loads(s) if str(x).strip()]
    return [part.strip() for part in s.split(",") if part.strip()]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Enmask SDM Platform"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    API_KEY: str = ""
    SECRET_KEY: str = "changemeplease"
    GOOGLE_CLIENT_ID: str = ""
    ADMIN_EMAILS: str = ""
    REPOSITORY_BACKEND: str = "memory"
    POSTGRES_META_DSN: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/enmask_meta"
    MONGODB_META_URI: str = "mongodb://mongodb:27017"
    METADATA_DATABASE: str = "enmask_meta"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    def cors_origins_list(self) -> List[str]:
        return _parse_str_list(self.BACKEND_CORS_ORIGINS)

    def admin_emails_list(self) -> List[str]:
        return _parse_str_list(self.ADMIN_EMAILS)


settings = Settings()
