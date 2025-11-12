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
python run_agent.py
```

That's it! The agent will automatically load your configuration from the `.env` file.

## Three Configuration Methods

The agent supports three ways to configure settings:

### 1. Environment Variables

Set environment variables in your shell:

```bash
export OPENAI_API_KEY='sk-proj-your-key-here'
export OPENAI_MODEL='gpt-5-mini'
export EU5_KNOWLEDGE_PATH='/path/to/eu5_agent'

python run_agent.py
```

### 2. .env File

Create a `.env` file in the project root directory:

```bash
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-5-mini
EU5_KNOWLEDGE_PATH=/path/to/eu5_agent
```

The agent automatically loads this file if `python-dotenv` is installed.

**Use when:** Local development, testing, or personal use.

### 3. Direct Parameters

When creating an agent programmatically:

```python
from eu5_agent.agent import EU5Agent

agent = EU5Agent(
    api_key="sk-proj-your-key-here",
    model="gpt-5-mini",
    knowledge_path="/path/to/knowledge"
)
```

**Use when:** Writing custom scripts or integrating with other tools.

## All Configuration Options

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | **Yes** | None | Your OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-5-mini` | Model to use |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | API endpoint |
| `EU5_KNOWLEDGE_PATH` | No | Repository's `knowledge/` directory | Knowledge base path |
| `TAVILY_API_KEY` | No | None | Tavily API key for web search (optional) |

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

- Fast (2-3 second responses)
- Cost-effective
- Good quality for strategy advice
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

- Higher quality responses
- Better at complex strategic reasoning
- More detailed analysis
- ⚠️ More expensive (3-5x cost)
- Same parameter constraints as gpt-5-mini

### gpt-4o / gpt-4-turbo

**Best for:** Users with existing gpt-4 workflows

```bash
OPENAI_MODEL=gpt-4o
# or
OPENAI_MODEL=gpt-4-turbo
```

**Characteristics:**

- Previous generation, still good quality
- Supports all standard OpenAI parameters
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

### Example 2: Environment Variables

```bash
# In your shell, deployment script or systemd service
export OPENAI_API_KEY='sk-proj-xyz789...'
export OPENAI_MODEL='gpt-5-mini'
export EU5_KNOWLEDGE_PATH='/opt/eu5_agent'

# Run the agent
python run_agent.py
```

### Example 3: Docker Container

```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY eu5_agent/ ./eu5_agent/
COPY run_agent.py .

# Set configuration
ENV OPENAI_API_KEY=sk-proj-...
ENV OPENAI_MODEL=gpt-5-mini
ENV EU5_KNOWLEDGE_PATH=/app/knowledge

CMD ["python", "run_agent.py"]
```

### Example 4: Testing Different Models

```bash
# Test with gpt-5-mini
OPENAI_MODEL=gpt-5-mini python run_agent.py --query "How do estates work?"

# Test with gpt-5 (more detailed)
OPENAI_MODEL=gpt-5 python run_agent.py --query "How do estates work?"

# Test with gpt-4o (previous generation)
OPENAI_MODEL=gpt-4o python run_agent.py --query "How do estates work?"
```

## Alternative LLM Providers

The agent supports **OpenAI-compatible API providers**, allowing you to use free or
cheaper alternatives by changing `OPENAI_BASE_URL` and `OPENAI_API_KEY`.

### Requirements

All providers must support:

- **OpenAI Chat Completions API** format
- **Function calling** (for knowledge base + web search tools)

Most modern LLMs meet these requirements through OpenAI-compatible endpoints.

### Groq (FREE - 14,400 requests/day)

**Best for:** Free usage, ultra-fast inference

**Setup:**

```bash
# .env file
OPENAI_API_KEY=gsk_your_groq_api_key_here
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-8b-instant
```

**Get API Key:** https://console.groq.com/

**Available Models:**

- `llama-3.1-8b-instant` - Fast, good quality
- `llama-3.1-70b-versatile` - Best quality
- `mixtral-8x7b-32768` - Large context window
- `gemma2-9b-it` - Google's Gemma model

**Free Tier:** 14,400 requests/day, 30 requests/minute

**Pros:**

- Completely free
- Ultra-fast (LPU hardware)
- Reliable function calling

**Cons:**

- ⚠️ Rate limits
- ⚠️ Smaller models than GPT-4

### Google AI Studio (FREE - 1M tokens/minute)

**Best for:** Massive free tier, Google's latest models

**Setup:**

```bash
# .env file
OPENAI_API_KEY=your_google_api_key_here
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_MODEL=gemini-2.5-flash
```

**Get API Key:** https://aistudio.google.com/apikey

**Available Models:**

- `gemini-2.5-flash` - Fast, excellent quality
- `gemini-1.5-pro` - Highest quality
- `gemini-1.5-flash` - Previous generation

**Free Tier:** 1M tokens per minute (extremely generous)

**Pros:**

- Massive free tier
- Latest Gemini models
- Excellent quality

**Cons:**

- ⚠️ Newer provider, less battle-tested

### OpenRouter (FREE models + paid access to 300+)

**Best for:** Model variety, accessing multiple providers

**Setup:**

```bash
# .env file
OPENAI_API_KEY=sk-or-v1-your_openrouter_key_here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=meta-llama/llama-3.3-70b-instruct
```

**Get API Key:** https://openrouter.ai/keys

**Free Models:**

- `meta-llama/llama-3.3-70b-instruct` - Excellent quality, completely free
- `google/gemini-2.0-flash-exp:free` - Google's latest
- `mistralai/mistral-7b-instruct:free` - Fast, lightweight

**Paid Access:**

- GPT-4, Claude, Gemini Pro, and 300+ other models
- Pay-per-use pricing

**Pros:**

- Access to many providers
- Some completely free models
- Fallback/routing options

**Cons:**

- ⚠️ Free models have rate limits
- ⚠️ Quality varies by model

### Together.ai (Free $25 trial)

**Best for:** Cost-effective paid option

**Setup:**

```bash
# .env file
OPENAI_API_KEY=your_together_api_key_here
OPENAI_BASE_URL=https://api.together.xyz/v1
OPENAI_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
```

**Get API Key:** https://api.together.ai/settings/api-keys

**Popular Models:**

- `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` - Fast, cheap
- `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo` - High quality
- `mistralai/Mixtral-8x7B-Instruct-v0.1` - Great balance

**Pricing:** ~$0.20-0.60 per 1M tokens (cheaper than OpenAI)

**Pros:**

- Free $25 trial
- Cheaper than OpenAI
- Many model options

**Cons:**

- ⚠️ Requires payment after trial

### DeepInfra (Free tier available)

**Best for:** Open-source models

**Setup:**

```bash
# .env file
OPENAI_API_KEY=your_deepinfra_api_key_here
OPENAI_BASE_URL=https://api.deepinfra.com/v1/openai
OPENAI_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct
```

**Get API Key:** https://deepinfra.com/dash/api_keys

**Available Models:**

- Many Llama, Mistral, Qwen models
- Free tier available

**Pros:**

- Free tier
- Many open models

**Cons:**

- ⚠️ Documentation less comprehensive

### Provider Cost Comparison

| Provider | Best Model | Cost (1M tokens) | Free Tier | Speed |
|----------|-----------|------------------|-----------|-------|
| OpenAI | gpt-5-mini | $0.10-0.40 | No | Fast |
| OpenAI | gpt-4o-mini | $0.15-0.60 | No | Fast |
| Groq | llama-3.1-70b | FREE | 14.4K req/day | Ultra-fast |
| Google AI | gemini-2.5-flash | FREE | 1M TPM | Fast |
| OpenRouter | llama-3.3-70b | FREE | Yes | Medium |
| Together.ai | llama-3.1-70b | $0.88 | $25 trial | Fast |

### Testing Alternative Providers

After configuring an alternative provider, test it:

```bash
# Test with verbose output
python run_agent.py --query "How do estates work?" --verbose

# Test function calling
python run_agent.py --query "What are common beginner mistakes?"

# Check response quality
python run_agent.py --query "Explain the market system in EU5"
```

### Function Calling Compatibility

All providers listed above support OpenAI-style function calling, but quality
varies:

**Excellent:**

- OpenAI (GPT-4, GPT-5)
- Google AI Studio (Gemini 2.5)
- Groq (Llama 3.1 70B)

**Good:**

- OpenRouter (depends on model)
- Together.ai (Llama 3.1)

**Test before use** - try a few queries with each provider to verify
function calling works reliably.

### Switching Between Providers

You can easily switch providers by changing environment variables:

```bash
# Use OpenAI
export OPENAI_API_KEY=sk-proj-...
export OPENAI_BASE_URL=https://api.openai.com/v1
export OPENAI_MODEL=gpt-5-mini

# Switch to Groq (free)
export OPENAI_API_KEY=gsk_...
export OPENAI_BASE_URL=https://api.groq.com/openai/v1
export OPENAI_MODEL=llama-3.1-70b-versatile

# Switch to Google AI Studio (free)
export OPENAI_API_KEY=AIza...
export OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
export OPENAI_MODEL=gemini-2.5-flash
```

Or create multiple `.env` files:

```bash
# .env.openai
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-5-mini

# .env.groq
OPENAI_API_KEY=gsk_...
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-70b-versatile

# Use specific config
cp .env.groq .env && python run_agent.py
```

## Web Search Configuration (Optional)

The agent can use **Tavily API** for web search when the local knowledge
base doesn't have the information needed. This is **completely optional** -
the agent works perfectly with just the 13 knowledge base files included in
the repository.

### Why Tavily?

Tavily is an AI-optimized search API specifically designed for LLM agents:

- **AI-Optimized Results** - Returns clean text, no HTML parsing needed
- **Domain Filtering** - Prioritizes `eu5.paradoxwikis.com` automatically
- **No Rate Limiting** - Official API, no scraping blocks
- **Fast** - Single API call vs. multiple HTTP requests
- **Free Tier** - 1000 searches per month (generous for most users)

**Previous Implementation:** Used `googlesearch-python` which was rate-limited
and unreliable. Replaced with Tavily in this version.

### Setup (Optional)

**1. Get FREE Tavily API Key:**

Visit: [tavily.com](https://tavily.com/)

- Sign up for free account
- Get API key from dashboard
- Free tier: 1000 searches/month

**2. Add to `.env` file:**

```bash
# Web Search (Optional)
TAVILY_API_KEY=tvly-your-api-key-here
```

**3. Test web search:**

```bash
# Query for content not in knowledge base
python run_agent.py --query "What's France's opening strategy?" --verbose

# Should see web_search tool calls returning wiki results
```

### How It Works

When you query about content not in the local knowledge base:

**Without Tavily:**
```
User: "What's France's opening strategy?"
Agent: → query_knowledge(nations)
       → No France guide found
       → web_search returns "No results"
       → Synthesizes response from general mechanics knowledge
```

**With Tavily:**
```
User: "What's France's opening strategy?"
Agent: → query_knowledge(nations)
       → No France guide found
       → web_search fetches EU5 wiki results
       → Synthesizes comprehensive response from wiki + mechanics
```

### Domain Prioritization

Tavily automatically prioritizes these domains in search results:

- `eu5.paradoxwikis.com` (official wiki)
- `europauniversalisv.wiki` (community wiki)

This ensures high-quality, relevant results for EU5 strategy questions.

### Free Tier Limits

- **1000 searches per month**
- **Resets monthly**
- **No credit card required**

For typical usage (5-10 searches per day), the free tier is more than
sufficient. Heavy users might hit limits toward end of month.

### Without Tavily

The agent functions normally without Tavily configuration:

- All knowledge base queries work perfectly
- England, economy, military, etc. queries fully supported
- ⚠️ Queries outside knowledge base won't have web search fallback
- ⚠️ Agent will synthesize answers from available mechanics knowledge

**Example:** "France opening strategy" without Tavily will give general
opening strategy advice based on mechanics (diplomacy, military, economy)
but won't have France-specific wiki content.

### Troubleshooting Tavily

**No results from web search:**

1. Check API key is set: `echo $TAVILY_API_KEY`
2. Verify API key is valid at [tavily.com](https://tavily.com/)
3. Check free tier quota hasn't been exceeded
4. Test with simple query first

**"Warning: tavily-python not installed":**

```bash
pip install tavily-python
```

**Rate limiting:**

If you exceed 1000 searches/month, web search will stop working until the
monthly reset. The agent will continue to work with local knowledge base only.

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

1. Check that knowledge path exists: `ls -la /path/to/eu5_agent`
2. Set correct path: `export EU5_KNOWLEDGE_PATH='/correct/path'`
3. Verify files exist: `ls /path/to/eu5_agent/*.md`

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
python eu5_agent/config.py

# Test the full agent
python test_agent_full.py

# Test with a real query
python run_agent.py --query "How do estates work?" --verbose
```

## Advanced: Custom Configuration

For advanced use cases, you can create a custom configuration:

```python
import sys
from eu5_agent.config import EU5Config
from eu5_agent.agent import EU5Agent

# Create custom config
config = EU5Config()
config.api_key = "sk-proj-custom-key"
config.model = "gpt-5"
config.knowledge_path = "/custom/path"

# Validate
is_valid, error = config.validate()
if not is_valid:
    print(f"Config error: {error}")
    sys.exit(1)

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
4. Verify all files exist: `ls eu5_agent/`
5. Check OpenAI status: https://status.openai.com/

For more help, see:
- Main README: `README_STANDALONE.md`
- OpenAI Docs: https://platform.openai.com/docs
- EU5 Agent Repo: (your repository link)
