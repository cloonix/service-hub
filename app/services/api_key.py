"""Service for API key management and authentication."""

import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.security import hash_api_key, verify_api_key
from app.models.api_key import APIKey


class APIKeyService:
    """Service for managing API keys."""

    @staticmethod
    def generate_api_key(prefix: str = "myapi_live") -> tuple[str, str, str]:
        """Generate a new API key.

        Args:
            prefix: Prefix for the API key (e.g., myapi_live, myapi_test)

        Returns:
            Tuple of (full_key, key_prefix, key_hash)
        """
        # Generate 24 bytes (32 chars base64) to keep total under 72 chars for bcrypt
        random_part = secrets.token_urlsafe(24)
        full_key = f"{prefix}_{random_part}"
        key_prefix = full_key[:8]
        key_hash = hash_api_key(full_key)

        return full_key, key_prefix, key_hash

    @staticmethod
    def create_api_key(
        db: Session,
        name: str,
        tier: str = "free",
        description: str | None = None,
        created_by: str | None = None,
        rate_limit: int = 100,
        rate_window: int = 60,
    ) -> tuple[APIKey, str]:
        """Create a new API key in the database.

        Args:
            db: Database session
            name: Descriptive name for the key
            tier: Access tier (free, premium, admin)
            description: Optional description
            created_by: Admin who created the key
            rate_limit: Maximum requests per window
            rate_window: Rate limit window in seconds

        Returns:
            Tuple of (APIKey model, plain_key_to_show_once)
        """
        full_key, key_prefix, key_hash = APIKeyService.generate_api_key()

        api_key = APIKey(
            name=name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            tier=tier,
            description=description,
            created_by=created_by,
            rate_limit=rate_limit,
            rate_window=rate_window,
            is_active=True,
        )

        try:
            db.add(api_key)
            db.commit()
            db.refresh(api_key)
        except Exception:
            db.rollback()
            raise

        return api_key, full_key

    @staticmethod
    def verify_api_key(db: Session, plain_key: str) -> APIKey | None:
        """Verify an API key and return the model if valid.

        Args:
            db: Database session
            plain_key: The plain API key to verify

        Returns:
            APIKey model if valid and active, None otherwise
        """
        # Extract prefix for fast lookup
        if len(plain_key) < 8:
            return None

        key_prefix = plain_key[:8]

        # Query by prefix
        db_key = db.query(APIKey).filter(APIKey.key_prefix == key_prefix).first()

        if not db_key:
            return None

        # Check key_hash is not None (should never be None for valid keys)
        if not db_key.key_hash:
            return None

        # Verify hash
        if not verify_api_key(plain_key, db_key.key_hash):
            return None

        # Check if active
        if not db_key.is_active:
            return None

        # Update last_used timestamp
        db_key.last_used = datetime.now(timezone.utc)
        db.commit()

        return db_key

    @staticmethod
    def deactivate_api_key(db: Session, key_id: int) -> bool:
        """Deactivate an API key.

        Args:
            db: Database session
            key_id: ID of the key to deactivate

        Returns:
            True if deactivated, False if not found
        """
        db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
        if not db_key:
            return False

        db_key.is_active = False
        db.commit()
        return True

    @staticmethod
    def list_api_keys(db: Session, include_inactive: bool = False) -> list[APIKey]:
        """List all API keys.

        Args:
            db: Database session
            include_inactive: Whether to include inactive keys

        Returns:
            List of APIKey models
        """
        query = db.query(APIKey)
        if not include_inactive:
            query = query.filter(APIKey.is_active == True)

        return query.order_by(APIKey.created_at.desc()).all()

    @staticmethod
    def get_api_key_stats(db: Session, key_id: int) -> dict[str, Any] | None:
        """Get statistics for an API key.

        Args:
            db: Database session
            key_id: ID of the key

        Returns:
            Dictionary with key statistics or None if not found
        """
        db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
        if not db_key:
            return None

        return {
            "id": db_key.id,
            "name": db_key.name,
            "tier": db_key.tier,
            "is_active": db_key.is_active,
            "rate_limit": db_key.rate_limit,
            "rate_window": db_key.rate_window,
            "created_at": db_key.created_at.isoformat() if db_key.created_at else "",
            "last_used": db_key.last_used.isoformat() if db_key.last_used else None,
            "created_by": db_key.created_by,
        }
