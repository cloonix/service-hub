"""Tests for core cache functionality."""

import time

import pytest

from app.core.cache import TTLCache


def test_cache_basic_get_set():
    """Test basic cache get and set operations."""
    cache = TTLCache(ttl_seconds=60, max_size=10)

    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    assert cache.get("nonexistent") is None


def test_cache_ttl_expiration():
    """Test that entries expire after TTL."""
    cache = TTLCache(ttl_seconds=1, max_size=10)

    cache.set("key", "value")
    assert cache.get("key") == "value"

    time.sleep(1.1)
    assert cache.get("key") is None


def test_cache_lru_eviction():
    """Test LRU eviction when max size is reached."""
    cache = TTLCache(ttl_seconds=60, max_size=3)

    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    # Adding fourth item should evict the oldest (key1)
    cache.set("key4", "value4")

    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"
    assert cache.get("key4") == "value4"


def test_cache_stats():
    """Test cache statistics tracking."""
    cache = TTLCache(ttl_seconds=60, max_size=10)

    cache.set("key1", "value1")
    cache.get("key1")  # Hit
    cache.get("key2")  # Miss

    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["size"] == 1
    assert stats["max_size"] == 10


def test_cache_clear():
    """Test cache clear operation."""
    cache = TTLCache(ttl_seconds=60, max_size=10)

    cache.set("key1", "value1")
    cache.set("key2", "value2")

    cache.clear()

    assert cache.get("key1") is None
    assert cache.get("key2") is None
    assert cache.stats()["size"] == 0
