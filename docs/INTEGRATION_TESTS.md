# Integration Tests for OpenAI API

This document describes the integration tests for OpenAI API interactions in the EU5 Strategy Agent.

## Overview

The integration tests (`tests/test_openai_integration.py`) make real OpenAI API calls to verify:

1. **Basic Chat Completion** - Minimal prompt with content and usage assertions
2. **Tool Call Handshake** - Model correctly handles tool definitions and returns tool_calls
3. **Error Handling** - Invalid models and token limits are handled properly

## Running Integration Tests

### Prerequisites

You need a valid OpenAI API key. Get one from [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### Environment Variables

Set these environment variables before running integration tests:

```bash
# Required
export OPENAI_API_KEY=your-api-key-here

# Optional (with defaults)
export OPENAI_MODEL=gpt-5-mini
export OPENAI_BASE_URL=https://api.openai.com/v1
```

### Running Tests

**Run only integration tests:**

```bash
pytest -m openai_integration
```

**Run all tests (unit + integration):**

```bash
pytest
```

**Skip integration tests (run only unit tests):**

```bash
pytest -m "not openai_integration"
```

**Run specific integration test:**

```bash
pytest tests/test_openai_integration.py::TestOpenAIChatCompletion::test_basic_chat_completion -v
```

## Test Details

### Test Categories

#### 1. Chat Completion Tests (`TestOpenAIChatCompletion`)

- **`test_basic_chat_completion`** - Verifies:
  - Response contains non-empty content
  - Usage information is present (prompt_tokens, completion_tokens, total_tokens)
  - Response completes successfully
  
- **`test_chat_completion_with_system_message`** - Verifies:
  - System message is processed correctly
  - Response is relevant to the system context

#### 2. Tool Calling Tests (`TestOpenAIToolCalling`)

- **`test_tool_call_handshake`** - Verifies:
  - Model returns tool_calls when appropriate tools are defined
  - Response structure is valid
  - Tool arguments are properly formatted
  
- **`test_tool_call_with_query_knowledge_tool`** - Verifies:
  - Model can handle custom EU5-specific tool definitions
  - Tool parameters are validated

#### 3. Error Handling Tests (`TestOpenAIErrorHandling`)

- **`test_invalid_model_handling`** - Verifies:
  - API returns appropriate error for invalid model names
  
- **`test_max_tokens_limit`** - Verifies:
  - Response respects max_completion_tokens limit
  - finish_reason indicates if response was truncated

## Cost Considerations

Integration tests are designed to minimize API costs:

- **Max tokens per test**: ≤ 50 completion tokens
- **Single-turn interactions**: No multi-turn conversations
- **Minimal prompts**: Short, simple test prompts
- **Estimated cost**: < $0.01 per full test run (6 tests)

With gpt-5-mini:
- Input: ~$0.10 per 1M tokens
- Output: ~$0.40 per 1M tokens
- 6 tests × ~100 tokens each = ~600 tokens ≈ $0.0003

## Skipping Tests

Tests automatically skip when `OPENAI_API_KEY` is not set:

```bash
# These will be skipped without the API key
pytest tests/test_openai_integration.py -v
```

Output:
```
tests/test_openai_integration.py::TestOpenAIChatCompletion::test_basic_chat_completion SKIPPED
tests/test_openai_integration.py::TestOpenAIChatCompletion::test_chat_completion_with_system_message SKIPPED
...
6 skipped in 0.53s
```

## Using Alternative Providers

The tests work with any OpenAI-compatible API. Set `OPENAI_BASE_URL` to use alternative providers:

### Groq (Free)

```bash
export OPENAI_API_KEY=your-groq-api-key
export OPENAI_BASE_URL=https://api.groq.com/openai/v1
export OPENAI_MODEL=llama-3.1-8b-instant
pytest -m openai_integration
```

### Google AI Studio (Free)

```bash
export OPENAI_API_KEY=your-google-api-key
export OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
export OPENAI_MODEL=gemini-2.5-flash
pytest -m openai_integration
```

### OpenRouter

```bash
export OPENAI_API_KEY=your-openrouter-api-key
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
export OPENAI_MODEL=meta-llama/llama-3.3-70b-instruct
pytest -m openai_integration
```

**Note:** Some tests (like `test_invalid_model_handling`) may behave differently with alternative providers.

## Troubleshooting

### Tests are skipped

**Problem:** All integration tests show as "SKIPPED"

**Solution:** Set the `OPENAI_API_KEY` environment variable:
```bash
export OPENAI_API_KEY=your-api-key-here
pytest -m openai_integration
```

### Authentication errors

**Problem:** `401 Unauthorized` or `Invalid API key`

**Solution:**
1. Verify your API key is correct
2. Check if the key has been revoked at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
3. Ensure the key has not expired

### Model not found errors

**Problem:** `404 Model not found`

**Solution:**
1. Check if the model name is correct (`OPENAI_MODEL`)
2. Verify your account has access to the model
3. Try with a different model (e.g., `gpt-4o`, `gpt-4o-mini`)

### Rate limit errors

**Problem:** `429 Rate limit exceeded`

**Solution:**
1. Wait a moment before running tests again
2. Check your API usage quota
3. Use a different API key if available

## CI/CD Integration

In CI/CD pipelines, integration tests can be:

1. **Skipped by default** (recommended):
   ```yaml
   - run: pytest -m "not openai_integration"
   ```

2. **Run only when API key is available**:
   ```yaml
   - run: pytest
     env:
       OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
   ```

3. **Run on schedule** (e.g., nightly):
   ```yaml
   - cron: '0 0 * * *'  # Daily at midnight
   ```

## Contributing

When adding new integration tests:

1. Mark tests with `@pytest.mark.openai_integration`
2. Use the `openai_client` and `openai_model` fixtures
3. Keep `max_completion_tokens ≤ 50`
4. Add skip behavior when API key is missing
5. Document expected behavior in docstrings
6. Consider cost impact (prefer single-turn interactions)

Example:

```python
@pytest.mark.openai_integration
def test_new_feature(openai_client, openai_model):
    """
    Test new OpenAI feature.
    
    Verifies:
    - Feature works as expected
    - Response is valid
    """
    response = openai_client.chat.completions.create(
        model=openai_model,
        messages=[{"role": "user", "content": "test"}],
        max_completion_tokens=50,
    )
    
    assert response.choices[0].message.content
    # Add your assertions here
```

## References

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [pytest markers documentation](https://docs.pytest.org/en/stable/how-to/mark.html)
- [EU5 Strategy Agent Configuration Guide](CONFIGURATION.md)
