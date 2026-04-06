# Refactor Plan: Ranked Recommendations

> Concrete changes to make OneShot a stronger meta-harness.

---

## Decision Framework

Each recommendation is evaluated against:

- **Impact**: How much does this improve harness performance/inspectability/evaluability?
- **Risk**: How likely is this to break existing workflows?
- **Effort**: How much work to implement?
- **Identity**: Does this preserve or erode the repo's distinct character?

Categories:
- **Must do now**: High impact, low-medium risk, justifies immediate implementation
- **Should do next**: High impact, requires more thought or depends on must-do items
- **Later**: Valuable but not urgent
- **Probably not worth doing**: Interesting but low leverage or high risk

---

## Must Do Now

### 1. Add trace substrate to dispatch runner

**What**: Modify `core/dispatch/run.py` to write trace.json, prompt.md, and output.raw for every dispatch.

**Why**: Without traces, we cannot measure anything. This is the prerequisite for all empirical improvement.

**Impact**: HIGH — enables all future optimization
**Risk**: LOW — additive, doesn't change existing behavior
**Effort**: MEDIUM — ~100 lines of Python

**Files to create/modify**:
- Modify: `core/dispatch/run.py` — add `write_trace()` function, call it from `dispatch_single()`
- Create: `eval/traces/.gitkeep`
- Create: `eval/traces/` directory structure

**Specific changes**:
- `dispatch_single()` already collects all needed data (worker, exit_code, duration, errors, usage)
- Add a `trace_dir` parameter (default: `eval/traces/{date}/`)
- Write `trace.json` with the schema from `trace_architecture.md`
- Write `prompt.md` with the actual prompt text
- Write `output.raw` by copying the raw output file
- Existing `write_manifest()` continues to work (it's the derived human-readable summary)

---

### 2. Add classification and routing benchmarks

**What**: Create the first benchmark sets and eval runner.

**Why**: Without benchmarks, we cannot detect regressions. Classification accuracy is the highest-leverage metric to track.

**Impact**: HIGH — enables regression detection and informed tuning
**Risk**: LOW — additive only
**Effort**: MEDIUM — ~20 benchmark tasks + eval runner script

**Files to create**:
- `eval/benchmarks/classification/search/` — 20 tasks
- `eval/benchmarks/classification/validation/` — 10 tasks
- `eval/benchmarks/classification/holdout/` — 10 tasks
- `eval/benchmarks/routing/` — 10 tasks
- `eval/results/.gitkeep`
- `scripts/eval.sh` — top-level runner
- `eval/scripts/run_classification.py` — classification accuracy checker
- `eval/scripts/run_routing.py` — routing correctness checker
- `eval/scripts/run_config_check.py` — cross-validation

---

### 3. Add config consistency validation

**What**: Add a Python script that cross-validates all YAML configs against Python enums and each other.

**Why**: Hidden coupling (TaskClass ↔ LANE_ASSIGNMENTS, worker names across configs) is a real drift risk. One automated check catches it all.

**Impact**: MEDIUM — prevents silent breakage
**Risk**: LOW — read-only validation
**Effort**: LOW — ~80 lines

**Files to create**:
- `eval/scripts/run_config_check.py`

**What it checks**:
1. Every TaskClass in the Python enum has an entry in LANE_ASSIGNMENTS
2. Every LANE_ASSIGNMENTS lane exists in lanes.yaml
3. Every worker in lane worker_pools exists in workers.yaml
4. Every category_preference key matches a TaskCategory enum value
5. Every model in models.yaml has a lane that exists in lanes.yaml
6. workers.yaml glm entry has plan_expires

---

### 4. Consolidate instruction sources

**What**: Make `.claude/rules/*.md` files thin wrappers that point to `docs/instructions/*.md`. Remove duplicated content from rules files.

**Why**: Currently, behavior is defined in both `docs/instructions/core.md` AND `.claude/rules/core.md` (which says "See @docs/instructions/core.md"). But some rules files (khamel-mode.md, codex.md, community.md) have substantial unique content. The thin-wrapper pattern is right but inconsistently applied.

**Impact**: MEDIUM — reduces instruction sprawl, makes single source of truth actually true
**Risk**: MEDIUM — could break progressive disclosure if done wrong
**Effort**: MEDIUM

**Specific approach**:
- Rules files that are pure references (core.md, delegation.md, service.md, web.md, cli.md) are already correct
- Rules files with unique content (khamel-mode.md, codex.md, community.md) keep their content
- Add a validation check: every rule referenced in CLAUDE.md should exist
- No content moves between docs/instructions/ and .claude/rules/ — just enforce the DRY boundary

**Files to modify**:
- `.claude/rules/core.md` — already a reference, keep
- `.claude/rules/delegation.md` — already a reference, keep
- `scripts/validate-docs.sh` — add rule-file validation

---

## Should Do Next

### 5. Make worker preference empirical

**What**: Add a trace aggregation script that computes per-worker success rates by category. Use this to inform (not override) category_preference in lanes.yaml.

**Why**: Right now, "codex is best for coding" is an assumption. With traces, it becomes measurable.

**Impact**: HIGH — this is the core optimization loop
**Risk**: LOW — advisory, doesn't change routing automatically
**Effort**: MEDIUM — needs trace data first

**Depends on**: #1 (trace substrate)

**Files to create**:
- `eval/scripts/worker_stats.py` — aggregates traces into per-worker stats
- `eval/scripts/suggest_preferences.py` — compares actual stats vs current preferences

---

### 6. Add prompt versioning

**What**: Track prompt template versions. When the dispatch template changes, increment the version. Traces record which version was used.

**Why**: Prompt construction is the #3 leverage point. Without versioning, you can't attribute changes in worker output to prompt changes.

**Impact**: MEDIUM — enables prompt optimization
**Risk**: LOW — additive metadata
**Effort**: LOW — ~20 lines

**Depends on**: #1 (trace substrate)

**Specific changes**:
- Add `"prompt": {"template": "dispatch_v1"}` to trace.json (already in schema)
- When dispatch template changes, bump to `dispatch_v2`
- The prompt.md file is the full rendered prompt — that's the versioned artifact

---

### 7. Add eval to CI

**What**: Run classification, routing, and config validation in GitHub Actions on every PR.

**Why**: Prevents regressions in harness behavior.

**Impact**: MEDIUM — safety net for all future changes
**Risk**: LOW — fast tests, non-blocking initially
**Effort**: LOW — adapt existing CI workflow

**Depends on**: #2 (benchmarks), #3 (config validation)

**Files to modify**:
- `.github/workflows/ci.yml` — add eval step

---

### 8. Extract prompt template from Markdown into code

**What**: Move the dispatch prompt template from `_shared/dispatch.md` Step 2 into a Python function that generates it. The Markdown still documents the template but isn't the source of truth.

**Why**: Currently, the prompt is constructed by Claude reading Markdown instructions and following them. This means prompt quality varies between sessions. A code-generated prompt is consistent and measurable.

**Impact**: HIGH — #3 leverage point
**Risk**: MEDIUM — changes how dispatch works
**Effort**: HIGH — requires careful template design

**Depends on**: #1 (trace substrate), #6 (prompt versioning)

**Files to create**:
- `core/dispatch/prompt_builder.py` — builds prompts from structured input

---

## Later

### 9. Risk inference improvement

**What**: Use trace data to refine risk keywords. Find false positives (medium-risk tasks classified as high) and false negatives (high-risk tasks classified as medium).

**Depends on**: Traces with scoring data.

### 10. AGENTS.md auto-generation

**What**: Script that reads config/ and docs/ and generates AGENTS.md. Eliminates hand-maintained summary.

**Depends on**: #3 (config validation), #4 (instruction consolidation).

### 11. SQLite aggregation for traces

**What**: If trace count exceeds ~500, add a SQLite DB with read-only views.

**Depends on**: Enough traces to justify it.

---

## Probably Not Worth Doing

### X. Generic framework extraction

This repo is opinionated and personal. Abstracting it into a framework would destroy its character without adding value. Reject.

### X. Web UI for traces

The whole point is grep/cat/find/jq. A web UI adds complexity without adding power. Reject.

### X. Database for config/state

YAML files are the right tool. SQLite for trace aggregation only if needed (later). Reject for config.

### X. Dynamic lane assignment

The current static mapping (task_class → lane) is simple and works. Making it dynamic adds complexity without clear benefit unless we have strong evidence from traces that different classes need different lanes. Defer.

---

## Migration Risk Summary

| Change | Breaking? | Rollback |
|--------|-----------|----------|
| #1 Trace substrate | No | Delete eval/traces/ |
| #2 Benchmarks | No | Delete eval/benchmarks/ |
| #3 Config validation | No | Delete eval/scripts/ |
| #4 Instruction consolidation | Potentially | Git revert |
| #5 Empirical preferences | No | Delete eval/scripts/worker_stats.py |
| #6 Prompt versioning | No | Remove template field |
| #7 Eval in CI | No | Remove CI step |
| #8 Prompt builder | Yes | Restore Markdown-only dispatch |

---

## Essential Identity vs Historical Accident

### Essential (preserve)

- Claude-first planning
- Lane-based routing with task classes
- Category-based worker preference
- Filesystem-native inspectability
- Progressive disclosure
- Self-contained dispatch prompts
- Risk-based autonomy gating
- The operator taxonomy (short/full/conduct)
- Config-driven policy (YAML)
- SOPS/Age secrets management

### Historical Accident (can change)

- Specific keyword lists in infer_category/infer_risk
- Hardcoded LANE_ASSIGNMENTS (could move to config)
- Worker preference orderings (should become empirical)
- The `1shot/` directory name
- The `.beads/` directory (deprecated, still in tree)
- Session archives in `docs/sessions/` (encrypted, not practically useful)
