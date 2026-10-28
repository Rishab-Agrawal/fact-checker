import pytest

from fact_checker import evidence, graph
from fact_checker.evidence import credible
from fact_checker.graph import cite, fresh

EVIDENCE = [{"id": "F1", "title": "Alt News rated a claim \"False\"", "url": "https://altnews.in/x"}]


def test_verdict_without_existing_citation_is_unverifiable():
    judgement = {"verdict": "false", "confidence": 0.9, "rationale": "r", "citations": ["W7"]}
    assert cite(judgement, EVIDENCE, "c")["verdict"] == "unverifiable"


def test_cited_verdict_keeps_sources():
    judgement = {"verdict": "false", "confidence": 0.9, "rationale": "r", "citations": ["F1"]}
    out = cite(judgement, EVIDENCE, "c")
    assert out["verdict"] == "false"
    assert out["sources"] == [{"title": EVIDENCE[0]["title"], "url": "https://altnews.in/x"}]


def test_memory_is_fresh_only_within_window_and_never_from_the_future():
    assert fresh("2026-10-01", "2026-10-26")
    assert not fresh("2026-08-01", "2026-10-26")
    assert not fresh("2026-10-27", "2026-10-26")


def test_credible_uses_domain_ratings_and_official_suffixes():
    assert credible("https://www.reuters.com/a")
    assert credible("https://pib.gov.in/x")
    assert not credible("https://www.infowars.com/a")  # rated, but low
    assert not credible("https://notreuters.com/a")  # unrated
    assert not credible("https://viral-news.blogspot.com/x")  # blogspot.com's rating isn't this blog's


def test_a_message_with_nothing_to_check_never_reaches_claude(monkeypatch):
    monkeypatch.setattr(graph, "checkable", lambda text: False)
    monkeypatch.setattr(graph, "llm", lambda effort: pytest.fail("Claude was called"))
    forward = {"text": "Good morning! Have a blessed day", "image": None, "image_type": None, "received_at": ""}
    assert graph.extract({"forward": forward}) == {"claims": []}
    assert graph.reply({"results": []}) == {"reply": graph.NO_CLAIMS}


def test_jev_outage_falls_through_to_claude(monkeypatch):
    def down():
        raise ConnectionError("Jev unreachable")
    monkeypatch.setattr(evidence, "jev", down)
    assert evidence.checkable("Good morning!")
