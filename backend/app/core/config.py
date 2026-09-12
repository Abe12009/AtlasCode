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

    #: Firebase project id used to validate the audience/issuer of incoming
    #: Firebase ID tokens. This value is public (it ships in every web client);
    #: the security of the flow comes from signature verification against
    #: Google's public keys, not from keeping it secret. Leave it empty to run
    #: with AtlasCode's own email/password authentication only.
    firebase_project_id: str = ""

    # --- Cody (AI companion) ------------------------------------------------
    #: Server-side only. Never returned in any response body or logged; the
    #: frontend only ever talks to /cody/*, never to OpenRouter directly.
    openrouter_api_key: str = ""
    cody_model: str = "anthropic/claude-haiku-4.5"
    #: Per-user cap enforced in app.api.cody by counting that user's own
    #: CodyMessage rows created in the trailing hour -- no separate counter
    #: table needed, and it self-corrects if a request fails to write.
    cody_rate_limit_per_hour: int = 30
    #: How many of the user's most recent messages (user + assistant turns)
    #: are replayed as context on each request. Bounds token cost per call
    #: regardless of how long someone's history has grown.
    cody_history_context_size: int = 10

    # --- Password reset by email (local-password accounts) -----------------
    #: Resend API key. Server-side only. Leave empty to disable password
    #: reset by email; /auth/forgot-password then returns 503 rather than
    #: silently failing to deliver anything.
    resend_api_key: str = ""
    #: "Display Name <address@domain>" as Resend expects in the From header.
    #: Must be a verified sender/domain in the Resend account being used.
    email_from_address: str = "AtlasCode <onboarding@resend.dev>"
    #: Origin the emailed reset link points at, e.g. https://app.atlascode.com.
    #: No trailing slash.
    frontend_base_url: str = "http://localhost:5173"
    password_reset_token_expire_minutes: int = 30
    #: Enforced in app.services.password_reset by counting PasswordResetAttempt
    #: rows in the trailing hour -- same "count rows in a window" style as
    #: Cody's per-user limit, applied per-email and per-IP since this endpoint
    #: is reachable pre-auth.
    password_reset_rate_limit_per_email_per_hour: int = 3
    password_reset_rate_limit_per_ip_per_hour: int = 10

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