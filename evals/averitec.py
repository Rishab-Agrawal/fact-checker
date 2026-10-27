"""Score the research subgraph on AVeriTeC dev claims (real-world claims with gold verdicts).

Evidence is capped at each claim's date, so the agent can't find the fact-check the dataset was built from.
Usage: python evals/averitec.py [n]   (default 40)
Each run is saved to the eval_runs table, with the deployed commit.
"""

import json
import os
import random
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime

import psycopg
from langchain_core.callbacks import get_usage_metadata_callback
from langgraph.store.memory import InMemoryStore
from psycopg.types.json import Jsonb

from fact_checker import graph as fc
from fact_checker.evidence import EMBED_DIMS, embeddings

DATA = "https://raw.githubusercontent.com/MichSchli/AVeriTeC/main/data/dev.json"
LABELS = {
    "Supported": "true",
    "Refuted": "false",
    "Conflicting Evidence/Cherrypicking": "misleading",
    "Not Enough Evidence": "unverifiable",
}


def macro_f1(gold: list[str], pred: list[str]) -> float:
    scores = []
    for label in LABELS.values():
        tp = sum(g == p == label for g, p in zip(gold, pred))
        wrong = sum((g == label) != (p == label) for g, p in zip(gold, pred))
        scores.append(2 * tp / (2 * tp + wrong) if tp else 0.0)
    return sum(scores) / len(scores)


def main(n: int = 40) -> None:
    sample = random.Random(0).sample(json.load(urllib.request.urlopen(DATA)), n)
    # A fresh memory per run: verdicts from earlier runs would leak answers.
    research = fc.research_builder.compile(
        store=InMemoryStore(index={"embed": embeddings(), "dims": EMBED_DIMS, "fields": ["claim"]})
    )
    inputs = [
        {"claim": c["claim"], "as_of": datetime.strptime(c["claim_date"], "%d-%m-%Y").date().isoformat()}
        for c in sample
    ]
    start = time.time()
    with get_usage_metadata_callback() as usage:
        outputs = research.batch(inputs, {"max_concurrency": 4}, return_exceptions=True)
    rows = [
        {"claim": c["claim"], "as_of": i["as_of"], "gold": LABELS[c["label"]]}
        | ({"error": repr(o)} if isinstance(o, Exception) else
           {k: o["results"][0][k] for k in ("verdict", "confidence", "rationale", "sources", "from_memory")})
        for c, i, o in zip(sample, inputs, outputs)
    ]
    gold, pred = [r["gold"] for r in rows], [r.get("verdict", "error") for r in rows]
    metrics = {
        "n": n,
        "accuracy": sum(g == p for g, p in zip(gold, pred)) / n,
        "macro_f1": macro_f1(gold, pred),
        "errors": pred.count("error"),
        "confusion (gold -> predicted)": {f"{g} -> {p}": k for (g, p), k in sorted(Counter(zip(gold, pred)).items())},
        "seconds": round(time.time() - start),
        "tokens": {model: u["total_tokens"] for model, u in usage.usage_metadata.items()},
    }
    config = {"model": fc.MODEL, "debate_below": fc.DEBATE_BELOW}
    with psycopg.connect(os.environ["DATABASE_URL"]) as db:
        db.execute("CREATE TABLE IF NOT EXISTS eval_runs "
                   "(at timestamptz DEFAULT now(), commit text, metrics jsonb, config jsonb, rows jsonb)")
        db.execute("INSERT INTO eval_runs (commit, metrics, config, rows) VALUES (%s, %s, %s, %s)",
                   (os.getenv("RAILWAY_GIT_COMMIT_SHA"), Jsonb(metrics), Jsonb(config), Jsonb(rows)))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main(*map(int, sys.argv[1:]))
