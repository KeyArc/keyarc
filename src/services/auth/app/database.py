"""Database session management for the Auth service."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from services.auth.app.config import settings


engine = create_async_engine(settings.database_url, pool_size=5, max_overflow=10, echo=settings.debug)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Dependency that provides an async database session.

    Yields:
        An async database session that is automatically closed after use.
    """
    async with AsyncSessionLocal() as session:
        yield session
