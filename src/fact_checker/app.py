"""Paste a forwarded message, get verdicts. Run: streamlit run src/fact_checker/app.py"""

import base64
from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from fact_checker.evidence import DB_URL, EMBED_DIMS, embeddings
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


@st.cache_resource
def graph():
    pool = ConnectionPool(DB_URL, open=True, kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row})
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
text = st.text_area("Forwarded message", height=160)
image = st.file_uploader("Or a screenshot", type=["png", "jpg", "jpeg", "webp"])

if st.button("Check", type="primary", disabled=not (text.strip() or image)):
    st.session_state.thread = uuid4().hex
    forward = {
        "text": text,
        "image": base64.b64encode(image.getvalue()).decode() if image else None,
        "image_type": image.type if image else None,
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
    run({"forward": forward}, {"configurable": {"thread_id": st.session_state.thread}})

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
