# MCP-Orchestrated AI Travel Agent — Planning & Infrastructure

## 1. Overview

**Project Vision:** Build an intelligent AI travel agent that demonstrates MCP (Model Context Protocol) orchestration patterns through a structured, multi-step workflow for personalized travel planning. The MVP agent coordinates a fixed sequence of MCP protocol calls (geocoding → POI → Wikipedia) for each user query. Dynamic tool selection and agent autonomy are future goals, not part of the current implementation.


**Core Goals:**

* Demonstrate MCP protocol-driven agent coordination of a structured, multi-step workflow
* Implement multi-step reasoning chains across distributed MCP servers (fixed workflow for MVP)
* Showcase error recovery and graceful degradation in agent workflows
* Provide hands-on learning with MCP orchestration patterns


**High-Level Roadmap:** 5-week sprint-based development focusing on the 20% of agent orchestration features that deliver 80% of learning value, progressing from basic protocol-driven tool communication (fixed workflow) to more sophisticated agent reasoning in future phases.

> **Note:** This Planning document builds directly on the requirements and goals defined in `PRD.md`. It translates those requirements into actionable architecture, technology choices, and implementation phases.

---


**MCP Orchestration vs. Traditional Function Calling**

> **Critical Design Principle:**
> The MVP agent coordinates a fixed, protocol-driven workflow by calling independent MCP servers in a set sequence (geocoding → POI → Wikipedia) for each user query. All tool invocations use the MCP protocol, not direct function calls. Dynamic tool selection and agent autonomy are future enhancements, not part of the current implementation. This is foundational for the architecture and for all agent orchestration and workflow design decisions in this project.

---

## 2. Milestones & Phases

| Milestone/Phase                  | Description                                                   | Target Date | Key Deliverables                                                   |
| :------------------------------- | :------------------------------------------------------------ | :---------- | :----------------------------------------------------------------- |
| **Sprint 1: Foundation**         | MCP server infrastructure & basic agent-tool communication    | Week 1      | 3 MCP servers, basic agent client, tool connectivity               |
| **Sprint 2: Agent Intelligence** | Implement core agent intent analysis and structured workflow orchestration | Week 2      | Intent analysis, structured workflow orchestration, result synthesis |
| **Sprint 3: Orchestration**      | Contextual tool chaining and intelligent result synthesis     | Week 3      | Multi-step workflows, result fusion, contextual responses          |
| **Sprint 4: Resilience**         | Error handling, fallback strategies, and graceful degradation | Week 4      | Error recovery, retry logic, alternative tool paths                |
| **Sprint 5: Enhancement**        | Conversation memory, follow-up handling, and optimization     | Week 5      | Context retention, conversation state, performance tuning          |
| **Demo Ready**                   | Complete MCP orchestration proof-of-concept                   | End Week 5  | Functional travel agent with all learning objectives met           |

## 3. Technical Stack

### Backend (Python Ecosystem)

* **AI Agent Framework:** Python 3.11+ with asyncio for concurrent MCP server orchestration
- **LLM Integration:** OpenAI GPT-4o-mini via official `openai` Python library for decision-making and orchestration
- **MCP Protocol:** Structured workflow coordination via MCP client-server communication
* **MCP Implementation:** Python MCP SDK (`fastmcp` package) for server creation and client orchestration
* **Backend Framework:** FastAPI with async support for agent API endpoints and MCP server hosting
* **HTTP Client:** `httpx` for async external API calls to OSM and Wikipedia
* **Data Validation:** Pydantic v2 for request/response models and MCP tool schemas
* **Environment Management:** Poetry for dependency management and virtual environments

### Frontend (React TypeScript)

* **Framework:** React 18 with TypeScript for type-safe component development
* **Build Tool:** Vite for fast development and optimized builds
* **UI Components:** Headless UI + Tailwind CSS for clean chat interface design
* **State Management:** Zustand for lightweight global state (conversation history)
* **HTTP Client:** Axios with TypeScript types for backend communication
* **Real-time Updates:** Server-Sent Events for streaming agent responses

### External APIs

* **OpenStreetMap Nominatim:** Geocoding and location resolution
* **Overpass API:** POI discovery and geographic queries
* **Wikipedia API:** Article content and summaries

### Development & Deployment

* **Testing:** pytest (Python), Vitest (TypeScript/React)
* **Code Quality:** Black, isort, mypy (Python), ESLint, Prettier (TypeScript)
* **Containerization:** Docker with multi-stage builds
* **Development Environment:** Docker Compose for local orchestration

> **Note:** For local development and integration testing, you can use `run_all_servers.py` to start all MCP servers in parallel without Docker. This is for developer convenience only; Docker Compose will be the standard for full-stack and production workflows.

* **Process Management:** uvicorn for FastAPI, npm scripts for React

## 4. Infrastructure & Architecture

### Architecture Overview


**Distributed MCP Server Orchestration:**
The MVP agent acts as a protocol-driven coordinator across specialized MCP servers, each handling domain-specific APIs and data sources. For each user query, the agent always follows the same structured workflow: geocoding, then POI search, then Wikipedia enrichment. Each MCP server exposes its tool(s) via the MCP protocol, and the agent invokes them in a fixed sequence. Dynamic tool selection and agent autonomy are planned for future phases, but are not part of the current implementation. This protocol-driven orchestration enables extensibility and future autonomy not achievable with static function-calling approaches.

### Component Tree & Mapping

```
MCP Travel Agent System
├── React TypeScript Frontend
│   ├── Chat Interface Component → PRD: Natural Language Interaction
│   ├── Conversation State Management → PRD: User Stories
│   ├── Response Streaming Display → Real-time agent responses
│   └── Error Boundary & Loading States
│
├── FastAPI Backend + GPT-4o-mini Agent Orchestrator
│   ├── Intent Classification Engine → PRD: Natural Language Processing
│   ├── Workflow Coordination → PRD: Structured Travel Planning
│   ├── Intent Analysis Engine → PRD: User Preference Interpretation
│   ├── Error Recovery Handler → PRD: Error Recovery
│   ├── Response Synthesis → PRD: Dynamic Result Synthesis
│   └── Conversation Memory Store → PRD: User Preference Memory
│
├── Geocoding FastMCP Server (Python)
│   ├── OSM Nominatim Wrapper → PRD: geocode_tool
│   ├── Location Resolution Logic
│   └── Coordinate Validation & Caching
│
├── POI Discovery FastMCP Server (Python)
│   ├── Overpass API Wrapper → PRD: poi_search_tool
│   ├── Category-based Search Logic
│   └── Result Filtering & Ranking
│
├── Wikipedia FastMCP Server (Python)
│   ├── Wikipedia API Wrapper → PRD: wikipedia_lookup_tool
│   ├── Content Extraction & Summarization
│   └── Multi-language Support
```

### Detailed Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     React TypeScript Frontend                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Chat UI       │  │ Conversation    │  │ Response        │ │
│  │   Component     │  │ State Store     │  │ Streaming       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │ Streamable HTTP / SSE
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 FastAPI Backend + GPT-4o-mini Agent            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Intent Analysis │  │ Tool Selection  │  │ Response Synth  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                    │              │              │              │
                    ▼              ▼              ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │  Geocoding   │ │ POI Discovery│ │  Wikipedia   │
            │FastMCP Server│ │FastMCP Server│ │FastMCP Server│
            │              │ │              │ │              │
            │ Nominatim    │ │ Overpass API │ │ Wikipedia    │
            │ Integration  │ │ Integration  │ │ Integration  │
            └──────────────┘ └──────────────┘ └──────────────┘
```

### Environments

* **Development:** Local Docker Compose with hot reload for both Python backend and React frontend
* **Testing:** Isolated pytest environment with mocked external APIs and TypeScript test runner
* **Demo:** Single-machine deployment optimized for proof-of-concept demonstrations

### Deployment Strategy

* **Frontend:** Vite build output served as static files or via CDN
* **Backend:** FastAPI with uvicorn in Docker containers
* **MCP Servers:** Individual FastMCP containers with health checks
* **Service Discovery:** Agent maintains registry of available MCP servers with load balancing
* **Development Workflow:** Docker Compose with volume mounts for live code reloading

### Communication Patterns

```
User Input → React Frontend → FastAPI Backend → GPT-4o-mini Agent Decision → 
[Parallel/Sequential MCP Server Calls] → Response Synthesis → 
Streamable HTTP (chunked) / SSE (fallback) → Real-time Frontend Updates
```

## 5. Dependencies & Integrations

### External APIs & Rate Limits

* **OpenAI GPT-4o-mini API** — Primary agent reasoning engine (Cost-optimized, 200K context)
* **OpenStreetMap Nominatim** — Geocoding and location resolution (1 request/second per IP)
* **Overpass API** — POI discovery and geographic queries (Reasonable use policy, \~10MB/query limit)
* **Wikipedia API** — Article content and summaries (5000 requests/hour per IP)

### Key Python Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
mcp = {version="^0.8.0", extras=["cli"]}  # MCP SDK with CLI tools
openai = "^1.3.0"  # GPT-4o-mini integration
httpx = "^0.25.0"  # Async HTTP client
pydantic = "^2.5.0"  # Data validation
python-multipart = "^0.0.6"  # File upload support
python-jose = {extras = ["cryptography"], version = "^3.3.0"}

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
black = "^23.9.0"
isort = "^5.12.0"
mypy = "^1.6.0"
```

### Key Frontend Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.2.0",
    "zustand": "^4.4.0",
    "axios": "^1.5.0",
    "@headlessui/react": "^1.7.0",
    "tailwindcss": "^3.3.0",
    "@heroicons/react": "^2.0.0"
  },
  "devDependencies": {
    "vite": "^4.4.0",
    "vitest": "^0.34.0",
    "@testing-library/react": "^13.4.0",
    "eslint": "^8.50.0",
    "@typescript-eslint/parser": "^6.7.0",
    "prettier": "^3.0.0"
  }
}
```

## 6. Risks & Mitigations

| Risk                                  | Impact                            | Probability | Mitigation Strategy                                                        |
| :------------------------------------ | :-------------------------------- | :---------- | :------------------------------------------------------------------------- |
| **GPT-4o-mini API Rate Limiting**     | Agent workflow failures           | Medium      | Implement exponential backoff, request queuing, usage monitoring dashboard |
| **External API Rate Limiting**        | Degraded functionality            | High        | Aggressive caching (Redis), request batching, fallback data sources        |
| **MCP Server Communication Failures** | Partial functionality loss        | Medium      | Health checks, circuit breakers, graceful degradation to available tools   |
| **Complex Agent Reasoning Loops**     | Performance/cost issues           | Medium      | Token usage monitoring, conversation turn limits, timeout controls         |
| **React State Management Complexity** | Frontend bugs                     | Low         | TypeScript strict mode, comprehensive testing, simple state patterns       |
| **Learning Objective Scope Creep**    | Timeline delays                   | High        | Weekly sprint reviews, strict 80/20 adherence, feature freeze after Week 4 |
| **Over-Engineering MCP Patterns**     | Complexity without learning value | Medium      | Focus on demonstrable patterns, avoid premature abstractions               |
| **Development Environment Setup**     | Team onboarding delays            | Low         | Comprehensive Docker Compose setup, detailed README instructions           |

**Sprint 5 Enhancement - TODO: OAuth TokenVerifier stub** for future enhancement of MCP authentication patterns.

## 7. Planning Process & Updates

### Planning Methodology

* **Sprint-based Learning:** Weekly iterations with measurable MCP orchestration pattern demonstrations
* **Test-Driven MCP Development:** Each agent orchestration feature validated through automated test scenarios
* **Continuous Integration:** Automated testing of agent decision-making accuracy and tool selection

### Responsibility Matrix

* **Backend/MCP Architecture:** Python developer defines server boundaries and agent orchestration logic
* **Frontend/UX:** React TypeScript developer creates intuitive chat interface with real-time updates
* **Integration Testing:** Cross-stack validation of agent workflows and error handling
* **Learning Validation:** Each sprint demonstrates specific MCP orchestration concepts from PRD

### Development Workflow

```
Feature Branch → Local Testing (Docker Compose) → 
MCP Integration Tests → Code Review → 
Agent Behavior Validation → Merge to Main
```

### Change Management

* **Daily Standups:** Track MCP learning progress and technical blockers
* **Weekly Sprint Reviews:** Validate agent orchestration patterns meet learning objectives
* **Architecture Decision Records:** Document key MCP patterns and design decisions
* **Backlog Refinement:** Maintain strict focus on demonstrable agent orchestration value

### Success Metrics Tracking

* **MCP Protocol Mastery:** ≥95% successful workflow coordination in standardized test scenarios
* **Intent Analysis Quality:** ≥80% accurate user preference extraction
* **Error Recovery:** ≥75% graceful degradation during simulated API failures
* **Performance:** <3 second average response time for simple queries, <10 seconds for complex multi-tool workflows
* **Learning Documentation:** Comprehensive capture of MCP orchestration patterns for knowledge transfer

### Communication & Documentation

* **Sprint Retrospectives:** Weekly learning extraction and process improvement
* **Technical Blog Posts:** Document key MCP orchestration discoveries for broader community
* **Demo Preparation:** End-of-sprint demonstrations of agent behavior patterns
* **Knowledge Transfer:** Structured documentation of reusable MCP orchestration patterns

## 8. Development Setup & Quick Start

### Prerequisites

* Python 3.11+
* Node.js 18+
* Docker & Docker Compose
* OpenAI API key

### Local Development Environment

```bash
# Clone and setup backend
git clone <repo-url>
cd mcp-travel-agent
poetry install
poetry run python -m pytest  # Verify setup

# Setup frontend
cd frontend
npm install
npm run dev  # Start development server

# Start all MCP servers
docker-compose up -d  # Starts all 4 MCP servers + Redis cache

# Start main agent orchestrator
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

```bash
# .env file
OPENAI_API_KEY=sk-...
NOMINATIM_USER_AGENT=mcp-travel-agent/1.0
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

> For requirements, see `PRD.md`. For agent workflow details, see `AGENTS.md`. For step-by-step implementation of planning and PRD, consult `Tasks.md`.

---
