"""
EU5 Web Search using Tavily API

Tavily is an AI-optimized search API designed specifically for LLM agents.
It provides structured, clean results with content extraction and relevance scoring.

Advantages over Google scraping:
- Official API (no scraping, no rate limits/blocking)
- AI-optimized content extraction (clean text, no HTML parsing)
- Domain filtering (prioritize eu5.paradoxwikis.com)
- Faster response times (single API call)
- Relevance scoring for better results
"""

import os
from typing import List, Dict, Optional


def search_eu5_wiki(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search for EU5 content using Tavily API, prioritizing the official wiki.

    Args:
        query: Search query (will be prefixed with "EU5" if not already)
        max_results: Maximum number of results to return

    Returns:
        List of search results with 'title', 'url', and 'snippet'
    """
    # Check if Tavily API key is available
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        # Tavily is optional - if not configured, return empty list
        # Agent will handle this gracefully
        return []

    # Ensure query includes EU5 context
    if "eu5" not in query.lower() and "europa universalis" not in query.lower():
        query = f"EU5 {query}"

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=api_key)

        # Search with domain prioritization for EU5 wiki
        response = client.search(
            query=query,
            max_results=max_results,
            include_domains=["eu5.paradoxwikis.com", "europauniversalisv.wiki"],
            search_depth="basic"  # Use "advanced" for more comprehensive results
        )

        results = []

        # Extract results from Tavily response
        for item in response.get("results", []):
            results.append({
                "title": item.get("title", "EU5 Wiki Page"),
                "url": item.get("url", ""),
                "snippet": item.get("content", "")[:300] + "..."  # Limit snippet length
            })

        return results

    except ImportError:
        # Tavily not installed
        print("Warning: tavily-python not installed. Run: pip install tavily-python")
        return []
    except Exception as e:
        # Return empty list on error, agent will handle it
        print(f"Tavily search error: {e}")
        return []


def search_eu5_wiki_comprehensive(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Comprehensive search for EU5 content using Tavily's advanced search mode.

    This version uses deeper search with more extensive crawling.
    Use this when you need more thorough coverage or the basic search
    doesn't return enough relevant results.

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        List of detailed search results
    """
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return []

    # Ensure query includes EU5 context
    if "eu5" not in query.lower() and "europa universalis" not in query.lower():
        query = f"EU5 {query}"

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=api_key)

        # Advanced search with more comprehensive results
        response = client.search(
            query=query,
            max_results=max_results,
            include_domains=["eu5.paradoxwikis.com", "europauniversalisv.wiki"],
            search_depth="advanced",  # More thorough search
            include_raw_content=False  # Get clean text only
        )

        results = []

        for item in response.get("results", []):
            results.append({
                "title": item.get("title", "EU5 Content"),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
                "score": item.get("score", 0.0)  # Relevance score
            })

        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x.get("score", 0.0), reverse=True)

        return results

    except ImportError:
        print("Warning: tavily-python not installed. Run: pip install tavily-python")
        return []
    except Exception as e:
        print(f"Tavily comprehensive search error: {e}")
        return []


# Quick test function
if __name__ == "__main__":
    print("Testing EU5 Web Search with Tavily API")
    print("="*60)

    # Check if API key is set
    if not os.getenv("TAVILY_API_KEY"):
        print("\n⚠️  TAVILY_API_KEY not set!")
        print("Get your free API key at: https://tavily.com/")
        print("Then set it: export TAVILY_API_KEY='your-key-here'")
        exit(1)

    # Test basic search
    query = "France opening strategy"
    print(f"\n🔍 Searching for: {query}")
    results = search_eu5_wiki(query, max_results=3)

    if results:
        print(f"\n✓ Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['url']}")
            print(f"   {result.get('snippet', '')[:150]}...")
            print()
    else:
        print("\n✗ No results found (check API key or quota)")

    # Test comprehensive search
    print("\n" + "="*60)
    print("Testing comprehensive search:")
    print("="*60)

    comp_results = search_eu5_wiki_comprehensive("estates mechanics", max_results=3)

    if comp_results:
        print(f"\n✓ Found {len(comp_results)} comprehensive results:\n")
        for i, result in enumerate(comp_results, 1):
            score = result.get('score', 0.0)
            print(f"{i}. {result['title']} (score: {score:.2f})")
            print(f"   {result['url']}")
            print()
    else:
        print("\n✗ No comprehensive results found")
