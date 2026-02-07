# Performance Documentation

Complete performance analysis, benchmarks, and optimization guides for the EU5 Strategy Agent.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[README_PERFORMANCE.md](README_PERFORMANCE.md)** | **Start here!** User guide and quick reference |
| [PERFORMANCE_INDEX.md](PERFORMANCE_INDEX.md) | Master index with navigation |
| [PERFORMANCE_QUICKREF.md](PERFORMANCE_QUICKREF.md) | Quick reference card |
| [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md) | Detailed metrics and analysis |

## 🛠️ Benchmarking Tools

Located in the repository root:

- `benchmark.py` - Comprehensive benchmark suite
- `analyze_bottlenecks.py` - Bottleneck analysis tool
- `verify_fix.py` - Optimization verification

See [../../BENCHMARKS.md](../../BENCHMARKS.md) for tool usage.

## 📊 Quick Stats

| Metric | Value |
|--------|-------|
| Agent initialization | 0.11ms |
| Knowledge query (cached) | 0.007ms |
| Message trimming (500 msgs) | 0.002ms |
| Throughput | 135K queries/sec |
| **Grade** | **A+** 🏆 |

## 🚀 Quick Start

```bash
# From repository root
python3 benchmark.py --profile
python3 analyze_bottlenecks.py
cat docs/performance/README_PERFORMANCE.md
```

## 📈 Recent Optimizations

### 2026-02-07: Path Resolution Caching
- **Impact:** 27% faster cached queries
- **Files:** `eu5_agent/knowledge.py`
- **Details:** See [../../OPTIMIZATION_SUMMARY.md](../../OPTIMIZATION_SUMMARY.md)

## 🔗 Related Documentation

- [BENCHMARKS.md](../../BENCHMARKS.md) - Benchmarking tool guide
- [OPTIMIZATION_SUMMARY.md](../../OPTIMIZATION_SUMMARY.md) - Optimization history
- [CLAUDE.md](../../CLAUDE.md) - Architecture and implementation notes

---

**Status:** Production Ready ✅
**Last Updated:** 2026-02-07
