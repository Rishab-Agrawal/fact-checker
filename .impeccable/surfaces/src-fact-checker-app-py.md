---
version: 1
slug: "src-fact-checker-app-py"
primary_target: "src/fact_checker/app.py"
related_targets: []
---

# Check page

Scope: the whole Streamlit page (`src/fact_checker/app.py`). Mode: Operate.
Audience and job: see PRODUCT.md. The task is one action: give a forward, read the verdicts.
Constraints: Streamlit theme config and public elements; CSS only through documented hooks (`st-key-*` classes).

## Direction contract

THESIS: A fact-checker that behaves like the chat assistants people already use. It refuses the form-and-button tool page: no labels, no instructions block, no repeated copy.

OWN-WORLD: claude.ai, pinned by the user and executed straight. Warm off-white ground (#faf9f5), white input field, near-black warm text, terracotta (#c96442) as the single accent. Literata serif for all text. Verdicts are coloured badges with drawn icons. Rounded 0.75rem corners, pill buttons.

STORY: The visitor sees one question and one input, pastes or taps an example, watches the check progress, and reads a plain-language reply with a verdict per claim and its sources.

FIRST VIEWPORT: Empty page. The greeting "What should we check?", with a terracotta check mark, sits centred at about 45% of the viewport height. The input sits directly under it, 704px wide on desktop, placeholder "Paste a message or screenshot". Three example pills sit centred below it. After a check starts, the input pins to the bottom and the conversation scrolls above it.

FORM: Pinned canon: claude.ai chat, named by the user. No concept-seed roll, since the direction was pinned. Code-led, because no image generation is available.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
