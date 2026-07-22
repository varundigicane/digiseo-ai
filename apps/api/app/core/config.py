from functools import lru_cache
from urllib.parse import urlparse

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_async_database_url(url: str) -> str:
    """Convert Railway/Heroku postgres URLs to SQLAlchemy asyncpg form."""
    if not url:
        return url
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+asyncpg" not in url.split("://", 1)[0]:
        url = "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url


def normalize_sync_database_url(url: str) -> str:
    if not url:
        return url
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    # Strip asyncpg driver if somehow present
    url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "DigiSEO AI"
    APP_ENV: str = "development"
    API_URL: str = "http://localhost:8000"
    WEB_URL: str = "http://localhost:3000"
    # Comma-separated extra CORS origins (Railway preview URLs, custom domains)
    CORS_ORIGINS: str = ""
    SECRET_KEY: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7
    PORT: int = 8000

    DATABASE_URL: str = "sqlite+aiosqlite:///./digiseo.db"
    DATABASE_URL_SYNC: str = "sqlite:///./digiseo.db"
    DATABASE_SSL: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "digiseo_chunks"

    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_STARTER: str = "price_starter"
    STRIPE_PRICE_PROFESSIONAL: str = "price_professional"
    STRIPE_PRICE_BUSINESS: str = "price_business"

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_AI_API_KEY: str = ""

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/integrations/google/callback"

    MOCK_LLM: bool = True
    MOCK_CRAWL: bool = False

    CREDITS_STARTER: int = 500
    CREDITS_PROFESSIONAL: int = 2000
    CREDITS_BUSINESS: int = 8000
    CREDITS_ENTERPRISE: int = 50000

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _async_db(cls, v: str) -> str:
        return normalize_async_database_url(v or "")

    @field_validator("DATABASE_URL_SYNC", mode="before")
    @classmethod
    def _sync_db(cls, v: str) -> str:
        return normalize_sync_database_url(v or "")

    @model_validator(mode="after")
    def _derive_sync_and_ssl(self):
        # If only Railway DATABASE_URL is set, derive sync URL
        if self.DATABASE_URL.startswith("postgresql+asyncpg://") and (
            not self.DATABASE_URL_SYNC or self.DATABASE_URL_SYNC.startswith("sqlite")
        ):
            self.DATABASE_URL_SYNC = normalize_sync_database_url(
                self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
            )
        host = ""
        try:
            host = urlparse(self.DATABASE_URL.replace("+asyncpg", "")).hostname or ""
        except Exception:
            pass
        # Private Railway network does not need (and often breaks with) verified TLS.
        # Public proxy hosts (*.proxy.rlwy.net) need SSL.
        if host.endswith(".railway.internal"):
            self.DATABASE_SSL = False
        elif (
            host.endswith(".proxy.rlwy.net")
            or host.endswith(".rlwy.net")
            or (host.endswith(".railway.app") and not host.endswith(".railway.internal"))
        ):
            self.DATABASE_SSL = True
        return self

    def cors_allow_origins(self) -> list[str]:
        origins = {
            self.WEB_URL,
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3010",
            "http://127.0.0.1:3010",
        }
        for part in self.CORS_ORIGINS.split(","):
            o = part.strip()
            if o:
                origins.add(o)
        return [o for o in origins if o]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
