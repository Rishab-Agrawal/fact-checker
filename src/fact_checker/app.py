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
VERDICTS = {
    "true": ":green-badge[:material/check: True]",
    "false": ":red-badge[:material/close: False]",
    "misleading": ":orange-badge[:material/warning: Misleading]",
    "unverifiable": ":gray-badge[:material/help: Unverified]",
}
AVATAR = ":material/fact_check:"
USER_AVATAR = ":material/person:"
EXAMPLES = {
    "UNESCO's best national anthem": "Proud moment for every Indian! UNESCO has declared Jana Gana Mana the best national "
                                     "anthem in the world. Share with everyone!",
    "Hot water kills the virus": "Japanese doctors advise: drinking hot water every 15 minutes washes the coronavirus "
                                 "into the stomach, where acid kills it. Forward to everyone you love.",
    "दिसंबर में 6 दिन अंधेरा": "नासा ने पुष्टि की है कि दिसंबर में पृथ्वी पर 6 दिन तक पूरा अंधेरा रहेगा। सभी को बताएं।",
}
# ponytail: in-memory, so limits reset on redeploy and assume one replica; move to Postgres if the app scales out
PER_IP_DAILY = 10


@st.cache_resource
def checks() -> defaultdict[str, list[float]]:
    return defaultdict(list)


def allow(ip: str) -> bool:
    now, seen = time.time(), checks()
    seen[ip] = [t for t in seen[ip] if now - t < 86400]
    if len(seen[ip]) >= PER_IP_DAILY:
        return False
    seen[ip].append(now)
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


def config(thread: str) -> dict:
    return {"configurable": {"thread_id": thread}}


def run(payload, thread: str) -> None:
    with st.status("Checking…") as status:
        for _, update in graph().stream(payload, config(thread), stream_mode="updates", subgraphs=True):
            for node in update:
                if node in STEPS:
                    status.update(label=STEPS[node])
                    status.write(STEPS[node])
        status.update(label="Checked", state="complete")


def show_forward(forward) -> None:
    if forward["image"]:
        st.image(base64.b64decode(forward["image"]), width=320)
    if forward["text"]:
        st.text(forward["text"])


def show_answer(values) -> None:
    st.markdown(values["reply"])
    for r in values.get("results", []):
        with st.expander(f"{VERDICTS[r['verdict']]} {r['claim']}"):
            st.write(r["rationale"])
            st.markdown("\n".join(f"- [{s['title']}]({s['url']})" for s in r["sources"]))
            st.markdown(f":small[Confidence {r['confidence']:.0%}" + (" · from an earlier check" if r["from_memory"] else "") + "]")


def check(text: str, image) -> None:
    forward = {
        "text": text,
        "image": base64.b64encode(image.getvalue()).decode() if image else None,
        "image_type": image.type if image else None,
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
    with st.chat_message("user", avatar=USER_AVATAR):
        show_forward(forward)
    with st.chat_message("assistant", avatar=AVATAR):
        ip = st.context.headers.get("X-Real-IP") or st.context.ip_address  # Railway's edge sets X-Real-IP
        if allow(ip):
            notify_admin(ip, text, image)
            thread = uuid4().hex
            run({"forward": forward}, thread)
            show_answer(graph().get_state(config(thread)).values)
            st.session_state.threads.append(thread)
        else:
            st.markdown(f"You've reached today's limit of {PER_IP_DAILY} checks. Please try again tomorrow.")


def submitted(example: str | None = None) -> None:
    st.session_state.submitted = True
    st.session_state.example = example


st.set_page_config(page_title="Fact checker", page_icon=AVATAR)
threads = st.session_state.setdefault("threads", [])
chat_input = {
    "placeholder": "Paste a message or screenshot", "key": "prompt", "max_chars": 4000,
    "accept_file": True, "file_type": ["png", "jpg", "jpeg", "webp"], "on_submit": submitted,
}

# Until the first check, the greeting and input sit centred; after it, the input pins to the bottom.
if not (st.session_state.pop("submitted", False) or threads):
    with st.container(key="welcome", horizontal_alignment="center", vertical_alignment="center", gap="medium"):
        st.html("<style>.st-key-welcome { min-height: 70dvh } "
                ".st-key-welcome h1 { font-size: clamp(1.75rem, 7vw, 2.75rem); text-wrap: balance }</style>")
        st.title(f":primary[{AVATAR}] What should we check?", anchor=False, text_alignment="center")
        st.chat_input(**chat_input)
        with st.container(horizontal=True, horizontal_alignment="center"):
            for label in EXAMPLES:
                st.button(label, on_click=submitted, args=(label,))
    st.stop()

for thread in threads:
    values = graph().get_state(config(thread)).values
    with st.chat_message("user", avatar=USER_AVATAR):
        show_forward(values["forward"])
    with st.chat_message("assistant", avatar=AVATAR):
        show_answer(values)

if prompt := st.chat_input(**chat_input):
    check(prompt.text, prompt.files[0] if prompt.files else None)
elif example := st.session_state.pop("example", None):
    check(EXAMPLES[example], None)
