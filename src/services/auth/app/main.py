"""Auth service FastAPI application."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.auth.app.config import settings
from services.auth.app.database import engine
from services.auth.app.logging import get_logger, setup_logging
from services.auth.app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Sets up logging on startup and disposes of the database engine on shutdown.
    """
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting Auth service", app_name=settings.app_name)
    yield
    logger.info("Shutting down Auth service")
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
