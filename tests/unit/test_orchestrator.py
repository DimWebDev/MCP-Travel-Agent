import pytest

from app.agent.orchestrator import AgentOrchestrator
from app.agent.models import AgentResponse


class DummyClient:
    def __init__(self, data, fail: bool = False):
        self.data = data
        self.fail = fail
        self.last_payload = None

    async def call(self, payload):
        self.last_payload = payload
        if self.fail:
            raise RuntimeError("boom")
        return self.data

    async def health(self):  # pragma: no cover - not used here
        return True


@pytest.mark.asyncio
async def test_orchestrator_happy_path():
    geo = DummyClient({"lat": 1.0, "lon": 2.0})
    poi = DummyClient([{"name": "Test"}])
    wiki = DummyClient({"summary": "info"})
    orchestrator = AgentOrchestrator(
        {"geocoding": geo, "poi": poi, "wikipedia": wiki}
    )

    resp = await orchestrator.handle_query("Rome")
    assert isinstance(resp, AgentResponse)
    assert poi.last_payload == {"latitude": 1.0, "longitude": 2.0}
    assert {r.source for r in resp.results} == {
        "geocoding",
        "poi",
        "wikipedia",
    }


@pytest.mark.asyncio
async def test_orchestrator_geocode_failure():
    geo = DummyClient({}, fail=True)
    poi = DummyClient([])
    wiki = DummyClient({"summary": "info"})
    orchestrator = AgentOrchestrator(
        {"geocoding": geo, "poi": poi, "wikipedia": wiki}
    )

    resp = await orchestrator.handle_query("Nowhere")
    sources = {r.source for r in resp.results}
    assert "geocoding" not in sources  # failed geocode skipped
    assert "poi" not in sources  # POI not called due to missing coords
    assert "wikipedia" in sources
