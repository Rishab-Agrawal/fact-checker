---
version: 1
slug: "src-fact-checker-static-index-html"
primary_target: "src/fact_checker/static/index.html"
related_targets: ["src/fact_checker/static/style.css","src/fact_checker/static/app.js","src/fact_checker/app.py"]
---

# Check page

Scope: the chat page (`src/fact_checker/static/`) and the API it streams from (`src/fact_checker/app.py`). Mode: Operate.
Audience and job: see PRODUCT.md. The task is one action: give a forward, read the verdicts, maybe copy the reply back into the chat it came from.
Constraints: plain HTML/CSS/JS, no build step; all text built with textContent (forwards and replies are untrusted).

## Direction contract

THESIS: A fact-checker that behaves like the chat assistants people already use. It refuses the form-and-button tool page: no labels, no instructions block, no repeated copy, no avatars.

OWN-WORLD: claude.ai, pinned by the user and executed straight. Warm ivory ground (#faf9f5), with a dark twin (#262624) that follows the device. White two-row composer with a soft shadow. Warm sand user bubbles on the right; unboxed replies on the left. Terracotta (#c96442) is the single accent, used for the mark (Lucide's message-circle-check, matching the Lucide-drawn icon set), the send button, focus and selection. Literata serif throughout, with Noto Serif Devanagari for Hindi. Verdict badges pair a colour, a drawn icon and a word.

STORY: The visitor sees one question and one input. They paste text or a screenshot, or tap an example. They watch the current step pulse ("Searching the web…"), then read a plain-text reply they can copy, with one expandable row per claim holding its rationale, sources and confidence.

FIRST VIEWPORT: Empty page. The greeting "What should we check?" sits centred a little above the middle, with the terracotta mark before it. The composer (44rem wide) is directly below it: the textarea on top, then a row with an attach button on the left and the send button on the right. Three example pills sit centred below. The signature move is that, on the first send, the composer glides to the bottom (a View Transition) and the conversation grows above it.

FORM: Pinned canon: claude.ai chat, named by the user. No concept-seed roll, since the direction was pinned. Code-led, because no image generation is available.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
