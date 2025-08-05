import pytest
from fastapi.testclient import TestClient

from app import main
from app.agent.orchestrator import AgentOrchestrator


class DummyClient:
    def __init__(self, data):
        self.data = data

    async def call(self, payload):
        return self.data

    async def health(self):
        return True


@pytest.fixture()
def client(monkeypatch):
    geo = DummyClient({"lat": 1.0, "lon": 2.0})
    poi = DummyClient([{"name": "Test"}])
    wiki = DummyClient({"summary": "info"})
    orchestrator = AgentOrchestrator(
        {"geocoding": geo, "poi": poi, "wikipedia": wiki}
    )
    monkeypatch.setattr(main, "orchestrator", orchestrator)
    return TestClient(main.app)


def test_query_endpoint(client):
    resp = client.post("/query", json={"query": "Rome"})
    assert resp.status_code == 200
    body = resp.json()
    assert "results" in body
    assert len(body["results"]) == 3


def test_health_endpoint(client):
    resp = client.get("/health/geocoding")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
