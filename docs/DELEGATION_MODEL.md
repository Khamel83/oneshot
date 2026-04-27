# Delegation Model

## Overview

The oneshot delegation harness enforces a separation between **planning** and **implementation**:

- **Claude Code** is the **planner/reviewer**. It writes task specs, reviews results, and decides next steps.
- **External workers** are the **implementers**. They receive bounded task specs and produce diffs.

This is not a preference — it's a structural constraint enforced by git worktrees.

## Why Mechanical Enforcement

Prompt-only enforcement ("please delegate, don't implement") fails because LLMs default to doing the work themselves. The worktree boundary makes it impossible to cheat:

- Workers run in `../oneshot-worktrees/<id>` on branch `worker/<id>`.
- The main working tree is never modified by a worker.
- Claude Code reviews the diff, not the files.

Even if Claude "helpfully" writes code for the worker, the runner still operates in a separate directory. The worker's output is what gets reviewed.

## Dispatch Lifecycle

```
1. Claude writes a bounded task spec
2. ./bin/oneshot dispatch --lane <lane> --task-file <spec>
   → Creates task dir, worktree, renders worker.md
   → Writes dry-run command to worker.log (MVP)
3. Worker executes in the worktree (future: live runner)
4. ./bin/oneshot collect <id>
   → Gathers diff.patch, result.md, test.log
5. ./bin/oneshot review <id>
   → Claude reads the review bundle
6. Verdict: accept / reject / escalate / follow-up
```

## When to Use Each Lane

| Lane | Use when |
|------|----------|
| `cheap_fast` | Lint fixes, formatting, trivial docstrings, simple test additions |
| `cheap_summary` | Summaries, data extraction, low-risk transforms |
| `routine_coder` | **Default.** Normal bounded implementation and tests. |
| `strong_reasoning` | Hard refactors, cross-file changes, ambiguous failures |
| `premium_reasoning` | Escalation only. Failed twice, or design-sensitive. |

## When Claude Implements Inline

These are the only exceptions to the dispatch-first rule:

1. **Pure planning/review/research** — no code changes.
2. **User override** — "just do it inline" / "skip dispatch".
3. **Harness bootstrap** — changes to `oneshot_cli/`, `.oneshot/config/`, `.claude/commands/`, enforcement rule, harness docs.
4. **Minor review fixes** — typo in `result.md`, status updates. Not rewriting worker code.

## Cost Philosophy

Claude Code sessions are expensive. External workers (ZAI, OpenCode Go) are cheap or free. The delegation model exists to:

- Minimize tokens spent on mechanical implementation work
- Reserve Claude for planning, review, and complex decisions
- Make delegation the path of least resistance

The `premium_reasoning` lane exists as an escape hatch, not a default. If a task reaches premium, something went wrong in the routing or the spec.
