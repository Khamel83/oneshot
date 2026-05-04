# OneShot Lite Architecture

Date: 2026-05-04

## Decision

OneShot Lite is not an orchestration framework.

OneShot Lite is a small private adapter kit that makes better-maintained agent workflow projects usable in Khamel's repos and machines.

The split:

- **Superpowers owns coding workflow.**
- **Matt Pocock skills own selected engineering thinking tools.**
- **Karpathy guidelines own always-on coding behavior.**
- **A Karpathy-style wiki owns compounding knowledge.**
- **OneShot Lite owns private glue.**

If a feature is generic enough that another project can maintain it, OneShot Lite should not own it.

## Design Goal

Reduce OneShot from a broad operator framework into a thin layer that answers:

1. Where is the source of truth for this repo?
2. Which external workflow should handle this task?
3. What private context/tooling must be injected?
4. How do we preserve continuity across sessions?

That is it.

## Non-Goals

OneShot Lite should not:

- compete with Superpowers for plan/execute/review/TDD workflows
- maintain its own generic TDD/debugging process
- be a public skills marketplace
- become a second-brain product
- own all memory, wiki, and agent orchestration
- force every task through a custom router
- keep duplicate `.claude/skills`, `.agents/skills`, `.claude/commands`, docs, and Python code in sync forever

## Target Stack

| Layer | Owner | Why |
|---|---|---|
| Coding workflow | Superpowers | Closest replacement for `/short`, `/full`, `/conduct`, plan/execute/review/TDD. |
| Engineering thinking | Matt Pocock skills | Better focused tools for grilling, architecture review, diagnosis, PRD/issues, domain glossary. |
| Behavioral guardrails | Karpathy guidelines | Low-overhead rules: think first, simplicity, surgical changes, verifiable goals. |
| Knowledge/wiki | Karpathy wiki implementation | Persistent Markdown knowledge beats chat-only memory for research and synthesis. |
| Private adapters | OneShot Lite | Argus, secrets, homelab facts, repo source-of-truth maps, handoff/restore. |

## Command Surface

OneShot Lite should expose only commands that are private or glue-specific.

### Keep

| Command | Role |
|---|---|
| `/doc` | Argus-backed docs capture and research packs. |
| `/research` | Argus-backed deep research saved to repo artifacts. |
| `/freesearch` | Cheap/fast Argus lookup. |
| `/handoff` | Save next-session state. |
| `/restore` | Resume from a handoff. |
| `/secrets` | SOPS/Age vault wrapper. |
| `/update` | Sync OneShot Lite adapters/instructions into projects. |
| `/adversarial-review` | Thin Gemini second-opinion wrapper. |

### Replace

| Current OneShot Command | Replacement |
|---|---|
| `/short` | Superpowers default workflow, with OneShot context preflight. |
| `/full` | Superpowers brainstorming/planning/execution workflow. |
| `/conduct` | Superpowers subagent-driven development or execute-plan. |
| `/debug` | Superpowers systematic-debugging or Matt `diagnose`; do not maintain both locally. |
| `/tdd` | Superpowers TDD or Matt `tdd`; do not maintain a OneShot duplicate. |
| `/vision` | Browser/vision plugin unless a private Argus/browser adapter is needed. |
| `/janitor` | Keep as read-only signal only, or archive if it remains a sprawling product surface. |

### Add One Thin Front Door

Optional:

```text
/work
```

`/work` should not implement a workflow. It should:

1. inspect repo context
2. load OneShot private rules
3. recommend or invoke the right external workflow
4. write a handoff when useful

Examples:

- coding/refactor task -> "Use Superpowers"
- vague design -> "Use Matt grill-with-docs"
- bug -> "Use Superpowers systematic-debugging or Matt diagnose"
- research -> "Use OneShot /research"
- knowledge accumulation -> "Use wiki-ingest/wiki-query"
- secrets/config -> "Use OneShot /secrets"

## Core Data Model

OneShot Lite should keep a small, explicit registry instead of encoding behavior across many skills.

### `config/repos.yaml`

Maps repos to source-of-truth files and private rules.

Example:

```yaml
repos:
  /Users/khamel83/github/argus:
    kind: platform
    source_of_truth:
      - docs/handoff-next-session.md
      - docs/security-hardening-plan.md
    verification:
      - "uv --directory /Users/khamel83/github/argus run pytest tests/ -v --tb=short"
    notes:
      - "Default deployment guidance is Tailscale/private or loopback-safe."

  /Users/khamel83/github/divorce:
    kind: litigation
    source_of_truth:
      - CLAUDE.md
      - CASE_BRIEF.md
      - ARCHIVE/MANIFEST.md
      - SETTLEMENT/NUMBERS.md
    verification:
      - "python3 TOOLS/validate_numbers.py"
    notes:
      - "Ask before using PRIVATE/ unless explicitly authorized."
```

### `config/adapters.yaml`

Maps task classes to external owners.

Example:

```yaml
adapters:
  coding_workflow:
    owner: superpowers
    command_hint: "/brainstorming -> /write-plan -> /execute-plan"

  debugging:
    owner: superpowers
    fallback: mattpocock:diagnose

  architecture_review:
    owner: mattpocock:improve-codebase-architecture

  research:
    owner: oneshot:research

  docs_capture:
    owner: oneshot:doc

  wiki:
    owner: wiki-skills
```

### `1shot/handoffs/`

Keep this. It is useful and personal.

### `docs/research/`

Keep this. Research should become durable repo artifacts.

## Runtime Flow

### Coding Task

```text
user asks for coding/refactor/debug
  -> OneShot Lite preflight reads config/repos.yaml
  -> injects repo source-of-truth and constraints
  -> hands workflow to Superpowers or Matt skill
  -> OneShot Lite records handoff/result if needed
```

OneShot Lite should not dispatch its own task graph unless there is a private reason to use Codex/Gemini/Argus directly.

### Research Task

```text
user asks for research
  -> OneShot Lite uses Argus
  -> saves markdown artifact under docs/research/<slug>/
  -> optionally ingests the artifact into wiki
```

### Wiki Task

```text
source appears or user asks "what do we know?"
  -> wiki-ingest raw/source
  -> wiki-query for answer
  -> OneShot Lite only records where wiki lives and how to invoke it
```

### Handoff Task

```text
context low or session ending
  -> /handoff writes concise current state
  -> includes repo path, current decision, next command, modified files
```

## File Layout

Target structure:

```text
oneshot/
├── bin/
│   └── oneshot
├── config/
│   ├── repos.yaml
│   ├── adapters.yaml
│   └── machines.yaml
├── core/
│   ├── argus/
│   ├── handoff/
│   ├── secrets/
│   └── context/
├── docs/
│   ├── architecture/
│   └── research/
├── 1shot/
│   └── handoffs/
└── scripts/
    ├── oneshot-update.sh
    └── validate-lite.sh
```

Archive or delete after migration:

```text
core/dispatch/
core/router/
large generic operator skills
duplicate .agents/skills mirror unless it is the chosen packaging target
generic TDD/debug/full/short/conduct skill bodies
```

## Migration Plan

### Phase 1: Freeze

- Stop adding new OneShot generic skills.
- Mark `/short`, `/full`, `/conduct`, `/debug`, and `/tdd` as deprecated wrappers.
- Add a README note that generic coding process is delegated upstream.

### Phase 2: Install External Owners

- Install Superpowers as the default coding workflow.
- Install selected Matt skills only if they do not duplicate Superpowers too much.
- Install Karpathy guidelines as always-on instructions.
- Pick one wiki implementation and record its root path.

### Phase 3: Build Lite Registry

- Add `config/repos.yaml`.
- Add `config/adapters.yaml`.
- Add a small command that prints the recommended workflow for a repo/task.
- Keep the first version read-only.

### Phase 4: Replace Commands With Wrappers

Current:

```text
/full implements planning and dispatch
```

Target:

```text
/full says: deprecated; use Superpowers flow.
It still preloads OneShot repo context and writes handoff artifacts.
```

### Phase 5: Delete or Archive

When wrappers are stable:

- archive old router/dispatch docs under `archive/oneshot-v14/`
- remove duplicate skill copies
- split/retire Janitor if it remains too large
- rewrite README around OneShot Lite

## Keep/Archive Matrix

| Component | Action |
|---|---|
| Argus client/search/docs | Keep |
| SOPS/Age secrets wrapper | Keep |
| Handoff/restore | Keep |
| Repo source-of-truth rules | Keep |
| Machine facts | Keep |
| Generic task router | Archive |
| Dispatch runner | Archive unless still needed for Argus/Gemini wrappers |
| Generic `/short`/`/full`/`/conduct` | Replace with wrappers |
| Generic `/debug`/`/tdd` | Replace with upstream skills |
| Janitor | Keep read-only signals or archive |
| `.agents/skills` duplicate | Decide one packaging target; remove the other |

## Test for Whether a Feature Belongs

A feature belongs in OneShot Lite only if at least one is true:

1. It depends on Khamel's private infrastructure.
2. It depends on repo-specific source-of-truth rules.
3. It preserves cross-session continuity.
4. It safely exposes secrets/private tools.
5. It routes to an external tool with private context.

If none are true, upstream owns it.

## Final Shape

OneShot Lite should feel boring:

```text
private context + Argus + secrets + handoff + update + adapters
```

The work should feel less like maintaining a framework and more like maintaining a small set of local instruction files that make the rest of the ecosystem work correctly for this user.
