"""
Simple in-memory LRU cache with basic stats for integration tests.

Not meant to be a full-featured cache - offers basic get/set/clear and
hit/miss counters. This keeps the repository dependency-free and safe
for unit tests and CI environments.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple


class LRUCache:
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        # Return cached value if present and update LRU order
        if key in self._cache:
            value = self._cache.pop(key)
            self._cache[key] = value
            self._hits += 1
            return value
        self._misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        if key in self._cache:
            # Remove old instance so that it becomes the most recent
            self._cache.pop(key)
        elif len(self._cache) >= self.maxsize:
            # Remove oldest entry
            self._cache.popitem(last=False)
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> Dict[str, int]:
        return {
            "size": len(self._cache),
            "maxsize": self.maxsize,
            "hits": self._hits,
            "misses": self._misses,
        }


# Module-level default caches
knowledge_cache = LRUCache(maxsize=256)
search_cache = LRUCache(maxsize=1024)


def clear_all_caches() -> None:
    knowledge_cache.clear()
    search_cache.clear()
