# ONE_SHOT v13 — Operator Framework

**9 slash commands.** Two operators. Seven utilities.

---

## Operators

| Command | Purpose |
|---------|---------|
| `/short` | Quick iterations on existing projects |
| `/full` | New projects, refactors, complex work |

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

## Utility Commands

| Command | Purpose |
|---------|---------|
| `/handoff` | Save context before /clear |
| `/restore` | Resume from handoff |
| `/research` | Background research mode |
| `/doc` | Cache external documentation |
| `/freesearch` | Zero-token web search (Exa) |
| `/vision` | Image/website visual analysis |
| `/secrets` | SOPS/Age secrets management |

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

## Where Commands Live

```
~/.claude/commands/     → User-level commands (9 files)
```

Commands are NOT in this skills directory. This INDEX.md is reference only.

---

## Full Spec

See `AGENTS.md` for complete operator protocol, decision defaults, and auto-approval rules.
