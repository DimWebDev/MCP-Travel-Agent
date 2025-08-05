# Product Requirements Document: MCP-Orchestrated AI Travel Agent

**Main Takeaway:**  
Build an intelligent AI travel agent that uses Model Context Protocol tools to orchestrate itinerary generation. An AI agent (GPT-4o-mini) makes contextual decisions about which tools to invoke, how to interpret user preferences, and how to synthesize information from OpenStreetMap and Wikipedia into personalized travel recommendations. Focus on the 20% of agent orchestration features that deliver 80% of learning value.

**Backend Framework:** FastMCP servers with MCP tool integration  
**AI Agent:** GPT-4ο-mini via API with MCP orchestration (not traditional function calling)  
**MCP Implementation:** Python MCP SDK for tool creation  
**Frontend:** Simple HTML/JavaScript for agent chat interface (no complex mapping initially)  
**Data Storage:** In-memory conversation state (no database required for MVP)

## 1. Objective and Scope  

Deliver a **proof-of-concept MCP agent system** that demonstrates intelligent tool orchestration for travel planning. Unlike traditional web applications with predetermined workflows, this system features an AI agent that makes dynamic decisions about which MCP tools to invoke based on natural language user requests.

**Core Learning Objectives:**
- **Agent Decision Making:** How AI agents choose which tools to use based on context
- **Multi-Step Reasoning:** How agents chain tool calls together intelligently  
- **Error Recovery:** How agents handle failed API calls or adapt when tools return poor results
- **Natural Language Processing:** How agents interpret user intent and generate contextual responses

**MCP Tools to Build:**
- `geocode_tool` - wraps OSM Nominatim for location resolution
- `poi_search_tool` - wraps Overpass API for point-of-interest discovery
- `wikipedia_lookup_tool` - wraps Wikipedia APIs for detailed descriptions

## 1.1 MCP Protocol vs Traditional Function Calling

**Critical Architecture Distinction:** This system uses **MCP (Model Context Protocol)** for dynamic tool discovery and orchestration, NOT predetermined function calling.

**How MCP Works:**
1. **Tool Discovery:** MCP servers automatically inform the orchestrator about available tools and their capabilities
2. **Dynamic Selection:** The AI agent analyzes user queries and dynamically selects which exposed tools to invoke
3. **Protocol Communication:** Tools are executed via MCP protocol calls to independent servers
4. **Flexible Orchestration:** The agent can discover and use new tools without code changes

**MCP Flow:**
```
User Query → AI Analysis → Dynamic Tool Discovery → MCP Protocol Calls → Result Synthesis
```

**Key Advantage:** Unlike traditional function calling where tools are hardcoded, MCP servers expose their capabilities dynamically, allowing the orchestrator to make intelligent decisions about which tools to use based on real-time analysis of user intent.

## 2. User Stories (Natural Language Interaction)

1. **As a history enthusiast**, I say "Plan a historical walking tour of Rome" and receive POIs focused on ancient sites with rich historical context.
2. **As a food lover**, I request "Show me the best local food experiences in Barcelona" and get restaurant recommendations with cultural background.
3. **As a family traveler**, I ask "What can we do in Paris with young children?" and receive family-friendly attractions with practical tips.
4. **As a budget traveler**, I say "Free activities in Berlin for a weekend" and get cost-conscious recommendations with insider knowledge.

## 3. Pareto-Sized MCP Orchestration Features

| MCP Orchestration Feature              | Learning Value Delivered                    | Implementation Effort |
|----------------------------------------|---------------------------------------------|----------------------|
| 1. Intent Classification & Tool Selection | Core agent decision-making patterns        | Low                  |
| 2. Contextual Tool Chaining             | Multi-step reasoning and workflow management| Low                  |
| 3. Dynamic Result Synthesis             | Information fusion and natural language generation | Low           |
| 4. Graceful Error Handling              | Robust agent behavior under failure conditions | Low              |
| 5. User Preference Memory               | Context retention across conversations      | Medium               |
| 6. Tool Result Quality Assessment       | Agent evaluation and filtering capabilities | Medium               |

## 4. MCP Tool Specifications

### 4.1 Geocode Tool
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Geocoding Server")

@mcp.tool()
def geocode_location(location_name: str) -> dict:
    """
    Resolves location names to coordinates using OSM Nominatim
    Returns: {'lat': float, 'lon': float, 'display_name': str}
    """

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

### 4.2 POI Search Tool  
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("POI Discovery Server")

@mcp.tool()
def search_pois(latitude: float, longitude: float, 
                category: str = "tourism", radius: int = 5000) -> List[dict]:
    """
    Discovers points of interest using Overpass API
    Categories: tourism, historic, restaurant, entertainment, shopping
    Returns: [{'name': str, 'lat': float, 'lon': float, 'type': str}]
    """

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

### 4.3 Wikipedia Lookup Tool
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Wikipedia Server")

@mcp.tool()
def get_wikipedia_info(poi_name: str, location_context: str) -> dict:
    """
    Fetches Wikipedia summaries and extracts for POIs
    Returns: {'summary': str, 'extract': str, 'url': str}
    """

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

## 5. Agent Orchestration Architecture

### 5.1 Agent System Design
The core system centers around an **AI Agent Controller** that receives natural language requests and orchestrates MCP tool usage through dynamic discovery:

```python
class TravelAgent:
    def __init__(self, llm_client, mcp_clients):
        self.llm = llm_client  # GPT-4o-mini for decision making
        self.mcp_clients = mcp_clients  # MCP client connections to tool servers
        self.conversation_memory = []
        self.available_tools = {}  # Dynamically discovered from MCP servers
    
    async def discover_available_tools(self):
        """MCP servers inform orchestrator of their exposed tools"""
        for client in self.mcp_clients:
            tools = await client.list_tools()  # MCP protocol call
            self.available_tools.update(tools)
    
    async def process_request(self, user_request: str) -> str:
        # AI agent analyzes request against dynamically discovered tools
        tool_selection = await self.llm.analyze_and_select_tools(
            user_request, 
            self.available_tools,  # Tools exposed by MCP servers
            self.conversation_memory
        )
        
        # Execute selected tools via MCP protocol
        results = await self.orchestrate_mcp_calls(tool_selection)
        
        # AI synthesizes results into response
        return await self.llm.synthesize_response(results, user_request)
```

### 5.2 Agent Decision Flow
1. **Tool Discovery:** Agent queries MCP servers to learn what tools are available
2. **Intent Analysis:** Agent interprets user preferences (history, food, family, budget, etc.)
3. **Dynamic Tool Selection:** Agent decides which discovered tools to invoke based on user context
4. **MCP Protocol Execution:** Agent calls selected tools via MCP protocol communication
5. **Quality Assessment:** Agent evaluates tool results and decides whether to invoke additional tools
6. **Synthesis:** Agent combines information into personalized, coherent recommendations
7. **Memory Update:** Agent retains context for follow-up questions

### 5.3 Example Agent Reasoning Process
**User:** "Plan a romantic evening in Paris"

**Agent Reasoning:**
- *Tool Discovery:* Query MCP servers → Discover geocoding, POI search, and Wikipedia tools available
- *Intent Analysis:* Romantic activities, evening timing, Paris location
- *Dynamic Tool Selection:* Based on available tools, select geocoding → POI search (restaurants/viewpoints) → Wikipedia (ambiance context)
- *MCP Orchestration:* Execute tool sequence via MCP protocol calls to respective servers
- *Synthesis:* Combine MCP tool results into evening itinerary with romantic narrative

## 6. Implementation Milestones

| Sprint | MCP Orchestration Goals                                    | Duration |
|--------|------------------------------------------------------------|----------|
| 1      | Build MCP tool wrappers; basic agent-tool communication   | 1 week   |
| 2      | Implement agent decision-making for tool selection        | 1 week   |
| 3      | Add contextual tool chaining and result synthesis         | 1 week   |
| 4      | Implement error handling and graceful degradation         | 1 week   |
| 5      | Add conversation memory and follow-up question handling   | 1 week   |

## 7. Success Metrics for MCP Learning

- **Agent Autonomy:** Agent successfully selects appropriate tools without hardcoded workflows in ≥90% of test cases
- **Contextual Adaptation:** Agent modifies tool usage based on user preferences (e.g., "historical" vs "family-friendly") in ≥80% of requests  
- **Error Recovery:** Agent gracefully handles tool failures and finds alternative information sources in ≥75% of error scenarios
- **Synthesis Quality:** Agent-generated responses demonstrate meaningful information fusion rather than simple concatenation
- **Learning Demonstration:** Clear evidence of MCP orchestration patterns in code architecture and agent behavior

## 8. Technical Stack (Minimal Complexity)

**Backend Framework:** FastAPI with MCP tool integration  
**AI Agent:** Claude-3.5 or GPT-4 via API with MCP orchestration  
**MCP Implementation:** Python MCP SDK for tool creation  
**MCP Protocol:** Dynamic tool discovery and invocation (not predetermined function calls)  
**Frontend:** Simple HTML/JavaScript for agent chat interface (no complex mapping initially)  
**Data Storage:** In-memory conversation state (no database required for MVP)

## 9. Key Differentiators from Traditional PRD

This MCP-based approach fundamentally differs from traditional web applications:

**Traditional Function Calling:** User input → Predetermined function sequence → Fixed response format  
**MCP Orchestration:** User input → Tool discovery from MCP servers → AI analysis → Dynamic tool selection → MCP protocol execution → Contextual synthesis → Personalized response

The agent becomes the intelligent orchestrator that dynamically discovers available tools from MCP servers, makes contextual decisions about which tools to invoke, and handles uncertainty through flexible protocol communication. This design prioritizes learning agent orchestration patterns over building a polished travel application.

## 10. Future MCP Enhancements (Beyond 80/20)

- **Multi-Agent Orchestration:** Specialized agents for different travel domains (food, culture, adventure)
- **Tool Learning:** Agents that improve tool selection based on user feedback
- **Complex Workflow Management:** Multi-day itinerary planning with dependency management
- **Integration Expansion:** Additional MCP tools for weather, transportation, booking systems

This PRD transforms the original deterministic web application into a genuine MCP learning environment where an AI agent orchestrates tool usage through intelligent decision-making, providing hands-on experience with the core patterns of agent orchestration that transfer to more sophisticated MCP applications.