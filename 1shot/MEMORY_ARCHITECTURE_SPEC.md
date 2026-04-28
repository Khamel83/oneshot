# OneShot Memory Architecture Spec

## Purpose
Design a repo-first memory system for OneShot that supports Claude Code, OpenCode, Gemini, Codex, and related tools while preserving project boundaries and keeping work memory with the target repo.

## Design Principles
- Repo-first ownership: the target repo owns its durable working memory.
- OneShot as orchestrator: OneShot captures, indexes, retrieves, and reviews memory, but does not become the primary home of project knowledge.
- Human + machine split: stable knowledge should be readable by humans; transient and operational memory can stay machine-oriented.
- Abstracted cross-repo reuse: cross-project learning should prefer distilled lessons over raw foreign notes.
- Provenance over certainty: conflicting memory is preserved and surfaced instead of silently collapsed.
- Graceful degradation: repo-local memory remains useful if the central index is down.

## Audience Split

### OneShot Internal Responsibilities
OneShot itself is responsible for:
- defining the repo memory contract
- writing and promoting memory according to policy
- maintaining provenance and conflict metadata
- indexing repo-local memory into the private search layer
- enforcing retrieval order and review gates
- degrading safely when the external index is unavailable

### Customer Repo Responsibilities
Each customer repo is responsible for:
- storing durable project memory locally
- declaring its memory policy mode
- exposing stable, readable memory documents for both humans and agents
- allowing OneShot to maintain the operational `.oneshot/` layer alongside the repo’s working files

This split keeps OneShot product logic centralized while leaving project truth with the project.

## Ownership Model

### Default
- Memory is enabled by default.
- Each target repo declares a per-repo memory mode.
- Single-user assumptions apply to this design.

### Hard Exclusions
- Personal/legal systems such as divorce-related work are outside this memory fabric.
- Secrets and credentials must never be treated as normal shared engineering memory.

## Storage Topology

### Repo-Local Canonical Layer: `docs/agents/`
This is the durable, human-readable layer.

Use it for:
- decisions
- blockers and resolutions
- important commands and operational runbooks
- curated architecture/context summaries
- promoted reusable lessons

Properties:
- committed to git by default
- safe to read cold by an agent or a human
- treated as the highest-trust memory source inside a repo

### Repo-Local Operational Layer: `.oneshot/`
This is the machine-facing support layer.

Use it for:
- session summaries
- checkpoint summaries
- provenance records
- conflict records
- abstraction drafts
- retrieval metadata
- local manifests and indexes
- transient state

Properties:
- mixed commit policy
- optimized for OneShot and tool orchestration
- can contain local-only state that is not meant to be canonical project knowledge

### External Private Index Layer
Hosted within homelab, OCI, and Tailscale boundaries.

Role:
- index repo-local memory across projects
- support search and cross-repo abstraction retrieval
- provide secondary retrieval services

Non-role:
- it is not the source of truth
- it must not become the only place memory exists

## Initial First-Class Memory Categories
V1 should explicitly support:
- decisions
- session summaries
- important commands and runbooks
- blockers and resolutions

Later candidates:
- glossary/domain language
- architecture summaries
- open questions
- review findings

## Memory Lifecycle

### States
- captured: raw signal or observation exists
- summarized: compressed into session/checkpoint form
- promoted: elevated into durable repo memory
- conflicted: contradictory durable entries coexist
- superseded: a newer durable entry replaces prior guidance without deleting history
- archived: retained for history, excluded from normal retrieval

### Capture Cadence
- checkpoint-based capture during meaningful progress boundaries
- end-of-session summaries
- extra summarization only for unusually large sessions

This avoids trying to make continuous raw capture equal to durable truth.

## Write Policy

### Default
- broad automatic signal capture is allowed
- any supported tool may contribute signals

### Requirement
Every durable write must preserve provenance:
- source tool
- source session or run
- timestamp
- status/confidence when available

### Rationale
Historical trace is more valuable than premature cleanup. The system should store enough information to reconstruct how a memory arrived, even when it later proves incomplete or wrong.

## Conflict Policy
- Never silently overwrite conflicting durable memory.
- Preserve both sides with provenance.
- Mark the memory as conflicted.
- Surface the conflict during retrieval.

This prefers transparent ambiguity over false certainty.

## Per-Repo Policy Modes
Each repo should declare one of these modes:
- portable
- isolated
- sensitive
- private/no-cross-repo

### Intended Behavior
- portable: eligible for cross-repo abstractions
- isolated: same-repo retrieval only unless explicitly escalated
- sensitive: tighter promotion and retrieval defaults
- private/no-cross-repo: excluded from the cross-repo layer entirely

## Retrieval Model

### Same-Repo Retrieval Order
1. `docs/agents/` canonical memory
2. `.oneshot/` operational memory
3. local conflict/supersession indicators

### Cross-Repo Retrieval Order
1. abstracted cross-repo lessons
2. same-topic portable patterns with trust/sensitivity tags
3. raw foreign repo memory only by explicit escalation

### Portable By Default
- tooling patterns
- infra and network patterns
- orchestration patterns
- debugging lessons
- runbook patterns
- review and governance lessons

### Not Portable By Default
- repo-specific business logic
- product-bound architecture decisions
- unresolved local findings
- raw session notes
- repo-bound assumptions

## Cross-Repo Abstraction Pool
- Maintain one global private abstraction pool.
- Tag entries by trust and sensitivity.
- Prefer abstraction over direct replay of raw repo-local memory.

This gives broad learning without turning every repo into every other repo.

## Commit Policy

### Commit by Default
Inside `docs/agents/`:
- decisions
- blockers and resolutions
- runbooks
- curated stable summaries

### Usually Local / Uncommitted
Inside `.oneshot/`:
- raw session summaries
- checkpoint scratch state
- retrieval caches
- machine indexes
- unresolved conflict work state

### Selective Promotion
Some `.oneshot/` artifacts can be promoted and committed if they become stable, curated repo knowledge.

## Review Governance

### Default Rule
Normal work does not require full cross-model quorum review.

### High-Risk Rule
Use planner plus cross-model quorum for high-risk work only.

High-risk classes include:
- infra or config changes
- security or privacy changes
- cross-repo changes
- lasting architecture changes
- destructive or migration-heavy code changes

Normal work should use planner review plus ordinary verification.

## New Repo Onboarding
For a repo with no memory yet:
- generate the standard scaffold automatically
- infer initial context from existing repo files where possible
- start with empty history but structured memory locations

This avoids blocking adoption on manual setup.

## Failure and Degraded Mode
If the external index is unavailable:
- same-repo memory still works from repo-local files
- no repo loses its durable truth
- cross-repo retrieval may degrade, but project-local operation should remain intact

This is mandatory for trust.

## Recommended Initial Folder Responsibility Split

### `docs/agents/`
- long-lived repo memory
- stable operator guidance
- durable human-readable knowledge

### `.oneshot/`
- orchestration state
- machine-oriented session memory
- conflict and provenance records
- retrieval support files

## Recommended Repo Layout v1

### Stable committed layer
```text
docs/agents/
  MEMORY_POLICY.md
  DECISIONS.md
  BLOCKERS.md
  RUNBOOKS.md
  CONTEXT.md
```

Suggested responsibilities:
- `MEMORY_POLICY.md`: repo mode, portability, sensitivity, and commit rules
- `DECISIONS.md`: durable decisions and supersessions
- `BLOCKERS.md`: active blockers plus resolved lessons worth keeping
- `RUNBOOKS.md`: important commands and operational procedures
- `CONTEXT.md`: optional stable architecture/domain summary once the first four categories are working well

### Operational layer
```text
.oneshot/
  sessions/
  checkpoints/
  conflicts/
  provenance/
  abstractions/
  index/
```

Suggested responsibilities:
- `sessions/`: end-of-session summaries and large-session compressions
- `checkpoints/`: in-flight summaries at meaningful milestones
- `conflicts/`: contradictory memory entries kept side by side
- `provenance/`: source-tool and source-session records
- `abstractions/`: drafts and promoted cross-repo lessons
- `index/`: local manifests and retrieval support artifacts

This layout is a recommendation, not yet a locked schema. The goal is to standardize the memory shape without overcommitting to implementation details before retrieval behavior is built.

## OneShot Productization Requirements
To make this work for downstream customer repos, OneShot needs to provide:
- a standard scaffold generator
- a policy-mode declaration mechanism
- a stable promotion format for first-class memory categories
- retrieval rules that behave the same across repos
- a central index that can be enabled without becoming the only copy of memory
- migration-safe defaults so customer repos can adopt incrementally

## Non-Goals For V1
- full personal-memory system
- UI/dashboard work
- provider-specific protocol wiring
- centralized memory replacing repo-local truth

## Success Conditions
The memory architecture is working when:
- target repos own their own durable memory cleanly
- cross-repo retrieval produces useful abstractions without contamination
- stale or conflicting memory is visible instead of silently trusted
- the central index improves recall without becoming a dependency for basic operation
- important work gets stronger review without making every task heavyweight
