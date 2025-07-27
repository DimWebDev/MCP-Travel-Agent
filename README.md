# MCP Travel Agent 🚀

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
