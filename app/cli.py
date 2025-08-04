"""Simple CLI entry point for manual agent testing.

This module implements the CLI-first workflow described in Tasks.md Task T006.
It allows developers to interact with the orchestrator without the FastAPI
layer, aligning with the "CLI-first" approach in Planning.md §2.
"""

from __future__ import annotations

import asyncio
import json
from typing import NoReturn

from .agent.orchestrator import create_orchestrator


async def repl() -> NoReturn:
    """Read–eval–print loop for issuing agent queries from the terminal."""

    orchestrator = create_orchestrator()
    print("MCP Travel Agent REPL. Type 'quit' to exit.")
    while True:
        query = input(">> ").strip()
        if query.lower() in {"quit", "exit"}:
            break
        response = await orchestrator.handle_query(query)
        print(json.dumps(response.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(repl())
