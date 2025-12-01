# EU5 Strategy Agent

## Lightweight, standalone strategy advisor for Europa Universalis 5

Get expert strategic guidance for EU5 using GPT-5-mini with a comprehensive
knowledge base covering all 8 main game panels.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Features

- **GPT-5-mini Powered** - Fast, cost-effective AI-driven strategy advice
- **Comprehensive Knowledge Base** - 13 curated files covering all 8 EU5
  game panels
- **Web Search Fallback** - Automatically searches for missing content
  (prioritizes eu5.paradoxwikis.com)
- **Beautiful CLI** - Rich terminal formatting with markdown rendering
- **Flexible Configuration** - Environment variables, .env files, or direct parameters
- **Fast Responses** - 2-3 second response times

## Quick Start

### Installation

**From Source:**

```bash
git clone https://github.com/eggressive/eu5-strategy-agent.git
cd eu5-strategy-agent
pip install -r requirements.txt
```

### Configuration

1. **Copy the example configuration:**

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API key:**

   ```bash
   OPENAI_API_KEY=your-api-key-here
   OPENAI_MODEL=gpt-5-mini
   ```

3. **Get an API key** from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Important Notes for gpt-5-mini

- Does NOT support `temperature` parameter (uses default=1.0)
- Uses `max_completion_tokens` instead of `max_tokens`
- The agent handles these differences automatically

### Supported Models

The agent works with **OpenAI models** and **OpenAI-compatible providers**:

#### OpenAI Models

| Model | Best For | Cost (per 1M tokens) | Speed |
|-------|----------|---------------------|-------|
| `gpt-5-mini` | Default choice | ~$0.10-0.40 | Fast |
| `gpt-4o-mini` | Best value | $0.15-0.60 | Fast |
| `gpt-4o` | Highest quality | $2.50-10.00 | Medium |
| `gpt-4-turbo` | Previous gen | $10-30 | Medium |
| `gpt-3.5-turbo` | Budget option | $0.50-1.50 | Very fast |

Simply change `OPENAI_MODEL` in your `.env` file.

#### Free & Cheap Alternatives

Use **free OpenAI-compatible providers** by changing `OPENAI_BASE_URL`:

**Groq (14,400 free requests/day, ultra-fast):**

```bash
OPENAI_API_KEY=your-groq-api-key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-8b-instant
```

**Google AI Studio (1M free tokens/minute):**

```bash
OPENAI_API_KEY=your-google-api-key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_MODEL=gemini-2.5-flash
```

**OpenRouter (300+ models, some free):**

```bash
OPENAI_API_KEY=your-openrouter-api-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=meta-llama/llama-3.3-70b-instruct
```

#### Provider Comparison

| Provider | Best For | Free Tier | Get API Key |
|----------|----------|-----------|-------------|
| OpenAI | Quality, reliability | No | [platform.openai.com](https://platform.openai.com/api-keys) |
| Groq | Speed, free usage | 14.4K req/day | [console.groq.com](https://console.groq.com/) |
| Google AI Studio | Free tokens | 1M tokens/min | [aistudio.google.com](https://aistudio.google.com/apikey) |
| OpenRouter | Model variety | Select models | [openrouter.ai/keys](https://openrouter.ai/keys) |
| Together.ai | Cost-effective | $25 trial | [api.together.ai](https://api.together.ai/settings/api-keys) |

**Requirements:** All providers must support function calling (most modern
models do).

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for detailed setup instructions.

### Optional: Web Search

The agent can use **Tavily API** for web search when knowledge base doesn't
have the answer. This is completely **optional** - the agent works perfectly
with just the local knowledge base.

#### Enable Web Search (Optional)

1. **Get FREE Tavily API key** (1000 searches/month):
   [tavily.com](https://tavily.com/)

2. **Add to `.env` file:**

   ```bash
   TAVILY_API_KEY=your-tavily-api-key-here
   ```

#### Why Use Tavily?

- AI-optimized search results (clean text, no HTML parsing)
- Prioritizes `eu5.paradoxwikis.com` domain
- 1000 free searches per month
- Falls back gracefully when not configured

**Without Tavily:** Agent works perfectly for all content in knowledge base,
just can't search the web for content outside the local files.

### Usage

**Interactive Mode:**

```bash
python run_agent.py
```

**Single Query:**

```bash
python run_agent.py --query "How do estates work in EU5?"
```

**With Verbose Output:**

```bash
python run_agent.py --query "What are the best opening moves for England?" --verbose
```

**Programmatic Use:**

```python
from eu5_agent import EU5Agent

agent = EU5Agent()
response = agent.chat("How does the market system work?")
print(response)
```

## Running locally

If you want to run the CLI directly from the repository or make the console script available, use one of these approaches:

- Run from the repository root (recommended):

```bash
# Module invocation
python -m eu5_agent.cli --cache-stats
python -m eu5_agent.cli --query "How do estates work in EU5?"
```

- If you're inside the `eu5_agent/` directory or have PYTHONPATH conflicts, explicitly set `PYTHONPATH` to the repo root so Python can discover packages correctly:

```bash
PYTHONPATH=. python -m eu5_agent.cli --cache-stats
```

- Install an editable package (recommended for local development) to enable the console script `eu5-agent`:

```bash
pip install -e .
eu5-agent --cache-stats
eu5-agent --query "How do estates work?"
```

Note: Using `pip install -e .` will install the console script `eu5-agent` defined in `pyproject.toml` so you can run the CLI without `python -m`.

## Knowledge Base Coverage

The agent includes comprehensive knowledge covering:

### Mechanics (All 8 Game Panels)

- **Economy** - Trade, markets, taxation, income
- **Government** - Laws, institutions, cabinets, reforms
- **Production** - Buildings, goods, development
- **Society** - Estates, population classes, privileges
- **Diplomacy** - Relations, alliances, vassals, wars
- **Military** - Units, armies, commanders, morale
- **Warfare** - Combat, sieges, terrain, tactics
- **Geopolitics** - Regions, power projection, subjects
- **Advances** - Technology, ideas, innovations

### Strategy Guides

- **Beginner Route** - Learning path for new players
- **Common Mistakes** - Pitfalls to avoid

### Nation Guides

- **England** - Opening strategy with 50-year checklist

### Resources

- **External Wikis** - Community resources and links

## Example Queries

```bash
# Game Mechanics
python run_agent.py --query "How does the market system work?"

# Beginner Guidance
python run_agent.py --query "I'm new to EU5. Which nation should I start with?"

# Nation-Specific Strategy
python run_agent.py --query "What are the best opening moves for England?"

# Advanced Topics
python run_agent.py --query "What are common beginner mistakes to avoid?"
```

## Advanced Configuration

The agent supports three configuration methods:

1. **Environment Variables**
2. **.env File** (Recommended for development)
3. **Direct Parameters** (Programmatic use)

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for complete configuration guide.

## Requirements

- Python 3.11+
- OpenAI API key
- Dependencies (5 packages):
  - openai >= 1.0.0
  - pydantic >= 2.0.0
  - rich >= 13.0.0
  - tavily-python >= 0.3.0 (optional - for web search)
  - python-dotenv >= 1.0.0

## Documentation

- **[Configuration Guide](docs/CONFIGURATION.md)** - Complete configuration reference

## Architecture

This is a **standalone agent** independent of any framework:

- **Direct File Loading** - No vector database complexity
- **Simple OpenAI Integration** - Direct API calls with function calling
- **Minimal Dependencies** - Only 5 packages required
- **Fast Startup** - < 1 second initialization

The agent uses:

1. **Local knowledge base** (primary) - Direct markdown file loading
2. **Web search** - Tavily API for AI-optimized search
   - Prioritizes eu5.paradoxwikis.com
3. **GPT-5-mini** - OpenAI's latest efficient model

## Testing

### Unit Tests

Run the full test suite (excludes integration tests by default):

```bash
pytest
```

Run only unit tests (explicitly exclude integration tests):

```bash
pytest -m "not openai_integration"
```

### Integration Tests

- The repository includes optional integration tests that make real OpenAI API calls. These tests:

- Are gated behind the `openai_integration` pytest marker
- Skip automatically when `OPENAI_API_KEY` is not set
- Keep costs low (max_completion_tokens ≤ 50, single-turn interactions)
- Verify actual OpenAI API functionality

**Run integration tests:**

```bash
# Set your API key first
export OPENAI_API_KEY=your-api-key-here

# Optional: customize model and base URL
export OPENAI_MODEL=gpt-5-mini
export OPENAI_BASE_URL=https://api.openai.com/v1

# Run integration tests only
pytest -m openai_integration

# Run all tests (unit + integration)
pytest
```

**Note:** Integration tests will incur minimal API costs (typically < $0.01 per run).

### Quick API Test

Test your API key and model configuration:

```bash
python tests/test_openai_api.py
```

## Contributing

Contributions are welcome! See [TODO.md](TODO.md) for a complete list of planned
enhancements and areas where contributions are needed.

Pull requests, issue reports, and feedback are all appreciated.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [OpenAI API](https://openai.com/)
- Uses [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Knowledge sourced from [EU5 Wiki](https://eu5.paradoxwikis.com/)

## Support

- **Issues**:
  [GitHub Issues](https://github.com/yourusername/eu5-strategy-agent/issues)
- **Discussions**:
  [GitHub Discussions](https://github.com/yourusername/eu5-strategy-agent/discussions)

---

Made with ❤️ for the EU5 community
