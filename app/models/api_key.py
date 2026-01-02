"""SQLAlchemy model for API keys."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class APIKey(Base):
    """API key model for authentication and authorization.

    Attributes:
        id: Primary key
        name: Descriptive name for the API key
        key_prefix: First 8 characters for fast lookup
        key_hash: bcrypt hash of the full API key
        tier: Access tier (free, premium, admin)
        is_active: Whether the key is currently active
        rate_limit: Maximum requests allowed in rate window
        rate_window: Rate limit window in seconds
        created_at: When the key was created
        last_used: Last time the key was used
        created_by: Admin who created the key
        description: Optional description
        allowed_ips: JSON string of allowed IP addresses
    """

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    key_prefix = Column(String(8), nullable=False, index=True, unique=True)
    key_hash = Column(String, nullable=False)
    tier = Column(String, default="free", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Rate limiting configuration
    rate_limit = Column(Integer, default=100, nullable=False)
    rate_window = Column(Integer, default=60, nullable=False)

    # Audit trail
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_used = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=True)

    # Metadata
    description = Column(String, nullable=True)
    allowed_ips = Column(String, nullable=True)  # JSON array stored as string

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name={self.name}, tier={self.tier})>"
