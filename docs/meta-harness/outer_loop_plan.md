# Outer Loop Plan: Self-Improving Harness

> How OneShot becomes a repo that learns from its own operation.

---

## 1. What Is a Candidate Harness?

A candidate harness is a version of the harness (routing config, classification keywords, prompt template, risk keywords) that can be evaluated against the benchmark suite and compared to the current baseline.

A candidate is NOT a full code change. It is a policy change — swapping keyword lists, adjusting worker preferences, or changing prompt templates — that can be measured without deploying to production.

### What Gets Versioned Per Candidate

| Component | Versioned? | How |
|-----------|-----------|-----|
| `core/task_schema.py` (keywords, LANE_ASSIGNMENTS) | Yes | Git branch or commit |
| `config/lanes.yaml` (worker pools, preferences) | Yes | Git branch or commit |
| `config/workers.yaml` (worker definitions) | Yes | Git branch or commit |
| Dispatch prompt template | Yes | `prompt_version` in trace.json |
| `.claude/skills/_shared/dispatch.md` | Yes | Git branch or commit |
| `docs/instructions/task-classes.md` | Yes | Git branch or commit |
| `.claude/skills/*/SKILL.md` (operator prompts) | No | Too large, too coupled |
| `core/dispatch/run.py` (execution logic) | No | Structural, not policy |
| `core/search/argus_client.py` | No | Infrastructure |
| Templates, community starter | No | Unrelated |

---

## 2. Candidate Evaluation

### Automated Evaluation

```bash
# On a candidate branch:
./scripts/eval.sh --save candidate-v1

# On baseline (master):
./scripts/eval.sh --save baseline

# Compare:
./scripts/eval.sh --compare baseline
```

A candidate passes automated eval if:
- Classification accuracy does not regress by > 5%
- Routing correctness = 100% (it's deterministic)
- Config consistency = 100%

### Trace-Based Evaluation (requires real dispatch data)

When enough traces exist (> 20 per worker-category combination):

```bash
# Compare success rates between two config versions
python3 eval/scripts/compare_traces.py \
  --baseline eval/traces/2026-03-*/ \
  --candidate eval/traces/2026-04-*/
```

Metrics:
- Dispatch success rate per worker per category
- Average latency per worker
- Retry rate per lane
- Escalation rate

### Human Evaluation (for prompt template changes)

When the dispatch prompt template changes, run a small set of identical tasks under both versions and compare output quality using the human rubric from `eval_framework.md`.

---

## 3. Candidate Rejection

A candidate is rejected if:
1. Any primary eval metric regresses by > 5%
2. It breaks existing dispatch behavior (routing changes produce wrong lanes)
3. It introduces a new dependency or infrastructure requirement
4. The operator (you) decides it's not worth the complexity

Rejection is recorded in `eval/rejected/`:
```
eval/rejected/
  2026-04-05--codex-first-for-writing.json   # {"reason": "codex writing quality 30% worse than gemini", "metrics": {...}}
```

---

## 4. Frontier Tracking

The Pareto frontier is the set of non-dominated harness configurations.

We track two primary frontiers:
1. **Cost vs Success**: minimize cost while maintaining success rate
2. **Latency vs Success**: minimize latency while maintaining success rate

Frontier records live in `eval/frontier/`:
```
eval/frontier/
  frontier.json    # Current frontier: list of {config_sha, metrics, date}
  history.jsonl    # Append-only log of all evaluated configs
```

### frontier.json format

```json
{
  "generated_at": "2026-04-05T12:00:00Z",
  "frontier": [
    {
      "config_sha": "a0be591",
      "description": "baseline v14.2",
      "evaluated_at": "2026-04-05",
      "metrics": {
        "classification_accuracy": 100,
        "routing_accuracy": 100,
        "dispatch_success_rate": null,
        "avg_latency_seconds": null
      }
    }
  ]
}
```

---

## 5. Promotion

When a candidate outperforms the current baseline on the frontier:

1. Merge the candidate branch to master
2. Run `./scripts/eval.sh --save promoted-{description}`
3. Update `eval/frontier/frontier.json` — add new point, remove dominated points
4. Commit with message: `harness: promote {description} ({config_sha})`

---

## 6. Overfitting Protections

| Risk | Protection |
|------|-----------|
| Overfitting to search set | Holdout set only run after changes are finalized |
| Optimizing for eval at expense of real work | Eval tasks are real, representative tasks, not synthetic |
| Frequent small changes masking slow drift | Weekly summary review, not per-commit |
| Keyword bloat in classifier | Max keyword list size: 30 per category. When exceeded, audit and prune. |
| Worker preference thrashing | Minimum 20 traces per worker-category before changing preference |
| Prompt template complexity | Max prompt version changes: 4 per quarter |

---

## 7. The Three Loop Versions

### V0: Manual Loop (Now)

The operator runs eval, reads results, makes decisions.

```
1. Make a change (add keyword, adjust preference)
2. ./scripts/eval.sh
3. If regression → revert
4. If improvement → commit
5. Every few weeks: review trace data, identify patterns
```

No automation. No frontier tracking. Just eval + human judgment.
This is what we have now.

### V1: Semi-Automated Loop (Next)

Add trace collection and periodic reporting.

```
1. Dispatches automatically write traces (already done)
2. Weekly: python3 eval/scripts/worker_stats.py → see success rates
3. Monthly: ./scripts/eval.sh --save monthly-{date} → track regression
4. Quarterly: review frontier, prune keywords, update preferences
5. Candidate changes tested against eval before merge
```

This adds:
- `eval/scripts/worker_stats.py` — trace aggregation
- `eval/scripts/compare_traces.py` — trace comparison
- CI gate: eval must pass before merge
- Frontier file tracking

### V2: Agent-Proposed Patch Loop (Later)

An agent proposes harness changes based on trace evidence.

```
1. Agent reads traces, identifies patterns:
   "gemini_cli fails 40% on coding tasks but succeeds 95% on research"
2. Agent proposes a patch:
   "Remove gemini_cli from coding category_preference in cheap lane"
3. Agent runs eval on a worktree:
   git worktree add .candidate
   (apply patch in worktree)
   cd .candidate && ./scripts/eval.sh --save agent-proposal-1
4. Agent compares against baseline:
   ./scripts/eval.sh --compare baseline
5. If improvement and no regression → agent opens PR
6. Human reviews and merges
```

This adds:
- Worktree-based candidate evaluation (isolated)
- Automated patch proposal from trace patterns
- PR creation with eval evidence
- Human approval gate remains

The agent cannot self-merge. The operator always has final say.

---

## 8. Minimal V0 Script

The v0 loop needs nothing beyond what we've already built:

```bash
# Make a change
vim core/task_schema.py

# Test it
./scripts/eval.sh

# If good, commit
git add core/task_schema.py eval/
git commit -m "harness: improve classification keywords for {reason}"
```

The key insight: the eval substrate IS the outer loop. Everything else is automation around it. The substrate is already in place. The loops are just discipline and habits.

---

## 9. What Remains Opinionated and Hand-Authored

These should NOT be automated or empirically optimized:

1. **Operator skill prompts** (conduct, full, short SKILL.md) — These encode your judgment about how work should flow. They're the identity of the harness.
2. **Decision defaults** (simplest implementation, follow existing pattern) — These are values, not metrics.
3. **Stack defaults** (Vercel, Supabase, Python) — Infrastructure preference, not optimization target.
4. **Anti-patterns** (no nginx, no AWS, no React) — Engineering judgment, not data-driven.
5. **Risk thresholds** (auth = high risk) — Safety policy, not something to tune based on success rates.
6. **The planner/worker split** (Claude thinks, workers execute) — Architectural conviction.
7. **Filesystem-native inspectability** — Design principle, not something to measure.

These are the repo's identity. The eval system measures how well the *mechanism* works (classification, routing, dispatch), not whether the *values* are correct.
