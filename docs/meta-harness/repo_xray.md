# Repo X-Ray: OneShot as a Harness

> Generated 2026-04-05. Concrete map of how this repo works as an LLM harness.

---

## 1. Harness Architecture Map

### The Control Flow

```
User invokes /short, /full, or /conduct
    |
    v
Skill prompt loaded from .claude/skills/{operator}/SKILL.md
    |
    v
Intake: detect providers, ask questions, write 1shot/PROJECT.md
    |
    v
Plan: explore codebase, write ROADMAP.md, create TaskCreate per deliverable
    |
    v
Build Loop:
    |
    +-- Pick next unblocked task
    +-- Classify: task_class (TaskClass enum) + category (TaskCategory enum)
    +-- Resolve: python -m core.router.resolve --class X --category Y
    |       returns: {lane, workers[], review_with, search_backend, fallback_lane, risk}
    +-- If lane == premium: Claude handles inline (no dispatch)
    +-- Else: build self-contained prompt → dispatch to worker
    |       python -m core.dispatch.run --class X --category Y --prompt "..."
    +-- Capture output (JSONL for codex, JSON for gemini)
    +-- Validate against acceptance criteria
    +-- Write manifest to 1shot/dispatch/{id}.md
    +-- Commit or retry
    |
    v
Verify: tests, lint, acceptance criteria, diff-vs-plan
    |
    v
Challenge (conduct only): adversarial review by codex
    |
    v
Session-end learning: write to docs/instructions/learned/ if patterns repeat
```

### Subsystems

| Subsystem | Code Location | Config Location | Doc Location |
|-----------|---------------|-----------------|-------------|
| Task classification | `core/task_schema.py` | N/A (Python enums) | `docs/instructions/task-classes.md` |
| Lane routing | `core/router/lane_policy.py` | `config/lanes.yaml` | `docs/instructions/task-classes.md` |
| Category preference | `core/router/lane_policy.py:reorder_by_preference()` | `config/lanes.yaml:[lane].category_preference` | `.claude/skills/_shared/providers.md` |
| Worker selection | `core/dispatch/run.py:worker_available()` | `config/workers.yaml`, `config/models.yaml` | `.claude/skills/_shared/providers.md` |
| Risk gating | `core/task_schema.py:infer_risk()` | N/A (keyword lists) | `docs/instructions/task-classes.md` |
| Dispatch execution | `core/dispatch/run.py:dispatch_single()` | N/A | `.claude/skills/_shared/dispatch.md` |
| Output parsing | `core/dispatch/run.py:parse_*_output()` | N/A | `.claude/skills/_shared/dispatch.md` |
| Manifest generation | `core/dispatch/run.py:write_manifest()` | N/A | `.claude/skills/_shared/dispatch.md` |
| Search (Argus) | `core/search/argus_client.py` | `config/search.yaml` | `docs/instructions/search.md` |
| Plan schema | `core/plan_schema.py` | N/A | `.claude/skills/conduct/SKILL.md` |
| Retry/escalation | `.claude/skills/_shared/dispatch.md` Step 7 | `config/lanes.yaml:fallback_lane` | Same |
| Session learning | Operator skill prompt (Phase 5) | N/A | `docs/instructions/workflow.md` |

---

## 2. All Behavior Surfaces

### Where Behavior Is Encoded

| Medium | Files | Character |
|--------|-------|-----------|
| **Python code** | `core/task_schema.py`, `core/router/lane_policy.py`, `core/dispatch/run.py`, `core/search/argus_client.py`, `core/plan_schema.py`, `core/router/model_registry.py`, `core/router/resolve.py` | Machine-executable, testable |
| **YAML config** | `config/lanes.yaml`, `config/workers.yaml`, `config/models.yaml`, `config/search.yaml`, `config/providers.yaml` | Machine-readable policy |
| **Skill prompts (Markdown)** | `.claude/skills/conduct/SKILL.md`, `.claude/skills/full/SKILL.md`, `.claude/skills/short/SKILL.md`, `.claude/skills/_shared/dispatch.md`, `.claude/skills/_shared/providers.md`, + 7 utility skills | Instructs Claude's behavior in-session |
| **Rules (Markdown)** | `.claude/rules/core.md`, `khamel-mode.md`, `delegation.md`, etc. | Claude Code progressive disclosure |
| **Instructions (Markdown)** | `docs/instructions/core.md`, `coding.md`, `workflow.md`, `search.md`, `review.md`, `oneshot.md`, `task-classes.md` | Neutral source of truth, referenced by rules |
| **CL Templates** | `templates/AGENTS.md.j2`, `templates/CLAUDE.md.j2` | Project bootstrapping |
| **Shell scripts** | `scripts/ci.sh`, `scripts/validate-skills.sh`, `scripts/validate-docs.sh`, `scripts/check-*.sh`, + others | Operational glue |
| **Bats tests** | `tests/test_workflow.bats`, `tests/test_oneshot.bats` | E2E validation |

### Specific Behavior Surfaces

1. **Task classification**: `infer_category()` keywords + `infer_risk()` keywords (Python)
2. **Lane assignment**: `LANE_ASSIGNMENTS` dict (Python, hardcoded)
3. **Worker ordering**: `category_preference` per lane (YAML) + `reorder_by_preference()` (Python)
4. **Worker availability**: `worker_available()` checks CLIs + env vars + vault + plan expiry (Python)
5. **Prompt construction**: Template in `_shared/dispatch.md` Step 2 (Markdown, human-interpreted)
6. **Retry logic**: 3 attempts, lane escalation, circuit breaker (Markdown, enforced by Claude)
7. **Review gate**: Per-task-class `review_with` from lane config (YAML → Python → Markdown)
8. **Verification checklist**: Per-operator in skill prompts (Markdown)
9. **Scope creep detection**: `conduct/SKILL.md` Phase 2 Step 5 (Markdown, git diff vs plan)
10. **Session learning**: `conduct/SKILL.md` Phase 5, `workflow.md` (Markdown)
11. **Quality gate**: 75% consensus threshold (`providers.md`) (Markdown, advisory)
12. **Auto-approved actions**: Per-skill lists in each SKILL.md (Markdown)
13. **Decision defaults**: Per-skill tables in each SKILL.md + `AGENTS.md` (Markdown)
14. **Progressive disclosure**: `.claude/rules/README.md` detection logic → loads different rule subsets (Markdown)
15. **Terminal entry points**: Shell functions `shot`, `zai`, `or` defined in user's `.bashrc` (outside repo)

---

## 3. Ranked Leverage Points

Where changes would most affect system performance:

### Tier 1: High Leverage

| # | Point | Why | Current Gap |
|---|-------|-----|-------------|
| 1 | **Task classification accuracy** | Wrong classification → wrong lane → wrong worker → wasted cost + latency | `infer_category()` is pure keyword match, no learning from outcomes |
| 2 | **Worker selection empirical data** | Static preference order ignores actual success rates per worker per category | No trace data exists to build evidence on |
| 3 | **Prompt construction quality** | Self-contained prompts are the #1 determinant of worker output quality | Template exists only as Markdown instructions, never versioned or measured |
| 4 | **Instruction sprawl reduction** | Same behavior defined in 5+ places (rules, instructions, skills, AGENTS.md, conduct SKILL.md) | Any change requires updating all copies; drift is inevitable |
| 5 | **Trace/archive substrate** | Without raw traces, optimization is guesswork | Zero traces exist today |

### Tier 2: Medium Leverage

| # | Point | Why |
|---|-------|-----|
| 6 | Risk inference improvement | Keyword-based risk misses nuance; too many false positives/negatives |
| 7 | Config validation | lanes.yaml/workers.yaml can become inconsistent without detection |
| 8 | Eval framework | No way to know if changes improve or regress harness behavior |
| 9 | Skill prompt versioning | Skill prompts evolve without tracking what changed or why |

### Tier 3: Lower Leverage

| # | Point | Why |
|---|-------|-----|
| 10 | CI pipeline improvements | Already functional, not a bottleneck |
| 11 | OpenCode adapter | Experimental, low usage |
| 12 | Community starter template | Mature, not changing frequently |

---

## 4. Failure Modes, Drift Risks, and Hidden Couplings

### Failure Modes

| Failure | Detection | Current Mitigation |
|---------|-----------|-------------------|
| Worker unavailable when dispatched | `worker_available()` check before dispatch | Falls through to first pool entry if all unavailable |
| Dispatch timeout (300s hard cap) | `subprocess.TimeoutExpired` | No retry with adjusted prompt or different worker |
| ZAI plan expiry breaks GLM workers | `_zai_plan_active()` date check | Date is manually maintained in workers.yaml |
| Keyword classification misses edge cases | None (silent misclassification) | No feedback loop |
| Instruction drift across copies | `validate-docs.sh` catches some stale refs | Only checks counts and paths, not behavioral consistency |
| Circuit breaker on transient failures | 3 failures → skip | Network blips or auth hiccups counted same as real failures |
| Dispatch prompt too long for cheap model | None | No length check before dispatch |

### Drift Risks

1. **Instructions vs rules duplication**: `docs/instructions/core.md` and `.claude/rules/core.md` have the same content with "See @" references. The thin-rule layer adds indirection but risks the two drifting apart.
2. **Skill prompt vs dispatch protocol**: `_shared/dispatch.md` defines the protocol, but each operator skill (conduct, full, short) re-describes parts of it differently.
3. **AGENTS.md as compiled output**: AGENTS.md is a summary that must be kept in sync with underlying config. Currently hand-maintained.
4. **Config consistency**: lanes.yaml references workers that may not exist in workers.yaml. No cross-validation.

### Hidden Couplings

1. **TaskClass enum ↔ LANE_ASSIGNMENTS dict**: Adding a new TaskClass requires updating both the enum AND the dict. No validation.
2. **TaskClass ↔ task-classes.md**: The doc table must match the Python enums. No automated check.
3. **category_preference keys ↔ TaskCategory enum**: YAML keys must match enum values. No validation.
4. **dispatch.md worker commands ↔ core/dispatch/run.py**: The Markdown examples must match the actual command builders. Drift likely.
5. **Worker names across configs**: `codex`, `gemini_cli`, `glm_claude`, `claw_code` must be consistent across lanes.yaml, workers.yaml, and dispatch.py.

---

## 5. What Is Essential (Preserve)

These feel like core identity, not historical accident:

1. **Claude-first planning** — Claude is the orchestrator. Workers execute. This is the right architecture for this repo.
2. **Lane-based routing with task classes** — The classification→lane→worker pipeline is sound. The specific lanes/classes may evolve but the pattern is core.
3. **Instruction-driven behavior** — Skills and rules as the primary behavior mechanism, not opaque code. This is the right meta-harness approach.
4. **Filesystem-native inspectability** — grep/cat/find/jq as the primary interface. No custom UI. This is a real differentiator.
5. **Progressive disclosure** — Loading instructions based on project type. Saves tokens, keeps context relevant.
6. **Dispatch protocol with manifests** — Every dispatched task produces a trace. The current implementation is thin but the pattern is right.
7. **Category-based worker preference** — Research tasks go to different workers than coding tasks. Empirically correct.
8. **Risk-based autonomy gating** — High-risk tasks require approval. Low-risk tasks don't. Good operator experience.
9. **Self-contained prompts** — Workers get everything they need. No back-references. Right for CLI-based workers.
10. **The operator taxonomy (short/full/conduct)** — Three modes of engagement. Matches how work actually varies in scope and formality.

### What Is Historical Accident (Could Change)

1. **Specific keyword lists in infer_category/infer_risk** — Could become evidence-based rather than hand-authored
2. **Hardcoded LANE_ASSIGNMENTS** — Could become configurable
3. **Worker preference orderings** — Should become empirical, not assumed
4. **The `1shot/` directory name** — Fine, but no strong identity
5. **Specific test suite (bats)** — Works but could be anything
6. **OpenCode adapter** — Experimental, not core

---

## 6. One-Liner Summary

OneShot is a Markdown-driven orchestration harness with a small Python routing core, YAML policy, and CLI-based worker dispatch. Its strengths are clear architecture (plan→classify→route→dispatch→verify), filesystem-native traces, and opinionated defaults. Its weaknesses are: no empirical feedback loop, instruction sprawl across too many files, no evidence-based routing optimization, and zero trace data to learn from.
