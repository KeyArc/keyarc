"""Health check endpoint for the Account service."""

from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        A dictionary with the health status.
    """
    return {"status": "healthy"}
