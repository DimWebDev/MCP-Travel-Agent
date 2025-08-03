import json
from typing import Any, Dict

import httpx
import pytest

from app.mcp_servers.wikipedia import server
from app.mcp_servers.wikipedia.server import WikipediaRequest, WikipediaResponse


class MockResponse(httpx.Response):
    """Helper to create an httpx.Response with JSON."""

    def __init__(self, status_code: int, json_data: Dict[str, Any] | None = None):
        content = json.dumps(json_data or {}).encode()
        request = httpx.Request("GET", "https://testserver/")
        super().__init__(status_code, request=request, content=content)


@pytest.mark.asyncio
async def test_wikipedia_success(monkeypatch):
    mock_data = {
        "extract": "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Eiffel_Tower"}},
        "pageid": 9202,
        "title": "Eiffel Tower"
    }

    async def mock_search(poi_name: str, location_context: str | None = None) -> Dict[str, Any]:
        return mock_data

    async def async_noop():
        pass

    monkeypatch.setattr(server, "search_wikipedia", mock_search)
    monkeypatch.setattr(server.rate_limiter, "wait", async_noop)

    result = await server.get_wikipedia_info(
        WikipediaRequest(poi_name="Eiffel Tower", location_context="Paris")
    )
    
    assert isinstance(result, WikipediaResponse)
    assert "Eiffel Tower" in result.extract
    assert result.url == "https://en.wikipedia.org/wiki/Eiffel_Tower"


@pytest.mark.asyncio
async def test_wikipedia_not_found(monkeypatch):
    async def mock_search(poi_name: str, location_context: str | None = None) -> Dict[str, Any]:
        return {}  # No 'extract' key → article not found

    async def async_noop():
        pass

    monkeypatch.setattr(server, "search_wikipedia", mock_search)
    monkeypatch.setattr(server.rate_limiter, "wait", async_noop)

    with pytest.raises(RuntimeError, match="No Wikipedia article found"):
        await server.get_wikipedia_info(WikipediaRequest(poi_name="NonexistentPlace"))


@pytest.mark.asyncio
async def test_wikipedia_timeout(monkeypatch):
    async def mock_search(poi_name: str, location_context: str | None = None) -> Dict[str, Any]:
        raise httpx.TimeoutException("Timeout")

    async def async_noop():
        pass

    monkeypatch.setattr(server, "search_wikipedia", mock_search)
    monkeypatch.setattr(server.rate_limiter, "wait", async_noop)

    with pytest.raises(RuntimeError, match="timed out"):
        await server.get_wikipedia_info(WikipediaRequest(poi_name="Test"))


@pytest.mark.asyncio
async def test_wikipedia_http_error(monkeypatch):
    async def mock_search(poi_name: str, location_context: str | None = None) -> Dict[str, Any]:
        response = MockResponse(500, {"error": "Server Error"})
        error = httpx.HTTPStatusError("API Error", request=response.request, response=response)
        raise error

    async def async_noop():
        pass

    monkeypatch.setattr(server, "search_wikipedia", mock_search)
    monkeypatch.setattr(server.rate_limiter, "wait", async_noop)

    with pytest.raises(RuntimeError, match="Wikipedia API error"):
        await server.get_wikipedia_info(WikipediaRequest(poi_name="Test"))


@pytest.mark.asyncio
async def test_wikipedia_invalid_json_structure(monkeypatch):
    """Test handling of malformed Wikipedia API responses"""
    async def mock_search(poi_name: str, location_context: str | None = None) -> Dict[str, Any]:
        # Return data that will cause KeyError when accessing expected fields
        return {"unexpected_structure": "no extract field"}

    async def async_noop():
        pass

    monkeypatch.setattr(server, "search_wikipedia", mock_search)
    monkeypatch.setattr(server.rate_limiter, "wait", async_noop)

    with pytest.raises(RuntimeError, match="No Wikipedia article found"):
        await server.get_wikipedia_info(WikipediaRequest(poi_name="InvalidStructure"))
