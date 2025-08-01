# File: tests/integration/test_live_wikipedia.py

"""
Live Integration Test for Wikipedia FastMCP Server
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
    server_url = "http://127.0.0.1:8000/mcp"

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
