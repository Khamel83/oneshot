# Project: OneShot Repo-First Memory Architecture

## Goal
Design a real memory architecture for OneShot that works across Claude Code, OpenCode, Gemini, and Codex while keeping project memory owned by the target repo instead of the OneShot repo. The design must work for OneShot itself and for downstream customer repos where OneShot is used as the orchestration layer.

## Deliverable
This planning pass produces:
- a concrete architecture spec for repo-local memory plus a central private index
- a build-ready phased roadmap for implementation
- a fresh persistent task ledger for the memory architecture build effort
- explicit scope, risk, governance, and verification criteria for the next implementation pass

## Acceptance Criteria
- The current pass is preserved by date and name, not only as overwritten top-level files
- `1shot/MEMORY_ARCHITECTURE_SPEC.md` defines:
  - repo-local memory ownership
  - `docs/agents/` vs `.oneshot/` responsibilities
  - write, retrieval, conflict, commit, and review policies
  - cross-repo abstraction rules
  - infra placement across homelab, OCI, and Tailscale
- The roadmap is detailed enough that implementation can start in the next pass without reopening core design questions
- The task ledger is reseeded for the memory architecture build effort
- The plan explicitly protects against:
  - cross-project leakage
  - stale or conflicting memory being treated as truth
  - operational fragility in the private indexing layer

## Scope
In:
- OneShot memory model for normal engineering repos
- repo-local structure and lifecycle
- central private indexing/search assumptions
- cross-repo portability and abstraction rules
- review governance for important work
- single-user operating assumptions
- onboarding behavior for repos with no memory yet
- adaptation requirements for downstream customer repos

Out:
- implementation code changes
- infra provisioning details
- UI or dashboard work
- provider-specific wiring details for Codex, Gemini, OpenCode, or Claude
- personal/legal private-memory system design

## Constraints
- Work memory must live in the target repo, not in the OneShot repo
- Memory is default-on with per-repo policy modes
- Personal/legal work stays outside the general engineering memory system
- Repo-local memory should be durable and readable by both humans and agents
- Cross-repo retrieval is allowed, but must prefer abstracted lessons over raw foreign memory
- Stable memory should be committed; transient machine state should usually remain local
- The system must fit inside existing homelab, OCI, and Tailscale boundaries

## Riskiest / Most Uncertain Part
The main risk is building a memory system that is too broad and contaminates one repo with wrong or stale lessons from another, while also becoming operationally fragile enough that it stops being trusted.

## User Answers
- Planning pass deliverable: architecture spec plus execution roadmap
- Out of scope now: no code changes, no infra provisioning, no UI work, no personal-memory system, no provider-specific wiring
- Primary memory ownership: project/repo first
- Strict isolation: personal/legal matters and credentials/secrets
- Default storage model: hybrid repo files plus central private index
- Infra boundary: homelab + OCI + Tailscale mesh
- Review on important work: code changes, architecture decisions, infra/config changes, security/privacy changes, and cross-repo changes
- Top failure worries: cross-project leakage, stale or wrong memory, operational fragility
- Repo memory location: both `docs/agents/` and `.oneshot/`
- Capture cadence: checkpoints and end-of-session summaries, not continuous canonical writes

## Provider Baseline
- codex: available
- gemini: available
- argus: available

## Decision Defaults For This Pass
- Multiple valid designs: choose the simplest architecture that preserves repo boundaries
- Cross-repo reuse: abstracted first, raw memory only by escalation
- Conflicts: preserve both sides with provenance
- Review gate: planner plus cross-model quorum only for high-risk work
