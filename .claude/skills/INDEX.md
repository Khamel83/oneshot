# Skills Index

ONE_SHOT v8 - Ultra-compressed context (~2k tokens), aggressive delegation, parallel execution.

---

## Start Here (5 Core Skills)

These are the skills you'll use 90% of the time. Just say these phrases:

| Say This | Skill | What Happens |
|----------|-------|--------------|
| **"build me..."** | front-door | Interview → spec → structured plan |
| **"plan this..."** | create-plan | Create implementation plan |
| **"implement"** | implement-plan | Execute plan with beads tracking |
| **"debug this"** | debugger | Systematic hypothesis-based debugging |
| **"review code"** | code-reviewer | Quality + security review |

**Examples:**
- "Build me a REST API for user management"
- "Plan a feature that adds dark mode"
- "Implement the authentication plan"
- "Debug this TypeError in the login flow"
- "Review the new payment code for security issues"

---

## Interview Depth Control

Control how thorough the front-door interview is:

| Command | Questions | When to Use |
|---------|-----------|-------------|
| `/full-interview` | All 13+ | Greenfield projects, avoid rework |
| `/quick-interview` | Q1,Q2,Q6,Q12 | Experienced user, well-defined task |
| `/smart-interview` | Auto-detect | Reset to default behavior |

Or set `ONESHOT_INTERVIEW_DEPTH=full|smart|quick` in environment.

---

## Context Management (Always Available)

| Command | What It Does |
|---------|--------------|
| `bd ready` | See next available tasks |
| `bd list` | All tasks with status |
| "create handoff" | Save context before /clear |
| "resume" | Continue after /clear |
| "what's next" | Same as bd ready |

---

## Autonomous Mode

```bash
# Run Claude headless, come back with artifact
oneshot-build "A Python CLI that fetches weather data"

# Monitor progress
tail -f .agent/STATUS.md
```

---

## All Skills Reference

### Core (17) - Auto-Routed

| Skill | Triggers | Purpose |
|-------|----------|---------|
| **front-door** | "build me", "new project" | Interview & routing hub (now with auto-delegation) |
| **autonomous-builder** | "headless", "just build it" | Idea → artifact (resilient, survives disconnect) |
| **resilient-executor** | "keep running", "survive disconnect" | Disconnect-proof execution via tmux |
| **create-plan** | "plan", "design" | Structured planning |
| **implement-plan** | "implement", "build it" | Execute with beads + parallel tasks |
| **beads** | "ready tasks", "what's next" | Persistent task tracking (aggressive sync) |
| **debugger** | "bug", "fix", "broken" | Systematic debugging |
| **code-reviewer** | "review", "is this safe" | Quality & security review |
| **delegate-to-agent** | (auto-triggered) | Aggressive subagent delegation |
| **parallel-validator** | "validate", "check everything" | Run tests/lint/security in parallel |
| **batch-processor** | "rename across", "update all" | Apply changes to many files in parallel |
| **auto-updater** | (auto on session start) | Auto-update skills from GitHub |
| **create-handoff** | "handoff", "save context" | Preserve state before clear |
| **resume-handoff** | "resume", "continue" | Restore from beads/handoff |
| **failure-recovery** | "stuck", "looping" | Recovery + predictive context |
| **thinking-modes** | "think", "ultrathink" | Extended analysis (5 levels) |
| **secrets-vault-manager** | "secrets", "env" | SOPS/Age encryption |

### Advanced (17) - On-Demand

Use `/skill-name` or "use the X skill" to invoke these explicitly.

**Development:**
- **refactorer** - "refactor", "clean up code"
- **test-runner** - "run tests", "coverage"
- **performance-optimizer** - "slow", "optimize speed"

**Operations:**
- **git-workflow** - Conventional commits, PR creation
- **docker-composer** - Docker/Compose setup
- **ci-cd-setup** - GitHub Actions, pipelines
- **push-to-cloud** - Deploy to OCI-Dev
- **remote-exec** - SSH, tmux jobs
- **observability-setup** - Logging, metrics, alerts

**Data & APIs:**
- **database-migrator** - Schema changes, migrations
- **api-designer** - REST/GraphQL API design
- **oci-resources** - OCI database, object storage
- **convex-resources** - Convex reactive backend

**Documentation:**
- **documentation-generator** - README, LLM-OVERVIEW, ADRs

**Specialized:**
- **the-audit** - Strategic communication filter
- **visual-iteration** - Self-scoring UI design
- **delegate-to-agent** - Spawn isolated sub-agents
- **secrets-sync** - Two-way vault sync
- **hooks-manager** - Lifecycle automation
- **skillsmp-browser** - Browse & compare external skill marketplaces

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
| front-door | Single file change, micro task |
| create-plan | User gave explicit steps |
| thinking-modes | Obvious answer |
| implement-plan | Just 1-2 quick tasks |

---

**Version**: 7.4 | **Core**: 21 | **Advanced**: 18 | **Auto-Update**: Enabled | **Resilient**: tmux
