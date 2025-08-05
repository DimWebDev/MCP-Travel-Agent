"""Agent orchestration logic coordinating MCP tool calls.

The `AgentOrchestrator` encapsulates the decision flow described in
Planning.md §4 and implements basic error handling and logging per AGENTS.md.
The design keeps orchestration independent from the CLI and FastAPI layers.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Awaitable, Callable, Dict

from .clients import MCPClient
from .models import AgentResponse, ToolResult
from .query_parser import parse_user_query

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Coordinate requests across multiple MCP servers."""

    def __init__(
        self,
        clients: Dict[str, MCPClient],
        timeout: float = 10.0,
        query_parser: Callable[[str], Awaitable[Dict[str, str]]] = parse_user_query,
    ):
        self.clients = clients
        self.timeout = timeout
        self.logger = logger
        self.query_parser = query_parser

    async def handle_query(self, query: str) -> AgentResponse:
        """Process a user query by invoking multiple MCP tools.

        Workflow:
            1. Use GPT-4o-mini to parse the location and category
            2. Geocode the location to obtain coordinates (PRD.md §4.1)
            3. Use coordinates and category to search for POIs (PRD.md §4.2)
            4. Fetch Wikipedia info about the location (PRD.md §4.3)
        """

        self.logger.info("handle_query", extra={"query": query})
        results: list[ToolResult] = []

        parsed = await self.query_parser(query)
        location = parsed.get("location", query)
        category = parsed.get("category", "tourism")

        try:
            geocode_data = await asyncio.wait_for(
                self.clients["geocoding"].call({"location_name": location}),
                timeout=self.timeout,
            )
            results.append(ToolResult(source="geocoding", data=geocode_data))
        except Exception as exc:  # pragma: no cover - error path
            self.logger.error("geocoding failed", extra={"error": str(exc)})
            geocode_data = None

        if geocode_data and {"lat", "lon"} <= geocode_data.keys():
            try:
                poi_payload = {
                    "latitude": geocode_data["lat"],
                    "longitude": geocode_data["lon"],
                    "category": category,
                }
                poi_data = await asyncio.wait_for(
                    self.clients["poi"].call(poi_payload), timeout=self.timeout
                )
                results.append(ToolResult(source="poi", data=poi_data))
            except Exception as exc:  # pragma: no cover - error path
                self.logger.error("poi search failed", extra={"error": str(exc)})

        # Wikipedia can run in parallel since it doesn't depend on others
        async def call_optional(name: str, payload: Dict[str, object]):
            try:
                data = await asyncio.wait_for(
                    self.clients[name].call(payload), timeout=self.timeout
                )
                results.append(ToolResult(source=name, data=data))
            except Exception as exc:  # pragma: no cover - error path
                self.logger.error(
                    "%s failed", name, extra={"error": str(exc)}
                )

        await asyncio.gather(
            call_optional("wikipedia", {"poi_name": location}),
        )

        return AgentResponse(results=results)


# ---------------------------------------------------------------------------
# Factory utilities
# ---------------------------------------------------------------------------


def create_orchestrator() -> AgentOrchestrator:
    """Create an orchestrator with default MCP clients.

    URLs can be configured via environment variables to support different
    deployment setups as described in Planning.md §3.
    """

    clients = {
        "geocoding": MCPClient(
            os.getenv("GEOCODING_SERVER_URL", "http://127.0.0.1:8001/mcp"),
            "geocode_location",
        ),
        "poi": MCPClient(
            os.getenv("POI_SERVER_URL", "http://127.0.0.1:8002/mcp"),
            "search_pois",
        ),
        "wikipedia": MCPClient(
            os.getenv("WIKIPEDIA_SERVER_URL", "http://127.0.0.1:8003/mcp"),
            "get_wikipedia_info",
        ),
    }
    return AgentOrchestrator(clients)
