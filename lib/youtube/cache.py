"""Cache protocol for YouTube transcript service."""

from typing import Any, Protocol


class CacheProtocol(Protocol):
    """Protocol for cache implementations.

    Any cache implementation that wants to be used with TranscriptService
    must implement these methods.
    """

    def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        ...

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional time-to-live in seconds
        """
        ...
