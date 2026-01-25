"""Configuration settings for the Gateway service."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Gateway service configuration."""

    model_config = SettingsConfigDict(env_prefix="GATEWAY_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application settings
    app_name: str = "KeyArc Gateway"
    debug: bool = False
    port: int = 8002

    # JWT settings
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"

    # Downstream service URLs
    account_service_url: str = "http://localhost:8003"
    keys_service_url: str = "http://localhost:8004"

    # Logging settings
    log_level: str = "DEBUG"
    log_json: bool = True


settings = Settings()
