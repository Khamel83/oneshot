# OneShot Project Instructions

## Operator Rules
See @docs/instructions/core.md
See @docs/instructions/workflow.md
See @docs/instructions/coding.md
See @docs/instructions/search.md
See @docs/instructions/review.md

## Project-Specific
See @docs/instructions/oneshot.md

## Harness Eval & Traces
See @docs/meta-harness/eval_framework.md
See @docs/meta-harness/trace_architecture.md

### What This Is
The eval system lets you (or Claude in a session) verify that changes to the routing and classification code don't break anything. Think of it as tests for the routing layer — same idea as running tests after changing application code.

### What Happens Automatically
- Every dispatch writes a trace bundle to `eval/traces/{date}/{task_class}-{HHMMSS}-{worker}/`
- Traces include: `trace.json` (structured metadata), `prompt.md` (rendered prompt), `output.raw` (raw worker output)
- These accumulate passively — you don't need to do anything with them yet

### What Happens In-Session (Claude runs it, not you)
When you ask Claude to change `core/task_schema.py` keywords, `config/lanes.yaml`, or routing code, Claude should run `./scripts/eval.sh` afterward to confirm nothing broke. If it regresses, Claude fixes or reverts. You don't need to touch this.

### What's Planned But Not Built Yet
- `eval/scripts/worker_stats.py` — aggregate traces into per-worker success rates (needs trace data)
- `eval/scripts/compare_traces.py` — compare two trace directories (needs trace data)
- Eval as CI gate in `.github/workflows/ci.yml` (after eval stabilizes)
- Empirical worker preference adjustment based on trace evidence
- See `docs/meta-harness/refactor_plan.md` for full ranked list
- See `docs/meta-harness/outer_loop_plan.md` for self-improvement loop designs

## Tool-Specific (Claude Code)
See @.claude/rules/khamel-mode.md
See @.claude/rules/codex.md
