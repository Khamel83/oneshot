# Delegation Enforcement

## CORE RULE: Claude Does NOT Write Code

For ANY request that involves **code changes** (new files, edits, refactors, tests):
the default action is to **dispatch the task to a worker via the dispatch protocol**.
Claude plans, reviews, and integrates. Workers execute.

### How to Dispatch

```bash
# 1. Resolve lane and workers
python3 -m core.router.resolve --class <task_class> --category <category>

# 2. Build self-contained prompt (see _shared/dispatch.md template)

# 3. Dispatch
python3 -m core.dispatch.run \
  --class <task_class> \
  --category <category> \
  --prompt "Self-contained prompt..." \
  --output 1shot/dispatch \
  --manifest 1shot/dispatch
```

See `~/.claude/skills/_shared/dispatch.md` for the full prompt template and protocol.

### Lanes and When Claude Handles Inline

| Lane | Workers | Claude's Role |
|------|---------|---------------|
| **premium** | claude_code, codex | Claude handles inline (planning, review, integration) |
| **balanced** | codex, gemini_cli | Dispatch. Claude reviews output. |
| **cheap** | gemini_cli, codex, glm_claude | Dispatch. Claude reviews output. |
| **research** | gemini_cli, codex | Dispatch. Claude integrates findings. |
| **janitor** | free (openrouter) | Dispatch. No review needed. |

If the router returns `premium` lane, Claude handles the task inline.
**If it returns any other lane, you MUST dispatch.** There is no middle ground.

## Exceptions (Claude handles inline)

1. **Pure planning, review, or research** — no code changes.
2. **User explicit override** — "just do it inline", "skip dispatch", "do it yourself".
3. **Harness bootstrap** — changes to `oneshot_cli/`, `.claude/rules/delegation-enforcement.md`, `.claude/skills/_shared/`, and harness docs. The harness can't dispatch its own build.
4. **Minor review fixes** — typo corrections in `result.md`, status updates. But rewriting the worker's code is NOT a minor fix.
5. **Lane resolves to premium** — this is the ONLY lane where inline is acceptable.

## What "No Workers Available" Means

If `python3 -m core.router.resolve` fails, or returns an empty worker pool:
1. Stop. Tell the user workers are unavailable.
2. Do NOT silently fall back to doing the work yourself.

## After Dispatching

- Review worker output against acceptance criteria
- Validate (run tests, lint)
- Integrate and commit if valid
- If dispatch failed: retry with fallback_lane once, then log blocker

## Violation Pattern to Avoid

Do NOT say "I'll handle this one myself because it's simple" — that's the exact pattern this rule prevents.
Do NOT say "workers are unavailable" without actually running the router check — the config exists and codex/gemini are installed.
Do NOT use the Agent tool as a dispatch substitute — Agent spawns full Claude sessions, not lightweight CLI workers.
