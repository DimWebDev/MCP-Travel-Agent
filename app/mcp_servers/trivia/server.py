"""
Trivia MCP Server: Travel Fact Discovery via DuckDuckGo

This module implements a specialized MCP server that uses the
DuckDuckGo Instant Answer API to retrieve concise trivia facts for
travel-related topics. It performs context matching to ensure returned
facts are relevant to the provided travel context and applies a simple
source reliability scoring system to filter out low-quality information.

ARCHITECTURAL ROLE:
-------------------
The Trivia server functions as an enrichment provider within the
MCP-orchestrated travel agent system. It supplies interesting facts
about destinations or landmarks that can be incorporated into travel
recommendations. The server exposes a single tool `get_trivia` that
accepts a topic and optional context (e.g., city or country) and returns
a structured `TriviaResponse`.

DuckDuckGo's Instant Answer API has no official rate limits, but this
server includes a conservative rate limiter to ensure respectful usage
when operating in concurrent environments.
"""

from __future__ import annotations

import asyncio
import logging
import time

from typing import Any, Dict, Optional, Tuple
import os

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# MCP CONFIGURATION AND GLOBALS
# ---------------------------------------------------------------------------

mcp = FastMCP("Trivia Server")
logger = logging.getLogger("trivia-server")
logging.basicConfig(level=logging.INFO)

DUCKDUCKGO_URL = "https://api.duckduckgo.com/"
CONTACT_EMAIL = os.getenv("MCP_CONTACT_EMAIL", "contact@example.com")
HEADERS = {
    # Provide a contact address so DuckDuckGo can reach out if necessary.
    # The value can be overridden by setting ``MCP_CONTACT_EMAIL``.
    "User-Agent": f"MCP-Travel-Agent/1.0 ({CONTACT_EMAIL})",
    "Accept": "application/json",
}

# Conservative rate limit: 1 request/second

class RateLimiter:
    """Asynchronous rate limiter to enforce minimum delay between requests."""

    def __init__(self, rate_per_sec: float) -> None:
        self._interval = 1.0 / rate_per_sec
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def wait(self) -> None:
        """Sleep to maintain desired request rate."""
        async with self._lock:
            now = time.monotonic()
            sleep_for = self._last_call + self._interval - now
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            self._last_call = time.monotonic()

rate_limiter = RateLimiter(rate_per_sec=1)

# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class TriviaRequest(BaseModel):
    """Request model for trivia lookups."""

    topic: str = Field(description="Topic to search trivia for")
    context: Optional[str] = Field(
        default=None,
        description="Optional travel context such as a city or country",
    )

class TriviaResponse(BaseModel):
    """Structured trivia fact and metadata."""

    trivia: str = Field(description="Trivia fact text")
    source: str = Field(description="Source of the trivia fact")
    url: Optional[str] = Field(default=None, description="URL to the source")
    reliability: float = Field(
        description="Source reliability score between 0 and 1", ge=0.0, le=1.0
    )

# --- Resolve forward references for Pydantic v2 -----------------------------
TriviaRequest.model_rebuild()
TriviaResponse.model_rebuild()
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Reliability scoring and travel relevance helpers
# ---------------------------------------------------------------------------

SOURCE_RELIABILITY = {
    "wikipedia": 0.9,
    "britannica": 0.8,
    "duckduckgo": 0.6,
}
RELIABILITY_THRESHOLD = 0.6
TRAVEL_KEYWORDS = {
    "travel", "tourist", "tourism", "visit", "destination",
    "city", "country", "landmark", "museum", "beach", "mountain",
    "attraction", "monument", "historic", "culture", "architecture",
    "famous", "popular", "location", "site", "built", "constructed",
}

def score_source(source: str) -> float:
    """Return reliability score for a source name."""
    return SOURCE_RELIABILITY.get(source.lower(), 0.5)

def matches_context(text: str, request: TriviaRequest) -> bool:
    """Check if a fact matches provided context and travel relevance."""
    text_lower = text.lower()
    if request.context:
        context_words = request.context.lower().split()
        if not any(word in text_lower for word in context_words):
            return False
    topic_words = request.topic.lower().split()
    relevant_keywords = TRAVEL_KEYWORDS.union(topic_words)
    return any(word in text_lower for word in relevant_keywords)

# ---------------------------------------------------------------------------
# DuckDuckGo API wrapper
# ---------------------------------------------------------------------------

async def fetch_duckduckgo(topic: str, context: Optional[str]) -> Dict[str, Any]:
    """Query DuckDuckGo Instant Answer API and return JSON data."""
    query = f"{topic} {context}".strip()
    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "no_redirect": 1,
    }
    await rate_limiter.wait()
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(DUCKDUCKGO_URL, params=params, headers=HEADERS)
        response.raise_for_status()
        return response.json()

# ---------------------------------------------------------------------------
# Fact extraction logic with fallback strategy
# ---------------------------------------------------------------------------

def extract_fact(data: Dict[str, Any], request: TriviaRequest) -> Tuple[str, str, str]:
    """
    Extract a context-matched fact from DuckDuckGo response using fallback logic.

    FALLBACK STRATEGY:
    ------------------
    Stage 1: STRICT FILTERING - Both context matching AND travel relevance required
    Stage 2: RELAXED FILTERING - Only topic matching required (if Stage 1 fails)

    This two-stage approach ensures high-quality results when possible while
    providing graceful degradation to prevent "No trivia found" errors.
    """
    candidates: list[Tuple[str, str, str]] = []

    # Collect all potential facts from DuckDuckGo response
    abstract = data.get("AbstractText")
    if abstract:
        candidates.append(
            (abstract, data.get("AbstractSource", "DuckDuckGo"), data.get("AbstractURL", "")),
        )

    # Related topics may contain additional facts
    for item in data.get("RelatedTopics", []):
        if isinstance(item, dict):
            if "Text" in item:
                candidates.append((item["Text"], "DuckDuckGo", item.get("FirstURL", "")))
            elif "Topics" in item:
                for sub in item.get("Topics", []):
                    if "Text" in sub:
                        candidates.append((sub["Text"], "DuckDuckGo", sub.get("FirstURL", "")))

    # STAGE 1: Try strict filtering (context + travel keywords)
    strict_result = _extract_fact_strict(candidates, request)
    if strict_result[0]:
        return strict_result

    # STAGE 2: Fallback to relaxed filtering (topic-only)
    return _extract_fact_relaxed(candidates, request)

def _extract_fact_strict(candidates: list[Tuple[str, str, str]], request: TriviaRequest) -> Tuple[str, str, str]:
    """Apply strict filtering requiring both context matching AND travel relevance."""
    for text, source, url in candidates:
        if matches_context(text, request):
            return text, source, url
    return "", "", ""

def _extract_fact_relaxed(candidates: list[Tuple[str, str, str]], request: TriviaRequest) -> Tuple[str, str, str]:
    """Apply relaxed filtering requiring only topic matching."""
    topic_words = set(request.topic.lower().split())

    # First pass: topic match + optional context preference
    for text, source, url in candidates:
        text_lower = text.lower()
        if any(topic_word in text_lower for topic_word in topic_words):
            if request.context:
                context_words = request.context.lower().split()
                if any(context_word in text_lower for context_word in context_words):
                    return text, source, url
            else:
                return text, source, url

    # Final fallback: any topic match
    for text, source, url in candidates:
        text_lower = text.lower()
        if any(topic_word in text_lower for topic_word in topic_words):
            return text, source, url

    return "", "", ""

# ---------------------------------------------------------------------------
# MCP Tool Implementation
# ---------------------------------------------------------------------------

async def _get_trivia_impl(request: TriviaRequest) -> TriviaResponse:
    """
    Implementation of travel-related trivia fetching using DuckDuckGo Instant Answer API.

    WORKFLOW:
    1. Fetch data from DuckDuckGo with rate limiting
    2. Extract context-matched fact using fallback logic
    3. Score source reliability and filter low-quality results
    4. Return structured trivia response

    Raises:
        RuntimeError: On network errors, missing data, or low-reliability sources
    """
    try:
        data = await fetch_duckduckgo(request.topic, request.context)
    except httpx.TimeoutException as exc:
        logger.error("DuckDuckGo request timed out: %s", exc)
        raise RuntimeError("DuckDuckGo request timed out") from exc
    except httpx.HTTPError as exc:
        logger.error("DuckDuckGo API error: %s", exc)
        raise RuntimeError("DuckDuckGo API error") from exc

    fact, source, url = extract_fact(data, request)
    if not fact:
        raise RuntimeError("No travel-relevant trivia found")

    reliability = score_source(source)
    if reliability < RELIABILITY_THRESHOLD:
        raise RuntimeError("Low reliability source")

    return TriviaResponse(trivia=fact, source=source, url=url or None, reliability=reliability)


@mcp.tool()
async def get_trivia(request: TriviaRequest) -> TriviaResponse:
    """
    Fetch travel-related trivia using DuckDuckGo Instant Answer API.
    
    This is the MCP tool wrapper that delegates to the implementation function.
    """
    return await _get_trivia_impl(request)

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8004)
