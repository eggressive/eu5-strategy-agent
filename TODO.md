# TODO

This document tracks planned enhancements and features for the EU5 Strategy Agent.

## TIER 1 - Quality & Reliability

### Agent Reliability

- [x] Harden tool-call argument parsing so malformed JSON from the model surfaces as a graceful error instead of crashing the chat loop.

### Testing Infrastructure

- [x] Add unit tests for core agent functionality
- [ ] Add integration tests for OpenAI API interactions
- [x] Add tests for knowledge base loading
- [x] Add tests for web search fallback
- [ ] Migrate from manual test scripts to pytest test suite

### Configuration Validation

- [ ] Align `EU5Config.validate()` with knowledge path auto-detection (don’t fail validation when path is omitted; use the same resolution logic).
- [ ] Add configuration validation before agent starts
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

## TIER 3 - User Experience

**Rationale**: Improve usability for end users (your son and others).

### Conversation Management

- [ ] Add conversation history export/import
- [ ] Save conversation sessions to disk
- [ ] Resume previous conversations
- [ ] Add conversation search/filtering

### Performance Improvements

- [ ] Add async support for concurrent operations
- [ ] Parallelize knowledge base queries
- [ ] Improve response time for complex queries

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
