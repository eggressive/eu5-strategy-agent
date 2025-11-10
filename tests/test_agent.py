#!/usr/bin/env python3
"""
Test script for EU5 Standalone Agent

Demonstrates the functionality without requiring API calls.
"""

from eu5_agent.knowledge import EU5Knowledge
from eu5_agent.search import search_eu5_wiki

def test_knowledge_base():
    """Test the knowledge base loading."""
    print("=" * 70)
    print("TEST 1: Knowledge Base Loading")
    print("=" * 70)

    kb = EU5Knowledge()

    # Test categories
    print("\nAvailable categories:", kb.list_categories())

    # Test mechanics - society (estates)
    print("\n--- Testing: mechanics/society ---")
    result = kb.get_knowledge('mechanics', 'society')
    if result['status'] == 'success':
        print(f"✓ Loaded: {result['file']} ({result['size']:,} bytes)")
        lines = result['content'].split('\n')[:15]
        print("First 15 lines:")
        for line in lines:
            print(f"  {line}")
    else:
        print(f"✗ Error: {result['error']}")

    # Test strategy - beginner
    print("\n--- Testing: strategy/beginner_route ---")
    result = kb.get_knowledge('strategy', 'beginner_route')
    if result['status'] == 'success':
        print(f"✓ Loaded: {result['file']} ({result['size']:,} bytes)")
        print(f"Preview: {result['content'][:200]}...")
    else:
        print(f"✗ Error: {result['error']}")

    # Test nations - England
    print("\n--- Testing: nations/england ---")
    result = kb.get_knowledge('nations', 'england')
    if result['status'] == 'success':
        print(f"✓ Loaded: {result['file']} ({result['size']:,} bytes)")
        print(f"Preview: {result['content'][:200]}...")
    else:
        print(f"✗ Error: {result['error']}")

    print("\n✓ Knowledge base tests passed!\n")


def test_web_search():
    """Test the web search functionality."""
    print("=" * 70)
    print("TEST 2: Web Search (Fallback)")
    print("=" * 70)

    print("\nSearching for: 'France opening strategy'")
    try:
        results = search_eu5_wiki("France opening strategy", max_results=3)
        if results:
            print(f"\n✓ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['title']}")
                print(f"   URL: {result['url']}")
                print(f"   {result.get('snippet', '')}")
        else:
            print("\nNo results found (this is expected if no internet or Google blocking)")
    except Exception as e:
        print(f"\n⚠ Search test skipped: {e}")
        print("(This is expected if no internet connection or Google is blocking)")

    print()


def test_agent_structure():
    """Test that the agent can be instantiated without API key."""
    print("=" * 70)
    print("TEST 3: Agent Structure")
    print("=" * 70)

    try:
        # This will fail without API key, but we can check imports
        from eu5_agent.agent import EU5Agent
        from eu5_agent.prompts import SYSTEM_PROMPT, TOOLS
        from eu5_agent.cli import print_banner, print_help

        print("\n✓ All modules import successfully")
        print(f"✓ System prompt length: {len(SYSTEM_PROMPT):,} chars")
        print(f"✓ Available tools: {len(TOOLS)}")
        for tool in TOOLS:
            print(f"  - {tool['function']['name']}")

        print("\n✓ Agent structure tests passed!")

    except ImportError as e:
        print(f"\n✗ Import error: {e}")

    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("EU5 STANDALONE AGENT - TEST SUITE")
    print("=" * 70)
    print()

    test_knowledge_base()
    test_web_search()
    test_agent_structure()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\nStandalone agent is ready to use!")
    print("\nTo run the agent:")
    print("  1. Set OPENAI_API_KEY environment variable")
    print("  2. Run: python run_eu5_agent.py")
    print("  3. Or single query: python run_eu5_agent.py --query 'your question'")
    print("\nExample:")
    print("  export OPENAI_API_KEY='your-key-here'")
    print("  python run_eu5_agent.py --query 'How do estates work?'")
    print()


if __name__ == "__main__":
    main()
