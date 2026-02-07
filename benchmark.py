"""
Performance benchmarking and profiling script for EU5 Strategy Agent.

This script measures performance bottlenecks in:
1. Knowledge base loading and caching
2. Agent initialization
3. Message history trimming
4. OpenAI API calls (mocked for benchmarking)
5. Tool execution overhead

Run with:
    python benchmark.py
    python benchmark.py --profile  # Enable cProfile
    python benchmark.py --memory   # Enable memory profiling
"""

import argparse
import cProfile
import gc
import io
import pstats
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from eu5_agent.agent import EU5Agent
from eu5_agent.cache import clear_all_caches, knowledge_cache, search_cache
from eu5_agent.config import reset_config
from eu5_agent.knowledge import EU5Knowledge


class BenchmarkTimer:
    """Simple context manager for timing code blocks."""

    def __init__(self, name: str):
        self.name = name
        self.start_time = 0.0
        self.end_time = 0.0

    def __enter__(self):
        gc.collect()  # Clean up before benchmark
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time

    def __str__(self):
        return f"{self.name}: {self.elapsed*1000:.2f}ms"


def benchmark_function(
    func: Callable, iterations: int = 100, name: str = ""
) -> Dict[str, float]:
    """
    Benchmark a function over multiple iterations.

    Returns:
        Dictionary with min, max, mean, median times in milliseconds
    """
    times: List[float] = []

    for _ in range(iterations):
        gc.collect()
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    times.sort()
    return {
        "name": name or func.__name__,
        "iterations": iterations,
        "min_ms": times[0],
        "max_ms": times[-1],
        "mean_ms": sum(times) / len(times),
        "median_ms": times[len(times) // 2],
        "total_ms": sum(times),
    }


def benchmark_knowledge_loading():
    """Benchmark knowledge base file loading with and without cache."""
    print("\n" + "=" * 70)
    print("BENCHMARK: Knowledge Base Loading")
    print("=" * 70)

    kb = EU5Knowledge()

    # Benchmark: Cold load (no cache)
    def cold_load():
        clear_all_caches()
        kb.get_knowledge("mechanics", "economy")

    cold_stats = benchmark_function(cold_load, iterations=50, name="Cold load (no cache)")
    print(f"Cold load: {cold_stats['mean_ms']:.2f}ms (min: {cold_stats['min_ms']:.2f}ms)")

    # Benchmark: Warm load (with cache)
    kb.get_knowledge("mechanics", "economy")  # Prime the cache

    def warm_load():
        kb.get_knowledge("mechanics", "economy")

    warm_stats = benchmark_function(warm_load, iterations=1000, name="Warm load (cached)")
    print(
        f"Warm load: {warm_stats['mean_ms']:.4f}ms (min: {warm_stats['min_ms']:.4f}ms)"
    )

    speedup = cold_stats["mean_ms"] / warm_stats["mean_ms"]
    print(f"Cache speedup: {speedup:.1f}x faster")

    # Benchmark: Loading all knowledge files
    print("\nLoading all knowledge files...")
    categories = {
        "mechanics": [
            "economy",
            "government",
            "production",
            "society",
            "diplomacy",
            "military",
            "warfare",
            "geopolitics",
            "advances",
        ],
        "strategy": ["beginner_route", "common_mistakes"],
        "nations": ["england"],
        "resources": ["all"],
    }

    with BenchmarkTimer("Load all files (cold)") as timer:
        clear_all_caches()
        for category, subcategories in categories.items():
            for subcategory in subcategories:
                kb.get_knowledge(category, subcategory)
    print(timer)

    with BenchmarkTimer("Load all files (warm/cached)") as timer:
        for category, subcategories in categories.items():
            for subcategory in subcategories:
                kb.get_knowledge(category, subcategory)
    print(timer)

    print(f"\nCache stats: {knowledge_cache.stats()}")


def benchmark_agent_initialization():
    """Benchmark agent initialization time."""
    print("\n" + "=" * 70)
    print("BENCHMARK: Agent Initialization")
    print("=" * 70)

    # Mock OpenAI to avoid actual API calls
    with patch("eu5_agent.agent.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        def init_agent():
            reset_config()
            clear_all_caches()
            return EU5Agent(api_key="test-key")

        stats = benchmark_function(init_agent, iterations=100, name="Agent init")
        print(f"Agent initialization: {stats['mean_ms']:.2f}ms")
        print(f"  min: {stats['min_ms']:.2f}ms, max: {stats['max_ms']:.2f}ms")


def benchmark_message_trimming():
    """Benchmark message history trimming performance."""
    print("\n" + "=" * 70)
    print("BENCHMARK: Message History Trimming")
    print("=" * 70)

    with patch("eu5_agent.agent.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        agent = EU5Agent(api_key="test-key")

        # Test different history sizes
        for num_messages in [10, 50, 100, 200, 500]:
            # Build a large history with realistic turn groups
            agent.reset()
            for i in range(num_messages // 3):  # Each turn is ~3 messages
                agent.messages.append({"role": "user", "content": f"Question {i}"})
                agent.messages.append(
                    {"role": "assistant", "content": f"Response {i}"}
                )
                agent.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": f"call_{i}",
                        "content": f"Tool result {i}",
                    }
                )

            initial_len = len(agent.messages)

            def trim():
                agent._trim_messages()

            stats = benchmark_function(trim, iterations=1000, name=f"Trim {num_messages}")
            print(
                f"Trim {initial_len} messages: {stats['mean_ms']:.4f}ms "
                f"(trimmed to {len(agent.messages)})"
            )


def benchmark_tool_execution():
    """Benchmark tool execution overhead."""
    print("\n" + "=" * 70)
    print("BENCHMARK: Tool Execution")
    print("=" * 70)

    with patch("eu5_agent.agent.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        agent = EU5Agent(api_key="test-key")

        # Mock tool call object
        class MockToolCall:
            def __init__(self, name: str, args: str):
                self.id = "test_call_id"
                self.function = MagicMock()
                self.function.name = name
                self.function.arguments = args

        # Benchmark knowledge query
        tool_call = MockToolCall(
            "query_knowledge", '{"category": "mechanics", "subcategory": "economy"}'
        )

        def exec_knowledge():
            agent._execute_tool_call(tool_call)

        stats = benchmark_function(exec_knowledge, iterations=500, name="query_knowledge")
        print(f"Execute query_knowledge: {stats['mean_ms']:.3f}ms")

        # Benchmark web search (mocked)
        with patch("eu5_agent.search.search_eu5_wiki") as mock_search:
            mock_search.return_value = [
                {"title": "Test", "url": "http://test.com", "snippet": "Test snippet"}
            ]

            tool_call = MockToolCall("web_search", '{"query": "test query"}')

            def exec_search():
                agent._execute_tool_call(tool_call)

            stats = benchmark_function(exec_search, iterations=500, name="web_search")
            print(f"Execute web_search: {stats['mean_ms']:.3f}ms")


def benchmark_full_conversation():
    """Benchmark a complete conversation flow (mocked API)."""
    print("\n" + "=" * 70)
    print("BENCHMARK: Full Conversation Flow (Mocked)")
    print("=" * 70)

    with patch("eu5_agent.agent.OpenAI") as mock_openai:
        # Setup mock responses
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        # Simulate: User query -> Tool call -> Final response
        tool_call = MagicMock()
        tool_call.id = "call_1"
        tool_call.function.name = "query_knowledge"
        tool_call.function.arguments = '{"category": "mechanics", "subcategory": "economy"}'

        # First response: assistant requests tool
        first_response = MagicMock()
        first_response.choices = [MagicMock()]
        first_response.choices[0].message.tool_calls = [tool_call]
        first_response.choices[0].message.content = None
        first_response.choices[0].message.model_dump.return_value = {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "query_knowledge",
                        "arguments": '{"category": "mechanics", "subcategory": "economy"}',
                    },
                }
            ],
        }

        # Second response: final answer
        second_response = MagicMock()
        second_response.choices = [MagicMock()]
        second_response.choices[0].message.tool_calls = None
        second_response.choices[0].message.content = "Here's what you need to know..."
        second_response.choices[0].message.model_dump.return_value = {
            "role": "assistant",
            "content": "Here's what you need to know...",
        }

        mock_client.chat.completions.create.side_effect = [
            first_response,
            second_response,
        ]

        agent = EU5Agent(api_key="test-key")

        def full_chat():
            agent.reset()
            # Reset the mock side_effect for each iteration
            mock_client.chat.completions.create.side_effect = [
                first_response,
                second_response,
            ]
            return agent.chat("How does economy work?")

        stats = benchmark_function(full_chat, iterations=100, name="Full chat flow")
        print(f"Full conversation (1 tool call): {stats['mean_ms']:.2f}ms")
        print(f"  min: {stats['min_ms']:.2f}ms, max: {stats['max_ms']:.2f}ms")


def run_profiler(func: Callable, name: str):
    """Run cProfile on a function and display results."""
    print(f"\n{'='*70}")
    print(f"PROFILING: {name}")
    print("=" * 70)

    profiler = cProfile.Profile()
    profiler.enable()
    func()
    profiler.disable()

    # Print stats sorted by cumulative time
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(20)  # Top 20 functions
    print(s.getvalue())


def main():
    parser = argparse.ArgumentParser(description="Benchmark EU5 Strategy Agent")
    parser.add_argument(
        "--profile", action="store_true", help="Enable cProfile profiling"
    )
    parser.add_argument(
        "--memory", action="store_true", help="Enable memory profiling (requires tracemalloc)"
    )
    args = parser.parse_args()

    print("EU5 Strategy Agent - Performance Benchmark")
    print("=" * 70)

    # Run benchmarks
    benchmark_knowledge_loading()
    benchmark_agent_initialization()
    benchmark_message_trimming()
    benchmark_tool_execution()
    benchmark_full_conversation()

    # Profiling
    if args.profile:
        print("\n" + "=" * 70)
        print("DETAILED PROFILING")
        print("=" * 70)

        # Profile knowledge loading
        def profile_knowledge():
            clear_all_caches()
            kb = EU5Knowledge()
            for _ in range(10):
                kb.get_knowledge("mechanics", "economy")

        run_profiler(profile_knowledge, "Knowledge Loading (10 iterations)")

        # Profile agent initialization
        def profile_init():
            with patch("eu5_agent.agent.OpenAI") as mock_openai:
                mock_openai.return_value = MagicMock()
                for _ in range(10):
                    reset_config()
                    EU5Agent(api_key="test-key")

        run_profiler(profile_init, "Agent Initialization (10 iterations)")

    # Memory profiling
    if args.memory:
        try:
            import tracemalloc

            print("\n" + "=" * 70)
            print("MEMORY PROFILING")
            print("=" * 70)

            tracemalloc.start()

            # Test memory usage of knowledge base
            kb = EU5Knowledge()
            snapshot1 = tracemalloc.take_snapshot()

            # Load all knowledge
            for category, subcategories in {
                "mechanics": ["economy", "government", "production"],
                "strategy": ["beginner_route"],
            }.items():
                for subcategory in subcategories:
                    kb.get_knowledge(category, subcategory)

            snapshot2 = tracemalloc.take_snapshot()
            top_stats = snapshot2.compare_to(snapshot1, "lineno")

            print("\nTop 10 memory allocations:")
            for stat in top_stats[:10]:
                print(stat)

            tracemalloc.stop()

        except ImportError:
            print("\nMemory profiling requires Python 3.4+")

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
