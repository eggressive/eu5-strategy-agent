"""
EU5 Web Search

Simple Google search for EU5 wiki and strategy content.
Prioritizes results from eu5.paradoxwikis.com.
"""

from typing import List, Dict, Optional
from googlesearch import search as google_search


def search_eu5_wiki(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search Google for EU5 content, prioritizing the official wiki.

    Args:
        query: Search query (will be prefixed with "EU5" if not already)
        max_results: Maximum number of results to return

    Returns:
        List of search results with 'title', 'url', and optionally 'snippet'
    """
    # Ensure query includes EU5 context
    if "eu5" not in query.lower() and "europa universalis" not in query.lower():
        query = f"EU5 {query}"

    results = []

    try:
        # Use googlesearch-python to get results
        # It returns URLs, we'll format them
        urls = list(google_search(query, num_results=max_results * 2, lang="en"))

        # Prioritize eu5.paradoxwikis.com results
        wiki_results = [url for url in urls if "eu5.paradoxwikis.com" in url]
        other_results = [url for url in urls if "eu5.paradoxwikis.com" not in url]

        # Combine with wiki results first
        prioritized_urls = (wiki_results + other_results)[:max_results]

        for url in prioritized_urls:
            # Extract title from URL (simple approach)
            title = url.split("/")[-1].replace("_", " ").replace("-", " ")
            if not title:
                title = "EU5 Wiki Page"

            results.append({
                "title": title.title(),
                "url": url,
                "snippet": f"Source: {url.split('/')[2]}"  # Domain name
            })

    except Exception as e:
        # Return empty list on error, agent will handle it
        print(f"Search error: {e}")
        return []

    return results


# Alternative: More detailed search with BeautifulSoup (if needed)
def search_eu5_wiki_detailed(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search for EU5 content with detailed result extraction.

    This version fetches the actual page content and extracts snippets.
    Use this if you need more detailed search results.

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        List of detailed search results
    """
    import requests
    from bs4 import BeautifulSoup

    # Get basic search results first
    basic_results = search_eu5_wiki(query, max_results)

    detailed_results = []

    for result in basic_results:
        try:
            # Fetch the page
            response = requests.get(result["url"], timeout=5)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title (prefer <h1> or <title>)
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text().strip() if title_tag else result["title"]

            # Extract first paragraph as snippet
            snippet = ""
            first_p = soup.find('p')
            if first_p:
                snippet = first_p.get_text().strip()[:200] + "..."

            detailed_results.append({
                "title": title,
                "url": result["url"],
                "snippet": snippet or result.get("snippet", "")
            })

        except Exception as e:
            # If fetching fails, use basic result
            detailed_results.append(result)

    return detailed_results


# Quick test
if __name__ == "__main__":
    print("Testing EU5 Web Search")
    print("="*60)

    # Test search
    query = "France opening strategy"
    print(f"\nSearching for: {query}")
    results = search_eu5_wiki(query, max_results=3)

    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}")
        print(f"   {result.get('snippet', '')}")
        print()
