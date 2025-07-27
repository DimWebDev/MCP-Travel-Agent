# MCP Travel Agent Development Setup Guide

## Complete Setup & Run Instructions (macOS/Linux)

### Prerequisites
- Python 3.11+
- Poetry (Python package manager)
- Node.js 18+
- Docker Desktop
- Git

### Installation Commands

#### 1. Install Prerequisites (macOS)
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install python@3.11 poetry node docker git

# Install Docker Desktop from https://docker.com/products/docker-desktop
# Or install via Homebrew Cask:
brew install --cask docker
```

#### 2. Clone and Setup Project
```bash
# Clone the repository
git clone https://github.com/DimWebDev/MCP-Travel-Agent.git
cd MCP-Travel-Agent

# Install Python dependencies
poetry install

# Setup environment variables
cp .env.example .env
# Edit .env file and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-openai-api-key-here
```

#### 3. Verify Installation
```bash
# Check installations
poetry run python --version  # Should show Python 3.11+
poetry run python -c "import fastapi, mcp, openai; print('✅ All dependencies installed!')"
```

### How to Run the Application (Daily Workflow)

### 1. Start Docker Desktop
```bash
# Open Docker Desktop app (required for MCP servers)
open -a Docker
# Wait for Docker to start up completely
```

### 2. Start all MCP servers and Redis
```bash
docker-compose up -d
```

### 3. Start the main AI agent (FastAPI backend)
```bash
poetry run uvicorn app.agent.main:app --reload
```
*The agent will be available at http://localhost:8000*

### 4. Start the frontend (optional, for chat UI)
```bash
# In a new terminal
cd frontend
npm install  # Only needed first time
npm run dev
```
*The frontend will be available at http://localhost:3000*

---

## Testing

```bash
# Run all Python tests
poetry run pytest

# Run specific test files
poetry run pytest tests/unit/test_geocoding.py

# Check test coverage
poetry run pytest --cov=app
```

## Troubleshooting

### Common Issues

**Docker not starting:**
- Make sure Docker Desktop is running
- Check `docker ps` to see if containers are running

**Poetry command not found:**
- Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
- Add to PATH: `export PATH="$HOME/.local/bin:$PATH"`

**OpenAI API errors:**
- Check your `.env` file has the correct API key
- Verify key starts with `sk-`

**Port already in use:**
- Change ports in commands: `--port 8001` for agent, or kill existing processes

### Logs and Debugging

```bash
# View Docker logs
docker-compose logs

# View specific service logs
docker-compose logs geocoding-server

# Stop all services
docker-compose down
```

## Quick Start Summary

Once everything is installed:

```bash
# 1. Start Docker Desktop (GUI app)
open -a Docker

# 2. Start MCP servers
docker-compose up -d

# 3. Start agent (in new terminal)
poetry run uvicorn app.agent.main:app --reload

# 4. (Optional) Start frontend (in another terminal)
cd frontend && npm run dev
```

Visit:
- **API Documentation:** http://localhost:8000/docs
- **Chat Interface:** http://localhost:3000 (if frontend running)

---

## Notes
- You do **not** need to run individual MCP server scripts unless debugging.
- All MCP servers and Redis are managed by Docker Compose.
- The agent (FastAPI) and frontend run locally for best developer experience.
- Edit `.env` for API keys if needed.

---

For more details, see `README.md`, `Tasks.md`, and `Planning.md`.

---

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