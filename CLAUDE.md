# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EU5 Strategy Agent is a lightweight, standalone AI strategy advisor for Europa Universalis 5 using OpenAI's function calling API. The agent combines a curated local knowledge base with optional web search (Tavily API) to provide expert strategic guidance.

**Key characteristics:**
- Framework-independent: Direct OpenAI API integration, no LangChain or similar
- Minimal dependencies: 5 core packages (openai, pydantic, rich, tavily-python, python-dotenv)
- Fast startup: < 1 second initialization with in-memory LRU caching
- Multi-provider: Works with OpenAI and OpenAI-compatible APIs (Groq, Google AI Studio, OpenRouter)

## Development Commands

### Installation and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install in editable mode (recommended for development)
pip install -e .

# Install with dev dependencies
pip install -e .[dev]
```

### Running the Agent

```bash
# Interactive mode (from repo root)
python -m eu5_agent.cli

# Single query mode
python -m eu5_agent.cli --query "How do estates work?"

# With verbose output (shows tool calls)
python -m eu5_agent.cli --query "England opening" --verbose

# View cache statistics
python -m eu5_agent.cli --cache-stats

# Alternative: Use console script (after pip install -e .)
eu5-agent --query "How do estates work?"
```

### Testing

```bash
# Run all unit tests (excludes integration tests by default)
pytest

# Run unit tests explicitly
pytest -m "not openai_integration"

# Run integration tests (requires OPENAI_API_KEY)
export OPENAI_API_KEY=your-api-key
pytest -m openai_integration

# Run all tests (unit + integration)
pytest

# Run with coverage
pytest --cov=eu5_agent --cov-report=term-missing

# Run specific test file
pytest tests/test_agent_unit.py

# Run specific test function
pytest tests/test_agent_unit.py::test_agent_initialization
```

**Important:** Integration tests make real OpenAI API calls but are designed to minimize cost (max_completion_tokens ≤ 50).

### Code Quality

```bash
# Format code with Black
black eu5_agent/ tests/

# Lint with Ruff
ruff check eu5_agent/ tests/

# Type check with mypy
mypy eu5_agent/
```

## Architecture

### Core Components

1. **EU5Agent** (`agent.py`) - Main agent orchestrator
   - Manages OpenAI chat completions with function calling
   - Coordinates tool execution (knowledge base queries, web search)
   - Handles conversation state and message history
   - Implements agentic loop with max 10 iterations to prevent infinite loops

2. **EU5Knowledge** (`knowledge.py`) - Knowledge base loader
   - Direct markdown file loading from `eu5_agent/knowledge/`
   - Organized by categories: mechanics, strategy, nations, resources
   - Uses thread-safe LRU caching to avoid repeated disk I/O
   - Cache key includes knowledge_path to support multiple knowledge bases in tests

3. **EU5Config** (`config.py`) - Configuration management
   - Loads settings from environment variables or .env file
   - Singleton pattern with `get_config()` and `reset_config()` (for tests)
   - Model-specific handling: gpt-5 models use `max_completion_tokens` and don't support `temperature`

4. **Web Search** (`search.py`) - Tavily API integration
   - Optional fallback when knowledge base is insufficient
   - Two modes: `search_eu5_wiki()` (basic, used by agent) and `search_eu5_wiki_comprehensive()` (advanced)
   - Domain filtering prioritizes eu5.paradoxwikis.com
   - Client caching to avoid reinitializing on every search

5. **LRUCache** (`cache.py`) - In-memory caching
   - Thread-safe implementation using RLock for concurrent access
   - Separate caches: `knowledge_cache` (256 entries) and `search_cache` (1024 entries)
   - Tracks hits/misses for statistics

6. **CLI** (`cli.py`) - Rich terminal interface
   - Two modes: interactive (REPL) and single-query
   - Markdown rendering for agent responses
   - Special commands: reset, help, quit/exit, cache-stats

### Function Calling Architecture

The agent uses OpenAI's function calling with two tools defined in `prompts.py`:

1. **query_knowledge** - Query local knowledge base
   - Parameters: category (mechanics/strategy/nations/resources), subcategory (optional)
   - Executed by `EU5Agent._query_knowledge()`

2. **web_search** - Search web via Tavily API
   - Parameters: query (string), num_results (default 3)
   - Executed by `EU5Agent._web_search()`

**Agentic loop flow:**
1. User message added to conversation history
2. OpenAI API called with tools available
3. If assistant requests tool calls, execute them and add results to history
4. Loop continues until assistant returns final response or max_iterations (10) reached

### Knowledge Base Structure

```
eu5_agent/knowledge/
├── mechanics/         # 9 files covering 8 main EU5 game panels
│   ├── economy_mechanics.md
│   ├── government_mechanics.md
│   ├── production_mechanics.md
│   ├── society_mechanics.md
│   ├── diplomacy_mechanics.md
│   ├── military_mechanics.md
│   ├── warfare_mechanics.md
│   ├── geopolitics_mechanics.md
│   └── advances_mechanics.md
├── strategy/          # Beginner guides
│   ├── beginner_route.md
│   └── common_mistakes.md
├── nations/           # Nation-specific opening strategies
│   └── nation_england.md
└── resources/         # External links
    └── eu5_resources.md
```

**Knowledge retrieval pattern:**
- Files are loaded on demand (not at startup)
- Results are cached with key format: `knowledge:{resolved_path}:{category}:{subcategory}`
- Path is included in cache key to prevent stale content when multiple knowledge bases are used

### Testing Architecture

**Fixtures** (`tests/conftest.py`):
- `mock_openai_response` - Creates mock OpenAI API responses
- `temp_knowledge_base` - Temporary knowledge base with sample files
- `clean_env` / `mock_env` - Environment variable management
- `sample_tool_call` - Mock tool call objects
- `reset_config_singleton` - Autouse fixture that resets config singleton between tests

**Test organization:**
- Unit tests: `test_*_unit.py` - Pure unit tests with mocks
- Integration tests: `test_openai_integration.py` - Real API calls (marked with `@pytest.mark.openai_integration`)
- Legacy tests: `test_agent.py`, `test_openai_api.py` - Kept for compatibility

**Pytest markers:**
- `openai_integration` - Tests that make real OpenAI API calls (auto-skip if OPENAI_API_KEY not set)

### Configuration Hierarchy

1. **Direct parameters** (highest priority) - Passed to `EU5Agent(api_key=..., model=...)`
2. **Environment variables** - `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL`, etc.
3. **.env file** - Loaded via python-dotenv if present
4. **Defaults** - `gpt-5-mini`, `https://api.openai.com/v1`

**Auto-detection:** If `EU5_KNOWLEDGE_PATH` is not set, knowledge base is auto-detected at `eu5_agent/knowledge/` (package-relative).

### Module Import Pattern

When running from within subdirectories, Python module discovery can fail. The recommended patterns:

```bash
# From repo root (recommended)
python -m eu5_agent.cli

# From within eu5_agent/ directory, set PYTHONPATH
PYTHONPATH=.. python -m eu5_agent.cli

# Using editable install (best for development)
pip install -e .
eu5-agent
```

This is documented in README.md under "Running locally" section.

## Important Implementation Notes

### Thread Safety
- `LRUCache` uses `threading.RLock()` for thread-safe concurrent access
- All cache operations (get/set/clear/stats) are protected by the lock

### Model-Specific Behavior
- **gpt-5 models:** Don't support `temperature` parameter, use `max_completion_tokens` instead of `max_tokens`
- Detection in `EU5Config._check_temperature_support()` and `_check_max_completion_tokens()`
- Currently the code doesn't actually use these checks in API calls (opportunity for improvement)

### Caching Strategy
- Knowledge cache includes full resolved path to prevent stale content across multiple knowledge bases
- Search cache key excludes API key (security: avoid caching secrets)
- Caches are module-level singletons but can be cleared with `clear_all_caches()`

### Error Handling in Tools
- Tool execution uses defensive validation before calling functions
- Invalid arguments return error strings rather than raising exceptions
- Web search returns empty list on errors (agent handles gracefully)

### Iteration Limit
- Agent loop has `max_iterations=10` to prevent infinite tool calling loops
- Typical queries need 2-4 iterations (web search + knowledge lookups need 6-8)
- If limit reached, agent returns helpful message suggesting user break down query

## Configuration Files

- `pyproject.toml` - Project metadata, dependencies, tool configs (black, ruff, mypy, pytest)
- `.env.example` - Example environment configuration (user copies to `.env`)
- `requirements.txt` - Pinned dependencies for reproducible installs

## Console Script Entry Point

Defined in `pyproject.toml`:
```toml
[project.scripts]
eu5-agent = "eu5_agent.cli:main"
```

Available after `pip install -e .`
