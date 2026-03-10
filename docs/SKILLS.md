# ONE_SHOT Slash Commands Reference

**v13 — Operator Framework.** 9 commands total.

---

## Operators

### `/short` — Quick Iteration

Fast operator for existing projects. Loads context, asks what you're working on, executes in burn-down mode.

```
/short
/short <scope>
```

**Behavior:**
- Loads recent git commits and pending tasks
- Asks: "What are you working on?"
- Discovers relevant skills on demand
- Completes tasks fully before starting next
- Shows delegation summary on completion

**With scope:** Limits work to matching files

```
/short src/auth/*.ts    # Only work on auth files
```

### `/full` — Structured Work

Full operator for new projects, refactors, and complex implementations.

```
/full
/full <project-description>
```

**Behavior:**
- Creates IMPLEMENTATION_CONTEXT.md for persistent state
- Structured intake phase (goals, scope, architecture)
- Phase-based planning with milestones
- Skill discovery via SkillsMP
- Execution with context checkpoints
- Completion summary with verification

**Use when:** Starting a new project, major refactoring, complex features

---

## Context Management

### `/handoff`

Saves context before `/clear`. Captures what was done, what's in progress, decisions, blockers, next steps.

```
/handoff
```

### `/restore`

Resumes from handoff checkpoint. Checks native Tasks first, then reads handoff file.

```
/restore
```

---

## Research & Documentation

### `/research`

Background research using search APIs. Investigates topics without blocking conversation.

```
/research <topic>
```

### `/freesearch`

Zero-token web search via Exa API. Searches without consuming context budget.

```
/freesearch <query>
```

### `/doc`

Caches external documentation locally. Fetches from URL, saves to `~/github/docs-cache/`.

```
/doc <url>
/doc --list    # Show cached docs
```

---

## Utilities

### `/vision`

Visual analysis of websites and images. Handles screenshots and direct image URLs.

```
/vision https://example.com
/vision https://image.png "replicate"
```

### `/secrets`

SOPS/Age secrets management. Decrypts from `~/github/oneshot/secrets/`.

```
/secrets <name>
```

---

## Quick Reference

| I want to... | Use |
|--------------|-----|
| Quick iteration on existing work | `/short` |
| Start a new project | `/full` |
| Save context before clearing | `/handoff` |
| Resume after `/clear` | `/restore` |
| Research a topic | `/research` or `/freesearch` |
| Cache library docs | `/doc` |
| Analyze a website or image | `/vision` |
| Access secrets | `/secrets` |

---

## Architecture

**Before (v12):** 25+ menu commands
**After (v13):** 2 operators + 7 utilities

Operators discover skills on demand instead of maintaining a large command catalog.

---

## Decision Defaults

Operators apply these defaults without asking:

| Ambiguity | Default |
|-----------|---------|
| Multiple implementations | Simplest |
| Naming | Follow existing pattern |
| Refactor opportunity | Skip unless blocking |
| Stack | Follow CLAUDE.md defaults |
| Error handling | Match surrounding code |

---

## Auto-Approved Actions

- Reading any file
- Writing to scope-matched files
- Running tests and linters
- Creating context files (DECISIONS.md, BLOCKERS.md, etc.)
- Git commit (not push)

## Requires Confirmation

- Destructive operations (rm -rf, DROP TABLE)
- Git push to shared branches
- External API calls that cost money
- Deploying to production
