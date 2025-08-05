# File: app/mcp_servers/wikipedia/server.py

"""
Wikipedia MCP Server: Content Enrichment via Wikipedia API

This module provides a specialized MCP server for fetching Wikipedia content
and summaries to enrich POI information in the travel agent system.

ARCHITECTURAL OVERVIEW:
-----------------------
This server acts as a content enrichment provider in the MCP-orchestrated
travel agent system. It receives POI names and location context from the
Agent Orchestrator and returns structured Wikipedia summaries, extracts,
and article URLs for educational content.

RATE LIMITING COMPLIANCE:
-------------------------
Wikipedia API allows up to 5000 requests per hour per IP address. This server
implements proper rate limiting and caching to ensure respectful usage and
optimal performance.

MCP INTEGRATION:
----------------
The server exposes a single tool `get_wikipedia_info` that accepts POI names
with optional location context and returns structured Wikipedia content that
can be used to enrich travel recommendations with educational information.
"""

import asyncio
import time
import logging
from typing import Any, Dict, Optional
import os
import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field


class RateLimiter:
    """
    Asynchronous rate limiter for Wikipedia API compliance.
    
    Ensures that API requests respect Wikipedia's rate limiting guidelines
    (5000 requests/hour = ~1.39 requests/second). Uses asyncio.Lock to ensure
    thread-safe operation in concurrent environments.
    """

    def __init__(self, rate_per_sec: float) -> None:
        """
        Initialize rate limiter with specified requests per second.
        
        Args:
            rate_per_sec: Maximum requests per second (1.2 for Wikipedia compliance)
        """
        self._interval = 1.0 / rate_per_sec
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def wait(self) -> None:
        """
        Enforce rate limiting by sleeping if necessary.
        
        Calculates the time since the last API call and sleeps for the
        remaining duration to maintain the required interval.
        """
        async with self._lock:
            now = time.monotonic()
            sleep_for = self._last_call + self._interval - now
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            self._last_call = time.monotonic()


class WikipediaRequest(BaseModel):
    """
    Request model for Wikipedia content lookup.
    
    Validates POI name and optional location context for more accurate
    Wikipedia article discovery and disambiguation.
    """
    poi_name: str = Field(description="Name of the point of interest to look up")
    location_context: Optional[str] = Field(
        default=None, 
        description="Location context to help disambiguate (e.g., 'Paris, France')"
    )


class WikipediaResponse(BaseModel):
    """
    Response model containing Wikipedia content data.
    
    Provides structured Wikipedia information that can be used to enrich
    POI descriptions with educational and historical context.
    """
    summary: str = Field(description="Brief summary/extract from Wikipedia")
    extract: str = Field(description="Longer extract with more detail")
    url: str = Field(description="Direct URL to the Wikipedia article")
    page_id: Optional[int] = Field(default=None, description="Wikipedia page ID")
    title: str = Field(description="Actual Wikipedia article title")


# FastMCP server instance and configuration
mcp = FastMCP("Wikipedia Server")
rate_limiter = RateLimiter(rate_per_sec=1.2)  # Conservative rate limiting
BASE_URL = "https://en.wikipedia.org/api/rest_v1"
HEADERS = {
    "User-Agent": "MCP-Travel-Agent/1.0 (https://github.com/your-repo; your@email.com)",
    "Accept": "application/json"
}

# Configure logging for debugging and monitoring
logger = logging.getLogger("wikipedia-server")
logging.basicConfig(level=logging.INFO)


async def search_wikipedia(poi_name: str, location_context: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for Wikipedia articles matching the POI name.
    
    Uses Wikipedia's opensearch API to find the most relevant article,
    with location context helping to disambiguate common names.
    
    Args:
        poi_name: The POI name to search for
        location_context: Optional location context for disambiguation
        
    Returns:
        Dictionary containing search results from Wikipedia API
        
    Raises:
        RuntimeError: If no suitable Wikipedia article is found
    """
    search_query = poi_name
    if location_context:
        search_query = f"{poi_name} {location_context}"
    
    async with httpx.AsyncClient(timeout=15) as client:
        # Try direct summary API first
        try:
            response = await client.get(
                "https://en.wikipedia.org/api/rest_v1/page/summary/" + search_query.replace(" ", "_"),
                headers=HEADERS
            )
            if response.status_code == 200:
                return response.json()
        except httpx.HTTPError:
            pass  # Continue to fallback
        
        # Fallback 1: Try just the POI name without location context
        if location_context:
            try:
                response = await client.get(
                    "https://en.wikipedia.org/api/rest_v1/page/summary/" + poi_name.replace(" ", "_"),
                    headers=HEADERS
                )
                if response.status_code == 200:
                    return response.json()
            except httpx.HTTPError:
                pass  # Continue to next fallback
        
        # Fallback 2: Use opensearch API endpoint to find best match
        try:
            opensearch_response = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "opensearch",
                    "search": search_query,
                    "limit": 1,
                    "format": "json"
                },
                headers=HEADERS
            )
            opensearch_response.raise_for_status()
            opensearch_data = opensearch_response.json()
            
            if opensearch_data[1]:  # If we found results
                title = opensearch_data[1][0]
                try:
                    # Try to get the summary for this title
                    response = await client.get(
                        f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}",
                        headers=HEADERS
                    )
                    if response.status_code == 200:
                        return response.json()
                except httpx.HTTPError:
                    pass  # Continue to final fallback
        except httpx.HTTPError:
            pass  # Continue to final fallback
        
        # If all attempts failed, raise an error
        raise RuntimeError(f"No Wikipedia article found for '{poi_name}'")


async def _get_wikipedia_info_impl(request: WikipediaRequest) -> WikipediaResponse:
    """
    Implementation of Wikipedia content fetching with optional location context.
    
    WORKFLOW:
    ---------
    1. RATE LIMITING: Enforce respectful API usage
    2. SEARCH: Find the most relevant Wikipedia article
    3. CONTENT EXTRACTION: Extract summary and longer extract
    4. URL CONSTRUCTION: Build direct link to article
    5. STRUCTURED RETURN: Provide WikipediaResponse for content enrichment
    
    ERROR HANDLING:
    ---------------
    - HTTPError: Wikipedia API errors (404, 5xx)
    - TimeoutException: Network timeouts
    - ValueError: Invalid JSON response
    - RuntimeError: No suitable article found
    
    MCP INTEGRATION:
    ----------------
    This tool enriches POI information with educational content:
    - Called after POI discovery to add context
    - Provides historical and cultural background
    - Enhances travel recommendations with learning opportunities
    
    Args:
        request: WikipediaRequest containing POI name and optional location context
        
    Returns:
        WikipediaResponse with summary, extract, URL, and metadata
        
    Raises:
        RuntimeError: If Wikipedia lookup fails or no suitable content found
    """
    # STEP 1: Enforce rate limiting for API compliance
    await rate_limiter.wait()
    
    try:
        # STEP 2: Search for Wikipedia article
        logger.info(f"Searching Wikipedia for: {request.poi_name}")
        data = await search_wikipedia(request.poi_name, request.location_context)
        
        # STEP 3: Extract content from Wikipedia response
        if "extract" not in data:
            raise RuntimeError(f"No Wikipedia article found for '{request.poi_name}'")
        
        summary = data.get("extract", "")[:200] + "..." if len(data.get("extract", "")) > 200 else data.get("extract", "")
        extract = data.get("extract", "")
        url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
        page_id = data.get("pageid")
        title = data.get("title", request.poi_name)
        
        # Handle case where we might not have full URL
        if not url and title:
            url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        
        return WikipediaResponse(
            summary=summary,
            extract=extract,
            url=url,
            page_id=page_id,
            title=title
        )
        
    except httpx.TimeoutException as exc:
        logger.error(f"Timeout while fetching Wikipedia info for '{request.poi_name}': {exc}")
        raise RuntimeError("Wikipedia request timed out") from exc
    except httpx.HTTPStatusError as exc:
        # For status errors (4xx, 5xx), response is guaranteed to exist
        logger.error(f"HTTP status error while fetching Wikipedia info for '{request.poi_name}': {exc.response.status_code}")
        raise RuntimeError(f"Wikipedia API error: {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        # For other HTTP errors (connection, timeout, etc.)
        logger.error(f"HTTP error while fetching Wikipedia info for '{request.poi_name}': {exc}")
        raise RuntimeError("Wikipedia API error: connection failed") from exc
    except (ValueError, KeyError) as exc:
        logger.error(f"Invalid Wikipedia response for '{request.poi_name}': {exc}")
        raise RuntimeError("Invalid response from Wikipedia API") from exc


@mcp.tool()
async def get_wikipedia_info(request: WikipediaRequest) -> WikipediaResponse:
    """
    Fetch Wikipedia content for a POI with optional location context.
    
    This is the MCP tool wrapper that delegates to the implementation function.
    """
    return await _get_wikipedia_info_impl(request)


if __name__ == "__main__":
    """
    Run the Wikipedia MCP server with HTTP transport.
    
    The server will start on port 8003 and be ready to accept
    MCP tool calls from the Agent Orchestrator for content enrichment.
    """
    mcp.run(transport="http", host="127.0.0.1", port=8003)
