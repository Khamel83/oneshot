# Trace Architecture: Raw Evidence for Harness Optimization

> Filesystem-native trace storage. grep/cat/find/jq friendly. No custom UI.

---

## 1. Design Principles

1. **Raw traces are primary** — summaries are derived, never replacements
2. **Immutable artifacts** separated from **mutable derived** artifacts
3. **Every trace is self-contained** — one directory per dispatch, everything needed to reproduce
4. **Flat naming, hierarchical dirs** — `find` and `ls` work naturally
5. **JSON for machine data, Markdown for human data** — `jq` and `cat` work respectively
6. **No database** — files only. SQLite if we ever need aggregation queries (later)

---

## 2. Directory Tree

```
eval/
  traces/
    {YYYY-MM-DD}/
      {task_class}-{HHMMSS}-{worker}/
        trace.json          # Full dispatch trace (primary artifact, IMMUTABLE)
        prompt.md           # Rendered prompt sent to worker
        output.raw          # Raw worker output (JSONL or plain text)
        output.parsed.json  # Parsed structured output
        manifest.md         # Human-readable summary (DERIVED from trace.json)
        review.json         # If reviewed, the review result
        scoring.json        # If scored by eval, the eval result
      summary.json          # Daily aggregate (DERIVED, regenerated)

  results/
    {YYYY-MM-DD}--{description}.json  # Eval run results (IMMUTABLE)

  benchmarks/
    ... (see eval_framework.md)
```

### Naming Convention

- **Trace directory**: `{task_class}-{HHMMSS}-{worker}` — e.g., `implement_small-143022-codex`
- **Daily directory**: `2026-04-05`
- **Summary files**: Always end in `.json` for machine, `.md` for human
- **Immutable files**: `trace.json`, `prompt.md`, `output.raw`, `scoring.json`
- **Derived files**: `manifest.md`, `output.parsed.json`, `summary.json`

---

## 3. Schemas

### trace.json (Primary Artifact)

```json
{
  "trace_id": "implement_small-20260405-143022-codex",
  "schema_version": "1",
  "timestamp": "2026-04-05T14:30:22Z",
  "harness_version": "14.2",

  "classification": {
    "description": "Fix the auth bug in login.py",
    "task_class": "implement_small",
    "category": "coding",
    "risk_level": "high",
    "inferred_by": "infer_category + infer_risk"
  },

  "routing": {
    "lane": "cheap",
    "workers": ["codex", "gemini_cli", "glm_claude"],
    "selected_worker": "codex",
    "selection_reason": "first_available",
    "review_with": "claude_code",
    "fallback_lane": "balanced"
  },

  "prompt": {
    "template": "dispatch_v1",
    "word_count": 342,
    "file_path": "prompt.md"
  },

  "execution": {
    "worker": "codex",
    "command": "unset OPENAI_API_KEY && codex exec --json ...",
    "exit_code": 0,
    "started": "2026-04-05T14:30:22Z",
    "completed": "2026-04-05T14:32:45Z",
    "duration_seconds": 143.2
  },

  "output": {
    "raw_file": "output.raw",
    "parsed_file": "output.parsed.json",
    "errors": [],
    "message_preview": "Fixed the auth bug by..."
  },

  "validation": {
    "passed": true,
    "acceptance_criteria_met": ["auth bug fixed", "tests pass"],
    "acceptance_criteria_failed": []
  },

  "retry": {
    "attempt": 1,
    "previous_traces": [],
    "escalated": false,
    "escalation_reason": null
  },

  "cost": {
    "estimated_tokens": null,
    "estimated_cost_usd": 0,
    "worker_cost_basis": "subscription"
  },

  "config_snapshot": {
    "lanes_sha": "a0be591",
    "workers_sha": "a0be591",
    "models_sha": "a0be591"
  }
}
```

### prompt.md (Rendered Prompt)

The actual prompt sent to the worker, verbatim. Markdown format, following the dispatch template.

### output.raw (Raw Worker Output)

Unmodified output from the worker CLI. JSONL for codex, JSON for gemini, plain text otherwise.

### output.parsed.json (Parsed Output)

```json
{
  "worker": "codex",
  "messages": ["Fixed the auth bug by..."],
  "errors": [],
  "usage": {
    "input_tokens": 4500,
    "output_tokens": 1200
  }
}
```

### scoring.json (Eval Result, if scored)

```json
{
  "trace_id": "implement_small-20260405-143022-codex",
  "scored_at": "2026-04-05T15:00:00Z",
  "metrics": {
    "task_success": true,
    "classification_correct": true,
    "routing_correct": true,
    "latency_seconds": 143.2,
    "retry_count": 0,
    "escalated": false
  },
  "human_rating": null,
  "notes": null
}
```

### summary.json (Daily Aggregate, DERIVED)

```json
{
  "date": "2026-04-05",
  "total_dispatches": 12,
  "succeeded": 10,
  "failed": 2,
  "retry_rate": 0.167,
  "escalation_rate": 0,
  "avg_latency_seconds": 98.4,
  "by_worker": {
    "codex": {"dispatches": 7, "succeeded": 6, "avg_latency": 85.2},
    "gemini_cli": {"dispatches": 3, "succeeded": 3, "avg_latency": 120.1},
    "glm_claude": {"dispatches": 2, "succeeded": 1, "avg_latency": 110.5}
  },
  "by_task_class": {
    "implement_small": {"dispatches": 8, "succeeded": 7},
    "doc_draft": {"dispatches": 4, "succeeded": 3}
  },
  "by_lane": {
    "cheap": {"dispatches": 10, "succeeded": 8},
    "research": {"dispatches": 2, "succeeded": 2}
  },
  "generated_at": "2026-04-05T23:59:59Z",
  "trace_ids": ["implement_small-143022-codex", "..."]
}
```

---

## 4. Example Trace Bundles

### Successful Dispatch

```
eval/traces/2026-04-05/implement_small-143022-codex/
  trace.json          # All metadata, exit_code: 0, validation.passed: true
  prompt.md           # "Fix the auth bug in login.py..."
  output.raw          # JSONL from codex
  output.parsed.json  # {"messages": [...], "errors": []}
  manifest.md         # "Status: OK, Duration: 143s, Worker: codex"
  scoring.json        # {"metrics": {"task_success": true, ...}}
```

### Failed Dispatch (with Retry)

```
eval/traces/2026-04-05/implement_small-143500-gemini_cli/
  trace.json          # exit_code: 1, retry.attempt: 1, errors: ["Timeout"]

eval/traces/2026-04-05/implement_small-144200-codex/
  trace.json          # exit_code: 0, retry.attempt: 2, previous_traces: ["...gemini_cli"]
  prompt.md
  output.raw
  output.parsed.json
  manifest.md
  scoring.json
```

---

## 5. How Traces Enable Optimization

### Question: Which worker is best for coding tasks?

```bash
# Extract all coding task traces
grep -rl '"category": "coding"' eval/traces/*/ | \
  xargs jq -r '.execution.worker, .execution.duration_seconds, .output.errors' | \
  paste - - - | \
  sort | uniq -c | sort -rn
```

### Question: What's the retry rate for each lane?

```bash
for lane in cheap balanced premium research; do
  echo "=== $lane ==="
  grep -rl "\"lane\": \"$lane\"" eval/traces/*/ | \
    xargs jq -r '.retry.attempt' | \
    sort | uniq -c
done
```

### Question: Which task classes fail most?

```bash
grep -rl '"validation": {"passed": false}' eval/traces/*/ | \
  xargs jq -r '.classification.task_class' | \
  sort | uniq -c | sort -rn
```

### Question: Are prompts getting longer over time?

```bash
find eval/traces -name trace.json | \
  xargs jq -r '.timestamp + " " + (.prompt.word_count | tostring)' | \
  sort
```

All of these are `find`/`grep`/`jq` one-liners. No custom tools needed.

---

## 6. Config Snapshot Tracking

Each trace records `config_snapshot` with git SHA of config files. This means:

- You can always reproduce a trace by checking out the config SHA
- You can group traces by config version to see the effect of a change
- You can diff two config versions to understand what changed

```bash
# See all traces for a specific config version
grep -rl '"lanes_sha": "a0be591"' eval/traces/*/
```

---

## 7. Integration with Eval

The eval runner (`scripts/eval.sh`) produces traces for end-to-end benchmarks. These traces go in the same directory structure, making them directly comparable to production dispatch traces.

When running `--compare baseline`, the compare script:
1. Groups traces by benchmark task ID
2. Compares success, latency, retry count
3. Flags regressions > 5%
4. Produces a comparison report

---

## 8. Later Extensions (Not Now)

- **Frontier tracking**: When we have enough traces, track Pareto frontier of (cost, success_rate) over time
- **Candidate comparison**: Store traces from candidate harness versions alongside baseline
- **Automatic scoring**: For classification/routing benchmarks, scoring is automatic. For e2e, still manual.
- **SQLite aggregation**: If `find`/`jq` becomes too slow (hundreds of traces), migrate to SQLite with a read-only view
