# fact-checker

Paste a forwarded message (text or screenshot). It extracts the checkable claims, researches each in parallel, and
replies in the sender's language with a verdict per claim (true / false / misleading / unverifiable) and sources.

## How it works

`src/fact_checker/graph.py` (LangGraph): `extract → research (one per claim, via Send) → reply`. Research, per claim:

```mermaid
graph TD
  recall -->|seen before| done([done])
  recall --> archive
  archive -->|usable| judge
  archive -->|nothing usable| web --> judge
  judge -->|unsure| advocate & skeptic --> judge
  judge --> finish --> done
```

- **recall** (memory): earlier verdicts; Jev confirms it is the same claim before one is reused.
- **archive** (RAG): ~88k professional fact-checks from Google's ClaimReview feed, in pgvector.
- **web** (corrective RAG): Tavily search.
- **advocate / skeptic** (multi-agent): two tool-using agents argue opposite sides, then the judge decides again, once.
- **finish**: a verdict citing no real evidence becomes unverifiable; confident ones (≥ 0.8) are remembered for 30 days.

## Design decisions

- **Jev only where it loses no quality**: passage relevance, prompt-injection and same-claim checks. Extraction,
  judging, debate and the reply stay with Claude: they generate text or reason across sources and dates, which are
  Jev's [documented weak spots](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md).
- **Evidence is capped at the claim's date**, so evals can't find the fact-check a benchmark claim came from.
- **The citation guard is code, not an LLM grader**: free, and it can't hallucinate.
- **One Postgres** holds the archive, graph checkpoints and memory.

## Run

Deployed on Railway from this repo (`railway.json`) with Railway Postgres. Locally: copy `.env.example` to `.env`, then

1. `uv run python -m fact_checker.ingest` loads the archive (estimate: 10 to 20 minutes, ~$0.05; re-run to add new ones)
2. `uv run streamlit run src/fact_checker/app.py`
3. `uv run pytest`

## Evals

`uv run python evals/averitec.py 40` runs research on 40 [AVeriTeC](https://github.com/MichSchli/AVeriTeC) claims and
writes accuracy, macro-F1, a confusion table and token usage to `evals/results/`. Commit results with the change they
measure.
