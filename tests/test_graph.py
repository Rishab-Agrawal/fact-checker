from types import SimpleNamespace

import pytest
from langgraph.store.memory import InMemoryStore

from fact_checker import evidence, graph
from fact_checker.evidence import credible
from fact_checker.graph import cite, fresh

EVIDENCE = [{"id": "F1", "title": "Alt News rated a claim \"False\"", "url": "https://altnews.in/x"}]


def jev_scores(*scores):
    answers = [SimpleNamespace(nouls={"confirms": SimpleNamespace(noul=s)}) for s in scores]
    return SimpleNamespace(batch=lambda inputs: answers)


def test_verdict_without_existing_citation_is_unverifiable():
    judgement = {"verdict": "false", "confidence": 0.9, "rationale": "r", "citations": ["W7"]}
    assert cite(judgement, EVIDENCE, "c")["verdict"] == "unverifiable"


def test_cited_verdict_keeps_sources():
    judgement = {"verdict": "false", "confidence": 0.9, "rationale": "r", "citations": ["F1"]}
    out = cite(judgement, EVIDENCE, "c")
    assert out["verdict"] == "false"
    assert out["sources"] == [{"title": EVIDENCE[0]["title"], "url": "https://altnews.in/x"}]


def test_a_page_cited_twice_is_one_source():
    judgement = {"verdict": "false", "confidence": 0.9, "rationale": "r", "citations": ["F1", "W1"]}
    out = cite(judgement, EVIDENCE + [{**EVIDENCE[0], "id": "W1"}], "c")
    assert len(out["sources"]) == 1


def test_a_confident_verdict_on_unvetted_sources_still_gets_the_debate():
    blog = {"id": "W1", "credible": False}
    judgement = {"verdict": "false", "confidence": 0.8, "citations": ["W1"]}
    state = {"evidence": [blog], "arguments": [], "judgement": judgement, "reference": False}
    assert graph.after_judge(state) == ["advocate", "skeptic"]
    assert graph.after_judge({**state, "reference": True}) == "finish"  # calendars and almanacs aren't rated
    blog["credible"] = True
    assert graph.after_judge(state) == "finish"


def test_a_reference_fact_two_sites_confirm_never_reaches_claude(monkeypatch):
    pages = [{"kind": "web", "url": f"https://{host}/x", "title": "t", "text": "t", "published": None, "credible": False}
             for host in ("a.com", "b.com")]
    monkeypatch.setattr(graph, "reference_fact", lambda claim: True)
    monkeypatch.setattr(graph, "search_archive", lambda *args: pytest.fail("archive searched"))
    monkeypatch.setattr(graph, "search_web", lambda *args: pages)
    monkeypatch.setattr(graph, "gate", lambda claim, found: found)
    monkeypatch.setattr(evidence, "jev", lambda: jev_scores(0.99, 0.99))
    monkeypatch.setattr(graph, "llm", lambda effort: pytest.fail("Claude was called"))
    out = graph.research_builder.compile(store=InMemoryStore()).invoke({"claim": "c", "as_of": "2026-11-08"})
    result = out["results"][0]
    assert result["verdict"] == "true"
    assert len(result["sources"]) == 2


def test_confirmation_takes_two_different_sites(monkeypatch):
    pages = [{"url": f"https://{host}/x", "title": "t", "text": "t"} for host in ("a.com", "www.a.com", "b.com")]
    monkeypatch.setattr(evidence, "jev", lambda: jev_scores(0.99, 0.99, 0.5))
    assert evidence.confirming("c", pages, "2026-11-08") == {}
    monkeypatch.setattr(evidence, "jev", lambda: jev_scores(0.99, 0.5, 0.99))
    assert set(evidence.confirming("c", pages, "2026-11-08")) == {"a.com", "b.com"}


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
    message = {"text": "Good morning! Have a blessed day", "image": None, "image_type": None, "received_at": ""}
    assert graph.extract({"message": message}) == {"claims": []}
    assert graph.reply({"results": []}) == {"reply": graph.NO_CLAIMS}


def test_jev_outage_falls_through_to_claude(monkeypatch):
    def down():
        raise ConnectionError("Jev unreachable")
    monkeypatch.setattr(evidence, "jev", down)
    assert evidence.checkable("Good morning!")
