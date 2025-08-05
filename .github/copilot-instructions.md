# Copilot Instructions

For all AI coding agents and contributors:

**Start by reading `AGENTS.md` in the project root.**

- It explains the workflow, code quality standards, contribution process, and project-specific conventions.
- Follow the step-by-step onboarding in `AGENTS.md` before referencing any other documentation.
- For requirements, architecture, and implementation details, see `PRD.md`, `Planning.md`, and `Tasks.md`.

## Architecture & Data Flow

This project implements an MCP (Model Context Protocol) orchestrated AI travel agent with:

1. **FastAPI Backend + Agent Orchestrator** (`app/agent/`) - Coordinates requests across multiple MCP servers
2. **Four FastMCP Microservices** (`app/mcp_servers/`):
   - **Geocoding** (port 8001) - Location resolution via OSM Nominatim
   - **POI Discovery** (port 8002) - Points of interest search via Overpass API
   - **Wikipedia** (port 8003) - Content enrichment from Wikipedia
   - **Trivia** (port 8004) - Travel facts from DuckDuckGo

The typical data flow: User query → Agent Orchestrator → MCP servers (in parallel/sequence) → Response synthesis → User

## Development Commands

```bash
# Start all MCP servers locally for development
poetry run python run_all_servers.py

# Hot-reload backend while editing
poetry run uvicorn app.agent.main:app --reload

# Unit & integration tests
poetry run pytest tests/unit
poetry run pytest tests/integration/test_live_geocode.py -s  # -s shows print output

# MCP server debugging with Inspector
poetry run python app/mcp_servers/geocoding/server.py  # Start server
poetry run fastmcp dev app/mcp_servers/geocoding/server.py  # Launch Inspector
```

## Key Project Conventions

- **MCP Server Pattern**: Each tool is an independent FastMCP server exposing tools via `@mcp.tool()` decorators
- **Transport Protocol**: Uses Streamable HTTP (preferred) over `/mcp` endpoints, with SSE as fallback
- **Git Workflow**: Feature branches named `feature/<description>`, PRs with explicit testing instructions
- **Testing**: Unit tests for components, integration tests for live server testing via MCP client
- **Documentation**: Update relevant .md files when architecture changes (see `AGENTS.md` Section 2)

> All essential knowledge for productive work in this codebase is maintained in `AGENTS.md`. Always consult it first.
