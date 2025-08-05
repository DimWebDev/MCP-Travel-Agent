"""
Geocoding MCP Server: Location Resolution via OpenStreetMap Nominatim

This module provides a specialized MCP server for converting location names
into geographic coordinates using the OpenStreetMap Nominatim geocoding service.

ARCHITECTURAL OVERVIEW:
-----------------------
This server acts as an intelligent data provider in the MCP-orchestrated
travel agent system. It handles the critical first step of travel planning:
resolving user-provided location names into precise coordinates that other
MCP servers can use for POI discovery, Wikipedia lookups, and trivia searches.

RATE LIMITING COMPLIANCE:
-------------------------
OpenStreetMap Nominatim requires respectful usage with a maximum of 1 request
per second per IP address. This server implements proper rate limiting to
ensure compliance and prevent service disruption.

MCP INTEGRATION:
----------------
The server exposes a single tool `geocode_location` that accepts location names
and returns structured coordinate data. The Agent Orchestrator will use this
tool when users provide location names instead of coordinates.
"""

import asyncio
import time
import logging
from typing import Any, List
import os

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel


class RateLimiter:
    """
    Asynchronous rate limiter for OpenStreetMap Nominatim API compliance.
    
    Ensures that API requests are spaced at least 1 second apart to comply
    with OSM's usage policy. Uses asyncio.Lock to ensure thread-safe operation
    in concurrent environments where multiple geocoding requests might be
    processed simultaneously.
    
    The rate limiter calculates the minimum time that must pass between calls
    and automatically sleeps if necessary to maintain the required interval.
    """

    def __init__(self, rate_per_sec: float) -> None:
        """
        Initialize rate limiter with specified requests per second.
        
        Args:
            rate_per_sec: Maximum requests per second (1.0 for Nominatim compliance)
        """
        self._interval = 1.0 / rate_per_sec
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def wait(self) -> None:
        """
        Enforce rate limiting by sleeping if necessary.
        
        Calculates the time since the last API call and sleeps for the
        remaining duration to maintain the required interval. Uses
        time.monotonic() to avoid issues with system clock changes.
        """
        async with self._lock:
            now = time.monotonic()
            sleep_for = self._last_call + self._interval - now
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            self._last_call = time.monotonic()


class GeocodeRequest(BaseModel):
    """
    Request model for geocoding operations.
    
    Validates that the location name is provided as a string. The location_name
    can be any human-readable location description such as:
    - City names: "Paris", "New York City"  
    - Addresses: "1600 Pennsylvania Avenue, Washington DC"
    - Landmarks: "Eiffel Tower", "Times Square"
    - Regions: "Tuscany, Italy", "Silicon Valley"
    """
    location_name: str


class GeocodeResponse(BaseModel):
    """
    Response model containing geocoded location data.
    
    Provides structured coordinate and descriptive information that other
    MCP servers in the travel agent system can use for further processing.
    
    Fields:
        lat: Latitude in decimal degrees (WGS84 coordinate system)
        lon: Longitude in decimal degrees (WGS84 coordinate system)  
        display_name: Human-readable location description from OSM database
                     (e.g., "Paris, Île-de-France, France")
    """
    lat: float
    lon: float
    display_name: str


# FastMCP server instance and configuration
mcp = FastMCP("Geocoding Server")
rate_limiter = RateLimiter(rate_per_sec=1)  # OSM Nominatim compliance
BASE_URL = "https://nominatim.openstreetmap.org"
HEADERS = {"User-Agent": "MCP-Travel-Agent"}  # Required by OSM usage policy

# Configure logging for debugging and monitoring
logger = logging.getLogger("geocoding-server")
logging.basicConfig(level=logging.INFO)


async def fetch_location(location_name: str) -> httpx.Response:
    """
    Execute HTTP request to OpenStreetMap Nominatim geocoding API.
    
    Sends a structured search request to the Nominatim service with proper
    headers and parameters. Uses async HTTP client with timeout to prevent
    hanging requests.
    
    Args:
        location_name: The location string to geocode
        
    Returns:
        httpx.Response object containing the API response
        
    Note:
        This function does not handle rate limiting - that responsibility
        belongs to the calling function to maintain proper separation of concerns.
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        return await client.get(
            "/search",
            params={"q": location_name, "format": "json", "limit": 1},
            headers=HEADERS,
        )


@mcp.tool()
async def geocode_location(request: GeocodeRequest) -> GeocodeResponse:
    """
    Resolve a location name to geographic coordinates using OSM Nominatim.
    
    WORKFLOW:
    ---------
    1. RATE LIMITING: Enforce 1 request/second compliance with OSM policy
    2. API REQUEST: Send location query to Nominatim with proper headers
    3. ERROR HANDLING: Manage timeouts, HTTP errors, and API failures gracefully
    4. RESPONSE PARSING: Extract coordinates and display name from JSON response
    5. VALIDATION: Ensure response structure matches expected format
    6. STRUCTURED RETURN: Provide GeocodeResponse for other MCP servers
    
    ERROR HANDLING:
    ---------------
    - TimeoutException: Network or server timeout (10 second limit)
    - HTTPError: Server returns error status codes (4xx, 5xx)
    - ValueError: Invalid JSON response from API
    - RuntimeError: Location not found or unexpected response structure
    
    MCP INTEGRATION:
    ----------------
    This tool serves as the foundation for location-based queries in the
    travel agent system. The returned coordinates are used by:
    - POI Discovery Server for finding nearby attractions
    - Wikipedia Server for location-specific content
    - Trivia Server for location-relevant facts
    
    Args:
        request: GeocodeRequest containing the location name to resolve
        
    Returns:
        GeocodeResponse with latitude, longitude, and display name
        
    Raises:
        RuntimeError: If geocoding fails due to network, parsing, or data issues
    """
    return await _geocode_location_impl(request)


async def _geocode_location_impl(request: GeocodeRequest) -> GeocodeResponse:
    """
    Internal implementation of geocode_location for unit testing.
    
    This function contains the actual geocoding logic and is used by both
    the MCP tool wrapper and unit tests. The separation allows for proper
    testing without MCP tool decoration complications.
    """
    # STEP 1: Enforce rate limiting to comply with OSM usage policy
    await rate_limiter.wait()
    
    try:
        # STEP 2: Execute API request with timeout and error handling
        response = await fetch_location(request.location_name)
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        logger.error(f"Timeout while geocoding '{request.location_name}': {exc}")
        raise RuntimeError("Geocoding request timed out") from exc
    except httpx.HTTPError as exc:
        logger.error(f"HTTP error while geocoding '{request.location_name}': {exc.response.status_code} - {exc}")
        raise RuntimeError(f"HTTP error: {exc.response.status_code}") from exc

    try:
        # STEP 3: Parse JSON response from Nominatim API
        data: List[dict[str, Any]] = response.json()
    except ValueError as exc:
        logger.error(f"Invalid JSON response for '{request.location_name}': {exc}")
        raise RuntimeError("Invalid response from geocoding API") from exc

    # STEP 4: Validate that results were found
    if not data:
        logger.warning(f"Location not found for '{request.location_name}'")
        raise RuntimeError("Location not found")

    # STEP 5: Extract and validate coordinate data from first result
    item = data[0]
    try:
        return GeocodeResponse(
            lat=float(item["lat"]),
            lon=float(item["lon"]),
            display_name=item["display_name"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        logger.error(f"Unexpected response structure for '{request.location_name}': {exc}")
        raise RuntimeError("Unexpected response structure") from exc


if __name__ == "__main__":
    """
    Run the geocoding MCP server with HTTP transport.
    
    The server will start on port 8001 and be ready to accept MCP tool calls 
    from the Agent Orchestrator. Use HTTP transport 
    for optimal performance and compatibility with the MCP 
    travel agent system architecture.
    """
    mcp.run(transport="http", host="127.0.0.1", port=8001)
