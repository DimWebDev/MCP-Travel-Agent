# MCP Alignment Verification Checklist

## ✅ Completed Alignments

### 1. Code-level naming and import fixes
- [x] **PRD.md** - Updated all `@mcp_tool` decorators to `@mcp.tool()` with proper FastMCP imports
- [x] **Tasks.md** - Updated T002-T005 task descriptions to use "Annotate function with `@mcp.tool()` from FastMCP"
- [x] **PRD.md** - Added `if __name__ == "__main__": mcp.run(transport="streamable-http")` to all server examples

### 2. Transport & run-command adjustments
- [x] **Setup.md** - Added MCP CLI installation: `poetry run pip install "mcp[cli]"`
- [x] **Setup.md** - Updated debug commands to use Poetry with `python` direct execution
- [x] **Planning.md** - Updated communication patterns from "HTTP/SSE" to "Streamable HTTP (chunked) / SSE (fallback)"
- [x] **Tasks.md** - Updated T014 to implement "fetch() & ReadableStream over `/mcp` (Streamable HTTP)"

### 3. Dependency declaration tweaks
- [x] **Planning.md** - Updated dependency to `mcp = {version="^0.8.0", extras=["cli"]}`
- [x] **Setup.md** - Added MCP CLI installation step in first-time setup

### 4. Textual references fixes
- [x] **Planning.md** - Updated all server references from "MCP Server" to "FastMCP Server"
- [x] **PRD.md** - Updated technical stack from "FastAPI with MCP tool integration" to "FastMCP servers with MCP tool integration"

### 5. Optional spec features marked as "later"
- [x] **Tasks.md** - Added T004-extra TODO for `@mcp.resource` city-guides
- [x] **Planning.md** - Added Sprint 5 Enhancement TODO for OAuth TokenVerifier stub

## 🔍 Verification Commands (Run After Implementation)

### 1. Unit discovery
```bash
# Using Poetry to run MCP development server
poetry run python -m mcp dev app/mcp_servers/geocoding/server.py
# Expected: MCP Inspector opens; "Tools → geocode_location" visible

# Alternative: Run server directly and test with MCP client
poetry run python app/mcp_servers/geocoding/server.py
```

### 2. Manifest download
```bash
curl -s http://localhost:3000/mcp/manifest.json
# Expected: JSON includes your tool's input/output schema
```

### 3. Orchestrator handshake
```bash
poetry run pytest tests/integration/test_agent_to_geocode.py
# Expected: Test passes; agent lists tool via MCP `list_tools`
```

### 4. Front-end stream
```bash
# Run React dev server; ask a city query
# Expected: Browser receives chunked text from `/mcp` endpoint, not SSE
```

## 📋 Next Steps

1. **Implement the code changes** - Your documentation is now MCP SDK aligned
2. **Create the actual server files** following the updated patterns in PRD.md
3. **Test with the verification commands** above
4. **Update any discovered issues** and re-run verification

## 🎯 Why This Alignment Matters

- **SDK Compatibility**: Your tools will auto-register and work with MCP clients
- **Transport Efficiency**: Streamable HTTP is the recommended transport (SSE is legacy)
- **Discovery & Manifests**: FastMCP auto-generates the manifest and capability handshake
- **Development Experience**: MCP Inspector will work correctly for debugging with Poetry

Your documentation is now **fully aligned** with the official MCP Python SDK (FastMCP, v0.8+) using Poetry as the package manager.
