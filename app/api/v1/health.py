"""Health and metrics API routes."""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_cache
from app.config import settings
from app.core.cache import TTLCache

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str


class CacheStats(BaseModel):
    """Cache statistics."""

    size: int
    max_size: int
    hits: int
    misses: int
    hit_rate: float
    ttl_seconds: int


class MetricsResponse(BaseModel):
    """Metrics response."""

    version: str
    environment: str
    cache: CacheStats


@router.get("/health", response_model=HealthResponse)
async def health_check() -> dict[str, Any]:
    """Health check endpoint.

    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/metrics", response_model=MetricsResponse)
async def metrics(cache: TTLCache = Depends(get_cache)) -> dict[str, Any]:
    """Get application metrics.

    Args:
        cache: Cache instance

    Returns:
        Application metrics including cache statistics
    """
    return {
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "cache": cache.stats(),
    }
