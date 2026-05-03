---
name: adversarial-review
description: Adversarial second-opinion review via Gemini. Challenges design decisions, not syntax. Use after significant architectural or implementation choices.
---

# /adversarial-review — Second-Opinion Design Critique

Claude orchestrates. Gemini critiques. Gemini comes in cold — no history of building the thing — so it challenges assumptions the current context has normalized.

This is not a bug-finder. It asks "is this the right approach?" not "what's broken?"

## Usage

`/adversarial-review [focus area]`

- `/adversarial-review` — general adversarial review of current diff
- `/adversarial-review auth` — focus on authentication assumptions
- `/adversarial-review data loss` — pressure-test data safety
- `/adversarial-review race conditions` — concurrency failure modes
- `/adversarial-review complexity` — is this simpler than it needs to be?

## Process

1. Check scope: `git diff HEAD --stat`. If > 20 files, ask user foreground vs background.
2. Check worker availability: `gemini --version`. Fall back to Codex if unavailable.
3. Capture the diff: `git diff HEAD` (or `git diff main...HEAD` if working tree clean).
4. Run adversarial review via Gemini with the diff and focus area.
5. Return output verbatim — do NOT paraphrase unless user asks.

## After the Review

- Push back on Gemini's points if you disagree — this is a debate, not a verdict
- If nothing substantive found, note that the design is solid
- Pairs well with `/review` — run adversarial first, review second

## Notes

- Best run after completing a significant design decision, before final commit
- For auth/security focus areas, treat every concern as HIGH priority
