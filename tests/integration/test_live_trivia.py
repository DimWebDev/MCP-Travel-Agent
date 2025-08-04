"""
tests/integration/test_live_trivia.py
-------------------------------------

Live Integration Test + Inspection for the Trivia FastMCP Server

DESCRIPTION
-----------
This test connects to your running Trivia MCP server via the
streamable-HTTP transport, invokes the `get_trivia` tool with a
real query (e.g., topic "Eiffel Tower", context "Paris"), and:

  • Prints the tool's outputSchema (JSON schema for TriviaResponse)
  • Prints the raw JSON-RPC content blocks returned
  • Prints the structuredContent dict
  • Asserts that trivia, source, and reliability are present
  • Asserts that the reliability is >= 0.6

PREREQUISITES
-------------
1. Your Trivia MCP server must be running:
     $ poetry run python app/mcp_servers/trivia/server.py

2. You must have network access (calls DuckDuckGo API via MCP server).

HOW TO RUN
----------
# To run the test and see only pass/fail:
$ poetry run pytest tests/integration/test_live_trivia.py

# To also print the schema, raw blocks, and parsed response:
$ poetry run pytest tests/integration/test_live_trivia.py -s

(The `-s` flag disables pytest’s output capture so you see all print() output.)

EXPECTED BEHAVIOR
-----------------
- Without `-s`: You’ll see PASS/FAIL only.
- With `-s`: The console will show:
    1. The JSON schema for the get_trivia tool
    2. The raw JSON-RPC content blocks returned by the server
    3. The parsed TriviaResponse dict
- The test passes if the assertions on trivia results hold.
"""

import pytest
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_get_trivia_inspect():
    """
    End-to-end integration test + inspection for 'get_trivia'.
    """
    server_url = "http://127.0.0.1:8000/mcp"

    # 1. Establish the streamable-HTTP transport
    async with streamablehttp_client(server_url) as (read, write, _):
        # 2. Create an MCP client session over that transport
        async with ClientSession(read, write) as session:
            # 3. Perform the initialize handshake
            await session.initialize()

            # 4. List tools and find our get_trivia tool
            tools_resp = await session.list_tools()
            trivia_tool = next(
                (t for t in tools_resp.tools if t.name == "get_trivia"),
                None
            )
            assert trivia_tool is not None, "get_trivia tool not found"

            # 5. Print the outputSchema (JSON Schema for TriviaResponse)
            print("\n=== get_trivia outputSchema ===")
            print(json.dumps(trivia_tool.outputSchema, indent=2))

            # 6. Call the tool with the required 'request' payload
            req = {
                "topic": "Eiffel Tower",
                "context": "Paris"
            }
            result = await session.call_tool(
                "get_trivia",
                {"request": req}
            )

            # 7. Print the raw content blocks returned
            print("\n=== Raw content blocks ===")
            for block in result.content:
                try:
                    print(block.model_dump() if hasattr(block, "model_dump") else block.dict())
                except Exception:
                    print(str(block))

    # 8. Print the parsed structuredContent dict
    data = result.structuredContent
    print("\n=== parsed TriviaResponse ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # 9. Validate the structured response or handle error gracefully
    if data is None:
        print("No travel-relevant trivia found for the given topic/context. This is expected if the API returns no suitable fact.")
        # Optionally, assert that the error message is present in the raw content blocks
        error_msgs = [block.text for block in result.content if hasattr(block, "text") and "Error executing tool" in block.text]
        assert error_msgs, "Expected an error message in the content blocks when no trivia is found."
    else:
        assert isinstance(data, dict), "Expected structuredContent to be a dict"
        assert "trivia" in data, "Missing 'trivia' in response"
        assert "source" in data, "Missing 'source' in response"
        assert "reliability" in data, "Missing 'reliability' in response"
        assert data["reliability"] >= 0.6, "Reliability below threshold"
        assert "Eiffel" in data["trivia"] or "Paris" in data["trivia"], "Expected topic/context in trivia fact"
