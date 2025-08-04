"""FastAPI wrapper for the agent orchestrator.

Exposes HTTP endpoints for agent queries and health checks as outlined in
PRD.md §4 and Planning.md §4. CORS configuration supports the React frontend
from Planning.md §3.
"""

from __future__ import annotations

import logging
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent.models import AgentQuery, AgentResponse
from .agent.orchestrator import AgentOrchestrator, create_orchestrator

logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Travel Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator: AgentOrchestrator = create_orchestrator()


@app.post("/query", response_model=AgentResponse)
async def query_agent(request: AgentQuery) -> AgentResponse:
    """Invoke the orchestrator with the supplied query."""
    try:
        return await orchestrator.handle_query(request.query)
    except Exception as exc:  # pragma: no cover - network errors
        logger.exception("query failed", extra={"error": str(exc)})
        raise HTTPException(500, detail="Agent processing failed") from exc


@app.get("/health/{service}")
async def health(service: str) -> Dict[str, str]:
    """Health check for individual MCP servers."""
    client = orchestrator.clients.get(service)
    if not client:
        raise HTTPException(404, detail="unknown service")
    healthy = await client.health()
    if not healthy:
        raise HTTPException(503, detail="unhealthy")
    return {"status": "ok"}
