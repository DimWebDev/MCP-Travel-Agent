# Tasks.md

##Step-by-Step Implementation

For each major feature or milestone, break down the implementation into clear, sequential steps. Reference PRD and Planning sections for context.

### Task T001: Set Up Project Structure and Poetry Environment

- [x] Initialize Git repository with `git init` and create .gitignore file
- [x] Create pyproject.toml with exact dependencies from Planning\#3 technical stack
- [x] Run `poetry install` and `poetry shell` to set up virtual environment
- [x] Create directory structure following Planning\#4 component architecture
- [x] Create .env.example with all environment variables from Planning\#5
- [x] Create empty __init__.py files in all Python packages
- [x] Verify setup with `poetry run python --version` and import tests
- [x] Document setup process in README.md (Planning\#8)


### Task T002: Create Geocoding MCP Server

- [x] Create app/mcp_servers/geocoding/server.py with OSM Nominatim wrapper (PRD\#4.1)
- [x] Implement rate limiting (1 req/sec) as specified in Planning\#5 dependencies
- [x] Add GeocodeRequest and GeocodeResponse Pydantic models for validation
- [x] Implement error handling for timeouts, HTTP errors, and API failures
- [x] Annotate function with `@mcp.tool()` from FastMCP
- [x] Write unit tests with mocked HTTP responses in tests/unit/test_geocoding.py
- [x] Create Dockerfile for containerized deployment (Planning\#4)
- [x] Test server manually with sample location queries



### Task T003: Create POI Discovery MCP Server

- [x] Create app/mcp_servers/poi_discovery/server.py with Overpass API wrapper (PRD#4.2)
- [x] Implement category mappings (tourism, historic, restaurant, entertainment, shopping)
- [x] Build Overpass QL query generator for different POI categories
- [x] Add result filtering and ranking logic based on distance.
- [x] Implement POISearchRequest and POIResult Pydantic models
- [x] Annotate function with `@mcp.tool()` from FastMCP
- [x] Write comprehensive unit tests with mocked Overpass API responses
- [x] Create Dockerfile and test with sample coordinate queries


### Task T004: Create Wikipedia MCP Server

- [ ] Create app/mcp_servers/wikipedia/server.py with Wikipedia API wrapper (PRD\#4.3)
- [ ] Implement content extraction and summarization logic
- [ ] Add rate limiting (5000 req/hour) as specified in Planning\#5
- [ ] Create WikipediaRequest and WikipediaResponse Pydantic models
- [ ] Implement multi-language support detection for international POIs
- [ ] Annotate function with `@mcp.tool()` from FastMCP
- [ ] Write unit tests with mocked Wikipedia API responses
- [ ] Create Dockerfile and test with sample POI name queries

#### Task T004-extra: Wikipedia MCP Server Extras

- [ ] Expose `/resources/city-guides/{city}.md` using `@mcp.resource` for static city-guide blurbs
- [ ] Implement multi-language support detection for international POIs (**DEFERRED** – English only for MVP)


### Task T005: Create Trivia MCP Server

- [ ] Create app/mcp_servers/trivia/server.py with DuckDuckGo API wrapper (PRD\#4.4)
- [ ] Implement instant answer extraction and fact discovery logic
- [ ] Add source reliability scoring and content filtering
- [ ] Create TriviaRequest and TriviaResponse Pydantic models
- [ ] Implement context matching for travel-relevant facts
- [ ] Annotate function with `@mcp.tool()` from FastMCP
- [ ] Write unit tests with mocked DuckDuckGo API responses
- [ ] Create Dockerfile and test with sample topic queries


### Task T006: Implement Basic FastAPI Agent Orchestrator

 - [ ] **CLI-first** The initial entry point should be a REPL or CLI that takes user queries from the terminal, orchestrates calls to MCP tools, and prints results. FastAPI endpoints will be layered in after CLI orchestration is functional.
 - [ ] Add basic HTTP/JSON wrapper in FastAPI so you can later swap in a browser UI
- [ ] Implement MCP client connections to all 4 servers (Planning\#4 architecture)
- [ ] Create agent request/response models with Pydantic validation
- [ ] Add health check endpoints for all MCP servers
- [ ] Configure CORS middleware for React frontend integration (Planning\#3)
- [ ] Implement structured logging for agent decisions and tool calls
- [ ] Add basic error handling and timeout management
- [ ] Test agent-to-MCP-server communication with sample requests

### Task T006-extra: Intelligent Radius Defaulting (OPTIONAL)

- **Dependencies:** Requires T002 (Geocoding) and T003 (POI Discovery) to be completed
- Add logic in the orchestrator so that every call to `search_pois` carries a sensible `radius` 
  based on:
  - Urban vs rural density (using the geocoding result)
  - POI category (e.g. ≤800 m for restaurants, 2 km for attractions)
  - User intent keywords (e.g. "nearby", "around")
- Ensure this defaulting is unit-tested.
- Update the FastAPI endpoint Pydantic model to accept an optional `radius` (with `None` default), 
  and fill in the orchestrated default before calling the MCP server.
- Document the policy in code comments and in the OpenAPI schema (so it shows up in `/docs`).



### Task T007: Set Up Docker Compose Development Environment

- [ ] Create docker-compose.yml with all 5 services (4 MCP servers + agent)
- [ ] Configure internal networking between containers (Planning\#4)
- [ ] Add Redis container for caching as specified in Planning\#3
- [ ] Set up volume mounts for development hot-reload
- [ ] Configure environment variable passing from .env file
- [ ] Add health checks for all services with proper timeouts
- [ ] Create startup script for development environment
- [ ] Test full environment startup and verify service discovery


### Task T008: Implement GPT-4o-mini Integration with Function Calling

- [ ] Install and configure OpenAI Python library with API key handling
- [ ] Create GPT-4o-mini client following Planning\#3 specifications
- [ ] Implement function calling schema for all 4 MCP tools (PRD\#4)
- [ ] Add conversation context management and memory
- [ ] Implement token usage monitoring as specified in Planning\#6 risks
- [ ] Add retry logic with exponential backoff for API failures
- [ ] Create unit tests with mocked OpenAI responses
- [ ] Add cost tracking and usage limits to prevent overruns


### Task T009: Create Intent Classification Logic

- [ ] Design user intent categories (historical, food, family, budget) from PRD\#2 user stories
- [ ] Implement prompt engineering for GPT-4o-mini intent extraction
- [ ] Create intent classification with confidence scoring
- [ ] Add fallback handling for unclear or ambiguous intents
- [ ] Implement context-aware intent refinement based on conversation history
- [ ] Create test cases for all user story scenarios from PRD\#2
- [ ] Add intent classification accuracy metrics and logging
- [ ] Document intent classification patterns for future enhancement


### Task T010: Build Dynamic Tool Selection Engine

- [ ] Implement tool selection logic based on classified user intents (PRD\#3)
- [ ] Create decision tree for single vs multi-tool execution patterns
- [ ] Add contextual parameter passing to selected MCP tools
- [ ] Implement parallel vs sequential tool execution logic
- [ ] Add tool availability checking and fallback strategies
- [ ] Create comprehensive tool selection test suite with edge cases
- [ ] Add detailed logging for agent decision tracking and debugging
- [ ] Validate ≥90% tool selection accuracy as specified in PRD\#7


### Task T011: Implement Basic Agent Decision-Making Tests

- [ ] Create automated test scenarios for all user stories from PRD\#2
- [ ] Implement tool selection accuracy testing with standardized inputs
- [ ] Add test cases for edge cases and error conditions
- [ ] Create performance benchmarks for agent response times (<3s simple queries)
- [ ] Implement test data fixtures for repeatable testing scenarios
- [ ] Add continuous integration test runner with GitHub Actions
- [ ] Create test reporting dashboard for monitoring agent behavior
- [ ] Validate core MCP learning objectives from PRD\#1 are demonstrable


### Task T012: Build Multi-Step Workflow Coordination

- [ ] Implement workflow orchestration engine for tool chaining (PRD\#5.2)
- [ ] Create dependency management between sequential tool calls
- [ ] Add conditional logic for tool execution based on previous results
- [ ] Implement workflow state management and progress tracking
- [ ] Add support for iterative refinement when initial results are poor
- [ ] Create workflow visualization for debugging complex agent decisions
- [ ] Write comprehensive workflow testing with multi-step scenarios
- [ ] Document common workflow patterns for knowledge transfer


### Task T013: Implement Contextual Result Synthesis

- [ ] Create result aggregation logic for combining multiple tool outputs (PRD\#3)
- [ ] Implement intelligent response generation using GPT-4o-mini synthesis
- [ ] Add contextual ranking of information importance based on user intent
- [ ] Create natural language response templates for different scenarios
- [ ] Implement citation and source attribution for transparency
- [ ] Add response quality assessment metrics and validation
- [ ] Create A/B testing framework for response quality improvement
- [ ] Validate response synthesis meets user story expectations from PRD\#2


### Task T014: Create React TypeScript Chat Interface

- [ ] Set up Vite + React + TypeScript project following Planning\#3 frontend stack
- [ ] Install and configure Tailwind CSS and Headless UI components
- [ ] Create chat message components with proper TypeScript interfaces
- [ ] Implement streaming with **fetch() & ReadableStream over `/mcp` (Streamable HTTP)**; keep SSE adapter for legacy
- [ ] Add conversation history display using Zustand state management
- [ ] Create loading states, error boundaries, and user feedback mechanisms
- [ ] Add responsive design for mobile and desktop viewports
- [ ] Implement accessibility features (ARIA labels, keyboard navigation)


### Task T015: Add Conversation State Management

- [ ] Implement conversation context storage in FastAPI backend
- [ ] Create user preference tracking across conversation sessions
- [ ] Add conversation history persistence with Redis caching
- [ ] Implement context-aware follow-up question handling
- [ ] Create conversation reset and clearing functionality
- [ ] Add conversation export/import capabilities for user data
- [ ] Test conversation continuity across browser sessions
- [ ] Add conversation analytics and insights for improvement


### Task T016: Implement Error Recovery and Fallback Strategies

- [ ] Create comprehensive error classification system for all failure modes
- [ ] Implement graceful degradation when individual MCP servers fail (Planning\#6)
- [ ] Add alternative tool usage when primary tools are unavailable
- [ ] Create user-friendly error messages and recovery suggestions
- [ ] Implement automatic retry logic with exponential backoff
- [ ] Add circuit breaker patterns for consistently failing services
- [ ] Create error recovery test scenarios and validation
- [ ] Validate ≥75% successful error recovery as specified in PRD\#7


### Task T017: Add Retry Logic and Circuit Breakers

- [ ] Implement exponential backoff for external API failures (Planning\#6)
- [ ] Create circuit breaker implementations for each MCP server
- [ ] Add health monitoring and automatic service recovery detection
- [ ] Implement request queuing during temporary service failures
- [ ] Create fallback data sources for critical geocoding and POI functions
- [ ] Add monitoring dashboards for service health visualization
- [ ] Test all failure scenarios and recovery patterns systematically
- [ ] Document error handling best practices for team knowledge


### Task T018: Create Comprehensive Integration Tests

- [ ] Create end-to-end test scenarios covering all user stories from PRD\#2
- [ ] Implement test automation for complete agent orchestration workflows
- [ ] Add performance testing for complex multi-tool query scenarios
- [ ] Create load testing for concurrent user scenarios and rate limits
- [ ] Implement test data management and cleanup procedures
- [ ] Add integration test reporting with detailed metrics and insights
- [ ] Create continuous integration pipeline with automated testing
- [ ] Validate all success metrics specified in PRD\#7 are achievable


### Task T019: Implement Graceful Degradation Patterns

- [ ] Create service availability detection for all external APIs
- [ ] Implement reduced functionality modes when services are unavailable
- [ ] Add clear user notifications of service limitations and alternatives
- [ ] Create offline/cached response capabilities for common queries
- [ ] Implement progressive enhancement patterns for optional features
- [ ] Add service restoration detection and automatic re-enabling
- [ ] Test all degradation scenarios with systematic validation
- [ ] Document degradation behavior and user communication strategies


### Task T020: Add Conversation Memory and Context Retention

- [ ] Implement long-term conversation context storage beyond session
- [ ] Create user preference learning from conversation interaction history
- [ ] Add personalization based on past travel interests and queries
- [ ] Implement conversation topic tracking and continuity management
- [ ] Create conversation summarization for very long interaction sessions
- [ ] Add privacy controls and data retention policies for user conversations
- [ ] Test context retention across multiple conversation sessions
- [ ] Validate improved recommendation quality with conversation memory


### Task T021: Implement Follow-up Question Handling

- [ ] Create context-aware question interpretation for follow-up queries
- [ ] Implement reference resolution for pronouns and contextual references
- [ ] Add clarification request generation when context is ambiguous
- [ ] Create conversation flow optimization for natural dialogue patterns
- [ ] Implement topic continuation and smooth topic switching detection
- [ ] Add intelligent follow-up suggestion generation for user guidance
- [ ] Test complex multi-turn conversation scenarios thoroughly
- [ ] Validate natural conversation flow meets user experience expectations


### Task T022: Performance Optimization and Caching

- [ ] Implement Redis caching for frequent external API calls (Planning\#5)
- [ ] Add response caching with appropriate TTL management for different data types
- [ ] Optimize GPT-4o-mini prompt engineering for faster response generation
- [ ] Implement connection pooling for all MCP server communications
- [ ] Add response compression and data transfer optimization
- [ ] Create performance monitoring and alerting for response time tracking
- [ ] Implement intelligent cache invalidation strategies for dynamic data
- [ ] Validate <3s response time for simple queries as specified in Planning\#7


### Task T023: Create Demo Documentation and Presentation

- [ ] Create comprehensive demo script showcasing all MCP orchestration features
- [ ] Prepare presentation materials highlighting key learning outcomes from PRD\#1
- [ ] Document all discovered MCP orchestration patterns for knowledge transfer
- [ ] Create video demonstrations of agent behavior in different scenarios
- [ ] Prepare technical deep-dive documentation for architecture decisions
- [ ] Create deployment guide for setting up demo environment
- [ ] Prepare comprehensive Q\&A materials for technical questions
- [ ] Validate all learning objectives from PRD\#1 are clearly demonstrable


## 5. Task Discovery \& Updates

**New Task Discovery Process:**
When new tasks emerge during implementation (common in AI agent development), follow this structured process:

1. **Immediate Documentation:** Add new task to this Tasks.md file with proper ID, description, and sprint assignment
2. **Impact Assessment:** Evaluate if new task requires updates to Planning.md architecture or PRD.md requirements
3. **Sprint Planning Integration:** Assign to current or future sprint based on priority and MCP learning value
4. **Learning Validation:** Ensure new task contributes to core MCP orchestration objectives from PRD\#1

> For requirements, see `PRD.md`. For planning and architecture, see `Planning.md`. For agent workflow, see `AGENTS.md`.

