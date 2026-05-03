# ONE_SHOT v14 — Operator Framework

**16 skills.** Three operators. Thirteen utilities.

---

## Operators

| Skill | Purpose |
|-------|---------|
| `/short` | Quick iterations on existing projects |
| `/full` | New projects, refactors, complex work |
| `/conduct` | Multi-model PMO orchestrator — asks questions first, routes across Claude + Codex + Gemini, loops until done |

### /short — Quick Iteration

Fast operator for existing work:
- Loads recent context (git log, tasks, decisions)
- Asks: "What are you working on?"
- Discovers relevant skills on demand
- Executes in burn-down mode
- Shows delegation summary on completion

### /full — Structured Work

Full operator for complex tasks:
- Creates IMPLEMENTATION_CONTEXT.md
- Structured intake and discovery
- Phase-based planning with milestones
- Skill discovery via SkillsMP
- Execution with context checkpoints
- Completion summary

---

## Utility Skills

| Skill | Purpose |
|-------|---------|
| `/handoff` | Save context before /clear |
| `/restore` | Resume from handoff |
| `/research` | Background research mode |
| `/doc` | Cache external documentation |
| `/freesearch` | Zero-token web search via Argus |
| `/vision` | Image/website visual analysis |
| `/adversarial-review` | Adversarial second-opinion review via Gemini — challenges design decisions |
| `/secrets` | SOPS/Age secrets management |
| `/debug` | Systematic debugging (4-phase: investigate → analyze → hypothesize → fix) |
| `/tdd` | Test-driven development (RED-GREEN-REFACTOR cycle) |
| `/janitor` | Background intelligence — test gaps, doc staleness, config drift |
| `/update` | Update project configuration via settings.json |

---

## Architecture

```
Menu-based (old):
25+ slash commands → user picks one → executes

Operator-based (v13):
/short or /full → discover skills → execute → summary
```

**Why?** Reduced complexity, fewer commands to maintain, skill discovery happens when needed.

---

## Where Skills Live

```
~/.claude/skills/<name>/SKILL.md  → Personal skills (available in all projects)
```

### Required Format

Each SKILL.md MUST have this frontmatter:

```yaml
---
name: skill-name
description: What it does and WHEN to use it. Include trigger keywords.
---
```

**Critical**: The `name:` field is REQUIRED. Without it, the skill won't be discovered.

### Example

```
~/.claude/skills/
├── short/
│   └── SKILL.md
├── full/
│   └── SKILL.md
├── handoff/
│   └── SKILL.md
└── ...
```

### Why Commands Didn't Work

Claude Code uses the **skills** system. The `.claude/commands/` directory holds legacy commands (dispatch, status, escalate-worker, review-worker) that are still active.

- Skills are **model-invoked** — Claude decides when to use them based on description
- Commands were **user-invoked** — required explicit `/command` typing

The `~/.claude/commands/` directory is deprecated. Use `~/.claude/skills/` instead.

---

## Full Spec

See `AGENTS.md` for complete operator protocol, decision defaults, and auto-approval rules.
