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
- [ ] Improve search capabilities (semantic search vs. direct file loading)
- [ ] Add conversation history export/import
- [ ] Implement rate limiting handling for web search
- [ ] Add support for custom knowledge base paths (currently hardcoded)

## Medium Priority

### Architecture Improvements

- [ ] Add async support for concurrent operations
- [ ] Implement proper logging system
- [ ] Add configuration validation
- [ ] Make knowledge base path configurable via environment variable

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
- [ ] Address web search rate limiting issues as they occur
- [ ] Keep dependencies up to date
