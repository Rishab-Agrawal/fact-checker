# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Two audiences, weighted equally:
- People who received a forwarded message (often in a family WhatsApp group) and want to know whether it is true before they believe or share it.
- First-time visitors seeing what it does. They rarely have a forward to hand and give it one or two tries.

## Product Purpose

Paste a forwarded message or a screenshot and get a reply in the sender's language with a verdict for each checkable claim (true, false, misleading, unverifiable), a rationale, and sources. Success: the visitor trusts the verdict enough to act on it, and a first-time visitor understands what the system does within seconds.

## Positioning

Each claim is researched on its own: earlier verdicts, an archive of ~88k professional fact-checks, then the web, and an advocate and a skeptic argue it out when the judge is unsure. Verdicts cite real sources or become unverifiable.

## Capabilities and Constraints

- FastAPI serves the API and one hand-written HTML/CSS/JS page; no frontend framework or build step.
- Errors never reach the page as details: visitors see a generic message, the server log gets the rest.
- Public with no login: 10 checks per IP per day. Anything that starts a check spends one.
- Accepts text up to 4,000 characters and one PNG, JPG or WebP screenshot up to 5 MB.
- Replies may be in any language the forward was written in.

## Brand Commitments

- Look and feel of claude.ai (user-pinned): a chat interface, user messages right, replies left, following the device's light or dark setting. On an empty page the greeting and input sit centered; once a check starts, the input moves to the bottom.
- Voice: minimal, friendly, simple. No copy repeated between the heading, the placeholder and other text.

## Product Principles

1. Verdicts first, evidence one tap away.
2. Never claim more certainty than the sources give.
3. A first-time visitor can start a check without reading instructions.
