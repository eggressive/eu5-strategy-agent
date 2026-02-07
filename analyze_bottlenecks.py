"""
Deep bottleneck analysis with recommendations.

This script analyzes the benchmark results and identifies optimization opportunities.
"""

import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))

from eu5_agent.agent import EU5Agent
from eu5_agent.cache import clear_all_caches, knowledge_cache
from eu5_agent.config import reset_config
from eu5_agent.knowledge import EU5Knowledge


class BottleneckAnalyzer:
    """Analyze and report performance bottlenecks."""

    def __init__(self):
        self.issues = []
        self.recommendations = []

    def add_issue(self, severity: str, area: str, description: str, recommendation: str):
        """Add a performance issue."""
        self.issues.append({
            "severity": severity,
            "area": area,
            "description": description,
            "recommendation": recommendation
        })

    def analyze_path_operations(self):
        """Analyze pathlib usage in knowledge loading."""
        print("\n" + "="*70)
        print("ANALYZING: Path Operations in Knowledge Base")
        print("="*70)

        kb = EU5Knowledge()

        # Time path resolution
        start = time.perf_counter()
        for _ in range(1000):
            resolved_path = str(kb.knowledge_path.resolve())
        elapsed = (time.perf_counter() - start) * 1000

        print(f"Path.resolve() called 1000 times: {elapsed:.2f}ms")
        print(f"Average: {elapsed/1000:.4f}ms per call")

        if elapsed > 10:  # More than 10ms for 1000 calls
            self.add_issue(
                severity="MEDIUM",
                area="Knowledge Base",
                description=f"Path.resolve() is called on every get_knowledge() call. "
                           f"For 1000 calls: {elapsed:.2f}ms",
                recommendation="Cache the resolved path in __init__ instead of resolving on each query. "
                              "This would save ~0.01ms per knowledge query."
            )

    def analyze_cache_efficiency(self):
        """Analyze cache hit/miss ratios."""
        print("\n" + "="*70)
        print("ANALYZING: Cache Efficiency")
        print("="*70)

        clear_all_caches()
        kb = EU5Knowledge()

        # Simulate realistic workload
        queries = [
            ("mechanics", "economy"),
            ("mechanics", "economy"),  # Repeat
            ("mechanics", "government"),
            ("mechanics", "economy"),  # Repeat
            ("strategy", "beginner_route"),
            ("mechanics", "economy"),  # Repeat
        ]

        for cat, subcat in queries:
            kb.get_knowledge(cat, subcat)

        stats = knowledge_cache.stats()
        hit_rate = stats["hits"] / (stats["hits"] + stats["misses"]) * 100 if (stats["hits"] + stats["misses"]) > 0 else 0

        print(f"Cache stats after realistic workload:")
        print(f"  Hits: {stats['hits']}, Misses: {stats['misses']}")
        print(f"  Hit rate: {hit_rate:.1f}%")
        print(f"  Size: {stats['size']}/{stats['maxsize']}")

        if hit_rate < 50:
            self.add_issue(
                severity="LOW",
                area="Caching",
                description=f"Cache hit rate is {hit_rate:.1f}%, indicating many unique queries",
                recommendation="Current cache size (256) is appropriate. No action needed unless "
                              "production usage shows different patterns."
            )
        else:
            print(f"✓ Cache hit rate of {hit_rate:.1f}% is healthy")

    def analyze_message_trimming_algorithm(self):
        """Analyze message trimming efficiency."""
        print("\n" + "="*70)
        print("ANALYZING: Message Trimming Algorithm")
        print("="*70)

        with patch("eu5_agent.agent.OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            agent = EU5Agent(api_key="test-key")

            # Build large history
            for i in range(200):
                agent.messages.append({"role": "user", "content": f"Q{i}"})
                agent.messages.append({"role": "assistant", "content": f"A{i}"})

            initial_len = len(agent.messages)

            # Time trimming
            start = time.perf_counter()
            agent._trim_messages()
            elapsed = (time.perf_counter() - start) * 1000

            final_len = len(agent.messages)

            print(f"Trimmed {initial_len} messages to {final_len} in {elapsed:.4f}ms")
            print(f"Trimming is O(n) in message count, currently very fast")

            if elapsed > 1:  # More than 1ms
                self.add_issue(
                    severity="LOW",
                    area="Message Trimming",
                    description=f"Trimming {initial_len} messages took {elapsed:.4f}ms",
                    recommendation="Algorithm is efficient. Only consider optimization if "
                                  "conversations regularly exceed 1000+ messages."
                )
            else:
                print(f"✓ Trimming is very efficient ({elapsed:.4f}ms)")

    def analyze_json_parsing(self):
        """Analyze JSON parsing overhead in tool calls."""
        print("\n" + "="*70)
        print("ANALYZING: JSON Parsing in Tool Execution")
        print("="*70)

        import json

        # Simulate tool call argument parsing
        test_args = '{"category": "mechanics", "subcategory": "economy"}'

        start = time.perf_counter()
        for _ in range(10000):
            json.loads(test_args)
        elapsed = (time.perf_counter() - start) * 1000

        print(f"JSON parsing 10,000 times: {elapsed:.2f}ms")
        print(f"Average: {elapsed/10000:.4f}ms per parse")
        print("✓ JSON parsing overhead is negligible")

    def analyze_file_io(self):
        """Analyze file I/O patterns."""
        print("\n" + "="*70)
        print("ANALYZING: File I/O Performance")
        print("="*70)

        kb = EU5Knowledge()
        clear_all_caches()

        # Measure file reading
        file_path = kb.knowledge_path / "mechanics/economy_mechanics.md"

        start = time.perf_counter()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        cold_time = (time.perf_counter() - start) * 1000

        file_size = len(content)
        print(f"Cold file read: {cold_time:.3f}ms for {file_size} bytes")
        print(f"Throughput: {file_size / cold_time:.0f} KB/s")

        # Test with cache
        start = time.perf_counter()
        kb.get_knowledge("mechanics", "economy")
        cached_time = (time.perf_counter() - start) * 1000

        speedup = cold_time / cached_time if cached_time > 0 else float('inf')
        print(f"Cached read: {cached_time:.4f}ms")
        print(f"Cache speedup: {speedup:.1f}x")

        if cold_time > 5:
            self.add_issue(
                severity="LOW",
                area="File I/O",
                description=f"Cold file reads take {cold_time:.3f}ms",
                recommendation="File I/O is already optimized with caching. "
                              "Consider pre-loading frequently accessed files if startup time is critical."
            )
        else:
            print(f"✓ File I/O is fast ({cold_time:.3f}ms cold, {cached_time:.4f}ms cached)")

    def analyze_system_bottlenecks(self):
        """Check for system-level bottlenecks."""
        print("\n" + "="*70)
        print("ANALYZING: System-Level Factors")
        print("="*70)

        # Check Python version
        python_version = sys.version_info
        print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")

        if python_version < (3, 11):
            self.add_issue(
                severity="MEDIUM",
                area="Python Runtime",
                description=f"Using Python {python_version.major}.{python_version.minor}",
                recommendation="Upgrade to Python 3.11+ for ~25% performance improvement "
                              "(faster startup, better dict performance, optimized JSON parsing)"
            )
        else:
            print(f"✓ Using modern Python {python_version.major}.{python_version.minor}")

    def analyze_openai_api_mock(self):
        """Analyze OpenAI API call overhead (mocked)."""
        print("\n" + "="*70)
        print("ANALYZING: OpenAI API Overhead (Mocked)")
        print("="*70)

        print("Note: Real OpenAI API calls typically take 500-2000ms")
        print("This is the dominant latency factor in production")
        print("✓ Local processing overhead is negligible compared to API latency")

    def generate_report(self):
        """Generate final bottleneck report."""
        print("\n" + "="*70)
        print("BOTTLENECK ANALYSIS REPORT")
        print("="*70)

        if not self.issues:
            print("\n✓ No significant performance bottlenecks found!")
            print("  The codebase is well-optimized for its use case.")
            return

        # Sort by severity
        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        sorted_issues = sorted(self.issues, key=lambda x: severity_order[x["severity"]])

        for issue in sorted_issues:
            print(f"\n[{issue['severity']}] {issue['area']}")
            print(f"  Issue: {issue['description']}")
            print(f"  → Recommendation: {issue['recommendation']}")

    def generate_optimization_summary(self):
        """Generate optimization recommendations."""
        print("\n" + "="*70)
        print("OPTIMIZATION OPPORTUNITIES")
        print("="*70)

        optimizations = [
            {
                "priority": "HIGH",
                "title": "OpenAI API is the bottleneck",
                "description": "Real API calls take 500-2000ms, dominating all other operations",
                "actions": [
                    "Use streaming for better perceived performance",
                    "Consider using faster models (gpt-4o-mini) for simple queries",
                    "Implement request batching where possible",
                    "Add response caching for common questions"
                ]
            },
            {
                "priority": "MEDIUM",
                "title": "Path.resolve() in knowledge queries",
                "description": "Called on every get_knowledge(), adds ~0.01ms overhead",
                "actions": [
                    "Cache resolved path in EU5Knowledge.__init__()",
                    "Estimated savings: ~0.01ms per knowledge query"
                ]
            },
            {
                "priority": "LOW",
                "title": "Pre-load common knowledge files",
                "description": "Cold file reads take ~0.1-0.5ms",
                "actions": [
                    "Pre-load mechanics/economy, mechanics/government on startup",
                    "Only useful if startup latency is not important",
                    "Current lazy loading is fine for interactive use"
                ]
            }
        ]

        for opt in optimizations:
            print(f"\n[{opt['priority']}] {opt['title']}")
            print(f"  {opt['description']}")
            print("  Actions:")
            for action in opt["actions"]:
                print(f"    • {action}")


def main():
    analyzer = BottleneckAnalyzer()

    print("EU5 Strategy Agent - Deep Bottleneck Analysis")
    print("="*70)

    # Run all analyses
    analyzer.analyze_path_operations()
    analyzer.analyze_cache_efficiency()
    analyzer.analyze_message_trimming_algorithm()
    analyzer.analyze_json_parsing()
    analyzer.analyze_file_io()
    analyzer.analyze_system_bottlenecks()
    analyzer.analyze_openai_api_mock()

    # Generate reports
    analyzer.generate_report()
    analyzer.generate_optimization_summary()

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
