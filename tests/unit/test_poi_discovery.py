import json
from typing import List

import httpx
import pytest

from app.mcp_servers.poi_discovery import server
from app.mcp_servers.poi_discovery.server import POISearchRequest, POIResult


class MockResponse(httpx.Response):
    def __init__(self, status_code: int, json_data: dict | None = None):
        content = json.dumps(json_data or {}).encode()
        request = httpx.Request("POST", "https://testserver/")
        super().__init__(status_code, request=request, content=content)


@pytest.mark.asyncio
async def test_search_success(monkeypatch):
    payload = {
        "elements": [
            {
                "type": "node",
                "lat": 1.0,
                "lon": 2.0,
                "tags": {"name": "Spot", "importance": "0.9"},
            }
        ]
    }

    async def mock_fetch(q: str) -> httpx.Response:
        return MockResponse(200, payload)

    monkeypatch.setattr(server, "fetch_overpass", mock_fetch)

    results = await server.search_pois(POISearchRequest(latitude=1.0, longitude=2.0))
    assert isinstance(results, list)
    assert isinstance(results[0], POIResult)
    assert results[0].name == "Spot"


@pytest.mark.asyncio
async def test_search_http_error(monkeypatch):
    async def mock_fetch(q: str) -> httpx.Response:
        return MockResponse(500)

    monkeypatch.setattr(server, "fetch_overpass", mock_fetch)

    with pytest.raises(RuntimeError, match="POI search failed"):
        await server.search_pois(POISearchRequest(latitude=0.0, longitude=0.0))


@pytest.mark.asyncio
async def test_search_invalid_json(monkeypatch):
    class BadResponse(httpx.Response):
        def json(self):
            raise ValueError("bad json")

    async def mock_fetch(q: str) -> httpx.Response:
        return BadResponse(200, request=httpx.Request("POST", "https://t/"))

    monkeypatch.setattr(server, "fetch_overpass", mock_fetch)

    with pytest.raises(RuntimeError, match="Invalid response"):
        await server.search_pois(POISearchRequest(latitude=0.0, longitude=0.0))


@pytest.mark.asyncio
async def test_ranking(monkeypatch):
    payload = {
        "elements": [
            {
                "type": "node",
                "lat": 1.0,
                "lon": 2.001,
                "tags": {"name": "B", "importance": "0.5"},
            },
            {
                "type": "node",
                "lat": 1.0005,
                "lon": 2.0,
                "tags": {"name": "A", "importance": "0.9"},
            },
        ]
    }

    async def mock_fetch(q: str) -> httpx.Response:
        return MockResponse(200, payload)

    monkeypatch.setattr(server, "fetch_overpass", mock_fetch)

    results = await server.search_pois(POISearchRequest(latitude=1.0, longitude=2.0))
    assert results[0].name == "A"
    assert results[1].name == "B"
