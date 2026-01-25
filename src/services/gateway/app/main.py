"""Gateway service FastAPI application."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.gateway.app.config import settings
from services.gateway.app.logging import get_logger, setup_logging
from services.gateway.app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Sets up logging on startup.
    """
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting Gateway service", app_name=settings.app_name)
    yield
    logger.info("Shutting down Gateway service")


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
