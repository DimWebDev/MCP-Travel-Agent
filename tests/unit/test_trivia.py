import json
from typing import Any, Dict

import httpx
import pytest

from app.mcp_servers.trivia import server
from app.mcp_servers.trivia.server import TriviaRequest, TriviaResponse


class MockResponse(httpx.Response):
    """Helper to build an httpx.Response with JSON content."""

    def __init__(self, status_code: int, json_data: Dict[str, Any] | None = None):
        content = json.dumps(json_data or {}).encode()
        request = httpx.Request("GET", "https://testserver/")
        super().__init__(status_code, request=request, content=content)


@pytest.mark.asyncio
async def test_trivia_success(monkeypatch):
    mock_data = {
        "AbstractText": "The Eiffel Tower in Paris attracts millions of tourists each year.",
        "AbstractSource": "Wikipedia",
        "AbstractURL": "https://en.wikipedia.org/wiki/Eiffel_Tower",
    }

    async def mock_fetch(topic: str, context: str | None) -> Dict[str, Any]:
        return mock_data

    async def async_noop():
        pass

    monkeypatch.setattr(server, "fetch_duckduckgo", mock_fetch)
    monkeypatch.setattr(server.rate_limiter, "wait", async_noop)

    result = await server._get_trivia_impl(
        TriviaRequest(topic="Eiffel Tower", context="Paris")
    )

    assert isinstance(result, TriviaResponse)
    assert "Paris" in result.trivia
    assert result.source == "Wikipedia"
    assert result.reliability >= 0.8


@pytest.mark.asyncio
async def test_trivia_low_reliability(monkeypatch):
    mock_data = {
        "AbstractText": "The Eiffel Tower in Paris has 1665 steps.",
        "AbstractSource": "RandomBlog",
    }

    async def mock_fetch(topic: str, context: str | None) -> Dict[str, Any]:
        return mock_data

    async def async_noop():
        pass

    monkeypatch.setattr(server, "fetch_duckduckgo", mock_fetch)
    monkeypatch.setattr(server.rate_limiter, "wait", async_noop)

    with pytest.raises(RuntimeError, match="Low reliability"):
        await server._get_trivia_impl(TriviaRequest(topic="Eiffel Tower", context="Paris"))


@pytest.mark.asyncio
async def test_trivia_no_relevant_fact(monkeypatch):
    mock_data = {
        "AbstractText": "This fact is unrelated and lacks travel context.",
        "AbstractSource": "Wikipedia",
    }

    async def mock_fetch(topic: str, context: str | None) -> Dict[str, Any]:
        return mock_data

    async def async_noop():
        pass

    monkeypatch.setattr(server, "fetch_duckduckgo", mock_fetch)
    monkeypatch.setattr(server.rate_limiter, "wait", async_noop)

    with pytest.raises(RuntimeError, match="No travel-relevant trivia"):
        await server._get_trivia_impl(TriviaRequest(topic="Eiffel Tower", context="Paris"))


@pytest.mark.asyncio
async def test_trivia_http_error(monkeypatch):
    async def mock_fetch(topic: str, context: str | None) -> Dict[str, Any]:
        raise httpx.HTTPStatusError(
            "error",
            request=httpx.Request("GET", "https://api.duckduckgo.com"),
            response=MockResponse(500),
        )

    async def async_noop():
        pass

    monkeypatch.setattr(server, "fetch_duckduckgo", mock_fetch)
    monkeypatch.setattr(server.rate_limiter, "wait", async_noop)

    with pytest.raises(RuntimeError, match="DuckDuckGo API error"):
        await server._get_trivia_impl(TriviaRequest(topic="Eiffel Tower"))
