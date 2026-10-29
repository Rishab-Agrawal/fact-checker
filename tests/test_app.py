import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from fact_checker import app


class FakeGraph:
    def __init__(self, fail: bool = False):
        self.fail = fail

    def stream(self, *args, **kwargs):
        yield (), {"name": "extract", "input": {}}
        yield (), {"name": "extract", "error": None, "result": {}}
        if self.fail:
            raise RuntimeError("secret detail")

    def get_state(self, config):
        values = {"reply": "False.", "results": [], "message": {"received_at": "2026-01-01T00:00:00+00:00"}}
        return SimpleNamespace(values=values, created_at="2026-01-01T00:00:07+00:00")


@pytest.fixture(autouse=True)
def no_admin_bot(monkeypatch):
    monkeypatch.delenv("TELEGRAM_ADMIN_BOT_TOKEN", raising=False)


def post(monkeypatch, graph, ip):
    monkeypatch.setattr(app, "graph", lambda: graph)
    response = TestClient(app.app).post("/api/checks", json={"text": "x"}, headers={"X-Real-IP": ip})
    return [json.loads(line) for line in response.text.splitlines()]


def test_rate_limit_is_per_ip():
    assert all(app.allow("1.1.1.1") for _ in range(app.PER_IP_DAILY))
    assert not app.allow("1.1.1.1")
    assert app.allow("2.2.2.2")


def test_check_streams_its_id_then_started_steps_then_the_result(monkeypatch):
    events = post(monkeypatch, FakeGraph(), "3.3.3.3")
    result = {"reply": "False.", "results": [], "seconds": 7}
    assert events[1:] == [{"step": "Reading the message"}, result]
    assert TestClient(app.app).get(f"/api/checks/{events[0]['id']}").json() == result


def test_a_running_check_reads_as_pending(monkeypatch):
    monkeypatch.setattr(app, "running", {"abc"})
    assert TestClient(app.app).get("/api/checks/abc").json() == {"pending": True}


def test_failure_reaches_the_page_only_as_a_generic_error(monkeypatch):
    events = post(monkeypatch, FakeGraph(fail=True), "4.4.4.4")
    assert events[-1] == {"error": "failed"}
    assert "secret" not in json.dumps(events)
