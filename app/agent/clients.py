"""Lightweight MCP client wrappers for the orchestrator.

These classes abstract the connection details to individual MCP servers so that
`AgentOrchestrator` can remain agnostic of transport specifics. The design
follows Planning.md §4 which calls for reusable client components.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger(__name__)


@dataclass
class MCPClient:
    """Generic MCP client wrapper.

    Attributes:
        server_url: Base URL of the MCP server (e.g. ``http://localhost:8001/mcp``)
        tool_name: Name of the MCP tool to invoke on this server
        timeout:   Per-request timeout in seconds
    """

    server_url: str
    tool_name: str
    timeout: float = 10.0

    async def call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the configured MCP tool with the provided payload."""
        try:
            async with streamablehttp_client(self.server_url, timeout=self.timeout) as (
                read,
                write,
                _,
            ):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        self.tool_name, {"request": payload}
                    )
                    return result.structuredContent or {}
        except Exception as exc:  # pragma: no cover - network failures
            logger.error(
                "tool call failed",
                extra={"tool": self.tool_name, "url": self.server_url, "error": str(exc)},
            )
            raise

    async def health(self) -> bool:
        """Basic health check by performing an initialize handshake."""
        try:
            async with streamablehttp_client(self.server_url, timeout=self.timeout) as (
                read,
                write,
                _,
            ):
                async with ClientSession(read, write) as session:
                    await session.initialize()
            return True
        except Exception as exc:  # pragma: no cover - network failures
            logger.error(
                "health check failed",
                extra={"url": self.server_url, "error": str(exc)},
            )
            return False
