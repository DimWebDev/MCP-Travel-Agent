"""
tests/integration/test_live_geocode.py
--------------------------------------

Live Integration Test + Inspection for the Geocoding FastMCP Server

DESCRIPTION
-----------
This test connects to your running Geocoding MCP server via the
streamable-HTTP transport, invokes the `geocode_location` tool with a
real query ("Berlin"), and:

  • Prints the tool's outputSchema (JSON schema for GeocodeResponse)
  • Prints the raw JSON-RPC content blocks returned
  • Prints the structuredContent dict
  • Asserts that "lat", "lon", and "display_name" exist
  • Asserts that "Berlin" appears in display_name

PREREQUISITES
-------------
1. Your Geocoding MCP server must be running:
     $ poetry run python app/mcp_servers/geocoding/server.py

2. You must have network access (this calls the real OpenStreetMap Nominatim API).

HOW TO RUN
----------
# To run the test and see only pass/fail:
$ poetry run pytest tests/integration/test_live_geocode.py

# To also print the schema, raw blocks, and response for inspection:
$ poetry run pytest tests/integration/test_live_geocode.py -s

(The `-s` flag disables pytest’s output capture so you see all print() output.)

EXPECTED BEHAVIOR
-----------------
- Without `-s`: You’ll see PASS/FAIL only.
- With `-s`: The console will show:
    1. The JSON schema for the geocode_location tool
    2. The raw JSON-RPC content blocks returned by the server
    3. The parsed `structuredContent` dict
- The test passes if the assertions on `structuredContent` hold.

"""

import pytest
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_geocode_location_inspect():
    """
    End-to-end integration test + inspection for 'geocode_location'.
    """
    server_url = "http://127.0.0.1:8000/mcp"

    # 1. Establish the streamable-HTTP transport
    async with streamablehttp_client(server_url) as (read, write, _):
        # 2. Create an MCP client session over that transport
        async with ClientSession(read, write) as session:
            # 3. Perform the initialize handshake
            await session.initialize()

            # 4. List tools and find our geocode_location tool
            tools_resp = await session.list_tools()
            geo_tool = next(
                (t for t in tools_resp.tools if t.name == "geocode_location"),
                None
            )
            assert geo_tool is not None, "geocode_location tool not found"

            # 5. Print the outputSchema (JSON Schema for GeocodeResponse)
            print("\n=== geocode_location outputSchema ===")
            print(json.dumps(geo_tool.outputSchema, indent=2))

            # 6. Call the tool with the required 'request' payload
            city = "Berlin"
            result = await session.call_tool(
                "geocode_location",
                {"request": {"location_name": city}}
            )

            # 7. Print the raw content blocks returned
            print("\n=== Raw content blocks ===")
            for block in result.content:
                try:
                    # Pydantic v2: use model_dump() or dict()
                    print(block.model_dump() if hasattr(block, "model_dump") else block.dict())
                except Exception:
                    print(str(block))

            # 8. Print the parsed structuredContent
            data = result.structuredContent
            print("\n=== structuredContent ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # 9. Validate the structured response
            assert isinstance(data, dict), "Expected structuredContent to be a dict"
            assert "lat" in data, "Missing 'lat' in response"
            assert "lon" in data, "Missing 'lon' in response"
            assert "display_name" in data, "Missing 'display_name' in response"
            assert city in data["display_name"], (
                f"Expected '{city}' to appear in display_name"
            )
