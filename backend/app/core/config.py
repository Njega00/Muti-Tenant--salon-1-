from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Salon Multi-Tenant Platform"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = Field(
        default="",
        validation_alias=AliasChoices("DATABASE_URL"),
    )
    SECRET_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET_KEY"),
        min_length=32,
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    STRIPE_SECRET_KEY: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, value: str | None) -> str:
        cleaned = (value or "").strip()
        placeholder_tokens = (
            "<user>", "<password>", "<host>",
            "user:password@host.neon.tech", "replace-with",
        )
        if not cleaned:
            raise ValueError("DATABASE_URL must be set in the environment")
        if any(token in cleaned for token in placeholder_tokens):
            raise ValueError("DATABASE_URL must be a real connection string")
        if not cleaned.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must start with postgresql://")
        return cleaned

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, value: str | None) -> str:
        cleaned = (value or "").strip()
        placeholder_tokens = (
            "change-me", "replace-with", "long-random-secret",
            "default-secret",
        )
        if not cleaned:
            raise ValueError("SECRET_KEY must be set in the environment")
        if any(token in cleaned.lower() for token in placeholder_tokens):
            raise ValueError("SECRET_KEY must be a real secret value")
        if len(cleaned) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return cleaned

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
