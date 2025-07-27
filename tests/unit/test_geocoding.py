import asyncio
import json
from typing import List

import httpx
import pytest

from app.mcp_servers.geocoding import server
from app.mcp_servers.geocoding.server import GeocodeRequest, GeocodeResponse, RateLimiter


class MockResponse(httpx.Response):
    """Helper to create an httpx.Response with JSON."""

    def __init__(self, status_code: int, json_data: List[dict] | None = None):
        content = json.dumps(json_data or []).encode()
        request = httpx.Request("GET", "https://testserver/")
        super().__init__(status_code, request=request, content=content)


@pytest.mark.asyncio
async def test_geocode_success(monkeypatch):
    async def mock_fetch(name: str) -> httpx.Response:
        return MockResponse(200, [{"lat": "1.0", "lon": "2.0", "display_name": "Test"}])

    monkeypatch.setattr(server, "fetch_location", mock_fetch)
    monkeypatch.setattr(server.rate_limiter, "wait", lambda: asyncio.sleep(0))

    result = await server.geocode_location(GeocodeRequest(location_name="Rome"))
    assert isinstance(result, GeocodeResponse)
    assert result.lat == 1.0
    assert result.lon == 2.0
    assert result.display_name == "Test"


@pytest.mark.asyncio
async def test_geocode_not_found(monkeypatch):
    async def mock_fetch(name: str) -> httpx.Response:
        return MockResponse(200, [])

    monkeypatch.setattr(server, "fetch_location", mock_fetch)
    monkeypatch.setattr(server.rate_limiter, "wait", lambda: asyncio.sleep(0))

    with pytest.raises(RuntimeError, match="Location not found"):
        await server.geocode_location(GeocodeRequest(location_name="Unknown"))


@pytest.mark.asyncio
async def test_geocode_http_error(monkeypatch):
    async def mock_fetch(name: str) -> httpx.Response:
        return MockResponse(500)

    monkeypatch.setattr(server, "fetch_location", mock_fetch)
    monkeypatch.setattr(server.rate_limiter, "wait", lambda: asyncio.sleep(0))

    with pytest.raises(RuntimeError, match="HTTP error"):
        await server.geocode_location(GeocodeRequest(location_name="Rome"))


@pytest.mark.asyncio
async def test_geocode_timeout(monkeypatch):
    async def mock_fetch(name: str) -> httpx.Response:
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(server, "fetch_location", mock_fetch)
    monkeypatch.setattr(server.rate_limiter, "wait", lambda: asyncio.sleep(0))

    with pytest.raises(RuntimeError, match="timed out"):
        await server.geocode_location(GeocodeRequest(location_name="Rome"))


@pytest.mark.asyncio
async def test_rate_limiter(monkeypatch):
    times = [0.0, 0.0, 0.1, 0.1, 1.2, 1.2]
    index = {"i": 0}

    def fake_monotonic():
        value = times[index["i"]]
        index["i"] += 1
        return value

    sleep_durations = []

    async def fake_sleep(d):
        sleep_durations.append(d)

    limiter = RateLimiter(1)
    monkeypatch.setattr(server.time, "monotonic", fake_monotonic)
    monkeypatch.setattr(server.asyncio, "sleep", fake_sleep)

    await limiter.wait()
    await limiter.wait()

    assert pytest.approx(sleep_durations[1], 0.01) == 0.9
