"""
tests/integration/test_live_poi_discovery.py
-------------------------------------------

Live Integration Test + Inspection for the POI Discovery FastMCP Server

DESCRIPTION
-----------
This test connects to your running POI Discovery MCP server via the
streamable-HTTP transport, invokes the `search_pois` tool with a
real query (Berlin, category "tourism"), and:

  • Prints the tool's outputSchema (JSON schema for POIResult[])
  • Prints the raw JSON-RPC content blocks returned
  • Prints the structuredContent list
  • Asserts that at least one POI is returned
  • Asserts that each POI has lat, lon, type, distance
  • Asserts that distances are sorted ascending

PREREQUISITES
-------------
1. Your POI Discovery MCP server must be running:
     $ poetry run python app/mcp_servers/poi_discovery/server.py

2. You must have network access (calls Overpass API via MCP server).

HOW TO RUN
----------
# To run the test and see only pass/fail:
$ poetry run pytest tests/integration/test_live_poi_discovery.py

# To also print the schema, raw blocks, and parsed POI list:
$ poetry run pytest tests/integration/test_live_poi_discovery.py -s

(The `-s` flag disables pytest’s output capture so you see all print() output.)

EXPECTED BEHAVIOR
-----------------
- Without `-s`: You’ll see PASS/FAIL only.
- With `-s`: The console will show:
    1. The JSON schema for the search_pois tool
    2. The raw JSON-RPC content blocks returned by the server
    3. The parsed POI list array
- The test passes if the assertions on POI results hold.
"""


import pytest
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_search_pois_inspect():
    """
    End-to-end integration test + inspection for 'search_pois'.
    """
    server_url = "http://127.0.0.1:8002/mcp"

    # 1. Establish the streamable-HTTP transport
    async with streamablehttp_client(server_url) as (read, write, _):
        # 2. Create an MCP client session over that transport
        async with ClientSession(read, write) as session:
            # 3. Perform the initialize handshake
            await session.initialize()

            # 4. List tools and find our search_pois tool
            tools_resp = await session.list_tools()
            poi_tool = next(
                (t for t in tools_resp.tools if t.name == "search_pois"),
                None
            )
            assert poi_tool is not None, "search_pois tool not found"

            # 5. Print the outputSchema (JSON Schema for POIResult[])
            print("\n=== search_pois outputSchema ===")
            print(json.dumps(poi_tool.outputSchema, indent=2))

            # 6. Call the tool with the required 'request' payload
            req = {
                "latitude": 52.5200,  # Berlin
                "longitude": 13.4050,
                "category": "tourism",
                "radius": 2000
            }
            result = await session.call_tool(
                "search_pois",
                {"request": req}
            )

            # 7. Print the raw content blocks returned
            print("\n=== Raw content blocks ===")
            for block in result.content:
                try:
                    print(block.model_dump() if hasattr(block, "model_dump") else block.dict())
                except Exception:
                    print(str(block))

            # 8. Print the parsed structuredContent list
            data = result.structuredContent
            pois = data.get("result", [])

            print("\n=== parsed POI list ===")
            print(json.dumps(pois, indent=2, ensure_ascii=False))

            # 9. Validate the structured response
            assert isinstance(data, dict) and "result" in data, "Expected structuredContent to be a dict with 'result' key"
            assert isinstance(pois, list) and len(pois) > 0, "No POIs returned"

            required_fields = {"lat", "lon", "type", "distance"}
            for poi in pois:
                for field in required_fields:
                    assert field in poi, f"Missing '{field}' in POI result"

            # Check that distances are sorted ascending
            distances = [poi["distance"] for poi in pois]
            assert distances == sorted(distances), "POIs not sorted by distance ascending"
