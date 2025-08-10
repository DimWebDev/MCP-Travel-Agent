"""Simple CLI entry point for manual agent testing.

This module implements the CLI-first workflow described in Tasks.md Task T006.
It allows developers to interact with the orchestrator without the FastAPI
layer, aligning with the "CLI-first" approach in Planning.md §2.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import NoReturn

from .agent.orchestrator import create_orchestrator


async def run_single(query: str) -> None:
    """Process a single query and print the JSON response."""

    orchestrator = create_orchestrator()
    response = await orchestrator.handle_query(query)
    print(json.dumps(response.model_dump(), indent=2, ensure_ascii=False))


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


def main() -> None:
    """Entry point for the CLI interface.

    If a query is provided as a positional argument, it is executed once and the
    program exits. Otherwise an interactive REPL session is started. This keeps
    the CLI flexible for automated tests and manual exploration.
    """

    parser = argparse.ArgumentParser(description="MCP Travel Agent CLI")
    parser.add_argument("query", nargs="?", help="Natural language travel request")
    args = parser.parse_args()

    if args.query:
        asyncio.run(run_single(args.query))
    else:
        asyncio.run(repl())


if __name__ == "__main__":
    main()
