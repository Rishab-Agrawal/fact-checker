"""The web app: the page and the API it streams checks from. Run: uvicorn fact_checker.app:app --reload"""

import json
import logging
import os
import threading
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from collections.abc import Iterator
from datetime import datetime, timezone
from functools import cache
from pathlib import Path
from queue import Queue
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, Field

from fact_checker.evidence import EMBED_DIMS, embeddings
from fact_checker.graph import builder

# Shown while each node runs.
STEPS = {
    "extract": "Reading the message",
    "recall": "Checking earlier verdicts",
    "archive": "Searching the fact-check archive",
    "web": "Searching the web",
    "judge": "Weighing the evidence",
    "advocate": "Hearing both sides",  # neutral: a running label must not read as the verdict
    "skeptic": "Hearing both sides",
    "reply": "Writing the reply",
}
# ponytail: in-memory, so limits reset on redeploy and assume one replica; move to Postgres if the app scales out
PER_IP_DAILY = 10
checks: defaultdict[str, list[float]] = defaultdict(list)
checks_lock = threading.Lock()


def allow(ip: str) -> bool:
    now = time.time()
    with checks_lock:
        checks[ip] = [t for t in checks[ip] if now - t < 86400]
        if len(checks[ip]) >= PER_IP_DAILY:
            return False
        checks[ip].append(now)
        return True


def notify_admin(ip: str, text: str, has_image: bool) -> None:
    """Tell the admin Telegram bot that someone ran a check."""
    if not (token := os.getenv("TELEGRAM_ADMIN_BOT_TOKEN")):
        return
    body = f"Check from {ip}" + (" (with screenshot)" if has_image else "") + f"\n\n{text}"
    data = urllib.parse.urlencode({"chat_id": os.environ["TELEGRAM_ADMIN_CHAT_ID"], "text": body[:4096]})
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", data.encode(), timeout=5)
    except OSError as e:  # a missed notice must not block the check
        logging.warning("Admin bot: %s", e)


@cache
def graph():
    pool = ConnectionPool(
        os.environ["DATABASE_URL"], open=True,
        kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
    )
    saver = PostgresSaver(pool)
    store = PostgresStore(pool, index={"embed": embeddings(), "dims": EMBED_DIMS, "fields": ["claim"]})
    saver.setup()
    store.setup()
    return builder.compile(checkpointer=saver, store=store)


class Check(BaseModel):
    text: str = Field("", max_length=4000)
    image: str | None = Field(None, max_length=7_000_000)  # base64 of a screenshot up to 5 MB
    image_type: Literal["image/png", "image/jpeg", "image/webp"] | None = None


def outcome(check_id: str) -> dict:
    """A finished check's result, from its last checkpoint, or a generic error."""
    state = graph().get_state({"configurable": {"thread_id": check_id}})
    if "reply" not in state.values:
        return {"error": "failed"}
    took = datetime.fromisoformat(state.created_at) - datetime.fromisoformat(state.values["message"]["received_at"])
    seconds = round(took.total_seconds())
    return {"reply": state.values["reply"], "results": state.values.get("results", []), "seconds": seconds}


# ponytail: in-memory like the limits, so a redeploy ends running checks and they read as failed
running: set[str] = set()


def run(check_id: str, message: dict, events: Queue) -> None:
    """Runs a check to the end and queues one event per step started, then the outcome, then None."""
    try:
        config = {"configurable": {"thread_id": check_id}}
        for _, task in graph().stream({"message": message}, config, stream_mode="tasks", subgraphs=True):
            if "input" in task and task["name"] in STEPS:
                events.put({"step": STEPS[task["name"]]})
        events.put(outcome(check_id))
    except Exception:
        logging.exception("Check failed")
        events.put({"error": "failed"})
    finally:
        running.discard(check_id)
        events.put(None)


def stream(message: dict) -> Iterator[str]:
    """The check's id, then its events as JSON lines. It runs on its own thread, so it ends even if the page leaves."""
    check_id, events = uuid4().hex, Queue()
    running.add(check_id)
    threading.Thread(target=run, args=(check_id, message, events), daemon=True).start()
    yield json.dumps({"id": check_id}) + "\n"
    while event := events.get():
        yield json.dumps(event) + "\n"


app = FastAPI(docs_url=None, redoc_url=None)


@app.post("/api/checks")
def check(body: Check, request: Request) -> StreamingResponse:
    if not (body.text.strip() or body.image) or bool(body.image) != bool(body.image_type):
        raise HTTPException(422)
    ip = request.headers.get("X-Real-IP") or request.client.host  # Railway's edge sets X-Real-IP
    if not allow(ip):
        raise HTTPException(429)
    notify_admin(ip, body.text, bool(body.image))
    message = body.model_dump() | {"received_at": datetime.now(timezone.utc).isoformat()}
    return StreamingResponse(stream(message), media_type="application/x-ndjson")


@app.get("/api/checks/{check_id}")
def result(check_id: str) -> dict:
    """Where the page finds a check whose stream broke: a reload, a closed tab, a phone asleep."""
    return {"pending": True} if check_id in running else outcome(check_id)


@app.middleware("http")
async def revalidate(request: Request, call_next):
    """Browsers check for a newer page and script on every load, so a deploy never pairs old JS with a new API."""
    response = await call_next(request)
    response.headers.setdefault("Cache-Control", "no-cache")
    return response


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True))
