"""Router de health check."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Health check simple."""
    return {"status": "healthy"}


@router.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"service": "rickmorty-orders", "version": "0.1.0"}
