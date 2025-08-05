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

```



## 🚦 Checking MCP Server Health with the Inspector GUI

> **Inspector for FastMCP 2.x+**
> 
> For FastMCP 2.x and later, always use `poetry run fastmcp dev ...` to launch the Inspector. The legacy `mcp dev` CLI is not compatible with FastMCP 2.x servers. The built-in Inspector provides a web-based UI for tool discovery and testing.

You can verify any FastMCP server end‐to‐end by using the **FastMCP Inspector**—a lightweight GUI + proxy that lets you visually discover and invoke your tools without hand-crafting JSON-RPC messages.

---

### 1. What Is the MCP Inspector?

* **UI**: A browser-based interface where you can browse **Tools**, **Resources**, and **Prompts**, view their schemas, and call them interactively.
* **Proxy**: A local HTTP proxy (default `localhost:6277`) that bridges the Inspector UI and your MCP server.  All traffic flows through this proxy so the UI can manage JSON-RPC sessions for you.

---

### 2. Launching the Inspector

In one terminal, start **your MCP server** (e.g. geocoding):

```bash
poetry run python app/mcp_servers/geocoding/server.py
```

Leave that running.


In a second terminal, start the Inspector:

```bash
poetry run fastmcp dev app/mcp_servers/geocoding/server.py
```

---


**To run with the POI Discovery server, use these analogous commands:**

In one terminal, start the **POI Discovery MCP server**:

```bash
poetry run python app/mcp_servers/poi_discovery/server.py
```

Leave that running.

In a second terminal, start the Inspector for the POI Discovery server:

```bash
poetry run fastmcp dev app/mcp_servers/poi_discovery/server.py
```

---


**To run with the Wikipedia server, use these analogous commands:**

In one terminal, start the **Wikipedia MCP server**:

```bash
poetry run python app/mcp_servers/wikipedia/server.py
```

Leave that running.

In a second terminal, start the Inspector for the Wikipedia server:

```bash
poetry run fastmcp dev app/mcp_servers/wikipedia/server.py
```

---




You’ll see output similar to:

```
⚙️ Proxy server listening on localhost:6277
🔑 Session token: 7d1324d291d383d3569a0d0a0722efa6ddc3cfeee6655e5cd6a69479b8c0a466
   Use this token to authenticate requests or set DANGEROUSLY_OMIT_AUTH=true to disable auth

🚀 MCP Inspector is up and running at:
   http://localhost:6274

🌐 Opening browser...
```

* **Port 6274**: the Inspector UI
* **Port 6277**: the proxy that forwards UI requests to your MCP server
* **Session token**: one-time key to unlock the proxy

---

### 3. Authenticating the Inspector

By default, the proxy requires the printed **Session token**. You have two options:

#### A. Paste the token in the UI

1. In your browser, go to [http://localhost:6274](http://localhost:6274).
2. In the left-hand panel, expand **Configuration → Authentication**.
3. Paste the token (e.g. `7d1324d291d...`) into the **Session Token** field and click **Save**.
4. Select **Transport Type → HTTP (streamable)** and set **Target →**

   ```
   http://127.0.0.1:8000/mcp
   ```
5. Click **Connect**.
6. The status indicator will switch from **Disconnected** → **Connected**, and your tools will appear in the center pane.

#### B. Disable auth (dev only)

If you’re on a private machine and don’t want to deal with tokens, restart with:

```bash
DANGEROUSLY_OMIT_AUTH=true poetry run mcp dev app/mcp_servers/geocoding/server.py
```

**Or for the POI Discovery server:**

```bash
DANGEROUSLY_OMIT_AUTH=true poetry run mcp dev app/mcp_servers/poi_discovery/server.py
```


This bypasses proxy authentication entirely.

---

### 4. Using the Inspector

Once **Connected**, the Inspector UI shows:

* **Tools**: click one (e.g. `geocode_location`)
* **Schema**: input fields auto-generated from your Pydantic models
* **Call panel**: enter parameters (e.g. `location_name = Athens`)
* **Result stream**: live view of structured JSON + text content

You can experiment freely—try edge cases, test error handling, and see progress messages in real time.

---

## 5 · Dev Workflow

### 5.1 · Quick Commands

```bash
# Hot-reload backend while editing
 poetry run uvicorn app.main:app --reload

# Unit tests (all MCP servers)
poetry run pytest tests/unit

# Formatting / lint
poetry run black .
poetry run isort .
```

Docker services stay up; restart them only after editing a micro-server.

### 5.2 · MCP Server Testing: Individual vs. Integration

**Individual MCP Server Testing** (Test one server in isolation):

```bash
# 1. Start the specific MCP server you want to test
poetry run python app/mcp_servers/geocoding/server.py
# OR
poetry run python app/mcp_servers/poi_discovery/server.py
# OR
poetry run python app/mcp_servers/wikipedia/server.py

# 2. In another terminal, run its integration test
poetry run pytest tests/integration/test_live_geocode.py -s
# OR
poetry run pytest tests/integration/test_live_poi_discovery.py -s
# OR
poetry run pytest tests/integration/test_live_wikipedia.py -s
```

**Full System Integration Testing** (All servers via orchestrator):

```bash
# 1. Start the full FastAPI orchestrator (which connects to all MCP servers)
poetry run uvicorn app.main:app --reload

# 2. Run comprehensive system tests
poetry run pytest tests/integration/ -s
```

### 5.3 · MCP Inspector for Visual Testing


For interactive testing and debugging of individual MCP servers:

```bash
# Start your MCP server first
poetry run python app/mcp_servers/geocoding/server.py

# Then launch the FastMCP Inspector in another terminal
poetry run fastmcp dev app/mcp_servers/geocoding/server.py
# Opens browser UI at http://localhost:6274
```

### 5.4 · Integration Tests Details

We include end-to-end integration tests for each FastMCP server:

* **Geocoding:** `tests/integration/test_live_geocode.py`
  - Connects via streamable-HTTP to running geocoding server
  - Lists the `geocode_location` tool and prints its JSON schema
  - Invokes the tool with `"Berlin"`
  - Prints raw JSON-RPC blocks and parsed `structuredContent`
  - Asserts that `lat`, `lon`, and `display_name` are returned

* **POI Discovery:** `tests/integration/test_live_poi_discovery.py`
  - Tests `search_pois` tool with Berlin tourism query
  - Validates POI results structure and distance sorting
  - Prints complete tool schema and response data

* **Wikipedia:** `tests/integration/test_live_wikipedia.py`
  - Tests `get_wikipedia_info` tool with "Eiffel Tower" query
  - Validates Wikipedia content extraction and URL generation
  - Ensures summary, extract, and title fields are present

**Run individual integration tests:**

```bash
# Must have the specific server running first:
poetry run python app/mcp_servers/geocoding/server.py

# Then execute in another terminal:
poetry run pytest tests/integration/test_live_geocode.py -s
```

The `-s` flag disables pytest's output capture so you see all debug information, including tool schemas and response structures.






## 🧪 How to Test Your MCP Agent (Health & Queries) TASK006

You can verify your MCP agent and all microservices are working with these commands:

### Health checks (all should return `{\"status\":\"ok\"}`)

```bash
curl http://localhost:8000/health/geocoding
curl http://localhost:8000/health/poi
curl http://localhost:8000/health/wikipedia
```

### Simple location queries (the scope of Task T006)

```bash
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query": "Rome"}' | jq
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query": "Paris"}' | jq
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query": "Tokyo"}' | jq
```

These will test the full orchestration pipeline: geocoding, POI discovery, and Wikipedia. For best results, use simple location names as queries. Complex travel planning queries will be supported in later tasks with GPT-4o-mini integration.

#### For pretty-printed JSON output (recommended for local development):

> **Before running the curl command below, make sure you have started all MCP servers locally:**
> 
> ```bash
> poetry run python run_all_servers.py
> ```
> 
> Then, in a separate terminal, start the FastAPI orchestrator:
> 
> ```bash
> poetry run uvicorn app.main:app --reload
> ```
> 
> Once both are running, you can test the orchestrator endpoint:

```bash
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query": "Rome"}' | jq
```

> **Tip:** [`jq`](https://stedolan.github.io/jq/) is a command-line JSON processor that formats and colors output for easier reading. Install it on macOS with:
> ```bash
> brew install jq
> ```