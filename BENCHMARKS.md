# Performance Benchmarking Tools

This directory contains comprehensive benchmarking and profiling tools for the EU5 Strategy Agent.

## Quick Start

```bash
# Run basic benchmarks
python3 benchmark.py

# Run with detailed profiling
python3 benchmark.py --profile

# Run with memory profiling
python3 benchmark.py --memory

# Deep bottleneck analysis
python3 analyze_bottlenecks.py

# Verify optimizations
python3 verify_fix.py
```

## Tools Overview

### 1. benchmark.py

Comprehensive benchmark suite measuring:
- Knowledge base loading (cold vs cached)
- Agent initialization
- Message history trimming
- Tool execution overhead
- Full conversation flow (mocked)

**Features:**
- Multiple iterations for statistical accuracy
- Min/max/mean/median timing
- cProfile integration (--profile flag)
- Memory profiling (--memory flag)

**Example output:**
```
Knowledge Base Loading:
  Cold load: 0.10ms
  Warm load: 0.0064ms
  Cache speedup: 1.5x

Agent Initialization: 0.11ms
Message Trimming (500 msgs): 0.002ms
Tool Execution: 0.08ms
```

### 2. analyze_bottlenecks.py

Deep analysis tool that:
- Identifies performance bottlenecks
- Analyzes path operations
- Checks cache efficiency
- Evaluates algorithms
- Generates recommendations

**Example output:**
```
[MEDIUM] Knowledge Base
  Issue: Path.resolve() called on every query
  → Cache resolved path in __init__()

[HIGH] OpenAI API is the bottleneck
  → Use streaming, faster models, caching
```

### 3. verify_fix.py

Validates applied optimizations:
- Measures query throughput
- Calculates time savings
- Confirms improvements

**Example output:**
```
10,000 cached queries: 63.76ms
Average per query: 0.0064ms
Throughput: 156,843 queries/second
Estimated time saved: 260ms
```

## Understanding the Results

### What's Fast (< 1ms)
- Agent initialization
- Knowledge queries (cached)
- Message trimming
- Tool execution

### What's Slow (> 100ms)
- OpenAI API calls (500-2000ms)
- Web search API calls (100-500ms)

**Key Insight:** Local operations are highly optimized. The only meaningful bottleneck is external API latency.

## Optimization History

### 2026-02-07: Path Resolution Caching

**Problem:** `Path.resolve()` was called on every knowledge query, adding ~0.027ms overhead.

**Solution:** Cache resolved path in `__init__()`:
```python
self._resolved_path = str(self.knowledge_path.resolve())
```

**Results:**
- 27% improvement in cached query performance
- Saves 0.026ms per query
- Saves 260ms over 10,000 queries

**Files changed:** `eu5_agent/knowledge.py`

## Profiling Tips

### Using cProfile

```bash
python3 benchmark.py --profile
```

Shows top functions by cumulative time. Look for:
- High `tottime` - function's own time
- High `cumtime` - function + callees
- High `ncalls` - frequently called functions

### Using Memory Profiling

```bash
python3 benchmark.py --memory
```

Shows top memory allocations. Watch for:
- Large allocations (> 1MB)
- Repeated small allocations
- Memory leaks (growing over time)

### Custom Benchmarking

Use `BenchmarkTimer` context manager:
```python
from benchmark import BenchmarkTimer

with BenchmarkTimer("My operation") as timer:
    # Code to benchmark
    do_something()

print(timer)  # "My operation: 1.23ms"
```

Or `benchmark_function()` for multiple iterations:
```python
from benchmark import benchmark_function

stats = benchmark_function(my_func, iterations=100)
print(f"Mean: {stats['mean_ms']:.2f}ms")
```

## Interpreting Metrics

### Good Performance Targets

| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| File I/O (4KB) | < 1ms | 0.028ms | ✅ Excellent |
| Cache lookup | < 0.1ms | 0.006ms | ✅ Excellent |
| Agent init | < 10ms | 0.11ms | ✅ Excellent |
| Message trim | < 1ms | 0.002ms | ✅ Excellent |

### When to Optimize

❌ **Don't optimize:**
- Operations < 1ms (diminishing returns)
- One-time operations (initialization)
- Operations dwarfed by API calls

✅ **Do optimize:**
- Operations called frequently (> 1000x)
- Operations in hot paths
- Operations causing user-visible latency

## Related Documentation

- **[docs/performance/PERFORMANCE_ANALYSIS.md](docs/performance/PERFORMANCE_ANALYSIS.md)** - Detailed analysis report
- **CLAUDE.md** - Architecture and optimization notes
- **tests/** - Unit tests including performance edge cases

## Continuous Monitoring

Run benchmarks:
- Before/after optimizations
- When adding new features
- After dependency upgrades
- On different Python versions

**Maintain performance as a feature.**
