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
- **Janitor** (`core/janitor/`) runs background intelligence via Claude Code hooks:
  - Test gaps, code smells, config drift, dependency map — computed fresh every session start
  - Session summaries, pattern mining — run at session end via free LLM (if OPENROUTER_API_KEY set)
  - Raw event log: `.janitor/events.jsonl` — every tool call recorded, append-only
  - Onboarding summary: `CLAUDE.local.md` — auto-generated daily, survives without janitor installed

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

## Project Intelligence
Need to understand what's been happening? Start here:

| Question | Look at |
|----------|---------|
| What's the current state of the project? | `CLAUDE.local.md` (auto-generated onboarding summary) |
| What type is this project? | `.janitor/project-type.json` (code, document, or hybrid) |
| What files were changed recently? | `.janitor/events.jsonl` — grep for `file_written` or `commit` |
| What decisions were made? | `.janitor/events.jsonl` — grep for `decision` |
| What's broken or stuck? | `.janitor/events.jsonl` — grep for `blocker` or `dead_end` |
| What approaches already failed? | `.janitor/events.jsonl` — grep for `dead_end` |
| What files have no tests? | `.janitor/test-gaps.json` (code/hybrid) |
| What files are too big? | `.janitor/code-smells.json` (code/hybrid) |
| What config is uncommitted? | `.janitor/config-drift.json` |
| What files have the most dependents? | `.janitor/dep-graph.json` (code/hybrid) |
| What patterns repeat across sessions? | `.janitor/patterns.json` |
| What documents are stale? | `.janitor/doc-staleness.json` (document/hybrid) |
| What documents are orphaned? | `.janitor/doc-orphans.json` (document/hybrid) |
| What documents link to what? | `.janitor/doc-crossrefs.json` (document/hybrid) |
| What documents changed recently? | `.janitor/doc-recent-activity.json` (document/hybrid) |
| What are the document clusters? | `.janitor/doc-clusters.json` (document/hybrid) |
| What files are unusually large? | `.janitor/doc-size-outliers.json` (all types) |
| What files are touched most? | `.janitor/critical-files.json` (all types) |
| What files have bus-factor risk? | `.janitor/knowledge-risk.json` (all types) |
