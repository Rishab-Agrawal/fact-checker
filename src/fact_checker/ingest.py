"""Load Google's ClaimReview feed (fact-checks from publishers worldwide) into the archive.

Re-running only embeds fact-checks that aren't in the archive yet, so it is safe to run daily.
Usage: python -m fact_checker.ingest [feed-url-or-path]
"""

import json
import sys
import urllib.request
import uuid
from datetime import date

from langchain_core.documents import Document
from langchain_postgres import Column
from langchain_postgres.v2.indexes import HNSWIndex
from sqlalchemy.exc import ProgrammingError

from fact_checker.evidence import ARCHIVE_TABLE, EMBED_DIMS, archive, engine

FEED = "https://storage.googleapis.com/datacommons-feeds/claimreview/latest/data.json"
BATCH = 1000


def parse(feed: dict) -> dict[str, Document]:
    docs = {}
    for element in feed["dataFeedElement"]:
        for review in element.get("item") or []:
            claim = (review.get("claimReviewed") or "").strip()
            rating = (review.get("reviewRating") or {}).get("alternateName")
            try:
                reviewed_at = date.fromisoformat(review["datePublished"][:10])
            except (KeyError, TypeError, ValueError):
                continue  # undated fact-checks can't be placed before or after a claim
            if not (claim and rating and review.get("url")):
                continue
            doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, review["url"] + claim))
            docs[doc_id] = Document(
                id=doc_id,
                page_content=claim,
                metadata={
                    "reviewed_at": reviewed_at,
                    "url": review["url"],
                    "publisher": (review.get("author") or {}).get("name") or "unknown",
                    "rating": rating.strip(),
                    "explanation": ((review.get("reviewRating") or {}).get("ratingExplanation") or "").strip(),
                },
            )
    return docs


def main(source: str = FEED) -> None:
    # ponytail: loads the whole feed (~200 MB) into memory, stream it with ijson if that becomes a problem
    with urllib.request.urlopen(source) if source.startswith("http") else open(source, "rb") as f:
        docs = parse(json.load(f))
    try:
        engine().init_vectorstore_table(ARCHIVE_TABLE, EMBED_DIMS, metadata_columns=[Column("reviewed_at", "DATE")])
    except ProgrammingError:
        pass  # already created
    store = archive()
    ids = list(docs)
    added = 0
    for i in range(0, len(ids), BATCH):
        batch = ids[i : i + BATCH]
        have = {d.id for d in store.get_by_ids(batch)}
        new = [docs[d] for d in batch if d not in have]
        if new:
            store.add_documents(new, ids=[d.id for d in new])
            added += len(new)
        print(f"\r{i + len(batch)}/{len(ids)} checked, {added} added", end="", flush=True)
    print()
    if not store.is_valid_index():
        store.apply_vector_index(HNSWIndex())


if __name__ == "__main__":
    main(*sys.argv[1:])
