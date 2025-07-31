import httpx
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


class POISearchRequest(BaseModel):
    latitude: float
    longitude: float
    category: Literal[
        "tourism", "historic", "restaurant", "entertainment", "shopping"
    ] = "tourism"
    radius: int = Field(5000, ge=100, le=50000)


class POIResult(BaseModel):
    name: str | None = None
    lat: float
    lon: float
    type: str
    distance: float
    importance: float | None = None


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in meters between two coordinates."""
    r = 6371000  # Earth radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * r * asin(sqrt(a))


def build_query(lat: float, lon: float, radius: int, category: str) -> str:
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
    async with httpx.AsyncClient(timeout=30) as client:
        return await client.post(OVERPASS_URL, data=query)


@mcp.tool()
async def search_pois(request: POISearchRequest) -> List[POIResult]:
    """Discover POIs using Overpass API around given coordinates."""
    query = build_query(
        request.latitude, request.longitude, request.radius, request.category
    )
    try:
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
    for el in elements:
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        if lat is None or lon is None:
            continue
        tags = el.get("tags", {})
        name = tags.get("name")
        imp = None
        imp_tag = tags.get("importance")
        try:
            imp = float(imp_tag) if imp_tag is not None else None
        except (TypeError, ValueError):
            imp = None
        distance = _haversine(request.latitude, request.longitude, lat, lon)
        results.append(
            POIResult(
                name=name,
                lat=float(lat),
                lon=float(lon),
                type=el.get("type", "node"),
                distance=distance,
                importance=imp,
            )
        )

    results.sort(key=lambda r: ((-(r.importance or 0)), r.distance))
    return results[:20]


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
