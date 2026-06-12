from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Salon Multi-Tenant Platform"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = 'postgresql://neondb_owner:npg_uorD58hQCiLj@ep-square-moon-apfr2j9j-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    SECRET_KEY: str = "Mukanga" 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    STRIPE_SECRET_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
