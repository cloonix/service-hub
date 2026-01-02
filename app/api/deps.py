"""FastAPI dependency functions."""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.core.cache import TTLCache
from app.core.exceptions import DisabledAPIKey, InvalidAPIKey
from app.core.rate_limit import RateLimiter
from app.database import get_db
from app.models.api_key import APIKey
from app.services.api_key import APIKeyService

# API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_cache(request: Request) -> TTLCache:
    """Get cache instance from app state.

    Args:
        request: FastAPI request object

    Returns:
        TTLCache instance
    """
    return request.app.state.cache


def get_rate_limiter(request: Request) -> RateLimiter:
    """Get rate limiter instance from app state.

    Args:
        request: FastAPI request object

    Returns:
        RateLimiter instance
    """
    return request.app.state.rate_limiter


async def get_current_api_key(
    api_key: str | None = Depends(api_key_header), db: Session = Depends(get_db)
) -> APIKey:
    """Verify API key and return the model.

    Args:
        api_key: API key from header
        db: Database session

    Returns:
        APIKey model if valid

    Raises:
        HTTPException: If key is missing, invalid, or disabled
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header.",
        )

    db_key = APIKeyService.verify_api_key(db, api_key)

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    if not db_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="API key is disabled"
        )

    return db_key


async def get_admin_api_key(
    current_key: APIKey = Depends(get_current_api_key),
) -> APIKey:
    """Verify that the current API key has admin tier.

    Args:
        current_key: Current API key from get_current_api_key

    Returns:
        APIKey model if admin tier

    Raises:
        HTTPException: If not admin tier
    """
    if current_key.tier != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    return current_key


async def check_rate_limit(
    api_key: APIKey = Depends(get_current_api_key),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
) -> APIKey:
    """Check rate limit for the current API key.

    Args:
        api_key: Current API key
        rate_limiter: Rate limiter instance

    Returns:
        APIKey if rate limit check passes

    Raises:
        HTTPException: If rate limit exceeded
    """
    if not rate_limiter.is_allowed(str(api_key.id), api_key.tier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(api_key.rate_window)},
        )

    return api_key
