# Tasks.md

> **MCP Workflow Principle (MVP)**  
> The agent **always executes a fixed, protocol-driven sequence**  
> **Geocode → POI → Wikipedia** for every query.  
> Dynamic tool discovery/selection is **out of scope for Phase 1**, deferred to Phase 2.

## Step-by-Step Implementation

For each major feature or milestone, break down the implementation into clear, sequential steps. Reference **PRD.md** and **Planning.md** for context.

---

### Task T001: Set Up Project Structure and Poetry Environment

- [x] Initialize Git repository with `git init` and create .gitignore file  
- [x] Create pyproject.toml with exact dependencies from Planning#3 technical stack  
- [x] Run `poetry install` and `poetry shell` to set up virtual environment  
- [x] Create directory structure following Planning#4 component architecture  
- [x] Create .env.example with all environment variables from Planning#5  
- [x] Create empty `__init__.py` files in all Python packages  
- [x] Verify setup with `poetry run python --version` and import tests  
- [x] Document setup process in README.md (Planning#8)  

---

### Task T002: Create Geocoding MCP Server

- [x] Create app/mcp_servers/geocoding/server.py with OSM Nominatim wrapper (PRD#4.1)  
- [x] Implement rate limiting (1 req/sec) as specified in Planning#5 dependencies  
- [x] Add GeocodeRequest and GeocodeResponse Pydantic models for validation  
- [x] Implement error handling for timeouts, HTTP errors, and API failures  
- [x] Annotate function with `@mcp.tool()` from FastMCP  
- [x] Write unit tests with mocked HTTP responses in tests/unit/test_geocoding.py  
- [x] Create Dockerfile for containerized deployment (Planning#4)  
- [x] Test server manually with sample location queries  

---

### Task T003: Create POI Discovery MCP Server

- [x] Create app/mcp_servers/poi_discovery/server.py with Overpass API wrapper (PRD#4.2)  
- [x] Implement category mappings (tourism, historic, restaurant, entertainment, shopping)  
- [x] Build Overpass QL query generator for different POI categories  
- [x] Add result filtering and ranking logic based on distance  
- [x] Implement POISearchRequest and POIResult Pydantic models  
- [x] Annotate function with `@mcp.tool()` from FastMCP  
- [x] Write comprehensive unit tests with mocked Overpass API responses  
- [x] Create Dockerfile and test with sample coordinate queries  

---

### Task T004: Create Wikipedia MCP Server

- [x] Create app/mcp_servers/wikipedia/server.py with Wikipedia API wrapper (PRD#4.3)  
- [x] Implement content extraction and summarization logic  
- [x] Add rate limiting (5000 req/hour) as specified in Planning#5  
- [x] Create WikipediaRequest and WikipediaResponse Pydantic models  
- [x] Annotate function with `@mcp.tool()` from FastMCP  
- [x] Write unit tests with mocked Wikipedia API responses  
- [x] Create Dockerfile and test with sample POI name queries  

#### Task T004-extra: Wikipedia MCP Server Extras

- [ ] Expose `/resources/city-guides/{city}.md` using `@mcp.resource` for static city-guide blurbs  
- [ ] Implement multi-language support detection for international POIs (**DEFERRED** – English only for MVP)  

---

### Task T006: Implement Basic FastAPI Agent Orchestrator

> **Dev Note:** During local development, agent orchestration and integration can be tested by running all MCP servers in parallel with `run_all_servers.py`. This script is for rapid iteration and should be replaced by Docker Compose for full-stack and production testing.

- **Fixed workflow additions:**  
  - Hard-code the 3-step chain: `geocode_location → search_pois → get_wikipedia_info`.  
  - Compute Haversine `distance_meters` for each POI.  
  - Enrich each POI with Wikipedia `{title, summary, url}`; use `null` if no match.  
  - Return JSON list sorted by `distance_meters` and limited by the `limit` parameter.  

- [x] **CLI-first**: Initial entry point is a REPL/CLI for user queries, orchestrates calls, prints results.  
- [x] Add basic HTTP/JSON wrapper in FastAPI for future browser UI.  
- [x] Implement MCP client connections to all 3 servers (Planning#4 architecture).  
- [x] Create agent request/response models with Pydantic validation.  
- [x] Add health check endpoints for all MCP servers.  
- [x] Configure CORS middleware for React frontend integration (Planning#3).  
- [x] Implement structured logging for agent decisions and tool calls.  
- [x] Add basic error handling and timeout management.  
- [x] Test agent-to-MCP-server communication with sample requests.  

---

#### Task T006-extra: Intelligent Radius Defaulting (OPTIONAL)

- [ ] **Dependencies:** T002 and T003 completed  
- [ ] Add orchestrator logic so every `search_pois` call uses a sensible `radius` based on:  
  - [ ] Urban vs. rural density  
  - [ ] POI category (e.g., ≤800 m for restaurants, 2 km for attractions)  
  - [ ] User keywords (“nearby”, “around”)  
- [ ] Ensure this defaulting is unit-tested.  
- [ ] Update FastAPI endpoint model to accept an optional `radius`.  
- [ ] Document policy in code comments and OpenAPI schema.  

---

### Task T007: GPT-4o-mini Integration with Fixed Workflow

- [ ] Install and configure OpenAI Python library with API key handling.
- [ ] Implement natural language query processing to extract location and preferences from user input.
- [ ] Create CLI interface that accepts queries like "Show me historical sites in Rome" or "Find romantic restaurants in Paris".
- [ ] Extract structured parameters (location, category keywords) to feed the fixed 3-step workflow.
- [ ] Invoke the fixed sequence: geocode_location → search_pois → get_wikipedia_info.
- [ ] Add MCP protocol error handling and retry logic.
- [ ] Create tests with realistic natural language inputs, not just curl commands, such as:
    - "What can I do in Barcelona for a romantic evening?"
    - "Show me family-friendly activities in London"
    - "I want to explore historical sites in Rome"


---

### Task T008: Create Intent Classification Logic **(DEFERRED – PHASE 2)**

- [ ] Placeholder for future dynamic intent extraction and categorization.  

---

### Task T009: Build Dynamic Tool Selection Engine **(DEFERRED – PHASE 2)**

- [ ] Placeholder for future autonomous tool-selection implementation.  

---

### Task T010: End-to-End Workflow Tests

- [ ] Create CLI test scenarios using natural language queries from PRD#2 user stories.
- [ ] Test the complete user journey: CLI input → GPT processing → MCP orchestration → formatted output.
- [ ] Assert output schema fields: `name`, `distance_meters`, `lat`, `lon`, `type`, `summary`, `url`.
- [ ] Verify `distance_meters` ascending order and that the limit parameter is respected.
- [ ] Confirm `wikipedia` field is `null` when no article is found.
- [ ] Test with diverse natural language inputs:
    - Clear queries: "Museums in Berlin"
    - Ambiguous queries: "Cool places in NYC"
    - Multi-intent queries: "Romantic dinner spots with history in Florence"
- [ ] Performance benchmarks: <3s for simple queries via CLI.
- [ ] Add automated test runner that simulates realistic user conversations.


---

### Task T011: Build Multi-Step Workflow Coordination **(MERGED INTO T006 for MVP)**

- [ ] Coordination logic is already in T006 via the fixed 3-step chain.  

---

### Task T012: Implement Contextual Result Synthesis

- [ ] Process GPT-4o-mini extracted intent to determine POI search parameters.
- [ ] Aggregate POIs from MCP servers, compute `distance_meters`, and enrich with Wikipedia data.
- [ ] Format human-readable responses for CLI output, not just JSON.
- [ ] Sort by distance and apply reasonable limits (e.g., top 10 POIs).
- [ ] Handle edge cases gracefully:
    - No POIs found for location
    - Wikipedia data unavailable
    - Ambiguous location names
- [ ] Test with CLI commands like:
    - `python agent_cli.py "Find historic sites near the Colosseum"`
    - `python agent_cli.py "Budget-friendly food in Tokyo"`

---

### Task T013: Set Up Docker Compose Development Environment

- [ ] Create `docker-compose.yml` with all 4 services (3 MCP servers + agent).  
- [ ] Configure internal networking (Planning#4).  
- [ ] Add Redis container for caching (deferred if needed).  
- [ ] Set up volume mounts for hot-reload.  
- [ ] Configure env var passing from `.env`.  
- [ ] Add health checks with timeouts.  
- [ ] Create startup script for development environment.  
- [ ] Test full environment startup and verify service discovery.  

---

### Task T014: Create React TypeScript Chat Interface **(STRETCH – PHASE 2+)**

- [ ] Set up Vite + React + TypeScript (Planning#3).  
- [ ] Install Tailwind CSS and Headless UI.  
- [ ] Create chat components with TypeScript interfaces.  
- [ ] Implement streaming via `fetch()` & ReadableStream over `/mcp`.  
- [ ] Add conversation history via Zustand.  
- [ ] Create loading states, error boundaries.  
- [ ] Ensure responsive design and accessibility.  

---

### Task T015: Add Conversation State Management **(STRETCH – PHASE 2+)**

- [ ] Implement conversation context storage in FastAPI.  
- [ ] Create user preference tracking across sessions.  
- [ ] Add Redis-backed persistence.  
- [ ] Implement follow-up question handling.  
- [ ] Create reset/clear functionality.  
- [ ] Add analytics.  

---

### Task T016: Implement Error Recovery and Fallback Strategies

- [ ] Classify all failure modes.  
- [ ] Graceful degradation when MCP servers fail.  
- [ ] Alternative tool usage within the fixed chain.  
- [ ] User-friendly error messages and suggestions.  
- [ ] Automatic retry with exponential backoff.  
- [ ] Circuit breaker patterns.  
- [ ] Create error recovery test scenarios.  
- [ ] Validate ≥75% graceful degradation.  

---

### Task T017: Add Retry Logic and Circuit Breakers **(MERGED INTO T016)**

- [ ] Covered by T016’s resilience scope.  

---

### Task T018: Create Comprehensive Integration Tests

- [ ] End-to-end tests covering all MVP flows.  
- [ ] Performance/load testing.  
- [ ] Cleanup procedures.  
- [ ] CI pipeline integration.  
- [ ] Validate PRD success metrics.  

---

### Task T019: Implement Graceful Degradation Patterns **(MERGED INTO T016)**

- [ ] Covered by T016’s resilience suite.  

---

### Task T020: Add Conversation Memory and Context Retention **(STRETCH – PHASE 2+)**

- [ ] Long-term context storage.  
- [ ] Personalization based on history.  
- [ ] Privacy controls.  

---

### Task T021: Implement Follow-up Question Handling **(STRETCH – PHASE 2+)**

- [ ] Context-aware reference resolution.  
- [ ] Clarification prompt generation.  
- [ ] Smooth topic switching.  

---

### Task T022: Performance Optimization and Caching **(STRETCH – PHASE 2+)**

- [ ] Redis caching for external calls.  
- [ ] Prompt/tokens optimization.  
- [ ] Connection pooling, compression.  
- [ ] Monitoring & alerts.  

---

### Task T023: Create Demo Documentation and Presentation

- [ ] Write demo script showcasing the fixed workflow and resilience.  
- [ ] Prepare slides highlighting learning objectives.  
- [ ] Document MCP orchestration patterns.  
- [ ] Record video demos.  
- [ ] Create Q&A materials.  
- [ ] Validate all learning objectives are demonstrable.  

---

## 5. Task Discovery & Updates

**New Task Discovery Process:**  
When new tasks emerge:
1. **Immediate Documentation:** Add new task with ID, description, sprint.  
2. **Impact Assessment:** Check if Planning.md or PRD.md updates required.  
3. **Sprint Planning:** Assign based on priority and MCP learning value.  
4. **Learning Validation:** Ensure new task aligns with core objectives.

> For requirements, see `PRD.md`. For planning and architecture, see `Planning.md`. For agent workflow, see `AGENTS.md`.
