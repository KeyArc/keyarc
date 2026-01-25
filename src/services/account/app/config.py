"""Configuration settings for the Account service."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Account service configuration."""

    model_config = SettingsConfigDict(env_prefix="ACCOUNT_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application settings
    app_name: str = "KeyArc Account Service"
    debug: bool = False
    port: int = 8003

    # Database settings
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/keyarc"

    # Logging settings
    log_level: str = "DEBUG"
    log_json: bool = True


settings = Settings()
