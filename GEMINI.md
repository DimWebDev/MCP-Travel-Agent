# GEMINI.md

This document provides a comprehensive overview of the MCP Travel Agent project, tailored for a Gemini agent. It includes information from `AGENTS.md` and the codebase analysis.

## 1. Project Overview

The MCP Travel Agent is a Python-based application that uses a multi-agent system to provide travel recommendations. It leverages several microservices for functionalities like geocoding, point-of-interest discovery, and Wikipedia integration. The project is orchestrated using the MCP (Multi-Agent Collaboration Protocol).

## 2. Development Workflow and Available tools

1.  **Codebase Analysis:** Before diving deep into the codebase, use the `analyze_codebase` tool to gain an initial understanding of the project structure, dependencies, and key components.
2.  **Review Project Documentation:** Before starting work, consult `PRD.md`, `Planning.md`, and `Tasks.md` and `README.md`.
3.  **Focused Changes:** Each pull request should address a single feature or fix, including tests and documentation.
4.  **No Secrets in Code:** Use environment variables for API keys and other sensitive information.
5.  **Clear Documentation:** Write clear, self-documenting code with clear comments. Adhere to Python best practices.
6.  **Seek Clarification:** Ask for help when requirements or architecture are unclear.
7.  **Update Tasks:** If new tasks are discovered during development, update `Tasks.md` to include them.
8.  **Use Context7 for Documentation:** When implementing a new feature, use the `context7` tools to retrieve the latest documentation for the technologies you are using.

## 3. Code Standards

*   **Best Practices:** Adhere to Python best practices.
*   **Clarity:** Code must be clear and self-documenting, with clear comments.
*   **Formatting:** Use consistent formatting and linting tools.
*   **Typing and Documentation:** Include type hints and documentation for public APIs.
*   **Naming Conventions:** Follow Python's naming conventions.
*   **MCP-Specific:**
    *   Clearly document agent decision-making logic.
    *   Implement robust error handling and fallback strategies.
    *   Use structured logging for debugging.
    *   Validate responses from external APIs.

## 4. Security

*   Never commit API keys or other sensitive data.
*   Sanitize all user inputs.

## 5. Git Guidelines

*   **Commit Messages:**
    ```
    [type]: brief description of change

    WHY: Context or problem being solved
    WHAT: Summary of the change made
    ```
    *   **Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `mcp`, `agent`, `orchestration`
*   **Pull Requests:**
    *   Provide a clear description of changes and testing instructions.
    *   Reference related tasks or issues.
    *   Ensure all tests pass and documentation is updated.
*   **Branch Naming:**
    *   `feature/<description>`
    *   `fix/<description>`
    *   `docs/<description>`

## 6. Codebase Analysis

### Project Structure

The project is organized into two main directories: `app` and `tests`.

*   `app`: Contains the main application logic, including the agent, MCP servers, and CLI.
    *   `agent`: Core agent logic, including clients, models, orchestrator, and query parser.
    *   `mcp_servers`: Microservices for geocoding, POI discovery, and Wikipedia.
*   `tests`: Contains unit and integration tests.

### Key Files

*   `app/main.py`: Main entry point for the application.
*   `app/agent/orchestrator.py`: The core of the agent, responsible for orchestrating the different services.
*   `app/agent/query_parser.py`: Parses user queries.
*   `run_all_servers.py`: A script to run all the MCP servers.

### Dependencies

The project uses several external libraries, including:

*   `fastapi`: For building the web servers.
*   `httpx`: For making HTTP requests.
*   `openai`: For interacting with the OpenAI API.
*   `pydantic`: For data validation.
*   `pytest`: For testing.

### Architectural Patterns

*   **Microservices:** The application is built using a microservices architecture, with separate services for different functionalities.
*   **MCP:** The Multi-Agent Collaboration Protocol is used to orchestrate the different agents and services.
*   **Logging:** The project uses structured logging for debugging.
*   **Middleware:** FastAPI middleware is used for CORS.
*   **Configuration Management:** Environment variables are used for configuration.

## 7. Important Documents

For detailed requirements, architecture, and implementation steps, see `PRD.md`, `Planning.md`, and `Tasks.md` and `README.md`.

