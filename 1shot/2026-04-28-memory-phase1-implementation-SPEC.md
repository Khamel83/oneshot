# OneShot Memory Phase 1 Implementation Spec

## Purpose
Translate the repo-first memory architecture into a build contract for the first implementation pass.

Phase 1 should deliver:
- a standard repo-local memory scaffold
- a per-repo memory policy document
- deterministic write targets for the first four memory categories
- same-repo retrieval behavior
- a minimal cross-repo abstraction contract
- a degraded-mode contract for the central index

This is still design/spec work. It defines what implementation must build next.

## Scope

### In Scope
- repo-local folder and file schema
- `MEMORY_POLICY.md` format
- promotion rules for:
  - decisions
  - session summaries
  - runbooks
  - blockers/resolutions
- same-repo retrieval contract
- cross-repo abstraction contract
- central index responsibility boundary
- degraded-mode behavior

### Out of Scope
- protocol/provider wiring
- UI work
- personal/private memory system
- advanced reconciliation workflows
- full cross-repo raw memory replay

## Phase 1 Deliverables

### Repo-local files
Every onboarded repo should have:

```text
docs/agents/
  MEMORY_POLICY.md
  DECISIONS.md
  BLOCKERS.md
  RUNBOOKS.md
  CONTEXT.md

.oneshot/
  sessions/
  checkpoints/
  conflicts/
  provenance/
  abstractions/
  index/
```

### OneShot responsibilities
OneShot must be able to:
- scaffold the above structure
- detect whether the structure already exists
- append/promote memory into the correct targets
- preserve provenance for every promoted item
- retrieve same-repo memory deterministically
- export abstractions to the private cross-repo layer

## File Contracts

### `docs/agents/MEMORY_POLICY.md`
Canonical repo memory policy.

Required fields:

```md
# Memory Policy

- mode: portable | isolated | sensitive | private
- owner: repo
- commit_stable_memory: true | false
- allow_cross_repo_abstractions: true | false
- allow_raw_cross_repo_retrieval: false | true
- secrets_policy: never-store
- summary_cadence: checkpoint-and-session-end
- review_gate: normal | high-risk-quorum
```

Required semantics:
- `mode` controls default retrieval boundaries
- `owner` is always `repo` in phase 1
- `allow_raw_cross_repo_retrieval` should default to `false`
- `secrets_policy` should always be `never-store` in phase 1

### `docs/agents/DECISIONS.md`
Durable decisions only.

Entry contract:

```md
## 2026-04-28 - Short decision title
- status: active | superseded
- source: claude | codex | gemini | opencode | mixed
- provenance: .oneshot/provenance/<id>.md
- summary: one-paragraph durable statement
- rationale: why this decision exists
- supersedes: optional prior decision reference
```

### `docs/agents/BLOCKERS.md`
Active blockers and resolved lessons worth preserving.

Entry contract:

```md
## 2026-04-28 - Short blocker title
- status: active | resolved
- source: <tool-or-session>
- provenance: .oneshot/provenance/<id>.md
- blocker: what is blocked
- resolution: blank if active, required if resolved
- follow_up: optional
```

### `docs/agents/RUNBOOKS.md`
Important commands and operational procedures, not raw command dumps.

Entry contract:

```md
## Runbook: <short name>
- status: active
- source: <tool-or-session>
- provenance: .oneshot/provenance/<id>.md

### When to use
<short description>

### Command / procedure
```bash
<command(s)>
```

### Notes
<constraints, warnings, expected output>
```

### `docs/agents/CONTEXT.md`
Optional stable architecture/domain summary.

Phase 1 rule:
- scaffold it
- do not require aggressive auto-population
- allow manual or promoted summaries later

## Operational Layer Contracts

### `.oneshot/sessions/`
- end-of-session summaries
- one file per session or run
- may be local-only

Suggested file naming:
- `<date>-<session-id>.md`

### `.oneshot/checkpoints/`
- in-flight checkpoint summaries
- one file per checkpoint event

### `.oneshot/provenance/`
- provenance records for promoted durable memory
- required for any promoted item in `docs/agents/`

Suggested contract:

```md
# Provenance
- id: <unique-id>
- created_at: <iso8601>
- repo: <repo-id>
- source_tool: <tool>
- source_session: <session-id>
- source_type: checkpoint | session | review | manual-promotion
- confidence: low | medium | high
- notes: optional
```

### `.oneshot/conflicts/`
- holds contradictory durable memory records
- do not auto-resolve in phase 1

### `.oneshot/abstractions/`
- cross-repo abstraction drafts and promoted lessons

Suggested abstraction contract:

```md
# Abstraction
- id: <unique-id>
- source_repo: <repo-id>
- trust: low | medium | high
- sensitivity: portable | isolated | sensitive | private
- category: tooling | infra | orchestration | debugging | runbook | governance
- promotes_from: <provenance-id or source file>

## Lesson
<abstracted reusable lesson>

## Non-portable details removed
<short note>
```

### `.oneshot/index/`
- local manifests and retrieval support state
- should not be treated as canonical project memory

## Promotion Rules

### Rule 1: Promote only into the right destination
- decisions -> `docs/agents/DECISIONS.md`
- blockers/resolutions -> `docs/agents/BLOCKERS.md`
- runbooks -> `docs/agents/RUNBOOKS.md`
- session summaries -> `.oneshot/sessions/` by default

### Rule 2: Session summaries are not durable by default
- they are captured automatically
- they become durable only when promoted into another category or intentionally curated

### Rule 3: Every promoted item needs provenance
- no provenance, no promotion

### Rule 4: Never store secrets
- if a source contains a secret, redact before any write
- phase 1 should fail safe: omit unsafe content rather than risk storing it

### Rule 5: Conflicts stay visible
- contradictory promoted items are preserved
- retrieval must surface conflict markers instead of choosing silently

## Retrieval Contract

### Same-repo retrieval
Given a repo query, phase 1 retrieval should search in this order:
1. `docs/agents/DECISIONS.md`
2. `docs/agents/BLOCKERS.md`
3. `docs/agents/RUNBOOKS.md`
4. `docs/agents/CONTEXT.md`
5. `.oneshot/` operational memory

Expected behavior:
- stable memory outranks operational memory
- conflicted entries are returned with conflict markers
- superseded decisions should be visible but ranked below active ones

### Cross-repo retrieval
Phase 1 should not retrieve raw foreign repo memory by default.

Allowed default path:
1. query the private abstraction pool
2. filter by repo policy and sensitivity
3. return abstracted lessons only

Raw foreign memory should require explicit escalation and is not required for phase 1.

## Central Index Contract

### Phase 1 role
The private index may:
- index repo-local durable memory
- index promoted abstractions
- support search across repos

The private index may not:
- become the only copy of project memory
- override repo-local truth
- return private/no-cross-repo content into general cross-repo queries

## Degraded-Mode Contract

If the central index is unavailable:
- same-repo retrieval must still work from repo-local files
- promotion into repo-local memory must still work
- cross-repo abstractions may be unavailable
- the system must report degraded mode explicitly instead of failing silently

Phase 1 success requires repo-local usefulness even when the external search layer is down.

## Onboarding Contract

For a repo with no memory yet, phase 1 implementation should:
- create the standard scaffold
- generate a default `MEMORY_POLICY.md`
- create empty stable memory files with short headers
- avoid inventing history
- optionally infer a minimal `CONTEXT.md` stub from repo files later, but not block on it

## Acceptance Criteria For The First Coding Pass
- a repo can be scaffolded automatically
- the first four memory categories have deterministic write targets
- every promoted entry gets provenance
- same-repo retrieval follows the specified ranking order
- cross-repo retrieval defaults to abstractions only
- the system behaves safely when the central index is unavailable
- the design works for OneShot itself and for downstream customer repos
