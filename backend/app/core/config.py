import json

from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache

INSECURE_DEFAULT_SECRET_KEY = "your-secret-key-change-in-production"


class Settings(BaseSettings):
    app_name: str = "AtlasCode"
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./atlascode.db"
    secret_key: str = INSECURE_DEFAULT_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30 * 24 * 60
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://[::1]:5173"]

    class Config:
        env_file = ".env"

    @field_validator("database_url", mode="before")
    @classmethod
    def use_async_postgres_driver(cls, value: str) -> str:
        """Render/Heroku-style providers hand out DATABASE_URL as
        postgres:// or postgresql:// (the sync scheme). The app's engine is
        async, so point those at the installed async driver (psycopg 3)
        instead of making every deploy remember to rewrite the URL by hand.
        sqlite:// and already-qualified URLs (postgresql+asyncpg://, etc.)
        pass through untouched.
        """
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value[len("postgres://"):]
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value[len("postgresql://"):]
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        """Accept a JSON array (existing .env format) or a plain
        comma-separated string (what Render's/Vercel's env var UIs make
        easiest to paste), so production config doesn't need JSON quoting.
        """
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

    @property
    def is_using_insecure_default_secret(self) -> bool:
        return self.secret_key == INSECURE_DEFAULT_SECRET_KEY


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if not settings.debug and settings.is_using_insecure_default_secret:
        raise RuntimeError(
            "SECRET_KEY is still the insecure default. Set a real SECRET_KEY "
            "environment variable before running with DEBUG=false."
        )
    return settings