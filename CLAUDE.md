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

## What Happens Automatically
- Every dispatch writes a trace bundle to `eval/traces/{date}/{task_class}-{HHMMSS}-{worker}/`
- Traces include: `trace.json` (structured metadata), `prompt.md` (rendered prompt), `output.raw` (raw worker output)

## What You Need To Do Manually
- **After changing `core/task_schema.py` keywords**: run `./scripts/eval.sh` — checks classification accuracy against 40 benchmarks
- **After changing `config/lanes.yaml` routing**: run `./scripts/eval.sh` — checks routing correctness against 10 benchmarks
- **After changing any config file**: run `./scripts/eval.sh` — cross-validates all YAML against Python enums
- **If eval regresses**: fix the change or revert. If you accept the regression (rare), save a new baseline with `./scripts/eval.sh --save {description}`
- **Later — when traces accumulate**: run `grep`/`jq` on `eval/traces/` to see worker success rates, latency patterns, retry rates. No rush on this.

### Eval Commands
```bash
./scripts/eval.sh                      # Run all benchmarks
./scripts/eval.sh --category routing   # Run one category
./scripts/eval.sh --save baseline      # Save results as named snapshot
./scripts/eval.sh --compare baseline   # Compare current against snapshot
```

### Trace Queries (use when you have enough traces)
```bash
# Success rate by worker
grep -rl '"status": "succeeded"' eval/traces/*/ | wc -l

# Failed dispatches
grep -rl '"status": "failed"' eval/traces/*/

# Specific worker traces
find eval/traces -name trace.json | xargs grep '"selected_worker": "codex"'
```

## What's Planned But Not Built Yet
- `eval/scripts/worker_stats.py` — aggregate traces into per-worker success rates (needs trace data)
- `eval/scripts/compare_traces.py` — compare two trace directories (needs trace data)
- Eval as CI gate in `.github/workflows/ci.yml` (after eval stabilizes)
- Empirical worker preference adjustment based on trace evidence
- See `docs/meta-harness/refactor_plan.md` for full ranked list
- See `docs/meta-harness/outer_loop_plan.md` for self-improvement loop designs

## Tool-Specific (Claude Code)
See @.claude/rules/khamel-mode.md
See @.claude/rules/codex.md
