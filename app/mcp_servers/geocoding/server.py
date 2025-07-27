import asyncio
import time
from typing import Any, List

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel


class RateLimiter:
    """Simple async rate limiter enforcing N requests per second."""

    def __init__(self, rate_per_sec: float) -> None:
        self._interval = 1.0 / rate_per_sec
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            sleep_for = self._last_call + self._interval - now
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            self._last_call = time.monotonic()


class GeocodeRequest(BaseModel):
    location_name: str


class GeocodeResponse(BaseModel):
    lat: float
    lon: float
    display_name: str


mcp = FastMCP("Geocoding Server")
rate_limiter = RateLimiter(rate_per_sec=1)
BASE_URL = "https://nominatim.openstreetmap.org"
HEADERS = {"User-Agent": "MCP-Travel-Agent"}


async def fetch_location(location_name: str) -> httpx.Response:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        return await client.get(
            "/search",
            params={"q": location_name, "format": "json", "limit": 1},
            headers=HEADERS,
        )


@mcp.tool()
async def geocode_location(request: GeocodeRequest) -> GeocodeResponse:
    """Resolve a location name to coordinates using OSM Nominatim."""

    await rate_limiter.wait()
    try:
        response = await fetch_location(request.location_name)
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise RuntimeError("Geocoding request timed out") from exc
    except httpx.HTTPError as exc:
        raise RuntimeError(f"HTTP error: {exc.response.status_code}") from exc

    try:
        data: List[dict[str, Any]] = response.json()
    except ValueError as exc:
        raise RuntimeError("Invalid response from geocoding API") from exc

    if not data:
        raise RuntimeError("Location not found")

    item = data[0]
    try:
        return GeocodeResponse(
            lat=float(item["lat"]),
            lon=float(item["lon"]),
            display_name=item["display_name"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("Unexpected response structure") from exc


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
