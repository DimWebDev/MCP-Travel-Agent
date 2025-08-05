# MCP Travel Agent 🚀

> [!IMPORTANT]  
> **Under Active Development** - Features and APIs are updated frequently. Check back for latest changes!

AI-powered travel assistant demonstrating **MCP (Model Context Protocol)** orchestration with multi-step reasoning, dynamic tool selection, and containerized microservices.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/DimWebDev/MCP-Travel-Agent.git
cd MCP-Travel-Agent
poetry install

# Environment setup
cp .env.example .env
# Edit .env to add your OpenAI API key (optional for basic testing)

# Start all MCP servers (local development)
poetry run python run_all_servers.py

# In another terminal, start the agent orchestrator
poetry run uvicorn app.main:app --reload
```

**Test your setup:**
- Open [http://localhost:8000/docs](http://localhost:8000/docs) for API documentation
- Try: `curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query": "Rome"}' | jq`

## 📋 Prerequisites

- **Python 3.11+** - `brew install python@3.11`
- **Poetry** - `curl -sSL https://install.python-poetry.org | python3 -`
- **Docker** (optional) - For containerized deployment
- **jq** (optional) - For pretty JSON output: `brew install jq`

## 🏗️ Architecture

```
app/
├── agent/              # FastAPI orchestrator with MCP client
│   ├── main.py        # Main FastAPI app
│   ├── orchestrator.py # Agent logic and tool coordination
│   ├── clients.py     # MCP server clients
│   └── models.py      # Pydantic data models
└── mcp_servers/       # Independent FastMCP servers
    ├── geocoding/     # Location resolution (OSM Nominatim)
    ├── poi_discovery/ # Points of interest (Overpass API)
    └── wikipedia/     # Content enrichment (Wikipedia API)
```

**Data Flow:** User Query → Agent Orchestrator → MCP Tools (parallel/sequential) → Response Synthesis

---

## 🧪 Testing & Development

### Health Checks
```bash
# Verify all services are running
curl http://localhost:8000/health/geocoding
curl http://localhost:8000/health/poi
curl http://localhost:8000/health/wikipedia
```

### Query Testing
```bash
# Test the full orchestration pipeline
curl -X POST http://localhost:8000/query 
  -H "Content-Type: application/json" 
  -d '{"query": "Rome"}' | jq
```

### Individual MCP Server Testing
```bash
# Start a specific server
poetry run python app/mcp_servers/geocoding/server.py

# Test with FastMCP Inspector (in another terminal)
poetry run fastmcp dev app/mcp_servers/geocoding/server.py
# Opens browser UI at http://localhost:6274
```

### Running Tests
```bash
# Unit tests
poetry run pytest tests/unit/

# Integration tests (requires running servers)
poetry run pytest tests/integration/ -s

# Code formatting
poetry run black .
poetry run isort .
```

## 🔧 Development Workflow

1. **Start all MCP servers:** `poetry run python run_all_servers.py`
2. **Start agent orchestrator:** `poetry run uvicorn app.main:app --reload`
3. **Make changes** with hot-reload enabled
4. **Test endpoints** via `/docs` or curl commands
5. **Run tests** before committing

## 📚 Project Documentation

- **[AGENTS.md](AGENTS.md)** - Development workflow and contribution guidelines
- **[PRD.md](PRD.md)** - Product requirements and user stories  
- **[Planning.md](Planning.md)** - Architecture and technical decisions
- **[Tasks.md](Tasks.md)** - Implementation roadmap and current status

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `poetry env use 3.11 && poetry install` |
| OpenAI auth errors | Add valid `OPENAI_API_KEY` to `.env` |
| Port conflicts | Change ports in `run_all_servers.py` or docker config |
| Docker issues | Ensure Docker is running: `docker --version` |

## 🎯 Current Status

✅ **Completed:**
- Basic MCP server infrastructure (geocoding, POI discovery, Wikipedia)
- FastAPI agent orchestrator with health checks
- CLI-first development and testing workflow
- Integration tests and MCP Inspector setup

🚧 **In Progress:**
- GPT-4o-mini integration for intelligent tool selection
- Advanced agent reasoning and multi-step workflows
- React TypeScript frontend interface

---

Happy hacking! 🚀 For detailed implementation steps, see [Tasks.md](Tasks.md).
