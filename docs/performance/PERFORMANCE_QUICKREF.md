# Performance Quick Reference

## 🚀 Run Benchmarks

```bash
python3 benchmark.py              # Basic benchmarks
python3 benchmark.py --profile    # With cProfile
python3 benchmark.py --memory     # With memory profiling
python3 analyze_bottlenecks.py    # Deep analysis
python3 verify_fix.py             # Verify optimizations
```

## 📊 Current Performance (2026-02-07)

| Operation | Time | Status |
|-----------|------|--------|
| Agent init | 0.11ms | ✅ Excellent |
| Knowledge query (cached) | 0.006ms | ✅ Excellent |
| Message trim (500 msgs) | 0.002ms | ✅ Excellent |
| Tool execution | 0.08ms | ✅ Excellent |
| **OpenAI API** | **500-2000ms** | ⚠️ **Bottleneck** |

## ⚡ Recent Optimizations

### 2026-02-07: Path Resolution Caching

**File:** `eu5_agent/knowledge.py`

**Change:**
```python
# Cache resolved path in __init__()
self._resolved_path = str(self.knowledge_path.resolve())
```

**Impact:**
- 27% faster cached queries
- +40% throughput (111K → 156K q/s)
- Saves 0.026ms per query

## 🎯 What to Optimize Next

### High Impact
1. **Response caching** - Cache common questions (saves 500-2000ms)
2. **Streaming** - Better UX, show partial results
3. **Smart model selection** - Use faster models for simple queries

### Medium Impact
4. **Python 3.11+** - Free 25% speedup (currently on 3.10)

### Low Impact
5. Pre-loading - Only for batch processing (current lazy loading is optimal)

## 🔍 Performance Debugging

### If Slow Performance

1. **Check if it's API latency:**
   ```bash
   # Add --verbose flag
   python -m eu5_agent.cli --query "test" --verbose
   ```
   Look for tool calls - each adds 500-2000ms

2. **Profile the code:**
   ```bash
   python3 benchmark.py --profile
   ```
   Look for functions with high `cumtime`

3. **Check cache stats:**
   ```python
   from eu5_agent.cache import knowledge_cache
   print(knowledge_cache.stats())
   ```
   Low hit rate? Add more cache entries.

### Expected Latencies

- Interactive query: **1-3 seconds** (mostly API)
- With 1 tool call: **2-4 seconds**
- With web search: **3-5 seconds**
- Agent reset: **< 1ms**

## 📈 Performance Targets

### Current Status: ✅ All targets met

| Target | Current | Status |
|--------|---------|--------|
| Agent init < 1ms | 0.11ms | ✅ 9x faster |
| Cache lookup < 0.01ms | 0.006ms | ✅ 1.6x faster |
| File I/O < 0.1ms | 0.028ms | ✅ 3.5x faster |
| Trim < 1ms | 0.002ms | ✅ 500x faster |

## 🛠️ Maintenance

### When to Re-benchmark

- ✅ Before/after adding features
- ✅ After dependency upgrades
- ✅ When Python version changes
- ✅ If users report slowness

### CI/CD Integration

```yaml
# Add to CI pipeline
- name: Run benchmarks
  run: |
    python3 benchmark.py
    python3 analyze_bottlenecks.py
```

## 📚 Documentation

- **PERFORMANCE_ANALYSIS.md** - Full analysis report
- **BENCHMARKS.md** - Tool documentation
- **OPTIMIZATION_SUMMARY.md** - Optimization history
- **CLAUDE.md** - Architecture notes

## 💡 Pro Tips

1. **Don't optimize < 1ms operations** - Focus on API latency
2. **Measure first, optimize second** - Use profiling tools
3. **Test after every change** - Ensure no regressions
4. **Document optimizations** - Help future maintainers

## 🎓 Learning Resources

### Understanding the Metrics

- **tottime** - Time spent in function only
- **cumtime** - Time spent in function + callees
- **ncalls** - Number of calls
- **percall** - Time per call

### Good Performance is...

- ✅ Sub-millisecond local operations
- ✅ Effective caching (>30% hit rate)
- ✅ O(n) or better algorithms
- ✅ Minimal allocations

### Red Flags

- ❌ Operations taking > 100ms (unless I/O)
- ❌ Growing memory usage
- ❌ O(n²) in hot paths
- ❌ Cache hit rate < 10%

---

**Last updated:** 2026-02-07
**Performance grade:** A+
**Status:** Production ready
