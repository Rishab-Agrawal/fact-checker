---
name: Fact checker
description: Paste a forward, get a verdict per claim, one check at a time.
colors:
  accent: "#18181b"
  link: "#18181b"
  bg: "#fcfcfc"
  surface: "#ffffff"
  bubble: "#f0f0f1"
  text: "#18181b"
  muted: "#63636b"
  placeholder: "#71717a"
  border: "#e6e6e9"
  border-strong: "#d2d2d7"
  "true": "#166534"
  "false": "#b91c1c"
  misleading: "#8a4b05"
  unverifiable: "#52525b"
  accent-dark: "#ededef"
  link-dark: "#ededef"
  bg-dark: "#111113"
  surface-dark: "#1c1c1f"
  bubble-dark: "#27272a"
  text-dark: "#ededef"
  muted-dark: "#a1a1aa"
  placeholder-dark: "#8e8e96"
  border-dark: "#2a2a2e"
  border-strong-dark: "#3f3f46"
  true-dark: "#7dcf9a"
  false-dark: "#f0a19b"
  misleading-dark: "#e9ac74"
  unverifiable-dark: "#b4b4bc"
typography:
  display:
    fontFamily: "Geist, Noto Sans Devanagari, sans-serif"
    fontSize: "clamp(1.75rem, 7vw, 2.5rem)"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Geist, Noto Sans Devanagari, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Geist, Noto Sans Devanagari, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
  badge:
    fontFamily: "Geist, Noto Sans Devanagari, sans-serif"
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
    textColor: "{colors.bg}"
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
  forward-quote:
    backgroundColor: "{colors.bubble}"
    textColor: "{colors.text}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: "0.75rem 1rem"
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

**Creative North Star: "Graphite"**

A fact-checker with the calm flow of the assistants people already use: claude.ai's flow, with its own look. One question, one input, then one result; each check stands alone, so it is not a chat. The world is graphite on near-white: a near-white ground, near-black ink, a white composer card and a grey quoted forward, with no accent hue at all. Ink is the accent, so the four verdict colours are the only colour on the page. A dark twin on near-black follows the device setting; there is no theme toggle.

Plain HTML, CSS and JS with no build step. Every token is a custom property on `:root` in `style.css`, and a single `prefers-color-scheme: dark` block reassigns the same names, so both themes come from one rule set. The favicon is an inline SVG data URI in `index.html` (so it changes with the page) and carries its own dark variant.

**Key Characteristics:**
- Near-white ground (near-black in dark), a white composer card, the forward quoted in a grey block, unboxed results.
- No hue but the verdicts: ink fills the send button and draws the mark, focus ring, caret and selection.
- Geist in every role, Noto Sans Devanagari for Hindi; one small size.
- Verdicts as tinted badges pairing a colour, a drawn icon and a word.
- Lucide-drawn line icons only; soft corners (0.5 / 0.75 / 1.25rem) and full pills.

## Colors

Cool greys from near-white to near-black, and four verdict colours that only ever mean a verdict. Each light token has a dark twin of the same name (`-dark` in the frontmatter); the stylesheet swaps them under `prefers-color-scheme: dark`.

### Primary
- **Ink** (accent, link): the same value as the text colour. The mark, the send button fill, the focus outline, the caret, the drag-over border, text selection (28% mix) and links (underlined at 35% of their colour, so they read as links without a hue).

### Neutral
- **Near-white Ground / Near-black Ground** (bg): the page and the `theme-color`; also the send arrow and the remove-button cross, which sit on ink.
- **White Surface / Graphite Surface** (surface): the composer card and hovered example pills.
- **Grey Bubble** (bubble): the quoted forward and the hover fill of quiet buttons.
- **Ink** (text): all body text.
- **Zinc Gray** (muted): secondary text, the progress line, source domains, idle icon buttons.
- **Placeholder**: the composer placeholder only.
- **Hairline** (border): every rule. **Strong Hairline** (border-strong): the focused composer, hovered pills, the scrollbar thumb.

### Verdict
- **True / False / Misleading / Unverifiable**: badge text, over a 14% tint of the same colour on the ground. False also colours the composer's inline error line. The dark set sits in one lightness band just below the ink, so no verdict outshouts another or the text.

### Named Rules
**The Ink Accent Rule.** There is no accent hue. Interactive emphasis is ink; hover softens it by mixing 80% ink toward the ground, never by adding a colour.

**The Verdict Colour Rule.** Green, red, amber and the verdict gray appear only in verdict badges (and red in error text), each paired with its icon and word so colour never carries the meaning alone.

**The Twin Rule.** A new colour is a new custom property with a value in both the light `:root` and the dark override. Never hard-code a colour in a component.

## Typography

**Body Font:** Geist (variable, 400 to 600, Google Fonts), falling back to Noto Sans Devanagari, then sans-serif.
**Display Font:** Geist.
**Devanagari:** Noto Sans Devanagari (400 to 600), reached through the same stack for Hindi text.

**Character:** A plain, precise grotesque at regular weight; the greeting is the only tightened, heavier line. Geist is a user-confirmed choice (recorded as a detector ignore-value in `.impeccable/config.json`). The Devanagari sans matches its stroke so Hindi forwards sit in the same voice.

### Hierarchy
- **Display** (500, clamp(1.75rem, 7vw, 2.5rem), 1.2, -0.025em, balanced wrap): the empty-page greeting only.
- **Body** (400, 1rem, 1.6): replies, rationales, the quoted forward, the composer.
- **Label** (400, 0.875rem): every secondary line: progress, example pills, copy and retry, domains, confidence, the footer note, the error line.
- **Badge** (500, 0.875rem, 1.6): verdict badges.

### Named Rules
**The One Small Size Rule.** There are two text sizes in a result: 1rem and `--small` (0.875rem). Nothing else.

**The Tabular Figures Rule.** Changing numbers (the "Checked in Ns" time and the confidence percentage) use `font-variant-numeric: tabular-nums`.

**The One Family Rule.** Geist everywhere, with Noto Sans Devanagari only as its Hindi partner. No serif, no mono, no second display face.

## Layout

One centred column, 44rem of content plus 1rem gutters, shared by `main` and `footer`. On the empty page the body centres vertically with 12dvh of bottom padding, so the greeting, composer and three example pills sit together a little above the middle. A check replaces the page and reads top to bottom: the forward quoted full width (folded to four lines with "Show all" when longer, so the verdict stays on the first screen), the result 1.5rem below it, left and unboxed, then the "New check" pill once the check ends, with the caution note under it while the result has verdicts. The composer is hidden there; the page opens at the top, never scrolled to the result's end, and Back returns to the empty page. Claims stack 0.5rem apart at full width. The footer respects the bottom safe-area inset. On coarse pointers the composer's icon buttons grow from 2rem to 2.5rem.

## Elevation & Depth

Nearly flat. Surfaces separate by tone and 1px hairlines; the one shadow is the composer's soft two-layer lift, shared by its "New check" twin, so the input reads as the object on the page.

### Shadow Vocabulary
- **Composer lift** (`box-shadow: 0 1px 2px rgb(0 0 0 / 0.04), 0 0.25rem 1rem rgb(0 0 0 / 0.04)`; dark `0.3` / `0.25` alpha): the composer and its "New check" twin.

### Named Rules
**The One Lift Rule.** Only the composer and its "New check" twin cast a shadow: the shared transition turns one into the other, and the lift keeps that seamless. Everything else is tone and hairline.

## Shapes

Three soft radii and a pill: 0.5rem for small controls and badges, 0.75rem for claim rows and image thumbnails, 1.25rem for the composer and the quoted forward, full pills for example chips (and a circle for the attachment's remove button). Borders are 1px hairlines. Icons are Lucide line icons drawn inline (24 viewBox, 2px round stroke, `currentColor`), including the mark (Lucide's message-circle-check in ink). Never emoji or text glyphs.

## Components

### Composer (signature)
- **Character:** the one object on the page; a white two-row card.
- **Shape:** 1.25rem corners, 1px hairline, the composer lift.
- **Content:** the auto-growing textarea (to 40dvh) on top; an actions row below with attach on the left and send on the right. An attached screenshot shows as a 4rem thumbnail with a small ink-filled remove circle.
- **Focus:** the border steps up to Strong Hairline; the textarea has no outline of its own. Drag-over sets the border to ink.
- **Motion:** the one motion moment. The composer and the "New check" pill share one View Transition name (0.45s, `cubic-bezier(0.16, 1, 0.3, 1)`): the pill arrives through it when a check ends and grows back into the centred composer on "New check". Reduced motion removes it along with every other animation and transition.

### Buttons
- **Send:** ink square (0.5rem corners, 2rem) with a ground-coloured up-arrow; disabled at 40% opacity; hover mixes 80% ink toward the ground; press scales to 0.94.
- **Attach:** the same square, transparent with a hairline border and a muted plus; hover fills Grey Bubble and turns the icon to ink.
- **Quiet (copy, try again):** muted label text with an optional icon, 0.5rem corners; hover fills Grey Bubble. Try again carries a hairline border, copy does not.

### Chips (example pills)
- **Style:** transparent, hairline border, full pill, muted label text.
- **Hover:** strong-hairline border, surface fill, ink text. Shown only on the empty page.

### Messages
- **Forward quote:** a `blockquote`, Grey Bubble, 1.25rem corners, full column width; an attached screenshot sits above the text with a hairline border and 0.75rem corners; text folds to four lines with a quiet "Show all" / "Show less" toggle.
- **Reply:** unboxed body text with linkified URLs, followed by a copy button.
- **Progress:** a disclosure line in muted label text with a chevron; while running, the current step pulses between muted and ink (1.6s), keeping full contrast at both ends.

### Cards / Containers (claim rows)
- **Corner Style:** 0.75rem.
- **Background:** none; 1px hairline border; header hover a 50% Grey Bubble wash.
- **Header:** verdict badge, the claim, and a muted chevron that rotates 180° on open (0.2s).
- **Body:** separated by a hairline; the rationale, a disc list of source links each with its muted domain, then the confidence line.

### Verdict Badges
Tinted 0.5rem-cornered badges: drawn icon plus one word in the verdict colour. Check/True, x/False, warning triangle/Misleading, circled question/Unverifiable.

## Do's and Don'ts

### Do:
- **Do** set colour, size, radius and easing through the `:root` custom properties, with a dark value for every colour.
- **Do** pair every verdict colour with its icon and word.
- **Do** use tabular figures for any changing number.
- **Do** draw new icons from Lucide, inline, stroked in `currentColor`.
- **Do** keep every animation inside the reduced-motion reset.

### Don't:
- **Don't** add an accent hue or a second typeface.
- **Don't** use the verdict colours outside verdicts and error text.
- **Don't** add a text size beyond the display, 1rem and 0.875rem.
- **Don't** give anything but the composer and "New check" a shadow.
- **Don't** add labels, instruction blocks, avatars, or copy that repeats the heading or placeholder.
