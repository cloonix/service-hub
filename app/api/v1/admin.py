"""Admin API routes for key management."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_admin_api_key, get_cache
from app.core.cache import TTLCache
from app.database import get_db
from app.models.api_key import APIKey
from app.schemas.common import SuccessResponse
from app.services.api_key import APIKeyService

router = APIRouter(prefix="/admin", tags=["Admin"])


class CreateAPIKeyRequest(BaseModel):
    """Request schema for creating API keys."""

    name: str = Field(..., min_length=1, max_length=100)
    tier: str = Field(default="free", pattern="^(free|premium|admin)$")
    description: str | None = None
    rate_limit: int = Field(default=100, ge=1, le=10000)
    rate_window: int = Field(default=60, ge=1, le=3600)


class CreateAPIKeyResponse(BaseModel):
    """Response schema for created API key."""

    success: bool = True
    api_key: str = Field(..., description="Full API key (shown only once)")
    key_id: int
    name: str
    tier: str


class APIKeyInfo(BaseModel):
    """API key information schema."""

    id: int
    name: str
    key_prefix: str
    tier: str
    is_active: bool
    rate_limit: int
    rate_window: int
    created_at: str
    last_used: str | None


@router.post("/keys", response_model=CreateAPIKeyResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    admin_key: APIKey = Depends(get_admin_api_key),
    db: Session = Depends(get_db),
) -> dict:
    """Create a new API key (admin only).

    Args:
        request: API key creation request
        admin_key: Admin API key for authorization
        db: Database session

    Returns:
        Created API key information including the full key
    """
    api_key, full_key = APIKeyService.create_api_key(
        db=db,
        name=request.name,
        tier=request.tier,
        description=request.description,
        created_by=admin_key.name,
        rate_limit=request.rate_limit,
        rate_window=request.rate_window,
    )

    return {
        "success": True,
        "api_key": full_key,
        "key_id": api_key.id,
        "name": api_key.name,
        "tier": api_key.tier,
    }


@router.get("/keys", response_model=list[APIKeyInfo])
async def list_api_keys(
    include_inactive: bool = False,
    admin_key: APIKey = Depends(get_admin_api_key),
    db: Session = Depends(get_db),
) -> list[dict]:
    """List all API keys (admin only).

    Args:
        include_inactive: Include inactive keys in the list
        admin_key: Admin API key for authorization
        db: Database session

    Returns:
        List of API key information
    """
    keys = APIKeyService.list_api_keys(db, include_inactive)

    return [
        {
            "id": key.id,
            "name": key.name,
            "key_prefix": key.key_prefix,
            "tier": key.tier,
            "is_active": key.is_active,
            "rate_limit": key.rate_limit,
            "rate_window": key.rate_window,
            "created_at": key.created_at.isoformat(),
            "last_used": key.last_used.isoformat() if key.last_used else None,
        }
        for key in keys
    ]


@router.delete("/keys/{key_id}", response_model=SuccessResponse)
async def deactivate_api_key(
    key_id: int,
    admin_key: APIKey = Depends(get_admin_api_key),
    db: Session = Depends(get_db),
) -> dict:
    """Deactivate an API key (admin only).

    Args:
        key_id: ID of the key to deactivate
        admin_key: Admin API key for authorization
        db: Database session

    Returns:
        Success response

    Raises:
        HTTPException: If key not found
    """
    success = APIKeyService.deactivate_api_key(db, key_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with ID {key_id} not found",
        )

    return {"success": True, "message": f"API key {key_id} deactivated successfully"}


@router.post("/cache/clear", response_model=SuccessResponse)
async def clear_cache(
    admin_key: APIKey = Depends(get_admin_api_key), cache: TTLCache = Depends(get_cache)
) -> dict:
    """Clear the application cache (admin only).

    Args:
        admin_key: Admin API key for authorization
        cache: Cache instance

    Returns:
        Success response
    """
    cache.clear()

    return {"success": True, "message": "Cache cleared successfully"}
