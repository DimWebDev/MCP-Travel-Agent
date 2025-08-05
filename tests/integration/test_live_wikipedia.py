"""
tests/integration/test_live_wikipedia.py
----------------------------------------

Live Integration Test + Inspection for the Wikipedia FastMCP Server

DESCRIPTION
-----------
This test connects to your running Wikipedia MCP server via the
streamable-HTTP transport, invokes the `get_wikipedia_info` tool with a
real query (e.g., "Eiffel Tower", location context "Paris"), and:

  • Prints the tool's outputSchema (JSON schema for WikipediaResponse)
  • Calls the tool and prints the structuredContent dict
  • Asserts that summary, extract, url, and title are present
  • Asserts that the title matches the POI

PREREQUISITES
-------------
1. Your Wikipedia MCP server must be running:
     $ poetry run python app/mcp_servers/wikipedia/server.py

2. You must have network access (calls Wikipedia API via MCP server).

HOW TO RUN
----------
# To run the test and see only pass/fail:
$ poetry run pytest tests/integration/test_live_wikipedia.py

# To also print the schema and structured response:
$ poetry run pytest tests/integration/test_live_wikipedia.py -s

(The `-s` flag disables pytest’s output capture so you see all print() output.)

EXPECTED BEHAVIOR
-----------------
- Without `-s`: You’ll see PASS/FAIL only.
- With `-s`: The console will show:
    1. The JSON schema for the get_wikipedia_info tool
    2. The parsed Wikipedia structuredContent dict
- The test passes if the assertions on Wikipedia results hold.
"""

import pytest
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_wikipedia_lookup():
    """
    End-to-end integration test for 'get_wikipedia_info'.
    """
    server_url = "http://127.0.0.1:8003/mcp"

    async with streamablehttp_client(server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools and find our Wikipedia tool
            tools_resp = await session.list_tools()
            wiki_tool = next(
                (t for t in tools_resp.tools if t.name == "get_wikipedia_info"),
                None
            )
            assert wiki_tool is not None, "get_wikipedia_info tool not found"

            # Print the outputSchema
            print("\n=== get_wikipedia_info outputSchema ===")
            print(json.dumps(wiki_tool.outputSchema, indent=2))

            # Call the tool
            result = await session.call_tool(
                "get_wikipedia_info",
                {"request": {"poi_name": "Eiffel Tower", "location_context": "Paris"}}
            )

            # Print the structured response
            data = result.structuredContent
            print("\n=== Wikipedia structuredContent ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # Validate the response
            assert isinstance(data, dict), "Expected structuredContent to be a dict"
            assert "summary" in data, "Missing 'summary' in response"
            assert "extract" in data, "Missing 'extract' in response"
            assert "url" in data, "Missing 'url' in response"
            assert "title" in data, "Missing 'title' in response"
            assert "Eiffel" in data["title"], "Expected 'Eiffel' in title"
