# ONE_SHOT v7.0

> **Context is the scarce resource.** Load minimal, atomize work, write state to disk.

---

## SKILL ROUTER (12 Core Skills)

```yaml
skill_router:
  # Entry
  - pattern: "new project|build me|help me|/interview|/front-door"
    skill: front-door

  # Autonomous (headless mode)
  - pattern: "autonomous|headless|background|overnight|just build it"
    skill: autonomous-builder

  # Planning
  - pattern: "plan|design|how should|what's the approach"
    skill: create-plan

  - pattern: "implement|execute|build it|run the plan"
    skill: implement-plan

  # Task Tracking (persistent)
  - pattern: "beads|ready tasks|what's next|next task|blockers|dependencies"
    skill: beads

  # Quality
  - pattern: "bug|error|fix|debug|broken|not working"
    skill: debugger

  - pattern: "review|check code|is this safe|pr review"
    skill: code-reviewer

  # Context Management
  - pattern: "handoff|save context|before clear|context low"
    skill: create-handoff

  - pattern: "resume|continue|pick up|from handoff"
    skill: resume-handoff

  # Recovery & Thinking
  - pattern: "stuck|looping|confused|start over"
    skill: failure-recovery

  - pattern: "think|ultrathink|super think|mega think"
    skill: thinking-modes

  # Secrets
  - pattern: "secrets|env|credentials|api key"
    skill: secrets-vault-manager
```

**All other skills**: Available on-demand via `/skill-name` or explicit request. See INDEX.md.

---

## CONTEXT MANAGEMENT

### Task Groups (3-5 tasks each)
```
Plan has N tasks → Create beads tasks with dependencies
Execute one group → bd update status → Check context
If context > 50% → Pause, bd sync, suggest /compact
After /compact → bd ready shows exactly what's next
```

### Beads = Persistent State
All task progress tracked via beads (survives /clear, /compact, sessions):
```bash
bd ready --json     # What's next?
bd update <id> --status in_progress
bd close <id> --reason "commit: abc123"
bd sync             # Always sync before session end
```

### Pre-Implementation Flow
```
If context > 30% before implement-plan:
  → bd sync (save current state)
  → Suggest /compact first
```

---

## FILE HIERARCHY

| Priority | File | Purpose |
|----------|------|---------|
| 1 | CLAUDE.md | Project-specific rules |
| 2 | AGENTS.md | This file (skill routing) |
| 3 | `.beads/` | Persistent task state (bd ready) |
| 4 | TODO.md | Session visibility |

---

## THINKING MODES

| Trigger | Depth |
|---------|-------|
| "think" | Quick check |
| "think hard" | Trade-offs |
| "ultrathink" | Architecture |
| "super think" | System design |
| "mega think" | Strategic |

---

## PHILOSOPHY

> "It's harder to read code than to write it." — Joel Spolsky

**NEVER rewrite from scratch.** Extend, refactor, use existing solutions.

**USER TIME IS PRECIOUS. AGENT COMPUTE IS CHEAP.**
Ask ALL questions UPFRONT. Get ALL info BEFORE coding.

---

## RESET

Say `(ONE_SHOT)` to re-anchor to these rules.

---

**Version**: 7.2 | **Core Skills**: 12 | **On-Demand**: 17 | **Agents**: 4
