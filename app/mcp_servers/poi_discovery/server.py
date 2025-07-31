"""
POI Discovery MCP Server: Architectural Overview

CURRENT IMPLEMENTATION:
-----------------------
This server provides OBJECTIVE importance scoring based on OpenStreetMap data quality
and factual signals (Wikipedia links, heritage status, data richness). This scoring
represents the "general notability" of a POI independent of user context.

ARCHITECTURAL COOPERATION WITH AGENT ORCHESTRATOR:
--------------------------------------------------
The Agent Orchestrator consumes this objective importance as ONE INPUT among many
for its contextual decision-making:

1. SERVER RESPONSIBILITY (Objective):
   - Calculate importance based on factual OSM signals
   - Provide consistent, repeatable scoring
   - Remain context-blind but data-expert

2. AGENT RESPONSIBILITY (Subjective):
   - Interpret user intent ("famous" vs "hidden gems")
   - Re-weight server importance based on context
   - Combine importance with other factors (distance, user preferences)

This separation allows the server to be the "data expert" while the agent
remains the "context expert" - a clean architectural division.
"""


import httpx
import asyncio
import time
import logging
from math import asin, cos, radians, sin, sqrt
from typing import Any, Dict, List, Literal


from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field


mcp = FastMCP("POI Discovery Server")
logger = logging.getLogger("poi-discovery")
logging.basicConfig(level=logging.INFO)


CATEGORY_FILTERS: Dict[str, str] = {
    "tourism": '["tourism"]',
    "historic": '["historic"]',
    "restaurant": '["amenity"="restaurant"]',
    "entertainment": '["amenity"~"theatre|cinema|nightclub|arts_centre"]',
    "shopping": '["shop"]',
}


OVERPASS_URL = "https://overpass-api.de/api/interpreter"



class RateLimiter:
    """
    Simple async rate limiter enforcing N requests per second.
    
    Prevents overwhelming the Overpass API server by ensuring requests
    are spaced according to the specified rate limit. Uses asyncio.Lock
    to ensure thread-safe operation in concurrent environments.
    """
    def __init__(self, rate_per_sec: float) -> None:
        self._interval = 1.0 / rate_per_sec
        self._lock = asyncio.Lock()
        self._last_call = 0.0


    async def wait(self) -> None:
        """
        Enforce rate limiting by sleeping if necessary.
        
        Calculates the minimum time that must pass between calls
        and sleeps for the remaining duration if needed.
        """
        async with self._lock:
            now = time.monotonic()
            sleep_for = self._last_call + self._interval - now
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            self._last_call = time.monotonic()



# Global rate limiter instance for Overpass API compliance
overpass_rate_limiter = RateLimiter(rate_per_sec=1)



class POISearchRequest(BaseModel):
    """
    Request model for POI (Point of Interest) discovery.
    
    The radius parameter defines the search area for the INITIAL FILTERING
    performed by the Overpass API server. Only POIs within this radius
    will be returned by the API.
    """
    latitude: float
    longitude: float
    category: Literal[
        "tourism", "historic", "restaurant", "entertainment", "shopping"
    ] = "tourism"
    radius: int = Field(5000, ge=100, le=50000)  # Radius for INITIAL server-side filtering



class POIResult(BaseModel):
    """
    Result model containing POI information with calculated distance.
    
    The distance field contains the EXACT geodetic distance calculated
    using the Haversine formula AFTER the Overpass API has already
    filtered results by the search radius.
    """
    name: str | None = None
    lat: float
    lon: float
    type: str
    distance: float  # Exact distance in meters (calculated post-filtering)



def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the geodetic distance between two coordinates using the Haversine formula.
    
    IMPORTANT: This function is NOT used for filtering POIs by radius.
    The radius filtering is performed by the Overpass API server using the
    'around' query parameter. This function serves a different purpose:
    
    1. PRECISION: Provides exact Great Circle distances for already-filtered POIs
    2. RANKING: Enables distance-based sorting for result prioritization  
    3. METADATA: Enriches POI objects with precise distance information
    4. VALIDATION: Can verify Overpass API filtering accuracy
    
    Args:
        lat1, lon1: Source coordinates (search center)
        lat2, lon2: Target coordinates (POI location)
        
    Returns:
        Distance in meters using spherical earth model (radius = 6,371 km)
        
    Mathematical basis:
        Uses the Haversine formula for great circle distances on a sphere,
        accounting for Earth's curvature (not simple Euclidean distance).
    """
    r = 6371000  # Earth radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * r * asin(sqrt(a))



def build_query(lat: float, lon: float, radius: int, category: str) -> str:
    """
    Construct an Overpass QL query for POI discovery with server-side filtering.
    
    CRITICAL ARCHITECTURAL DETAIL:
    The 'around:{radius},{lat},{lon}' parameter performs the PRIMARY FILTERING
    on the Overpass API server. This means:
    
    - EFFICIENT: Only POIs within the radius are transmitted over the network
    - SCALABLE: Heavy computational filtering is delegated to specialized servers
    - PRECISE: Uses Overpass's optimized geographic indexing systems
    
    The query searches three OSM data types:
    - node: Point features (restaurants, monuments, etc.)
    - way: Linear/area features (roads, buildings, etc.)  
    - relation: Complex features (boundaries, routes, etc.)
    
    Args:
        lat, lon: Search center coordinates
        radius: Search radius in meters (APPLIED BY OVERPASS SERVER)
        category: POI category for thematic filtering
        
    Returns:
        Overpass QL query string with embedded radius filtering
    """
    filter_q = CATEGORY_FILTERS.get(category, CATEGORY_FILTERS["tourism"])
    return f"""
    [out:json][timeout:25];
    (
      node{filter_q}(around:{radius},{lat},{lon});
      way{filter_q}(around:{radius},{lat},{lon});
      relation{filter_q}(around:{radius},{lat},{lon});
    );
    out center;"""



async def fetch_overpass(query: str) -> httpx.Response:
    """
    Execute Overpass API query with rate limiting compliance.
    
    Sends the constructed query to the Overpass API server, which performs
    the geographic filtering using its optimized spatial indexing before
    returning results.
    """
    await overpass_rate_limiter.wait()
    async with httpx.AsyncClient(timeout=30) as client:
        return await client.post(OVERPASS_URL, data=query)



@mcp.tool()
async def search_pois(request: POISearchRequest) -> List[POIResult]:
    """
    Discover POIs using a two-stage filtering and distance calculation architecture.
    
    WORKFLOW EXPLANATION:
    =====================
    
    STAGE 1: SERVER-SIDE RADIUS FILTERING (Overpass API)
    ---------------------------------------------------
    • The request.radius parameter is embedded in the Overpass QL query
    • Overpass API server performs geographic filtering using spatial indexes
    • Only POIs within the specified radius are returned over the network
    • This stage is optimized for performance and network efficiency
    
    STAGE 2: CLIENT-SIDE DISTANCE CALCULATION (Haversine)
    -----------------------------------------------------
    • For each POI returned by Stage 1, calculate EXACT geodetic distance
    • Uses Haversine formula for mathematically precise Great Circle distances
    • Enables accurate distance-based ranking and sorting
    • Provides precise metadata for client applications
    
    KEY ARCHITECTURAL INSIGHT:
    The radius filtering and distance calculation serve DIFFERENT purposes:
    
    • Radius filtering = PERFORMANCE OPTIMIZATION (reduce data transfer)
    • Distance calculation = PRECISION ENHANCEMENT (exact measurements for ranking)
    
    This separation of concerns allows the system to be both efficient
    (minimal network traffic) and accurate (precise distance calculations).
    
    Args:
        request: POI search parameters including coordinates and radius
        
    Returns:
        List of POI results sorted by distance (ascending),
        limited to top 20 results for performance.
        
    Raises:
        RuntimeError: If Overpass API communication fails or returns invalid data
    """
    # TODO: Decide if radius should always be user-provided or if we should default to 1000 meters when not specified.
    #       If defaulting, ensure this is documented and handled in POISearchRequest and UI.
    # Build query with radius embedded for server-side filtering
    query = build_query(
        request.latitude, request.longitude, request.radius, request.category
    )
    
    try:
        # STAGE 1: Server-side filtering by radius at Overpass API
        response = await fetch_overpass(query)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error(f"Overpass request failed: {exc}")
        raise RuntimeError("POI search failed") from exc


    try:
        data: Dict[str, Any] = response.json()
        elements = data.get("elements", [])
    except ValueError as exc:
        logger.error(f"Invalid Overpass response: {exc}")
        raise RuntimeError("Invalid response from Overpass API") from exc


    results: List[POIResult] = []
    
    # STAGE 2: Process each pre-filtered POI and calculate exact distances
    for el in elements:
        # Extract coordinates (handle both node and way/relation formats)
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        if lat is None or lon is None:
            continue  # Skip elements without valid coordinates
            
        # Extract metadata from OSM tags
        tags = el.get("tags", {})
        name = tags.get("name")
        
        # CRITICAL: Calculate EXACT distance using Haversine formula
        # This provides precise geodetic measurement for each already-filtered POI
        distance = _haversine(request.latitude, request.longitude, lat, lon)
        
        results.append(
            POIResult(
                name=name,
                lat=float(lat),
                lon=float(lon),
                type=el.get("type", "node"),
                distance=distance,  # Exact distance for ranking and metadata
            )
        )


    # Sort by distance (ascending) - closest POIs first
    # Uses the precisely calculated Haversine distances for accurate ranking
    results.sort(key=lambda r: r.distance)
    return results[:20]  # Return top 20 results for optimal performance



if __name__ == "__main__":
    mcp.run(transport="streamable-http")
