---
name: Fact checker
description: Paste a forward, get a verdict per claim, in a claude.ai-style chat.
colors:
  accent: "#c96442"
  link: "#a8502f"
  bg: "#faf9f5"
  surface: "#ffffff"
  bubble: "#f0eee6"
  text: "#29261b"
  muted: "#5e5a4e"
  placeholder: "#6f6b60"
  border: "#e3dfd3"
  border-strong: "#cfcabb"
  "true": "#25693a"
  "false": "#a8322d"
  misleading: "#9a4a0c"
  unverifiable: "#5e5a4e"
  accent-dark: "#d97757"
  link-dark: "#e8946f"
  bg-dark: "#262624"
  surface-dark: "#30302e"
  bubble-dark: "#141413"
  text-dark: "#ecebe4"
  muted-dark: "#a8a59b"
  placeholder-dark: "#9e9b91"
  border-dark: "#3e3e3a"
  border-strong-dark: "#55544e"
  true-dark: "#86cf96"
  false-dark: "#f2998e"
  misleading-dark: "#ecaa69"
  unverifiable-dark: "#bdbab0"
typography:
  display:
    fontFamily: "Literata, Noto Serif Devanagari, serif"
    fontSize: "clamp(1.75rem, 7vw, 2.5rem)"
    fontWeight: 400
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Literata, Noto Serif Devanagari, serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "Literata, Noto Serif Devanagari, serif"
    fontSize: "0.875rem"
    fontWeight: 400
  badge:
    fontFamily: "Literata, Noto Serif Devanagari, serif"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.6
rounded:
  sm: "0.5rem"
  md: "0.75rem"
  lg: "1.25rem"
  full: "999px"
spacing:
  column: "44rem"
  gutter: "1rem"
  stack: "0.5rem"
  message-gap: "2rem"
components:
  composer:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.lg}"
    padding: "0.875rem 0.75rem 0.625rem 1rem"
    width: "44rem"
  send-button:
    backgroundColor: "{colors.accent}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
    size: "2rem"
  attach-button:
    textColor: "{colors.muted}"
    rounded: "{rounded.sm}"
    size: "2rem"
  attach-button-hover:
    backgroundColor: "{colors.bubble}"
    textColor: "{colors.text}"
  example-pill:
    textColor: "{colors.muted}"
    typography: "{typography.label}"
    rounded: "{rounded.full}"
    padding: "0.375rem 0.875rem"
  example-pill-hover:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
  user-bubble:
    backgroundColor: "{colors.bubble}"
    textColor: "{colors.text}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: "0.625rem 1rem"
  claim-row:
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: "0.625rem 0.875rem"
  badge-true:
    textColor: "{colors.true}"
    typography: "{typography.badge}"
    rounded: "{rounded.sm}"
    padding: "0 0.5rem"
  badge-false:
    textColor: "{colors.false}"
    typography: "{typography.badge}"
    rounded: "{rounded.sm}"
    padding: "0 0.5rem"
  badge-misleading:
    textColor: "{colors.misleading}"
    typography: "{typography.badge}"
    rounded: "{rounded.sm}"
    padding: "0 0.5rem"
  badge-unverifiable:
    textColor: "{colors.unverifiable}"
    typography: "{typography.badge}"
    rounded: "{rounded.sm}"
    padding: "0 0.5rem"
  quiet-button:
    textColor: "{colors.muted}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "0.25rem 0.5rem"
  quiet-button-hover:
    backgroundColor: "{colors.bubble}"
    textColor: "{colors.text}"
---

# Design System: Fact checker

## Overview

**Creative North Star: "The Familiar Assistant"**

A fact-checker that looks and behaves like the chat assistant people already use: claude.ai, pinned by the user and executed straight. One question, one input, then a conversation. The world is warm paper rather than white screen: an ivory ground, warm near-black ink, one terracotta accent and one serif voice. A dark twin on warm charcoal follows the device setting; there is no theme toggle.

Plain HTML, CSS and JS with no build step. Every token is a custom property on `:root` in `style.css`, and a single `prefers-color-scheme: dark` block reassigns the same names. Components read those properties (the send arrow's white is the one literal), so both themes come from one rule set.

**Key Characteristics:**
- Warm ivory ground (charcoal in dark), a white composer card, sand user bubbles, unboxed replies.
- One accent, terracotta, for the mark, the send button, focus and selection.
- Literata in every role, Noto Serif Devanagari for Hindi; one small size.
- Verdicts as tinted badges pairing a colour, a drawn icon and a word.
- Lucide-drawn line icons only; soft corners (0.5 / 0.75 / 1.25rem) and full pills.

## Colors

Warm neutrals with one terracotta accent and four verdict colours that only ever mean a verdict. Each light token has a dark twin of the same name (`-dark` in the frontmatter); the stylesheet swaps them under `prefers-color-scheme: dark`.

### Primary
- **Terracotta** (accent): the mark, the send button fill, the focus outline, the caret, the drag-over border and text selection (28% mix). At 3.7:1 on the ivory ground it is for glyphs, fills and outlines, never text.
- **Terracotta Ink** (link): source and reply links (5.2:1 light, 6.4:1 dark).

### Neutral
- **Ivory Ground / Charcoal Ground** (bg): the page and the `theme-color`.
- **Paper White / Graphite Surface** (surface): the composer card and hovered example pills.
- **Sand Bubble** (bubble): the user's message, and the hover fill of quiet buttons. In dark it sits below the ground (#141413), so the bubble reads as a well, not a raised card.
- **Warm Ink** (text): all body text (14.4:1 light, 12.7:1 dark).
- **Stone Gray** (muted): secondary text, the progress line, source domains, idle icon buttons (6.5:1).
- **Placeholder**: the composer placeholder only (5.3:1 on the surface).
- **Sand Rule** (border): every hairline. **Strong Rule** (border-strong): hovered pills and the scrollbar thumb.

### Verdict
- **True / False / Misleading / Unverifiable**: badge text, with a 14% tint of the same colour over the ground as the fill. All clear 5.9:1 on their ground in both themes. Unverifiable shares Stone Gray in light. False also colours the composer's inline error line.

### Named Rules
**The One Accent Rule.** Terracotta is the only non-verdict hue. No second accent; hovers deepen the accent by mixing it toward the text colour (75%) rather than introducing a new one.

**The Verdict Colour Rule.** Green, red, orange and the verdict gray appear only in verdict badges (and red in error text), each paired with its icon and word so colour never carries the meaning alone.

**The Twin Rule.** A new colour is a new custom property with a value in both the light `:root` and the dark override. Never hard-code a colour in a component; the only literal is the send arrow's white, which sits on terracotta in both themes.

## Typography

**Body Font:** Literata (variable, opsz 7..72, weights 400 to 600, Google Fonts), falling back to Noto Serif Devanagari, then serif.
**Display Font:** Literata.
**Devanagari:** Noto Serif Devanagari (400 to 600), reached through the same stack for Hindi text.

**Character:** A bookish text serif in every role at regular weight; it reads as a calm letter, not a dashboard. The Devanagari serif matches its stroke so Hindi forwards sit in the same voice.

### Hierarchy
- **Display** (400, clamp(1.75rem, 7vw, 2.5rem), 1.2, -0.01em, balanced wrap): the empty-page greeting only.
- **Body** (400, 1rem, 1.65): replies, rationales, user messages, the composer.
- **Label** (400, 0.875rem): every secondary line: progress, example pills, copy and retry, domains, confidence, the footer note, the error line.
- **Badge** (500, 0.875rem, 1.6): verdict badges; the only place weight changes.

### Named Rules
**The One Small Size Rule.** There are two text sizes in conversation: 1rem and `--small` (0.875rem). Nothing else.

**The One Serif Rule.** Literata everywhere, with Noto Serif Devanagari only as its Hindi partner. No sans, no mono, no second display face.

## Layout

One centred column, 44rem of content plus 1rem gutters, shared by `main` and `footer`. On the empty page the body centres vertically with 12dvh of bottom padding, so the greeting, composer and three example pills sit together a little above the middle. After the first check the composer becomes a sticky footer that fades the ground in above it (a 1.5rem gradient) and the conversation grows above: messages 2rem apart, user messages right-aligned at up to min(85%, 36rem), assistant content left and unboxed. Claims stack 0.5rem apart at full width. The footer respects the bottom safe-area inset. On coarse pointers the composer's icon buttons grow from 2rem to 2.5rem.

## Elevation & Depth

Nearly flat. Surfaces separate by tone and 1px hairlines; the one shadow is the composer's soft ambient lift, so the input reads as the object on the page.

### Shadow Vocabulary
- **Composer lift** (`box-shadow: 0 0.25rem 1.25rem rgb(41 38 27 / 0.05)`; dark `rgb(0 0 0 / 0.25)`): the composer only.

### Named Rules
**The One Lift Rule.** Only the composer casts a shadow. Everything else is tone and hairline.

## Shapes

Three soft radii and a pill: 0.5rem for small controls and badges, 0.75rem for claim rows and image thumbnails, 1.25rem for the composer and user bubbles, full pills for example chips (and a circle for the attachment's remove button). Borders are 1px hairlines. Icons are Lucide line icons drawn inline (24 viewBox, 2px round stroke, `currentColor`), including the mark (Lucide's message-circle-check in terracotta). Never emoji or text glyphs.

## Components

### Composer (signature)
- **Character:** the one object on the page; a white two-row card.
- **Shape:** 1.25rem corners, 1px rule, the composer lift.
- **Content:** the auto-growing textarea (to 40dvh) on top; an actions row below with attach on the left and send on the right. An attached screenshot shows as a 4rem thumbnail with a small ink-filled remove circle.
- **Focus:** the border warms to a 55% terracotta mix; the textarea has no outline of its own. Drag-over sets the border to full terracotta.
- **Motion:** on the first send the composer glides from the centre to the bottom with a View Transition (0.45s, `cubic-bezier(0.16, 1, 0.3, 1)`). Reduced motion removes it along with every other animation and transition.

### Buttons
- **Send:** terracotta square (0.5rem corners, 2rem) with a white up-arrow; disabled at 40% opacity; hover mixes the accent 75% toward the text colour; press scales to 0.94.
- **Attach:** the same square, transparent with a rule border and a muted plus; hover fills Sand Bubble and turns the icon to ink.
- **Quiet (copy, try again):** muted label text with an optional icon, 0.5rem corners; hover fills Sand Bubble. Try again carries a rule border, copy does not.

### Chips (example pills)
- **Style:** transparent, rule border, full pill, muted label text.
- **Hover:** strong-rule border, surface fill, ink text. Shown only on the empty page.

### Messages
- **User bubble:** Sand Bubble, 1.25rem corners, right-aligned; attached images sit above it with a rule border and 0.75rem corners.
- **Reply:** unboxed body text with linkified URLs, followed by a copy button.
- **Progress:** a disclosure line in muted label text with a chevron; while running, the current step pulses between muted and ink (1.6s), keeping full contrast at both ends.

### Cards / Containers (claim rows)
- **Corner Style:** 0.75rem.
- **Background:** none; 1px rule border.
- **Header:** verdict badge, the claim, and a muted chevron that rotates 180° on open (0.2s).
- **Body:** separated by a rule; the rationale, a disc list of source links each with its muted domain, then the confidence line.

### Verdict Badges
Tinted 0.5rem-cornered badges: drawn icon plus one word in the verdict colour. Check/True, x/False, warning triangle/Misleading, circled question/Unverifiable.

## Do's and Don'ts

### Do:
- **Do** set colour, size, radius and easing through the `:root` custom properties, with a dark value for every colour.
- **Do** pair every verdict colour with its icon and word.
- **Do** use Terracotta Ink, not Terracotta, for any text-sized accent.
- **Do** draw new icons from Lucide, inline, stroked in `currentColor`.
- **Do** keep every animation inside the reduced-motion reset.

### Don't:
- **Don't** add a second accent colour or a second typeface.
- **Don't** use the verdict colours outside verdicts and error text.
- **Don't** add a text size beyond the display, 1rem and 0.875rem.
- **Don't** give anything but the composer a shadow.
- **Don't** add labels, instruction blocks, avatars, or copy that repeats the heading or placeholder.
