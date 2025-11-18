"""Application settings and constants."""
from functools import lru_cache
from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    app_name: str = "LMS Python Backend"
    app_secret_key: str = "dev-secret"
    access_token_ttl_minutes: int = 60
    refresh_token_ttl_hours: int = 24
    default_admin_email: EmailStr = EmailStr("admin@example.com")
    storage_bucket: str = "./uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
