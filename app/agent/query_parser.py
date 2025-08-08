"""Natural language query parsing using GPT-4o-mini.

This module converts free-form user input into structured parameters that
feed the fixed geocode → POI → Wikipedia workflow. It relies on the OpenAI
API and expects the ``OPENAI_API_KEY`` environment variable to be set.
"""

from __future__ import annotations

import json
import os
from typing import Dict

from openai import AsyncOpenAI

# The client is created once and re-used for all calls. A placeholder key is
# provided so test environments without a real API key can still import this
# module; tests patch the client's method to avoid real network calls.
_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "test-key"))

# Categories understood by the POI MCP server. The language model is asked to
# choose one of these values when interpreting user requests.
CATEGORIES = ["tourism", "historic", "restaurant", "entertainment", "shopping"]


async def parse_user_query(query: str) -> Dict[str, str]:
    """Extract a location and category keyword from ``query``.

    The function prompts GPT-4o-mini with clear instructions to return a JSON
    object containing ``location`` and ``category``. If the model output cannot
    be parsed, a conservative fallback is returned so downstream calls still
    receive usable values.
    """

    system_prompt = (
        "You are a parser that extracts travel parameters. "
        "Return a JSON object with keys 'location' and 'category'. "
        f"The category must be one of {CATEGORIES}."
    )

    try:
        response = await _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            temperature=0,
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        location = str(data.get("location", "")).strip() or query
        category = str(data.get("category", "tourism")).strip()
        if category not in CATEGORIES:
            category = "tourism"
        return {"location": location, "category": category}
    except Exception:
        # On any failure, fall back to using the raw query as the location and
        # a safe default category so that the workflow can still proceed.
        return {"location": query, "category": "tourism"}
