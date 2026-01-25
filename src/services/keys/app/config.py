"""Configuration settings for the Keys service."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Keys service configuration."""

    model_config = SettingsConfigDict(env_prefix="KEYS_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application settings
    app_name: str = "KeyArc Keys Service"
    debug: bool = False
    port: int = 8004

    # Database settings
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/keyarc"

    # Logging settings
    log_level: str = "INFO"
    log_json: bool = True


settings = Settings()
