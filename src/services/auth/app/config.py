"""Configuration settings for the Auth service."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Auth service configuration."""

    model_config = SettingsConfigDict(env_prefix="AUTH_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application settings
    app_name: str = "KeyArc Auth Service"
    debug: bool = False
    port: int = 8001

    # Database settings
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/keyarc"

    # Logging settings
    log_level: str = "INFO"
    log_json: bool = True


settings = Settings()
