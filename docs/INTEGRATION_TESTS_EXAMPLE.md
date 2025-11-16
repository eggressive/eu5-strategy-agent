# Integration Tests - Example Output

This document shows example output from running the OpenAI integration tests.

## Without API Key (Tests Skipped)

When `OPENAI_API_KEY` is not set, tests are automatically skipped:

```bash
$ pytest tests/test_openai_integration.py -v

================================================= test session starts ==================================================
collected 6 items

tests/test_openai_integration.py::TestOpenAIChatCompletion::test_basic_chat_completion SKIPPED (OPENAI_API_KEY...) [ 16%]
tests/test_openai_integration.py::TestOpenAIChatCompletion::test_chat_completion_with_system_message SKIPPED      [ 33%]
tests/test_openai_integration.py::TestOpenAIToolCalling::test_tool_call_handshake SKIPPED (OPENAI_API_KEY env...) [ 50%]
tests/test_openai_integration.py::TestOpenAIToolCalling::test_tool_call_with_query_knowledge_tool SKIPPED (OP...) [ 66%]
tests/test_openai_integration.py::TestOpenAIErrorHandling::test_invalid_model_handling SKIPPED (OPENAI_API_KE...) [ 83%]
tests/test_openai_integration.py::TestOpenAIErrorHandling::test_max_tokens_limit SKIPPED (OPENAI_API_KEY envi...) [100%]

================================================== 6 skipped in 0.51s ==================================================
```

## With API Key (Tests Run)

When `OPENAI_API_KEY` is set, tests make real API calls:

```bash
$ export OPENAI_API_KEY=sk-your-key-here
$ export OPENAI_MODEL=gpt-5-mini
$ pytest tests/test_openai_integration.py -v

================================================= test session starts ==================================================
collected 6 items

tests/test_openai_integration.py::TestOpenAIChatCompletion::test_basic_chat_completion PASSED                    [ 16%]
tests/test_openai_integration.py::TestOpenAIChatCompletion::test_chat_completion_with_system_message PASSED      [ 33%]
tests/test_openai_integration.py::TestOpenAIToolCalling::test_tool_call_handshake PASSED                         [ 50%]
tests/test_openai_integration.py::TestOpenAIToolCalling::test_tool_call_with_query_knowledge_tool PASSED         [ 66%]
tests/test_openai_integration.py::TestOpenAIErrorHandling::test_invalid_model_handling PASSED                    [ 83%]
tests/test_openai_integration.py::TestOpenAIErrorHandling::test_max_tokens_limit PASSED                          [100%]

================================================== 6 passed in 3.24s ==================================================
```

## Test Details

### Test Coverage

The integration tests verify:

1. **Basic Chat Completion**
   - Response contains non-empty content
   - Usage metrics (prompt_tokens, completion_tokens, total_tokens) are present
   - Token counts are correct

2. **System Message Processing**
   - System messages are respected
   - Responses align with system context

3. **Tool Call Handshake**
   - Model returns tool_calls when tools are defined
   - Tool call structure is valid
   - Arguments are properly formatted JSON

4. **Custom Tool Definitions**
   - Model handles EU5-specific tools
   - Tool parameters are validated

5. **Error Handling**
   - Invalid model names raise appropriate errors
   - Token limits are respected
   - finish_reason indicates truncation

### Cost Analysis

Example run with gpt-5-mini:

```
Test: test_basic_chat_completion
  - Prompt tokens: 14
  - Completion tokens: 8
  - Total tokens: 22
  - Cost: ~$0.000003

Test: test_chat_completion_with_system_message
  - Prompt tokens: 18
  - Completion tokens: 12
  - Total tokens: 30
  - Cost: ~$0.000005

Test: test_tool_call_handshake
  - Prompt tokens: 89
  - Completion tokens: 17
  - Total tokens: 106
  - Cost: ~$0.000016

Test: test_tool_call_with_query_knowledge_tool
  - Prompt tokens: 71
  - Completion tokens: 15
  - Total tokens: 86
  - Cost: ~$0.000013

Test: test_invalid_model_handling
  - (Error - no tokens charged)

Test: test_max_tokens_limit
  - Prompt tokens: 15
  - Completion tokens: 10
  - Total tokens: 25
  - Cost: ~$0.000004

TOTAL ESTIMATED COST: ~$0.000041 (less than 0.01 cents)
```

## Filtering Tests

### Run only integration tests:

```bash
$ pytest -m openai_integration
collected 103 items / 97 deselected / 6 selected
# Runs only the 6 integration tests
```

### Skip integration tests (unit tests only):

```bash
$ pytest -m "not openai_integration"
collected 103 items / 6 deselected / 97 selected
# Runs 97 unit tests, skips 6 integration tests
```

### Run all tests:

```bash
$ pytest
collected 103 items
# Runs all 103 tests (integration tests skip without API key)
```

## Using Alternative Providers

### Groq (Free & Fast)

```bash
$ export OPENAI_API_KEY=gsk-your-groq-key
$ export OPENAI_BASE_URL=https://api.groq.com/openai/v1
$ export OPENAI_MODEL=llama-3.1-8b-instant
$ pytest -m openai_integration -v

================================================= test session starts ==================================================
tests/test_openai_integration.py::TestOpenAIChatCompletion::test_basic_chat_completion PASSED                    [ 16%]
tests/test_openai_integration.py::TestOpenAIChatCompletion::test_chat_completion_with_system_message PASSED      [ 33%]
tests/test_openai_integration.py::TestOpenAIToolCalling::test_tool_call_handshake PASSED                         [ 50%]
tests/test_openai_integration.py::TestOpenAIToolCalling::test_tool_call_with_query_knowledge_tool PASSED         [ 66%]
tests/test_openai_integration.py::TestOpenAIErrorHandling::test_invalid_model_handling PASSED                    [ 83%]
tests/test_openai_integration.py::TestOpenAIErrorHandling::test_max_tokens_limit PASSED                          [100%]

================================================== 6 passed in 1.12s ==================================================
```

**Note:** Groq is often faster than OpenAI (1.12s vs 3.24s in this example) and completely free!

## Continuous Integration

In CI/CD, tests can be configured to:

1. **Always skip** (default - no API key set):
   ```yaml
   - run: pytest
     # Integration tests automatically skipped
   ```

2. **Run with secret**:
   ```yaml
   - run: pytest -m openai_integration
     env:
       OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
   ```

3. **Skip explicitly**:
   ```yaml
   - run: pytest -m "not openai_integration"
     # Never runs integration tests
   ```

## Troubleshooting

### All tests skip

If you set the API key but tests still skip:

```bash
# Check if variable is actually set
$ echo $OPENAI_API_KEY
# Should show your key

# Try exporting it again
$ export OPENAI_API_KEY=your-key-here

# Run with verbose output
$ pytest tests/test_openai_integration.py -v -s
```

### Some tests fail

If `test_invalid_model_handling` fails:
- This is expected with some providers that don't validate model names
- The test can be skipped with: `pytest -m openai_integration -k "not invalid_model"`

If `test_tool_call_handshake` fails:
- Some models may not support tool calling
- Try with a different model that supports function calling

## Summary

The integration tests provide confidence that:
- ✅ OpenAI API credentials are valid
- ✅ The configured model is accessible
- ✅ Basic chat completion works
- ✅ Tool calling / function calling works
- ✅ Error handling is robust
- ✅ Token limits are respected

All while keeping costs minimal (< $0.01 per test run) and allowing tests to be easily skipped or filtered.
