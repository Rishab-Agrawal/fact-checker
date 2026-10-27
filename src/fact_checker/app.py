"""Paste a forwarded message, get verdicts. Run: streamlit run src/fact_checker/app.py"""

import base64
import logging
import os
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from fact_checker.evidence import EMBED_DIMS, embeddings
from fact_checker.graph import builder

STEPS = {
    "extract": "Read the message",
    "recall": "Checked earlier verdicts",
    "archive": "Searched the fact-check archive",
    "web": "Searched the web",
    "judge": "Weighed the evidence",
    "advocate": "Argued it is true",
    "skeptic": "Argued it is false",
    "reply": "Wrote the reply",
}
VERDICTS = {"true": "✅ True", "false": "❌ False", "misleading": "⚠️ Misleading", "unverifiable": "❔ Unverified"}
# ponytail: in-memory, so limits reset on redeploy and assume one replica; move to Postgres if the app scales out
PER_IP_HOURLY, DAILY = 5, 50


@st.cache_resource
def checks() -> defaultdict[str, list[float]]:
    return defaultdict(list)


def allow(ip: str) -> bool:
    now, seen = time.time(), checks()
    seen[ip] = [t for t in seen[ip] if now - t < 3600]
    seen["all"] = [t for t in seen["all"] if now - t < 86400]
    if len(seen[ip]) >= PER_IP_HOURLY or len(seen["all"]) >= DAILY:
        return False
    seen[ip].append(now)
    seen["all"].append(now)
    return True


def notify_admin(ip: str, text: str, image) -> None:
    """Tell the admin Telegram bot that someone ran a check."""
    if not (token := os.getenv("TELEGRAM_ADMIN_BOT_TOKEN")):
        return
    body = f"Check from {ip}" + (" (with screenshot)" if image else "") + f"\n\n{text}"
    data = urllib.parse.urlencode({"chat_id": os.environ["TELEGRAM_ADMIN_CHAT_ID"], "text": body[:4096]})
    try:
        urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", data.encode(), timeout=5)
    except OSError as e:  # a missed notice must not block the check
        logging.warning("Admin bot: %s", e)


@st.cache_resource
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


def run(payload, config) -> None:
    with st.status("Checking…", expanded=True) as status:
        for _, update in graph().stream(payload, config, stream_mode="updates", subgraphs=True):
            for node in update:
                if node in STEPS:
                    status.write(STEPS[node])
        status.update(label="Done", state="complete", expanded=False)


st.title("Is this forward true?")
text = st.text_area("Forwarded message", height=160, max_chars=4000)
image = st.file_uploader("Or a screenshot", type=["png", "jpg", "jpeg", "webp"])

if st.button("Check", type="primary", disabled=not (text.strip() or image)):
    ip = st.context.headers.get("X-Real-IP") or st.context.ip_address  # Railway's edge sets X-Real-IP
    if allow(ip):
        notify_admin(ip, text, image)
        st.session_state.thread = uuid4().hex
        forward = {
            "text": text,
            "image": base64.b64encode(image.getvalue()).decode() if image else None,
            "image_type": image.type if image else None,
            "received_at": datetime.now(timezone.utc).isoformat(),
        }
        run({"forward": forward}, {"configurable": {"thread_id": st.session_state.thread}})
    else:
        st.warning("Limit reached for now. Please try again later.")

if "thread" in st.session_state:
    snapshot = graph().get_state({"configurable": {"thread_id": st.session_state.thread}})
    if reply := snapshot.values.get("reply"):
        st.success(reply)
        for r in snapshot.values.get("results", []):
            with st.expander(f"{VERDICTS[r['verdict']]} · {r['claim']}"):
                st.write(r["rationale"])
                for s in r["sources"]:
                    st.markdown(f"- [{s['title']}]({s['url']})")
                st.caption(f"Confidence {r['confidence']:.0%}" + (" · from an earlier check" if r["from_memory"] else ""))
