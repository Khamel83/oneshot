# ONE_SHOT v7.0

> **Context is the scarce resource.** Load minimal, atomize work, write state to disk.

---

## SKILL ROUTER (10 Core Skills)

```yaml
skill_router:
  # Entry
  - pattern: "new project|build me|help me|/interview|/front-door"
    skill: front-door

  # Planning
  - pattern: "plan|design|how should|what's the approach"
    skill: create-plan

  - pattern: "implement|execute|build it|run the plan"
    skill: implement-plan

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

  # Secrets (only data skill in core)
  - pattern: "secrets|env|credentials|api key"
    skill: secrets-vault-manager
```

**All other skills**: Available on-demand via `/skill-name` or explicit request. See INDEX.md.

---

## CONTEXT MANAGEMENT

### Task Groups (3-5 tasks each)
```
Plan has N tasks → Divide into groups of 3-5
Execute one group → Write running state → Check context
If context > 50% → Pause, suggest /compact
After /compact → Resume from running state file
```

### Running State File
During implementation, write progress to:
```
thoughts/shared/runs/YYYY-MM-DD-{plan-name}.md
```

### Pre-Implementation Flow
```
If context > 30% before implement-plan:
  → Auto-create handoff
  → Suggest /compact first
```

---

## FILE HIERARCHY

| Priority | File | Purpose |
|----------|------|---------|
| 1 | CLAUDE.md | Project-specific rules |
| 2 | AGENTS.md | This file (skill routing) |
| 3 | Running state | Implementation progress |
| 4 | TODO.md | Session tasks |

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

**Version**: 7.0 | **Core Skills**: 10 | **On-Demand**: 19 | **Agents**: 4
