---
version: 1
slug: "src-fact-checker-static-index-html"
primary_target: "src/fact_checker/static/index.html"
related_targets: ["src/fact_checker/static/style.css","src/fact_checker/static/app.js","src/fact_checker/app.py"]
---

# Check page

Scope: the check page (`src/fact_checker/static/`) and the API it streams from (`src/fact_checker/app.py`). Mode: Operate.
Audience and job: see PRODUCT.md. The task is one action: give a forward, read the verdicts, maybe copy the reply back into the chat it came from.
Constraints: plain HTML/CSS/JS, no build step; all text built with textContent (forwards and replies are untrusted).

## Direction contract

THESIS: A fact-checker with the calm flow of the assistants people already use, one check at a time. It refuses the form-and-button tool page: no labels, no instructions block, no repeated copy, no avatars.

OWN-WORLD: Graphite, chosen by the user over two other rendered minimal directions: claude.ai's flow, its own look. Near-white ground (#fcfcfc) and near-black ink (#18181b), inverted in a dark twin (#111113 / #ededef) that follows the device. White two-row composer with a hairline border and soft shadow. The forward quoted in a grey block at the top; unboxed results below it. No accent hue: ink is the accent (send button, mark, focus, selection), so the verdicts are the only colour on the page. Geist throughout, with Noto Sans Devanagari for Hindi. Verdict badges pair a colour, a drawn Lucide icon and a word.

STORY: The visitor sees one question and one input. They paste text or a screenshot, or tap an example. They watch the current step pulse ("Searching the web…"), then read a plain-text reply they can copy, with one expandable row per claim holding its rationale, sources and confidence.

FIRST VIEWPORT: Empty page. The greeting "What should we check?" sits centred a little above the middle, with the ink mark before it. The composer (44rem wide) is directly below it: the textarea on top, then a row with an attach button on the left and the send button on the right. Three example pills sit centred below. Each check replaces the page and reads top to bottom: the forward quoted (folded to four lines when long), the result, then a "New check" pill; Back starts over too. The signature move: the pill and the composer share one View Transition name, so the pill arrives through that transition when a check ends and grows back into the composer on "New check", making starting over feel like the same object returning.

FORM: Flow pinned to claude.ai; look chosen by the user from three rendered minimal directions after rejecting a rolled hand as not minimal enough (roll ad20c278). Code-led, because no image generation is available.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
