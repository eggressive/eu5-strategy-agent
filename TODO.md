# TODO

This document tracks planned enhancements and features for the EU5 Strategy Agent.

## TIER 1 - Quality & Reliability

### Configuration Validation

- [ ] Align `EU5Config.validate()` with knowledge path auto-detection (don’t fail validation when path is omitted; use the same resolution logic).
  
  Note: `EU5Knowledge` auto-detects a packaged knowledge base when `EU5_KNOWLEDGE_PATH` is omitted — update `EU5Config.validate()` and its tests to use the same behavior (avoid failing validation when knowledge path is omitted).
- [ ] Add configuration validation before agent starts (call `EU5Config.validate()` during CLI and/or `EU5Agent` initialization and provide clear, actionable messages to users)
- [ ] Validate API keys exist and have correct format
- [ ] Check knowledge base path exists and is readable
- [ ] Verify model compatibility (function calling support)
- [ ] Provide clear error messages for misconfigurations

### Tavily Integration Testing

- [ ] Differentiate Tavily misconfiguration/missing API key from genuine zero-result searches to give clearer user feedback.
- [ ] Test Tavily API with various query types
- [ ] Test with different complexity levels
- [ ] Verify fallback behavior when Tavily fails
- [ ] Document optimal query patterns for Tavily
- [ ] Monitor API usage and rate limits

## TIER 2 - Cost Reduction

**Rationale**: OpenAI GPT-5 is expensive - alternative providers can significantly reduce costs.

### Alternative LLM Providers

- [ ] Test Groq integration (free tier, very fast)
- [ ] Test Google AI Studio (Gemini free tier)
- [ ] Test OpenRouter with free models
- [ ] Document provider-specific quirks and limitations
- [ ] Create provider comparison guide (cost, speed, quality)

### Performance Optimization

- [ ] Implement caching mechanism for repeated queries
- [ ] Cache knowledge base query results
- [ ] Add response memoization for identical questions
- [ ] Monitor and log cache hit rates
  
  Note: The code currently caches Tavily client instances, but it does not cache responses or provide memoization; adding an LRU or disk cache for knowledge/query results would reduce LLM/API cost and improve response time.

## TIER 3 - User Experience

**Rationale**: Improve usability for end users (your son and others).

### Conversation Management

- [ ] Add conversation history export/import
- [ ] Save conversation sessions to disk
- [ ] Resume previous conversations
- [ ] Add conversation search/filtering
  
  Note: The interactive mode supports conversation history in-memory but lacks persistence; saving to JSON or a small DB is recommended.

### Performance Improvements

- [ ] Add async support for concurrent operations
- [ ] Parallelize knowledge base queries
- [ ] Improve response time for complex queries
  
  Note: `pytest-asyncio` is included in dev dependencies, but repo code is largely synchronous; introducing async endpoints will enable parallelized knowledge/API usage.

## TIER 4 - Content Expansion

**Rationale**: Expand knowledge base once technical foundation is stable.

### High-Value Nation Guides

- [ ] Create Ottomans opening strategy guide
- [ ] Create France opening strategy guide
- [ ] Create Castile opening strategy guide
- [ ] Create Portugal opening strategy guide

### Missing Mechanics Verification

- [ ] Verify religion mechanics coverage
- [ ] Verify culture mechanics coverage
- [ ] Verify exploration mechanics coverage
- [ ] Document any missing estate mechanics

### Advanced Strategy Guides

- [ ] Colonial empire strategies
- [ ] Trade hegemony strategies
- [ ] Military conquest path guides
- [ ] Diplomatic victory strategies

## TIER 5 - Future Enhancements (Low Priority)

**Rationale**: Nice to have, but not critical for core functionality.

### CI/CD Pipeline

- [ ] Set up GitHub Actions workflow for testing
- [ ] Add automated linting (black, ruff, mypy)
- [ ] Add automated markdown linting

### Multiplayer Support

- [ ] Create multiplayer-specific strategy guides
- [ ] Document competitive play differences
- [ ] Add nation tier lists for multiplayer

### CLI & Help Text

- [ ] Fix CLI help/epilog to reference the correct module path (`eu5_agent.cli`) to avoid `ModuleNotFoundError`.
  
  Note: CLI examples currently mention `python -m eu5_standalone.cli`, which should be updated to `python -m eu5_agent.cli`.

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
- [ ] Keep dependencies up to date

### Completed This Session

#### Testing Infrastructure

- [x] Migrate from manual test scripts to pytest test suite

### Notes & Next Steps

- The repository already includes a strong pytest suite for agent functionality, knowledge loading, and web search. Suggested follow-ups:
  1. Update `EU5Config.validate()` to support knowledge auto-detection and adjust `tests/test_config_unit.py::TestConfigValidation` accordingly.
  2. Add clear differentiation for Tavily errors vs empty results (update `search_eu5_wiki()` to return structured status or an error type and update the agent behavior to show clearer messages).
  3. Implement request/response caching for knowledge retrieval and Tavily searches, with a cache hit metric and basic LRU memory/disk-backed cache.
  4. Add conversation export/import and CLI commands to save/restore sessions.
  5. Fix the CLI example paths to `eu5_agent.cli` and ensure help/epilog text is accurate.
