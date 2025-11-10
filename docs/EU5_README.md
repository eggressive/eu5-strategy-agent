# EU5 Strategy Agent - OpenManus Implementation

A locally-running AI agent for Europa Universalis 5 strategy advice, built on the OpenManus framework.

## Overview

This is a custom implementation of the EU5 Strategy Advisor using OpenManus, an open-source autonomous agent framework. Unlike the cloud-based Manus.im deployment, this runs entirely on your local machine with full control and customization.

## Features

- **Expert EU5 Knowledge**: Access to comprehensive game mechanics, strategies, and nation guides
- **Structured Knowledge Retrieval**: Custom tool for efficient category-based knowledge access
- **Local Execution**: Runs on your computer with full privacy control
- **Customizable**: Open-source codebase allows unlimited modifications
- **API-Powered**: Uses Claude/GPT-4 for intelligent responses (or local LLMs via Ollama)

## Quick Start

```bash
# 1. Set up environment
cd /home/dimitar/ai/eu5_agent/openmanus
python3.12 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
nano config/config.toml  # Add your API key

# 4. Run the agent
python run_eu5.py
```

**First Query**: "I'm new to EU5. Which nation should I start with?"

## Architecture

```
run_eu5.py (Entry Point)
    ↓
EU5Strategy Agent
    ↓
EU5KnowledgeTool ─→ Knowledge Base (6 markdown files)
```

The agent uses a custom knowledge tool to retrieve specific information from the EU5 knowledge base based on category (mechanics, strategy, nations, resources).

## Documentation

- **[SETUP.md](docs/SETUP.md)** - Complete setup instructions with troubleshooting
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture and data flow
- **[COMPARISON.md](docs/COMPARISON.md)** - OpenManus vs Manus.im comparison
- **[KNOWLEDGE_BASE_RESEARCH.md](docs/KNOWLEDGE_BASE_RESEARCH.md)** - Knowledge integration analysis

## Knowledge Base

The agent accesses the same EU5 knowledge base as the Manus.im deployment:

- `economy_mechanics.md` - Gold, taxation, minting, inflation
- `warfare_mechanics.md` - War mechanics, casus belli, warscore
- `beginner_route.md` - Progressive learning path
- `common_mistakes.md` - Five critical mistakes to avoid
- `nation_england.md` - England opening strategy
- `eu5_resources.md` - External wikis and guides

Knowledge base is symlinked from the main repository for easy updates.

## Usage Examples

### Interactive Mode
```bash
python run_eu5.py
# Then enter your question when prompted
```

### Command Line Mode
```bash
python run_eu5.py --prompt "What are the best opening moves for England?"
python run_eu5.py --prompt "How does the economy work in EU5?"
python run_eu5.py --prompt "What mistakes do beginners make?"
```

## Customization

### Adding New Nation Guides

1. Create `nation_{name}.md` in the knowledge base
2. Update `app/tool/eu5_knowledge.py`:
   ```python
   "nations": {
       "england": "nation_england.md",
       "france": "nation_france.md",  # Add this
   }
   ```
3. Restart the agent

### Adding Custom Tools

Create new tools in `app/tool/` and add to the agent:

```python
# In app/agent/eu5_strategy.py
from app.tool.eu5_calculator import EU5Calculator

available_tools: ToolCollection = Field(
    default_factory=lambda: ToolCollection(
        EU5KnowledgeTool(),
        EU5Calculator(),  # Your new tool
        Terminate(),
    )
)
```

## Configuration

Edit `config/config.toml` for:

- **LLM Model**: Claude, GPT-4, or local Ollama models
- **API Keys**: Anthropic or OpenAI
- **Token Limits**: Max response length
- **Temperature**: Response randomness (0.0 = deterministic)

## Cost

- **API Costs Only**: ~$0.01-0.05 per query
- **No Platform Fees**: Unlike managed services
- **Local LLM Option**: Use Ollama for zero API costs

## Privacy

- **Fully Local**: Agent runs on your machine
- **Direct API**: Queries go directly to LLM (no intermediary platform)
- **Your Data**: Knowledge base and queries stay under your control

## Comparison with Manus.im

| Feature | OpenManus | Manus.im |
|---------|-----------|----------|
| Setup | 15-30 min (technical) | 5-10 min (simple) |
| Cost | API only (~$1-5/mo) | API + platform fees |
| Control | Full customization | UI-limited |
| Privacy | Fully local | Platform-managed |
| Updates | Edit files + restart | Re-upload via UI |

See [COMPARISON.md](docs/COMPARISON.md) for detailed analysis.

## Development

### Project Structure

```
openmanus/
├── app/
│   ├── agent/
│   │   └── eu5_strategy.py      # EU5 Strategy Agent
│   ├── prompt/
│   │   └── eu5_strategy.py      # System & next-step prompts
│   └── tool/
│       └── eu5_knowledge.py     # Knowledge retrieval tool
├── config/
│   └── config.toml              # Configuration file
├── docs/
│   ├── SETUP.md                 # Setup guide
│   ├── ARCHITECTURE.md          # Technical docs
│   ├── COMPARISON.md            # Platform comparison
│   └── KNOWLEDGE_BASE_RESEARCH.md  # Integration analysis
├── knowledge_base/              # Symlink to ../
├── run_eu5.py                   # Entry point
└── EU5_README.md                # This file
```

### Testing

```bash
# Test with various query types
python run_eu5.py --prompt "Which nation for beginners?"  # Strategy
python run_eu5.py --prompt "How does economy work?"       # Mechanics
python run_eu5.py --prompt "England opening moves?"       # Nation-specific
```

## Troubleshooting

### Knowledge base not found
```bash
# Recreate symlink
ln -s /home/dimitar/ai/eu5_agent knowledge_base
```

### API key errors
- Check `config/config.toml` has correct API key
- Verify key format (starts with `sk-ant-` for Anthropic, `sk-` for OpenAI)

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

See [SETUP.md](docs/SETUP.md) for complete troubleshooting guide.

## Contributing

This is a custom agent implementation. To extend:

1. Add new knowledge base files
2. Create custom tools for calculations or APIs
3. Modify prompts for different behavior
4. Add multi-agent workflows

## License

- **OpenManus**: MIT License (https://github.com/FoundationAgents/OpenManus)
- **EU5 Knowledge Base**: Compiled from public sources (see main repo)
- **Custom Agent Code**: Same as main repository

## Support

- **Setup Issues**: See [SETUP.md](docs/SETUP.md)
- **Architecture Questions**: See [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **OpenManus Issues**: https://github.com/FoundationAgents/OpenManus/issues

---

**Version**: 1.0
**Created**: 2025-11-09
**OpenManus**: https://github.com/FoundationAgents/OpenManus
