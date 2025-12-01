import os
import sys
import pytest

from eu5_agent.cache import knowledge_cache, search_cache, clear_all_caches


def _reset_caches():
    clear_all_caches()
    # populate some entries and stats
    knowledge_cache.set("k:key", "value")
    # trigger a miss and hit
    _ = search_cache.get("unknown:key")  # miss
    search_cache.set("s:key", ["r1"])  # size
    _ = knowledge_cache.get("k:key")


def test_cache_stats_prints_and_skips_api_key(monkeypatch, capsys):
    """--cache-stats should print cache stats and not require OPENAI_API_KEY"""
    _reset_caches()
    # Ensure no OPENAI_API_KEY present
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    # Replace argv
    monkeypatch.setattr(sys, "argv", ["eu5cli", "--cache-stats"])

    from eu5_agent import cli

    with pytest.raises(SystemExit) as se:
        cli.main()

    assert se.value.code == 0
    out = capsys.readouterr().out
    # Table heading includes 'Cache' column and two cache rows
    assert "knowledge" in out
    assert "search" in out
    # check numbers reflect the set operations above
    assert "1" in out
