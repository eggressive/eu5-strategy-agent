# EU5 Standalone Agent - Configuration Guide

Complete guide to configuring the EU5 Standalone Strategy Agent.

## Quick Start

The **simplest** way to get started:

```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit and add your OpenAI API key
nano .env  # Change "your-openai-api-key-here" to your actual key

# 3. Run the agent
python run_eu5_standalone.py
```

That's it! The agent will automatically load your configuration from the `.env` file.

## Three Configuration Methods

The agent supports three ways to configure settings, in **priority order**:

### 1. Direct Parameters (Highest Priority)

When creating an agent programmatically:

```python
from eu5_standalone.agent import EU5Agent

agent = EU5Agent(
    api_key="sk-proj-your-key-here",
    model="gpt-5-mini",
    knowledge_path="/path/to/knowledge"
)
```

**Use when:** Writing custom scripts or integrating with other tools.

### 2. Environment Variables (Medium Priority)

Set environment variables in your shell:

```bash
export OPENAI_API_KEY='sk-proj-your-key-here'
export OPENAI_MODEL='gpt-5-mini'
export EU5_KNOWLEDGE_PATH='/home/dimitar/ai/eu5_agent'

python run_eu5_standalone.py
```

**Use when:** Running in production, Docker containers, or CI/CD pipelines.

### 3. .env File (Lowest Priority, but Recommended for Dev)

Create a `.env` file in the `openmanus/` directory:

```bash
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-5-mini
EU5_KNOWLEDGE_PATH=/home/dimitar/ai/eu5_agent
```

The agent automatically loads this file if `python-dotenv` is installed.

**Use when:** Local development, testing, or personal use.

## All Configuration Options

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | **Yes** | None | Your OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-5-mini` | Model to use |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | API endpoint |
| `EU5_KNOWLEDGE_PATH` | No | `/home/dimitar/ai/eu5_agent` | Knowledge base path |

### Getting an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-`)
5. Set it in your `.env` file or environment

## Model Selection

### gpt-5-mini (Recommended)

**Best for:** Most users, fast responses, cost-effective

```bash
OPENAI_MODEL=gpt-5-mini
```

**Characteristics:**
- ✅ Fast (2-3 second responses)
- ✅ Cost-effective
- ✅ Good quality for strategy advice
- ⚠️ Does NOT support `temperature` parameter
- ⚠️ Uses `max_completion_tokens` (not `max_tokens`)

The agent automatically handles these parameter differences.

**Cost:** ~$0.10 per 1M input tokens, ~$0.40 per 1M output tokens

### gpt-5

**Best for:** Complex analysis, multiple scenarios, advanced players

```bash
OPENAI_MODEL=gpt-5
```

**Characteristics:**
- ✅ Higher quality responses
- ✅ Better at complex strategic reasoning
- ✅ More detailed analysis
- ✗ More expensive (3-5x cost)
- Same parameter constraints as gpt-5-mini

### gpt-4o / gpt-4-turbo

**Best for:** Users with existing gpt-4 workflows

```bash
OPENAI_MODEL=gpt-4o
# or
OPENAI_MODEL=gpt-4-turbo
```

**Characteristics:**
- ✅ Previous generation, still good quality
- ✅ Supports all standard OpenAI parameters
- ⚠️ May be slower than gpt-5 models
- ⚠️ More expensive than gpt-5-mini

## Configuration Examples

### Example 1: Local Development

```bash
# .env file
OPENAI_API_KEY=sk-proj-abc123...
OPENAI_MODEL=gpt-5-mini
EU5_KNOWLEDGE_PATH=/home/user/eu5_agent
```

### Example 2: Production Server

```bash
# In your deployment script or systemd service
export OPENAI_API_KEY='sk-proj-xyz789...'
export OPENAI_MODEL='gpt-5-mini'
export EU5_KNOWLEDGE_PATH='/opt/eu5_agent'

# Run the agent
python run_eu5_standalone.py
```

### Example 3: Docker Container

```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements_standalone.txt .
RUN pip install -r requirements_standalone.txt

COPY eu5_standalone/ ./eu5_standalone/
COPY run_eu5_standalone.py .

# Set configuration
ENV OPENAI_API_KEY=sk-proj-...
ENV OPENAI_MODEL=gpt-5-mini
ENV EU5_KNOWLEDGE_PATH=/app/knowledge

CMD ["python", "run_eu5_standalone.py"]
```

### Example 4: Testing Different Models

```bash
# Test with gpt-5-mini
OPENAI_MODEL=gpt-5-mini python run_eu5_standalone.py --query "How do estates work?"

# Test with gpt-5 (more detailed)
OPENAI_MODEL=gpt-5 python run_eu5_standalone.py --query "How do estates work?"

# Test with gpt-4o (previous generation)
OPENAI_MODEL=gpt-4o python run_eu5_standalone.py --query "How do estates work?"
```

## Troubleshooting

### Error: "OPENAI_API_KEY not set"

**Problem:** The agent can't find your API key.

**Solutions:**
1. Check that `.env` file exists: `ls -la .env`
2. Check that API key is set: `echo $OPENAI_API_KEY`
3. Make sure `python-dotenv` is installed: `pip install python-dotenv`
4. Try setting environment variable directly: `export OPENAI_API_KEY='your-key'`

### Error: "Invalid API key"

**Problem:** The API key is incorrect or expired.

**Solutions:**
1. Verify key at https://platform.openai.com/api-keys
2. Check for typos (keys are case-sensitive)
3. Generate a new key if needed
4. Make sure key starts with `sk-proj-` or `sk-`

### Error: "Knowledge base not found"

**Problem:** The agent can't find the EU5 knowledge files.

**Solutions:**
1. Check that knowledge path exists: `ls -la /home/dimitar/ai/eu5_agent`
2. Set correct path: `export EU5_KNOWLEDGE_PATH='/correct/path'`
3. Verify files exist: `ls /home/dimitar/ai/eu5_agent/*.md`

### Error: "Unsupported parameter: temperature"

**Problem:** Using gpt-5-mini with explicit temperature parameter.

**Solution:** This should be handled automatically. If you see this error:
1. Update to latest agent code
2. Don't manually set temperature in API calls
3. Let the agent handle model-specific parameters

### Error: "Model not found"

**Problem:** The specified model doesn't exist or isn't available.

**Solutions:**
1. Check model name spelling: `gpt-5-mini` not `gpt5-mini`
2. Verify model access at https://platform.openai.com/docs/models
3. Try default: `unset OPENAI_MODEL` (uses gpt-5-mini)

## Testing Configuration

Test that your configuration is working:

```bash
# Test the config module
python eu5_standalone/config.py

# Test the full agent
python test_agent_full.py

# Test with a real query
python run_eu5_standalone.py --query "How do estates work?" --verbose
```

## Advanced: Custom Configuration

For advanced use cases, you can create a custom configuration:

```python
from eu5_standalone.config import EU5Config
from eu5_standalone.agent import EU5Agent

# Create custom config
config = EU5Config()
config.api_key = "sk-proj-custom-key"
config.model = "gpt-5"
config.knowledge_path = "/custom/path"

# Validate
is_valid, error = config.validate()
if not is_valid:
    print(f"Config error: {error}")
    exit(1)

# Use with agent
agent = EU5Agent(config=config)
response = agent.chat("Your question here")
```

## Best Practices

1. **Never commit API keys to git**
   - Add `.env` to `.gitignore`
   - Use `.env.example` for documentation

2. **Use .env for local development**
   - Easy to manage
   - Keeps secrets out of code
   - Works automatically

3. **Use environment variables for production**
   - More secure
   - Better for containers/servers
   - Standard practice

4. **Start with gpt-5-mini**
   - Fast and cheap
   - Good enough for most use cases
   - Upgrade to gpt-5 if you need better quality

5. **Test configuration before deployment**
   - Run `test_agent_full.py`
   - Try a simple query
   - Check verbose output

## Security Notes

- **Never share your API key** - it can be used to charge your account
- **Rotate keys regularly** - generate new keys every few months
- **Monitor usage** - check https://platform.openai.com/usage for unexpected charges
- **Use separate keys** - development vs production
- **Set spending limits** - configure at https://platform.openai.com/account/billing/limits

## Support

If you're still having configuration issues:

1. Run the test suite: `python test_standalone.py`
2. Check verbose output: `--verbose` flag
3. Review logs for error messages
4. Verify all files exist: `ls eu5_standalone/`
5. Check OpenAI status: https://status.openai.com/

For more help, see:
- Main README: `README_STANDALONE.md`
- OpenAI Docs: https://platform.openai.com/docs
- EU5 Agent Repo: (your repository link)
