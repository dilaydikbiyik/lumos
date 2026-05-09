"""
Daily disk cache for market data.
Uses diskcache to persist responses to disk; avoids hammering external APIs.
Cache TTL = 24 hours.
"""

import diskcache
from pathlib import Path

_CACHE_DIR = Path(__file__).parent.parent / ".cache"
_cache = diskcache.Cache(str(_CACHE_DIR), size_limit=200 * 1024 * 1024)  # 200 MB

TTL_SECONDS = 60 * 60 * 24  # 24 hours


def get(key: str):
    return _cache.get(key)


def set(key: str, value, ttl: int = TTL_SECONDS):
    _cache.set(key, value, expire=ttl)


def delete(key: str):
    _cache.delete(key)


def clear():
    _cache.clear()
