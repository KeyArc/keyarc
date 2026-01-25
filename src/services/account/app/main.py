"""Account service FastAPI application."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.account.app.config import settings
from services.account.app.database import engine
from services.account.app.routers import health
from shared.logging import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Sets up logging on startup and disposes of the database engine on shutdown.
    """
    setup_logging(log_level=settings.log_level, log_json=settings.log_json)
    logger = get_logger(__name__)
    logger.info("Starting Account service", app_name=settings.app_name)
    yield
    logger.info("Shutting down Account service")
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
