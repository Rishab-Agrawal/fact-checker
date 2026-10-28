---
name: Fact checker
description: Paste a forward, get a verdict per claim, in a claude.ai-style chat.
colors:
  terracotta: "#c96442"
  terracotta-ink: "#a8502f"
  ivory-ground: "#faf9f5"
  paper-white: "#ffffff"
  warm-ink: "#29261b"
  sand-rule: "#e3dfd3"
  stone-gray: "#5e5a4e"
  pebble-gray: "#e1e0db"
  verdict-green: "#25693a"
  verdict-red: "#a8322d"
  verdict-orange: "#9a4a0c"
typography:
  display:
    fontFamily: "Literata, serif"
    fontSize: "clamp(1.75rem, 7vw, 2.75rem)"
    fontWeight: 400
  body:
    fontFamily: "Literata, serif"
    fontSize: "1rem"
    fontWeight: 400
  label:
    fontFamily: "Literata, serif"
    fontSize: "0.875rem"
    fontWeight: 400
rounded:
  base: "0.75rem"
  full: "9999px"
components:
  chat-input:
    backgroundColor: "{colors.paper-white}"
    textColor: "{colors.warm-ink}"
    rounded: "{rounded.base}"
    width: "704px"
  example-pill:
    textColor: "{colors.warm-ink}"
    rounded: "{rounded.full}"
  example-pill-hover:
    textColor: "{colors.terracotta}"
  claim-expander:
    textColor: "{colors.warm-ink}"
    rounded: "{rounded.base}"
  badge-true:
    textColor: "{colors.verdict-green}"
    typography: "{typography.label}"
  badge-false:
    textColor: "{colors.verdict-red}"
    typography: "{typography.label}"
  badge-misleading:
    textColor: "{colors.verdict-orange}"
    typography: "{typography.label}"
  badge-unverified:
    backgroundColor: "{colors.pebble-gray}"
    textColor: "{colors.stone-gray}"
    typography: "{typography.label}"
---

# Design System: Fact checker

## Overview

**Creative North Star: "The Familiar Assistant"**

A fact-checker that looks and behaves like the chat assistant people already use: claude.ai, pinned by the user and executed straight. One question, one input, then a conversation. The world is warm paper rather than white screen: an ivory ground, warm near-black ink, one terracotta accent, and a single serif for everything.

All tokens live in the Streamlit theme (`.streamlit/config.toml`); components are Streamlit's public elements styled by that theme. The only custom CSS is the `.st-key-welcome` rule in `app.py`, which centres the empty-page greeting and sizes its heading. Streamlit hard-codes the user chat bubble (neutral gray) and the avatar frames; those are platform limits, not tokens.

**Key Characteristics:**
- Warm ivory ground, white input surfaces, hairline sand borders.
- One accent, terracotta, used sparingly.
- Literata serif for every role; headings at regular weight.
- Verdicts as tinted badges with drawn Material icons.
- Generous corners (0.75rem), pill-shaped buttons.

## Colors

Warm neutrals with one terracotta accent and three verdict colours that only ever mean a verdict.

### Primary
- **Terracotta**: the accent. The greeting's check-mark icon, Streamlit's focus and hover states. At 3.7:1 on the ground it is for glyphs and large marks only.
- **Terracotta Ink**: the deeper terracotta for link text (5.2:1), so source links stay legible.

### Neutral
- **Ivory Ground**: the page.
- **Paper White**: the chat input field.
- **Warm Ink**: all text (14.4:1 on the ground).
- **Sand Rule**: every widget border (theme `showWidgetBorder`).
- **Stone Gray**: muted text and the Unverified badge text.
- **Pebble Gray**: the Unverified badge fill.

### Verdict
- **Verdict Green / Red / Orange**: badge text for True, False, Misleading; Streamlit tints the badge fill from the same hue. All clear 5.9:1 on the ground.

### Named Rules
**The One Accent Rule.** Terracotta is the only non-verdict colour. No second accent.

**The Verdict Colour Rule.** Green, red and orange appear only in verdict badges, each paired with its icon and word so colour never carries the meaning alone.

## Typography

**Display Font:** Literata (with serif fallback), loaded from Google Fonts at weights 400, 500, 600.
**Body Font:** Literata.

**Character:** A bookish text serif in every role, regular-weight headings; it reads as a calm letter, not a dashboard.

### Hierarchy
- **Display** (400, clamp(1.75rem, 7vw, 2.75rem), balanced wrap): the empty-page greeting only.
- **Body** (400, 1rem): the reply, rationales, the forwarded message.
- **Label** (400, 0.875rem): verdict badges and the confidence line (`:small[]`).

### Named Rules
**The One Serif Rule.** Literata everywhere. Weight, not a second family, carries emphasis; headings stay at 400.

## Layout

Streamlit's centred layout: one column, 704px of content on desktop, full width on mobile. On an empty page the greeting, input and example pills sit centred in a container at least 70dvh tall. After the first check the input pins to the bottom and the conversation scrolls above it: user forward, then the assistant's status, reply and one expander per claim.

## Elevation & Depth

Flat. No shadows; surfaces separate by tone (white on ivory) and 1px sand borders.

## Shapes

Generous rounded corners (0.75rem) on inputs, expanders, the status box and chat bubbles; fully rounded pills for buttons. Icons are Material Symbols, drawn, never emoji or text glyphs.

## Components

### Buttons (example pills)
- **Shape:** full pill.
- **Style:** near-white fill (Streamlit lightens the ground), sand border, warm-ink text; the label is the example's short title.
- **Hover / Focus:** Streamlit default: terracotta border and text.

### Inputs / Fields (chat input)
- **Style:** white field, sand border, 0.75rem corners, 704px wide on desktop. A "+" opens the screenshot picker; the round send button sits right.
- **Focus:** Streamlit's terracotta focus border.

### Cards / Containers (status and claim expanders)
- **Corner Style:** 0.75rem.
- **Background:** transparent on ivory; sand border.
- **Content:** the header carries the verdict badge and the claim; the body holds rationale, linked sources, and the small confidence line.

### Verdict Badges (signature)
Tinted pill badges with a Material icon and one word: check/True (green), close/False (red), warning/Misleading (orange), help/Unverified (gray).

## Do's and Don'ts

### Do:
- **Do** set colour, font and radius through `.streamlit/config.toml`, not CSS.
- **Do** keep custom CSS to documented `st-key-*` hooks.
- **Do** pair every verdict colour with its icon and word.
- **Do** use Terracotta Ink, not Terracotta, for any text-sized accent.

### Don't:
- **Don't** add a second accent colour or a second typeface.
- **Don't** use green, red or orange outside verdicts.
- **Don't** add shadows; depth is tone and hairline borders.
- **Don't** add labels, instruction blocks, or copy that repeats the heading or placeholder.
