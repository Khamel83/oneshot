# Eval Framework: Measuring Harness Performance

> How to know if a change to OneShot makes things better or worse.

---

## 1. What We're Evaluating

The harness is the full pipeline: intake → classify → route → dispatch → capture → validate → integrate.

We don't evaluate model quality (that's the provider's job). We evaluate whether the harness makes good decisions about routing, prompting, and verification.

---

## 2. Benchmark Task Categories

| Category | Description | Example Tasks |
|----------|-------------|---------------|
| **classification** | How well does `infer_category()` classify task descriptions? | 20 hand-labeled descriptions |
| **routing** | Does the router pick the right lane and worker order? | 10 tasks across all task classes |
| **prompt_quality** | Do self-contained prompts produce useful worker output? | 5 tasks dispatched to each worker type |
| **dispatch_reliability** | Do dispatched tasks succeed on first attempt? | Run same tasks 3x, measure success rate |
| **verification** | Does the verification checklist catch real issues? | 5 tasks with injected bugs |
| **end_to_end** | Full /short or /conduct run on a well-defined goal | 3 target projects |

---

## 3. Benchmark Task Format

Each benchmark task is a JSON file:

```json
{
  "id": "cls-001",
  "category": "classification",
  "input": {
    "description": "Add error handling to the auth middleware",
    "files": ["api/auth.py"]
  },
  "expected": {
    "category": "coding",
    "task_class": "implement_medium",
    "risk_level": "high"
  },
  "notes": "auth keyword should trigger high risk"
}
```

Routing benchmark:

```json
{
  "id": "rte-001",
  "category": "routing",
  "input": {
    "task_class": "implement_small",
    "category": "coding"
  },
  "expected": {
    "lane": "cheap",
    "workers_first": "codex",
    "review_with": "claude_code"
  }
}
```

---

## 4. Metrics

### Primary Metrics (automated, always collected)

| Metric | How to Measure | Target |
|--------|---------------|--------|
| **classification_accuracy** | % of benchmark tasks where inferred category matches expected | > 90% |
| **risk_accuracy** | % of tasks where inferred risk matches expected | > 85% |
| **routing_correctness** | % of tasks where lane + first worker match expected | > 95% |
| **dispatch_success_rate** | % of dispatches with exit_code 0 and no errors | > 80% |
| **config_consistency** | Cross-validate lanes.yaml, workers.yaml, task_schema.py | 100% |

### Secondary Metrics (require traces)

| Metric | How to Measure | Target |
|--------|---------------|--------|
| **latency_p50** | Time from dispatch start to manifest write | < 60s |
| **latency_p95** | Same, 95th percentile | < 180s |
| **retry_rate** | % of tasks requiring > 1 dispatch attempt | < 20% |
| **escalation_rate** | % of tasks escalated to fallback lane | < 10% |
| **human_touch_rate** | % of tasks requiring human intervention | < 15% |

### Tertiary Metrics (require human judgment)

| Metric | How to Measure |
|--------|---------------|
| **output_usefulness** | 1-5 scale rubric on worker output quality |
| **prompt_clarity** | Expert review of dispatched prompt |
| **convention_adherence** | Does output follow repo patterns? |

---

## 5. Search / Validation / Holdout Sets

### Classification Benchmarks

- **Search set** (development): `eval/benchmarks/classification/search/*.json`
  - Used to tune keyword lists, thresholds
  - 20 tasks, balanced across categories
- **Validation set**: `eval/benchmarks/classification/validation/*.json`
  - Used during development to check for overfitting
  - 10 tasks
- **Holdout set**: `eval/benchmarks/classification/holdout/*.json`
  - Only run after changes are finalized
  - 10 tasks

### Routing Benchmarks

- Single set, no split needed (deterministic): `eval/benchmarks/routing/*.json`
  - 10 tasks covering all task classes + all categories

### End-to-End Benchmarks

- Small set of well-scoped tasks: `eval/benchmarks/e2e/*.json`
  - Each has a target repo, goal, acceptance criteria, and scoring script
  - 3 tasks initially

---

## 6. Pareto Comparison Strategy

When comparing two harness versions (e.g., baseline vs proposed change):

1. Run both versions against the same benchmark set
2. For each task, record: success/fail, latency, cost, context_size, retry_count
3. Plot on a Pareto frontier: (cost, success_rate) and (latency, success_rate)
4. A change is accepted if it:
   - Does not regress any primary metric by > 5%
   - Improves at least one primary metric
   - Does not increase human_touch_rate

If a change improves classification_accuracy by 10% but increases dispatch latency by 30%, it's a tradeoff — present both metrics to the operator.

---

## 7. Automated Checks (Implement Now)

```bash
# Run all automated benchmarks
./scripts/eval.sh

# Run specific benchmark category
./scripts/eval.sh --category classification
./scripts/eval.sh --category routing
./scripts/eval.sh --category config
```

What `eval.sh` does:

1. **Classification**: Import `infer_category` and `infer_risk`, compare against expected
2. **Routing**: Call `resolve()` for each benchmark, compare against expected
3. **Config**: Cross-validate YAML configs against Python enums (TaskClass, TaskCategory, workers)

---

## 8. Human Rubric (Implement Later)

For end-to-end and prompt_quality benchmarks:

| Dimension | 1 | 2 | 3 | 4 | 5 |
|-----------|---|---|---|---|---|
| **Task completion** | No useful output | Partial | Most of task done | Fully done | Done + extras |
| **Convention adherence** | Ignores repo patterns | Some alignment | Mostly follows | Follows well | Perfect match |
| **Output quality** | Garbled/noisy | Understandable | Clear | Well-structured | Publication-ready |

---

## 9. File Layout

```
eval/
  benchmarks/
    classification/
      search/         # 20 tasks for development
      validation/     # 10 tasks for dev-time validation
      holdout/        # 10 tasks, only run after finalizing changes
    routing/          # 10 tasks (deterministic, no split)
    e2e/              # 3 tasks with scoring scripts
  results/
    .gitkeep
    YYYY-MM-DD--{description}.json   # Append-only result snapshots
  scripts/
    run_classification.py
    run_routing.py
    run_config_check.py
    run_e2e.sh
    compare_results.py    # Pareto comparison between two result files
scripts/
  eval.sh              # Top-level runner
```

---

## 10. First Runnable Benchmark Set

See `eval/benchmarks/classification/search/` for 20 classification tasks.
See `eval/benchmarks/routing/` for 10 routing tasks.
See `scripts/eval.sh` for the runner.

---

## 11. Regression Detection

After any harness change:

```bash
./scripts/eval.sh --save baseline
# ... make changes ...
./scripts/eval.sh --compare baseline
```

The compare mode exits non-zero if any primary metric regressed by > 5%.
This becomes the gate in CI for harness changes.
