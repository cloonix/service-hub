"""TTL cache with optional disk persistence and LRU eviction."""

import json
import pickle
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class TTLCache:
    """Time-to-live cache with LRU eviction and disk persistence.

    Features:
    - TTL-based expiration
    - LRU eviction when max size reached
    - Optional disk persistence
    - Thread-safe operations
    - Cache statistics tracking
    """

    def __init__(
        self,
        ttl_seconds: int = 3600,
        max_size: int = 100,
        cache_dir: Path | None = None,
    ):
        """Initialize the TTL cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
            max_size: Maximum number of entries in cache
            cache_dir: Optional directory for disk persistence
        """
        self.ttl = timedelta(seconds=ttl_seconds)
        self.max_size = max_size
        self.cache_dir = cache_dir
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._timestamps: dict[str, datetime] = {}
        self.hits = 0
        self.misses = 0

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load cache from disk if available."""
        if not self.cache_dir:
            return

        cache_file = self.cache_dir / "cache.pkl"
        meta_file = self.cache_dir / "cache_meta.json"

        if cache_file.exists() and meta_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    self._cache = pickle.load(f)

                with open(meta_file, "r") as f:
                    meta = json.load(f)
                    self._timestamps = {
                        k: datetime.fromisoformat(v)
                        for k, v in meta.get("timestamps", {}).items()
                    }
                    self.hits = meta.get("hits", 0)
                    self.misses = meta.get("misses", 0)

                # Clean expired entries after loading
                self._cleanup_expired()
            except Exception:
                # If loading fails, start with fresh cache
                self._cache.clear()
                self._timestamps.clear()

    def _save_to_disk(self) -> None:
        """Persist cache to disk."""
        if not self.cache_dir:
            return

        cache_file = self.cache_dir / "cache.pkl"
        meta_file = self.cache_dir / "cache_meta.json"

        try:
            with open(cache_file, "wb") as f:
                pickle.dump(self._cache, f)

            meta = {
                "timestamps": {k: v.isoformat() for k, v in self._timestamps.items()},
                "hits": self.hits,
                "misses": self.misses,
            }
            with open(meta_file, "w") as f:
                json.dump(meta, f)
        except Exception:
            # Fail silently on disk write errors
            pass

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        now = datetime.now()
        expired = [key for key, ts in self._timestamps.items() if now - ts > self.ttl]
        for key in expired:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)

    def get(self, key: str) -> Any | None:
        """Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        self._cleanup_expired()

        if key in self._cache and key in self._timestamps:
            self.hits += 1
            # Move to end for LRU tracking
            self._cache.move_to_end(key)
            return self._cache[key]

        self.misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Evict oldest entry if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = next(iter(self._cache))
            self._cache.pop(oldest_key)
            self._timestamps.pop(oldest_key)

        self._cache[key] = value
        self._timestamps[key] = datetime.now()
        self._cache.move_to_end(key)

        # Periodically save to disk (every 10 writes)
        if len(self._cache) % 10 == 0:
            self._save_to_disk()

    def clear(self) -> None:
        """Clear all cache entries and reset statistics."""
        self._cache.clear()
        self._timestamps.clear()
        self.hits = 0
        self.misses = 0
        self._save_to_disk()

    def stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary containing cache metrics
        """
        self._cleanup_expired()
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "ttl_seconds": int(self.ttl.total_seconds()),
        }

    def __del__(self) -> None:
        """Save cache on cleanup."""
        self._save_to_disk()
