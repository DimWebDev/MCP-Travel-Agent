"""Pydantic models for the agent orchestrator.

These models provide a shared contract between the CLI and FastAPI layers.
They are designed following the architecture in Planning.md §4 and the data
validation requirements outlined in PRD.md §4.
"""

from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field


class AgentQuery(BaseModel):
    """Natural language query issued by a user.

    References:
        - PRD.md §2 user stories describing free-form queries
        - Planning.md §4 where the orchestrator sits between user input and MCP tools
    """

    query: str = Field(..., description="User request to be routed to MCP tools")


class ToolResult(BaseModel):
    """Result returned by an MCP tool.

    Each tool can return arbitrary structured data. The `source` field indicates
    which MCP server produced the data so callers can reason about downstream
    handling.
    """

    source: str = Field(..., description="Name of the MCP server producing the result")
    data: Any = Field(
        default_factory=dict,
        description="Structured content returned by the tool",
    )


class AgentResponse(BaseModel):
    """Aggregate response from the orchestrator.

    The orchestrator collects results from multiple MCP servers and returns a
    list of `ToolResult` objects. This mirrors the multi-tool coordination
    described in Planning.md §4.
    """

    results: List[ToolResult] = Field(
        default_factory=list,
        description="Ordered results from invoked MCP servers",
    )
