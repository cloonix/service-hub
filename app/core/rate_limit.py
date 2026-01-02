"""Rate limiting with sliding window algorithm."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any


class RateLimiter:
    """Simple sliding window rate limiter with per-tier support.

    Features:
    - Sliding window algorithm for accurate rate limiting
    - Support for different tiers (free, premium, admin)
    - Per-client tracking
    - Automatic cleanup of expired requests
    """

    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60,
        limits_per_tier: dict[str, tuple[int, int]] | None = None,
    ):
        """Initialize the rate limiter.

        Args:
            max_requests: Default maximum requests allowed
            window_seconds: Default time window in seconds
            limits_per_tier: Optional tier-specific limits
                Format: {"tier_name": (max_requests, window_seconds)}
        """
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.limits_per_tier = limits_per_tier or {}
        self.requests: dict[str, list[datetime]] = defaultdict(list)

    def is_allowed(self, client_id: str, tier: str = "free") -> bool:
        """Check if request is allowed for client.

        Args:
            client_id: Unique identifier for the client (e.g., API key ID)
            tier: Client tier (free, premium, admin)

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        now = datetime.now()

        # Get tier-specific limits or use defaults
        if tier in self.limits_per_tier:
            max_requests, window_seconds = self.limits_per_tier[tier]
            window = timedelta(seconds=window_seconds)
        else:
            max_requests = self.max_requests
            window = self.window

        # Remove old requests outside the window
        self.requests[client_id] = [
            ts for ts in self.requests[client_id] if now - ts < window
        ]

        # Check if under limit
        if len(self.requests[client_id]) < max_requests:
            self.requests[client_id].append(now)
            return True

        return False

    def get_stats(self, client_id: str, tier: str = "free") -> dict[str, Any]:
        """Get rate limit statistics for client.

        Args:
            client_id: Unique identifier for the client
            tier: Client tier

        Returns:
            Dictionary with current usage statistics
        """
        now = datetime.now()

        # Get tier-specific limits or use defaults
        if tier in self.limits_per_tier:
            max_requests, window_seconds = self.limits_per_tier[tier]
            window = timedelta(seconds=window_seconds)
        else:
            max_requests = self.max_requests
            window = self.window

        # Count active requests in current window
        active_requests = [ts for ts in self.requests[client_id] if now - ts < window]

        return {
            "client_id": client_id,
            "tier": tier,
            "requests_in_window": len(active_requests),
            "max_requests": max_requests,
            "window_seconds": int(window.total_seconds()),
            "remaining": max(0, max_requests - len(active_requests)),
        }

    def cleanup_old_clients(self, max_age_hours: int = 24) -> None:
        """Remove tracking data for clients with no recent activity.

        Args:
            max_age_hours: Remove clients inactive for this many hours
        """
        now = datetime.now()
        cutoff = now - timedelta(hours=max_age_hours)

        # Find clients with no recent requests
        inactive_clients = [
            client_id
            for client_id, timestamps in self.requests.items()
            if not timestamps or max(timestamps) < cutoff
        ]

        # Remove inactive clients
        for client_id in inactive_clients:
            del self.requests[client_id]
