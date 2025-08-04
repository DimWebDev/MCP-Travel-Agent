# MCP Travel Agent 🚀

> [!IMPORTANT]
> **GitHub Project Status:**  
> This repository is **under active development**. Features, documentation, and APIs will be updated frequently—check back often for the latest changes!
AI-powered travel assistant that showcases **MCP (Model Context Protocol)** orchestration:
multi-step reasoning, dynamic tool selection, and containerised micro-services.

---

## 1 · Prerequisites

| Tool | Version (min) | Install hint |
|------|---------------|--------------|
| **Python** | 3.11 | `brew install python@3.11` or distro package |
| **Poetry** | 1.8 | `curl -sSL https://install.python-poetry.org | python3 -` |
| **Docker + Compose** | 23+ | Docker Desktop or `apt install docker.io docker-compose` |
| **Git** | any | – |

 > **No front-end yet** – only the FastAPI backend and four MCP micro-servers.
 > **CLI-first approach:** Initial agent orchestration and MCP server testing will be done via a command-line interface (REPL) before building the frontend.

---

## 2 · Quick Start

```bash
# Clone
git clone https://github.com/DimWebDev/MCP-Travel-Agent.git
cd MCP-Travel-Agent

# Python deps
poetry install               # reads pyproject.toml
poetry run pip install "mcp[cli]"   # adds MCP CLI extra

# Local env vars (OpenAI optional for now)
cp .env.example .env
# edit .env if you want to test LLM calls

# Spin up micro-servers & Redis
docker-compose up -d --build

# Run FastAPI agent
poetry run uvicorn app.agent.main:app --reload
````

Open **[http://localhost:8000/docs](http://localhost:8000/docs)** → interactive Swagger UI
(Curl works too: `curl -X POST http://localhost:8000/plan -d 'Rome 2-day history tour'`)

---


## 2a · Running All MCP Servers Locally (No Docker)

For local development and integration testing, you can run all four MCP micro-servers in parallel using the provided script:

```bash
poetry run python run_all_servers.py
```

This will start:

- Geocoding Server:      http://127.0.0.1:8001/mcp/
- POI Discovery Server:  http://127.0.0.1:8002/mcp/
- Wikipedia Server:      http://127.0.0.1:8003/mcp/
- Trivia Server:         http://127.0.0.1:8004/mcp/

Press Ctrl+C to stop all servers.

> **Note:** This is an alternative to `docker-compose up` for local development. Use Docker for production or when you need Redis and all services together.

---
## 3 · Project Layout

```
app/
├── agent/                    ← FastAPI orchestrator
└── mcp_servers/             ← 4 independent FastMCP servers
    ├── geocoding/
    ├── poi_discovery/
    ├── wikipedia/
    └── trivia/
tests/                        ← Pytest suite
.env.example
docker-compose.yml            ← Redis + 4 micro-servers
pyproject.toml                ← Poetry dependencies
README.md                     ← you are here
```

---

## 4 · Key Dependencies

| Package            | Purpose              |
| ------------------ | -------------------- |
| **fastapi 0.111**  | HTTP API & auto-docs |
| **uvicorn 0.29**   | ASGI server (reload) |
| **mcp\[cli] 1.12** | MCP SDK & dev tools  |
| **httpx ≥ 0.27**   | async HTTP calls     |
| **pydantic 2.7**   | data validation      |
| **openai** (opt.)  | GPT-4o-mini calls    |

---

## 5 · Dev Workflow

```bash
# Hot-reload backend while editing
poetry run uvicorn app.agent.main:app --reload

# Unit / integration tests
poetry run pytest

# Formatting / lint
poetry run black .
poetry run isort .

```

Docker services stay up; restart them only after editing a micro-server.

---

## 6 · Troubleshooting

| Symptom                                          | Fix                                                        |
| ------------------------------------------------ | ---------------------------------------------------------- |
| **`ModuleNotFoundError`** after `poetry install` | run `poetry env use 3.11 && poetry install`                |
| **OpenAI auth errors**                           | add a valid key to `.env` (`OPENAI_API_KEY=sk-…`)          |
| **Ports 8000/6379 busy**                         | change in `docker-compose.yml` or pass `--port` to Uvicorn |
| **Docker daemon not running**                    | start Docker Desktop / `sudo service docker start`         |

---

## 7 · Roadmap (Tasks T002-T007)

1. **T002** – implement Geocoding FastMCP server
2. **T003** – POI Discovery server
3. **T004** – Wikipedia summary server
4. **T005** – Trivia server
5. **T006** – complete agent orchestration logic
6. **T007** – finalise `docker-compose.yml`

See `Tasks.md` for detailed acceptance criteria.

---

Happy hacking — and enjoy building your MCP-powered travel companion! 

```


## 🚦 Checking MCP Server Health with the Inspector GUI

You can verify any FastMCP server end‐to‐end by using the **MCP Inspector**—a lightweight GUI + proxy that lets you visually discover and invoke your tools without hand-crafting JSON-RPC messages.

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
poetry run mcp dev app/mcp_servers/geocoding/server.py
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
poetry run mcp dev app/mcp_servers/poi_discovery/server.py
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
poetry run mcp dev app/mcp_servers/wikipedia/server.py
```

---


**To run with the Trivia server, use these analogous commands:**

In one terminal, start the **Trivia MCP server**:

```bash
poetry run python app/mcp_servers/trivia/server.py
```

Leave that running.

In a second terminal, start the Inspector for the Trivia server:

```bash
poetry run mcp dev app/mcp_servers/trivia/server.py
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
poetry run uvicorn app.agent.main:app --reload

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
poetry run uvicorn app.agent.main:app --reload

# 2. Run comprehensive system tests
poetry run pytest tests/integration/ -s
```

### 5.3 · MCP Inspector for Visual Testing

For interactive testing and debugging of individual MCP servers:

```bash
# Start your MCP server first
poetry run python app/mcp_servers/geocoding/server.py

# Then launch the MCP Inspector in another terminal
poetry run mcp dev app/mcp_servers/geocoding/server.py
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

