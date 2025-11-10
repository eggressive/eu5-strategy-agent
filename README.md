# EU5 Strategy Agent

**Lightweight, standalone strategy advisor for Europa Universalis 5 (1337-1837)**

Get expert strategic guidance for EU5 using GPT-5-mini with a comprehensive knowledge base covering all 8 main game panels.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Features

- 🤖 **GPT-5-mini Powered** - Fast, cost-effective AI-driven strategy advice
- 📚 **Comprehensive Knowledge Base** - 13 curated files covering all 8 EU5 game panels
- 🌐 **Web Search Fallback** - Automatically searches for missing content (prioritizes eu5.paradoxwikis.com)
- 💻 **Beautiful CLI** - Rich terminal formatting with markdown rendering
- ⚙️ **Flexible Configuration** - Environment variables, .env files, or direct parameters
- 🚀 **Fast Responses** - 2-3 second response times
- 💰 **Cost-Effective** - Optimized for gpt-5-mini's pricing

## Quick Start

### Installation

**From Source:**
```bash
git clone https://github.com/yourusername/eu5-strategy-agent
cd eu5-strategy-agent
pip install -r requirements.txt
```

**Future PyPI Installation:**
```bash
pip install eu5-strategy-agent
```

### Configuration

1. **Copy the example configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your OpenAI API key:**
   ```bash
   OPENAI_API_KEY=your-openai-api-key-here
   OPENAI_MODEL=gpt-5-mini
   ```

3. **Get an OpenAI API key** from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

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

## Knowledge Base Coverage

The agent includes comprehensive knowledge covering:

### Mechanics (9 files - All 8 Game Panels)
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

## Configuration

The agent supports three configuration methods:

1. **Environment Variables** (Recommended for production)
2. **.env File** (Recommended for development)
3. **Direct Parameters** (Programmatic use)

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for complete configuration guide.

### Important Notes for gpt-5-mini

- Does NOT support `temperature` parameter (uses default=1.0)
- Uses `max_completion_tokens` instead of `max_tokens`
- The agent handles these differences automatically

## Requirements

- Python 3.11+
- OpenAI API key
- Dependencies (8 packages):
  - openai >= 1.0.0
  - pydantic >= 2.0.0
  - rich >= 13.0.0
  - googlesearch-python >= 1.2.3
  - requests >= 2.31.0
  - beautifulsoup4 >= 4.12.0
  - python-dotenv >= 1.0.0

## Documentation

- **[Configuration Guide](docs/CONFIGURATION.md)** - Complete configuration reference
- **[EU5 README](docs/EU5_README.md)** - EU5-specific documentation
- **[Cleanup Summary](docs/CLEANUP_SUMMARY.md)** - Development history

## Architecture

This is a **standalone agent** independent of any framework:

- **Direct File Loading** - No vector database complexity
- **Simple OpenAI Integration** - Direct API calls with function calling
- **Minimal Dependencies** - Only 8 packages required
- **Fast Startup** - < 1 second initialization

The agent uses:
1. **Local knowledge base** (primary) - Direct markdown file loading
2. **Web search** (fallback) - Google search prioritizing eu5.paradoxwikis.com
3. **GPT-5-mini** - OpenAI's latest efficient model

## Testing

Run the test suite:
```bash
python tests/test_agent.py
```

Test your API key and model:
```bash
python tests/test_openai_api.py
```

## Contributing

Contributions are welcome! Areas for contribution:

- **Knowledge Base** - Add more nation guides, strategies
- **Features** - New tools, better search, caching
- **Documentation** - Tutorials, examples, translations
- **Testing** - Unit tests, integration tests

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [OpenAI API](https://openai.com/)
- Uses [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Knowledge sourced from [EU5 Wiki](https://eu5.paradoxwikis.com/)

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/eu5-strategy-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/eu5-strategy-agent/discussions)

## Related Projects

- **OpenManus** - Full autonomous agent framework (if you need browser automation and complex workflows)

---

**Made with ❤️ for the EU5 community**
