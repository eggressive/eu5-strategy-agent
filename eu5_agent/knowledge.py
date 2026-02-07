"""
EU5 Knowledge Base Loader

Simple, direct file loading for the EU5 knowledge base.
No framework dependencies - just reads markdown files and returns content.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from .cache import knowledge_cache


class EU5Knowledge:
    """
    Loads and retrieves EU5 strategy knowledge from markdown files.

    Knowledge is organized into categories:
    - mechanics: Game mechanics (9 files covering 8 game panels)
    - strategy: Strategic guides for beginners
    - nations: Nation-specific opening strategies
    - resources: External wikis and community resources
    """

    # Knowledge base file mapping - organized by EU5's 8 main game panels
    KNOWLEDGE_MAP: Dict[str, Dict[str, str]] = {
        "mechanics": {
            # Core game mechanics covering all 8 main panels
            "economy": "mechanics/economy_mechanics.md",          # Economy panel
            "government": "mechanics/government_mechanics.md",    # Government panel
            "production": "mechanics/production_mechanics.md",    # Production panel
            "society": "mechanics/society_mechanics.md",          # Society panel (estates)
            "diplomacy": "mechanics/diplomacy_mechanics.md",      # Diplomacy panel
            "military": "mechanics/military_mechanics.md",        # Military panel (units/armies)
            "warfare": "mechanics/warfare_mechanics.md",          # Military panel (warfare)
            "geopolitics": "mechanics/geopolitics_mechanics.md",  # Geopolitics panel
            "advances": "mechanics/advances_mechanics.md",        # Advances panel
        },
        "strategy": {
            "beginner_route": "strategy/beginner_route.md",
            "common_mistakes": "strategy/common_mistakes.md",
        },
        "nations": {
            "england": "nations/nation_england.md",
        },
        "resources": {
            "all": "resources/eu5_resources.md",
        }
    }

    def __init__(self, knowledge_path: Optional[str] = None):
        """
        Initialize the knowledge loader.

        Args:
            knowledge_path: Path to knowledge base directory.
                           Defaults to the 'knowledge' directory in the repository.
        """
        if knowledge_path is None:
            # Try environment variable first
            knowledge_path = os.getenv("EU5_KNOWLEDGE_PATH", None)

            if knowledge_path is None:
                # Auto-detect knowledge base location (package relative)
                package_dir = Path(__file__).parent

                # Path(__file__) = .../eu5_agent/knowledge.py
                # .parent = eu5_agent package directory
                # / "knowledge" = knowledge directory inside package
                pkg_knowledge = package_dir / "knowledge"
                knowledge_path = str(pkg_knowledge)

        self.knowledge_path = Path(knowledge_path)

        if not self.knowledge_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found at {self.knowledge_path}"
            )

        # Cache the resolved path to avoid repeated path resolution
        # This saves ~0.027ms per get_knowledge() call
        self._resolved_path = str(self.knowledge_path.resolve())

    def list_categories(self) -> list[str]:
        """Get list of available knowledge categories."""
        return list(self.KNOWLEDGE_MAP.keys())

    def list_subcategories(self, category: str) -> Optional[list[str]]:
        """
        Get list of available subcategories for a category.

        Args:
            category: The category to list subcategories for

        Returns:
            List of subcategory names, or None if category not found
        """
        if category not in self.KNOWLEDGE_MAP:
            return None
        return list(self.KNOWLEDGE_MAP[category].keys())

    def get_knowledge(
        self,
        category: str,
        subcategory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve knowledge from the knowledge base.

        Args:
            category: Main category (mechanics, strategy, nations, resources)
            subcategory: Specific topic within category (optional)

        Returns:
            Dictionary with 'status', 'content', and optionally 'error' keys
        """
        # Validate category
        if category not in self.KNOWLEDGE_MAP:
            return {
                "status": "error",
                "error": f"Invalid category '{category}'. "
                        f"Available: {self.list_categories()}"
            }

        # If no subcategory, list available options
        if not subcategory:
            # For resources, default to 'all'
            if category == "resources":
                subcategory = "all"
            else:
                available = self.list_subcategories(category)
                if not available:
                    return {
                        "status": "list",
                        "content": f"Please specify a subcategory. Available in '{category}': (none)"
                    }
                return {
                    "status": "list",
                    "content": f"Please specify a subcategory. "
                              f"Available in '{category}': {', '.join(available)}"
                }

        # Validate subcategory
        if subcategory not in self.KNOWLEDGE_MAP[category]:
            available = self.list_subcategories(category)
            if not available:
                return {
                    "status": "error",
                    "error": f"Invalid subcategory '{subcategory}' for '{category}'. Available: (none)"
                }
            return {
                "status": "error",
                "error": f"Invalid subcategory '{subcategory}' for '{category}'. "
                        f"Available: {', '.join(available)}"
            }

        # Load the knowledge file
        filename = self.KNOWLEDGE_MAP[category][subcategory]
        file_path = self.knowledge_path / filename

        if not file_path.exists():
            return {
                "status": "error",
                "error": f"Knowledge file not found: {filename}"
            }
        # Use caching to avoid repeated disk reads
        # Use knowledge path in cache key to avoid stale cache when multiple
        # knowledge bases are used in a single process (e.g., tests or dynamic
        # loading of content). We use the pre-resolved path from __init__.
        cache_key = f"knowledge:{self._resolved_path}:{category}:{subcategory}"
        cached = knowledge_cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            result = {
                "status": "success",
                "content": content,
                "source": f"{category}/{subcategory}",
                "file": filename,
                "size": len(content)
            }

            knowledge_cache.set(cache_key, result)

            return result

        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to read {filename}: {str(e)}"
            }


# Quick test function
if __name__ == "__main__":
    kb = EU5Knowledge()

    print("Testing EU5 Knowledge Base Loader")
    print("="*60)

    # Test 1: List categories
    print("\nCategories:", kb.list_categories())

    # Test 2: List mechanics subcategories
    print("\nMechanics subcategories:", kb.list_subcategories("mechanics"))

    # Test 3: Get society mechanics
    result = kb.get_knowledge("mechanics", "society")
    if result["status"] == "success":
        print(f"\n✓ Loaded {result['file']}: {result['size']} bytes")
        print(f"  Preview: {result['content'][:200]}...")
    else:
        print(f"\n✗ Error: {result['error']}")
