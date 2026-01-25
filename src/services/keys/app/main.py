"""Keys service FastAPI application."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.keys.app.config import settings
from services.keys.app.database import engine
from services.keys.app.logging import get_logger, setup_logging
from services.keys.app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Sets up logging on startup and disposes of the database engine on shutdown.
    """
    setup_logging(log_level=settings.log_level, log_json=settings.log_json)
    logger = get_logger(__name__)
    logger.info("Starting Keys service", app_name=settings.app_name)
    yield
    logger.info("Shutting down Keys service")
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        A configured FastAPI application instance.
    """
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    app.include_router(health.router)
    return app


app = create_app()
