import threading
import time

from eu5_agent.cache import LRUCache, clear_all_caches


def _worker_set_get(cache: LRUCache, start_index: int, count: int):
    for i in range(start_index, start_index + count):
        cache.set(f"k{i}", f"v{i}")
        _ = cache.get(f"k{i}")
        # tiny sleep to allow concurrency scheduling
        time.sleep(0.001)


def test_lru_cache_thread_safety():
    """Ensure no exceptions occur with multiple threads and invariants hold."""
    clear_all_caches()
    cache = LRUCache(maxsize=50)

    # Launch multiple threads that set and get values concurrently
    threads = []
    for t in range(8):
        thr = threading.Thread(target=_worker_set_get, args=(cache, t * 100, 100))
        threads.append(thr)
        thr.start()

    for thr in threads:
        thr.join()

    # Ensure no more than maxsize elements in the cache
    stats = cache.stats()
    assert stats["size"] <= 50
    # Ensure some hits or misses occurred
    assert stats["hits"] + stats["misses"] > 0
