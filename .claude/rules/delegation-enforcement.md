# Delegation Enforcement

For any user request that asks for **code changes in this repo**, the default action is to **dispatch a task** via `/dispatch`, not to edit files yourself.

## Exceptions (inline is OK)

1. **Pure planning, review, or research** — no code changes.
2. **User explicit override** — "just do it inline", "skip dispatch", "do it yourself".
3. **Harness bootstrap** — changes to `oneshot_cli/`, `.oneshot/config/`, `.claude/commands/`, `.claude/rules/delegation-enforcement.md`, and harness docs. The harness can't dispatch its own build.
4. **Minor review fixes** — typo corrections in `result.md`, status updates. But rewriting the worker's code is NOT a minor fix.

## Lane selection defaults

- Normal implementation: `routine_coder`
- Trivial/mechanical: `cheap_fast`
- Summaries/extraction: `cheap_summary`
- Hard refactors/cross-file: `strong_reasoning`
- Escalation only: `premium_reasoning`

## After dispatching

Print the task-id and `./bin/oneshot review <id>` as the next step. Do not monitor or babysit — the user will trigger review when ready.

## Violation pattern to avoid

Do NOT say "I'll handle this one myself because it's simple" — that's the exact pattern this rule prevents. Use `/dispatch` even for small changes. The worktree boundary is the enforcement mechanism.
