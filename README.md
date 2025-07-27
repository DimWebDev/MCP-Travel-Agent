# MCP Travel Agent

An intelligent AI travel agent that demonstrates advanced MCP (Model Context Protocol) orchestration patterns through dynamic tool selection and multi-step reasoning for personalized travel planning.

## Project Setup Complete ✅

### Prerequisites
- Python 3.11+
- Poetry for dependency management
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mcp-travel-agent
   ```

2. **Install dependencies with Poetry**
   ```bash
   poetry install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Verify Installation

```bash
# Check Python version
poetry run python --version

# Test imports
poetry run python -c "import fastapi, mcp, openai, httpx, pydantic, uvicorn; print('✅ All imports successful!')"
```

### Project Structure

```
mcp-travel-agent/
├── app/
│   ├── agent/                 # FastAPI agent orchestrator
│   └── mcp_servers/          # Individual MCP servers
│       ├── geocoding/        # OSM Nominatim wrapper
│       ├── poi_discovery/    # Overpass API wrapper  
│       ├── wikipedia/        # Wikipedia API wrapper
│       └── trivia/          # DuckDuckGo API wrapper
├── tests/
│   └── unit/                # Unit tests
├── .env.example             # Environment variables template
├── pyproject.toml          # Poetry dependencies
└── README.md              # This file
```

### Dependencies Installed

- **FastAPI** 0.115.14 - Web framework for agent API
- **MCP SDK** 1.12.2 - Model Context Protocol implementation
- **OpenAI** 1.97.1 - GPT-4o-mini integration  
- **HTTPX** 0.27.2 - Async HTTP client
- **Pydantic** 2.11.7 - Data validation
- **Uvicorn** - ASGI server

### Next Steps

Continue with Task T002 to create the first MCP server (Geocoding). See `Tasks.md` for the complete implementation roadmap.

### Development

```bash
# Run with Poetry
poetry run uvicorn app.agent.main:app --reload

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .
```

For detailed requirements, see `PRD.md`. For architecture details, see `Planning.md`. For step-by-step tasks, see `Tasks.md`.
