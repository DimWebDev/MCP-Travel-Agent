# MCP Travel Agent Development Setup Guide

## First-Time Setup Commands (Ubuntu VM/Codex)

Run these commands once to set up your development environment in a fresh Ubuntu VM:

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3.11 python3-pip nodejs npm docker.io docker-compose git curl

# 2. Install Poetry (Python package manager)
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# 3. Clone and setup project structure
git clone 
cd mcp-travel-agent

# 4. Install Python dependencies
poetry install
poetry shell

# 5. Setup environment variables
cp .env.example .env
# Edit .env file with your OpenAI API key:
nano .env
# Add: OPENAI_API_KEY=sk-your-openai-api-key-here

# 6. Setup frontend dependencies
cd frontend
npm install
cd ..

# 7. Verify installation
poetry run python --version  # Should show Python 3.11+
poetry run python -c "import fastapi; print('FastAPI installed')"
poetry run python -c "import openai; print('OpenAI installed')"
```

## Daily Development Workflow Commands

Once your environment is set up, use these commands for daily development:

### Option 1: Full Docker Development (Recommended)
```bash
# Start all supporting services
docker-compose up -d  # Starts all MCP servers + Redis

# Start main agent (separate terminal)
poetry shell
poetry run uvicorn app.agent.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (separate terminal)
cd frontend && npm run dev
```

### Option 2: Individual Services for Debugging
```bash
# Start individual MCP servers for debugging
poetry run python app/mcp_servers/geocoding/server.py
poetry run python app/mcp_servers/poi_discovery/server.py
poetry run python app/mcp_servers/wikipedia/server.py
poetry run python app/mcp_servers/trivia/server.py

# Start agent orchestrator
poetry run uvicorn app.agent.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Commands
```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest tests/unit/
poetry run pytest tests/integration/

# Frontend tests
cd frontend && npm test
```

## Development Architecture & Docker Usage

### Why Docker is Used Here

**Docker is used for SERVICE ORCHESTRATION, not development containers:**

1. **Multiple MCP Servers**: Your project has 4 separate MCP servers (geocoding, POI discovery, Wikipedia, trivia) that need to run simultaneously
2. **Service Dependencies**: Redis for caching and inter-service communication
3. **Network Coordination**: All services need to communicate with each other on a shared network
4. **Development Convenience**: One command (`docker-compose up -d`) starts all supporting services

### Development Architecture Flow

```
Your Local Development Environment:
├── Poetry Python Environment (Agent Orchestrator) - Runs locally
├── Node.js/npm Environment (React Frontend) - Runs locally
└── Docker Compose Services (MCP Servers + Redis) - Runs in containers
```

**Key Point**: You DON'T develop inside Docker containers. Instead:
- **Agent orchestrator and frontend run locally** for easy debugging and hot reload
- **MCP servers run in Docker** for isolation and easy management
- **You edit code locally** with your preferred IDE/editor
- **Hot reload works** for both backend and frontend changes

## Prerequisites Before Commands Work

Before the development workflow commands will function properly, you need to complete these foundational tasks:

1. **Complete Task T001**: Project structure setup (directory creation, pyproject.toml, etc.)
2. **Add OpenAI API key**: Valid API key in your `.env` file
3. **Build MCP servers**: Complete Tasks T002-T005 (individual MCP server implementations)
4. **Create docker-compose.yml**: Complete Task T007 (service orchestration setup)
5. **Build FastAPI agent**: Complete Task T006 (main agent orchestrator)

## Recommended Development Sequence

### Week 1 Focus (Sprint 1):
```bash
# 1. Start with project structure setup
poetry install
# Complete Task T001 (project structure)

# 2. Build individual MCP servers incrementally
# Complete Tasks T002-T005 (one server at a time)
poetry run python app/mcp_servers/geocoding/server.py  # Test as you build

# 3. Create Docker orchestration
# Complete Task T007 (docker-compose.yml)
docker-compose up -d  # Should work after servers are built

# 4. Build main agent orchestrator
# Complete Task T006 (FastAPI agent)
poetry run uvicorn app.agent.main:app --reload  # Should work after agent is built
```

### Testing Throughout Development
```bash
# Test individual components as you build them
poetry run pytest tests/unit/test_geocoding.py
poetry run pytest tests/unit/test_poi_discovery.py

# Run full test suite
poetry run pytest
```

The commands in the daily workflow will work perfectly **after** you complete the foundational Sprint 1 tasks. Start with the project structure setup and build incrementally, testing each component as you go.