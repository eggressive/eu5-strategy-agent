# TODO

This document tracks planned enhancements and features for the EU5 Strategy Agent.

## High Priority

### PyPI Publication

- [ ] Publish package to PyPI for `pip install eu5-strategy-agent`
- [ ] Test PyPI installation process
- [ ] Set up PyPI credentials and publishing workflow
- [ ] Update README with actual PyPI installation instructions

### Testing Infrastructure

- [ ] Add unit tests for core agent functionality
- [ ] Add integration tests for OpenAI API interactions
- [ ] Add tests for knowledge base loading
- [ ] Add tests for web search fallback
- [ ] Migrate from manual test scripts to pytest test suite

### Alternative LLM Providers

- [ ] Test Groq integration with function calling
- [ ] Test Google AI Studio (Gemini) integration
- [ ] Test OpenRouter with free models
- [ ] Document provider-specific quirks and limitations
- [ ] Create provider comparison examples in docs

### Features

- [ ] Implement caching mechanism for repeated queries
- [x] Improve search capabilities (replaced Google with Tavily AI-optimized search)
- [ ] Add conversation history export/import
- [ ] Test Tavily API with various query types and complexity levels
- [x] Add support for custom knowledge base paths (configurable via EU5_KNOWLEDGE_PATH)

## Medium Priority

### Architecture Improvements

- [ ] Add async support for concurrent operations
- [x] Implement proper logging system (added logging for verbose mode, warnings module for library warnings)
- [ ] Add configuration validation
- [x] Make knowledge base path configurable via environment variable (EU5_KNOWLEDGE_PATH)

### Nation Guides

- [ ] Create Ottomans opening strategy guide
- [ ] Create France opening strategy guide
- [ ] Create Castile opening strategy guide
- [ ] Create Portugal opening strategy guide

### Advanced Strategy Guides

- [ ] Colonial empire strategies
- [ ] Trade hegemony strategies
- [ ] Military conquest path guides
- [ ] Diplomatic victory strategies

### Additional Mechanics

- [ ] Verify religion mechanics coverage
- [ ] Verify culture mechanics coverage
- [ ] Verify exploration mechanics coverage
- [ ] Document any missing estate mechanics

## Low Priority

### CI/CD Pipeline

- [ ] Set up GitHub Actions workflow for testing
- [ ] Add automated linting (black, ruff, mypy)
- [ ] Add automated markdown linting
- [ ] Configure automated PyPI publishing on release

### Multiplayer Support

- [ ] Create multiplayer-specific strategy guides
- [ ] Document competitive play differences
- [ ] Add nation tier lists for multiplayer

### Local Model Support (Experimental)

- [ ] Test Ollama integration with function calling
- [ ] Test LM Studio compatibility
- [ ] Document local model setup guide
- [ ] Add fallback for models without function calling

## Maintenance

### Ongoing Tasks

- [ ] Track EU5 game patches and update mechanics files
- [ ] Monitor EU5 wiki for new content and strategies
- [ ] Update knowledge base as DLCs are released
- [x] Address web search rate limiting issues (replaced Google with Tavily API)
- [ ] Keep dependencies up to date

### Completed This Session

**Tavily Integration:**
- [x] Replace Google search with Tavily API (AI-optimized, no rate limits)
- [x] Increase agent max_iterations to 10 for complex web search queries
- [x] Add Tavily API key configuration and documentation
- [x] Test and verify meaningful responses with web search
- [x] Add Tavily client caching for performance optimization
- [x] Add API key format validation (tvly- prefix)
- [x] Extract query context prefixing into helper function (DRY)

**Code Quality & Best Practices:**
- [x] Fix PEP 8 import issues in cli.py (move load_dotenv to module level)
- [x] Document intentional redundant .env loading in cli.py
- [x] Replace print() with warnings.warn() in search.py (6 replacements)
- [x] Replace print() with logger.info() in agent.py (3 replacements)
- [x] Configure logging in CLI for verbose mode
- [x] Fix unconditional ellipsis in content truncation
- [x] Remove unreachable dead code in agent.py
- [x] Simplify redundant sort key in search.py

**Type Safety:**
- [x] Add proper OpenAI SDK type annotations (ChatCompletionMessageParam, ChatCompletionToolParam)
- [x] Use cast() for message type handling
- [x] Add type: ignore for incomplete tool_call stubs
- [x] Fix Tavily client cache type annotation (Dict[str, Any])

**Configuration Architecture:**
- [x] Fix tavily_api_key config inconsistency (pass through config instead of env direct access)
- [x] Add TAVILY_API_KEY to configuration table in docs

**Documentation:**
- [x] Update README.md with Tavily information
- [x] Update CONFIGURATION.md with comprehensive Tavily section
- [x] Fix all markdownlint errors in CONFIGURATION.md (MD013, MD034, MD031, MD040, MD032)
- [x] Fix incorrect script names (run_eu5_standalone.py → run_agent.py) across all docs
- [x] Fix incorrect package names (eu5_standalone → eu5_agent) in docs
- [x] Obfuscate username from paths in documentation
- [x] Document search_eu5_wiki_comprehensive as library API
- [x] Add __all__ export list to search.py

**Dependency Management:**
- [x] Update requirements.txt (remove 3 packages, add tavily-python)
- [x] Sync pyproject.toml dependencies with requirements.txt
- [x] Update .env.example with Tavily documentation
