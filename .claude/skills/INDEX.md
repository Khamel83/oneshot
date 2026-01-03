# Skills Index

ONE_SHOT v7.0 - Context-first skill organization.

---

## Core Skills (10) - Always in Router

These skills are auto-routed based on patterns. Use them naturally.

| Skill | Trigger | Purpose |
|-------|---------|---------|
| **front-door** | "build me", "new project" | Interview & routing hub |
| **create-plan** | "plan", "design" | Structured planning |
| **implement-plan** | "implement", "build it" | Execute with task groups |
| **debugger** | "bug", "fix", "broken" | Systematic debugging |
| **code-reviewer** | "review", "is this safe" | Quality & security review |
| **create-handoff** | "handoff", "save context" | Preserve state before clear |
| **resume-handoff** | "resume", "continue" | Restore from handoff/running state |
| **failure-recovery** | "stuck", "looping" | Recovery from confusion |
| **thinking-modes** | "think", "ultrathink" | Extended analysis |
| **secrets-vault-manager** | "secrets", "env" | SOPS/Age encryption |

---

## On-Demand Skills (19) - Available by Name

These skills are **not auto-routed** but available when explicitly requested.
Use `/skill-name` or "use the X skill" to invoke.

### Development
| Skill | Use When |
|-------|----------|
| **refactorer** | "refactor", "clean up code" |
| **test-runner** | "run tests", "coverage" |
| **performance-optimizer** | "slow", "optimize speed" |

### Operations
| Skill | Use When |
|-------|----------|
| **git-workflow** | Need conventional commits, PR creation |
| **docker-composer** | Setting up containers |
| **ci-cd-setup** | GitHub Actions, pipelines |
| **push-to-cloud** | Deploy to OCI-Dev |
| **remote-exec** | Run on remote machines, tmux jobs |
| **observability-setup** | Logging, metrics, health checks |

### Data & APIs
| Skill | Use When |
|-------|----------|
| **database-migrator** | Schema changes, migrations |
| **api-designer** | Design REST/GraphQL APIs |
| **oci-resources** | OCI database, object storage |
| **convex-resources** | Convex reactive backend |

### Documentation
| Skill | Use When |
|-------|----------|
| **documentation-generator** | README, LLM-OVERVIEW, ADRs |

### Specialized
| Skill | Use When |
|-------|----------|
| **the-audit** | Strategic communication filtering |
| **beads** | Persistent cross-session task tracking |
| **visual-iteration** | Self-scoring UI design loop |
| **hooks-manager** | Configure lifecycle automation |
| **delegate-to-agent** | Spawn isolated sub-agents |
| **secrets-sync** | Two-way vault synchronization |

---

## Context Management

### Running State vs Handoff

| File | Location | Use |
|------|----------|-----|
| **Running state** | `thoughts/shared/runs/` | Mid-implementation (minimal) |
| **Handoff** | `thoughts/shared/handoffs/` | Full context preservation |

### Flow
```
implement-plan → writes running state → context > 50% → pause
/compact
resume → reads running state → continues at exact task
```

---

## Skill Chains

```
New Project:
  front-door → create-plan → [compact] → implement-plan

Add Feature:
  create-plan → [compact] → implement-plan

Debug Issue:
  thinking-modes → debugger → test-runner

Session Break:
  create-handoff → /compact → resume-handoff
```

---

## When NOT to Use Skills

| Skill | Skip When |
|-------|-----------|
| front-door | Micro task, single file change |
| create-plan | Simple change, user gave explicit steps |
| thinking-modes | Obvious answer, quick question |
| implement-plan | Just 1-2 tasks (do directly) |

---

**Version**: 7.0 | **Core**: 10 | **On-Demand**: 19
