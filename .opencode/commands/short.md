---
description: Quick iterations on existing projects
agent: build
---

# /short — Quick Iteration

Fast operator for existing projects. Load context, ask what's next, execute in burn-down mode.

## Usage

`/short` or `/short <scope>`

## Steps

### 1. Load Context

```bash
git log --oneline -5
git status --short
```

Read `1shot/DECISIONS.md` and `1shot/BLOCKERS.md` if they exist.
Load persistent tasks if available:
```bash
python3 scripts/tasks.py list 2>/dev/null
```

### 2. Ask What's Next

Use the `question` tool: "What are you working on?"

### 3. Pre-Flight Review (if non-trivial change)

Check available providers:
```bash
command -v codex >/dev/null 2>&1 && echo "codex: yes" || echo "codex: no"
command -v gemini >/dev/null 2>&1 && echo "gemini: yes" || echo "gemini: no"
```

If codex available, dispatch quick adversarial review before starting:
```bash
unset OPENAI_API_KEY && codex exec --sandbox danger-full-access "Quick review: what should I watch out for when [task]?"
```

This is advisory, not a gate.

### 4. Docs Check (if using external library/API)

```bash
cat ~/github/docs-cache/docs/cache/.index.md
```

If the tool is missing, fetch and cache it first. Use cached docs as source of truth.

### 5. Methodology Selection (automatic)

Inspect the task description. Apply the right protocol:
- **Bug fix** (fix, bug, broken, error, crash, failing, wrong, unexpected, regression,
  investigate, troubleshoot, not working, incorrect) → apply `/debug` protocol: investigate →
  analyze → hypothesize → fix. Phases 1-3 are read-only.
- **New feature / implementation** (implement, add, create, build, new endpoint, new function)
  → apply `/tdd` protocol: RED-GREEN-REFACTOR. No production code without a failing test.
- **Doc edit, config change, refactor**: no special methodology.

### 6. Execute in Burn-Down Mode

- Complete one task fully before starting next
- If blocked > 2 attempts: log to `1shot/BLOCKERS.md`, skip
- After significant changes, dispatch a review (see dispatch protocol below)
- Don't create todowrite items for every little thing — just do the work

### 7. Dispatch Protocol

For worker dispatch:
```bash
# Classify the task
cd ~/github/oneshot && python3 -m core.router.resolve --class <task_class>

# Dispatch to workers
~/github/oneshot/bin/dispatch --class <task_class> --prompt "task description"
```

### 8. Session Summary

On completion, show:
```
Session Summary
├─ Tasks completed: X
├─ Files changed: Y
├─ Reviews: N
└─ Next: [next task or "all done"]
```

## Decision Defaults

| Ambiguity | Default |
|-----------|---------|
| Multiple implementations | Simplest |
| Naming | Follow existing pattern |
| Refactor opportunity | Skip unless blocking |
| Codex review? | Always if available (advisory) |

## Auto-Approved

- Reading/writing files
- Running tests and linters
- Creating/updating `1shot/` files
- Git commit (not push)

## Requires Confirmation

- Destructive operations
- Git push
- Deploying to production
