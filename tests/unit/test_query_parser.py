import json

import pytest

from app.agent.query_parser import parse_user_query


class DummyResponse:
    def __init__(self, content: str):
        self.choices = [
            type("Choice", (), {"message": type("Msg", (), {"content": content})})
        ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query, expected",
    [
        (
            "What can I do in Barcelona for a romantic evening?",
            {"location": "Barcelona", "category": "restaurant"},
        ),
        (
            "Show me family-friendly activities in London",
            {"location": "London", "category": "entertainment"},
        ),
        (
            "I want to explore historical sites in Rome",
            {"location": "Rome", "category": "historic"},
        ),
    ],
)
async def test_parse_user_query(monkeypatch, query, expected):
    async def fake_create(*args, **kwargs):
        return DummyResponse(json.dumps(expected))

    monkeypatch.setattr(
        "app.agent.query_parser._client.chat.completions.create", fake_create
    )

    result = await parse_user_query(query)
    assert result == expected
