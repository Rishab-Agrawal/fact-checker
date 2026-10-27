# fact-checker

## Standard

Code and design, from architecture down to single lines, as a very experienced senior engineer would write them: no bloat, nothing stale, no over-engineering, easy to maintain. The `ponytail` skill is a useful guide, not the whole standard.

- Check if there are any standard/official way of doing what you are trying to do, rather than reinventing the wheel with sub-par quality.
- Comments: as crisp as possible. Never history, past mistakes or what changed.
- Keep diffs as small as possible. Not so commits are tiny: a small diff is evidence that nothing is bloated or over-engineered.
- When something goes stale, remove it in the same change.
- Lasting knowledge that the code, git and skills don't already hold goes in this file, never in Claude's auto-memory. Only what's necessary, as crisp as possible.

## Problems are symptoms

A bug, bloat or over-engineering usually points to something larger: weak design, a missing concept, a wrong abstraction. Goodhart's law applies: fixing only the instance treats the measure as the target. Find and fix the root cause.

## Project

- Jev (TypeSafe System One) only for narrow single-hop gates where it loses no quality; generation, multi-hop reasoning and dates stay with Claude. The README lists where.
