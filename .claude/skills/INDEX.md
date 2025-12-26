# Skills Index

Complete catalog of ONE_SHOT skills (27 total).

## Quick Reference

| Skill | Trigger | Purpose |
|-------|---------|---------|
| oneshot-core | "build me", "new project" | Full project creation with PRD |
| failure-recovery | "stuck", "looping" | Recovery from agent confusion |
| thinking-modes | "think", "ultrathink" | Extended analysis with personas |
| create-plan | "plan this" | Structured planning |
| implement-plan | "implement", "build it" | Execute approved plans |
| api-designer | "design API", "endpoints" | REST/GraphQL API design |
| create-handoff | "save context" | Preserve state before /clear |
| resume-handoff | "continue", "resume" | Restore from handoff |
| beads | "ready tasks", "blockers" | Git-backed persistent task tracking |
| debugger | "bug", "fix", "broken" | Systematic debugging |
| test-runner | "run tests", "coverage" | Execute and analyze tests |
| code-reviewer | "review", "is this safe" | Quality and security review |
| refactorer | "refactor", "clean up" | Safe code restructuring |
| performance-optimizer | "slow", "optimize" | Profile and improve |
| git-workflow | "commit", "PR" | Version control operations |
| push-to-cloud | "deploy", "ship" | Deploy to OCI-Dev |
| remote-exec | "run on", "sync and run" | Execute on remote machines |
| ci-cd-setup | "CI", "GitHub Actions" | Pipeline configuration |
| docker-composer | "docker", "containerize" | Container setup |
| observability-setup | "monitoring", "logging" | Logging, metrics, alerts |
| database-migrator | "migration", "schema" | Schema changes |
| documentation-generator | "docs", "README" | Generate documentation |
| secrets-vault-manager | "secrets", "env" | SOPS/Age encryption |
| secrets-sync | "sync secrets", "push secrets" | Two-way vault sync |
| the-audit | "audit this", "filter this" | Strategic communication filter |
| delegate-to-agent | "background", "isolated" | Route to native sub-agents |
| oci-resources | "oci database", "object storage" | OCI free-tier resources |

---

## By Category

### Core (3)
| Skill | Lines | Tools |
|-------|-------|-------|
| oneshot-core | 243 | Read, Write, Edit, Bash, Glob, Grep |
| failure-recovery | 229 | Read, Bash, Glob, Grep |
| thinking-modes | 227 | Read, Glob, Grep, Bash, Write, Edit, Task |

### Planning (3)
| Skill | Lines | Tools |
|-------|-------|-------|
| create-plan | 174 | Read, Glob, Grep, Write, Edit, Task |
| implement-plan | 161 | Read, Glob, Grep, Write, Edit, Bash, Task |
| api-designer | 379 | Read, Write, Edit |

### Context (3)
| Skill | Lines | Tools |
|-------|-------|-------|
| create-handoff | 201 | Read, Glob, Grep, Write, Edit |
| resume-handoff | 207 | Read, Glob, Grep, Write, Edit, Bash, Task |
| beads | ~210 | Bash, Read, Write, Edit, Glob |

### Development (5)
| Skill | Lines | Tools |
|-------|-------|-------|
| debugger | 159 | Bash, Read, Glob, Grep |
| test-runner | 200 | Bash, Read, Write, Edit |
| code-reviewer | 237 | Read, Glob, Grep |
| refactorer | 198 | Read, Write, Edit, Glob, Grep |
| performance-optimizer | 172 | Bash, Read, Write, Edit, Glob |

### Operations (6)
| Skill | Lines | Tools |
|-------|-------|-------|
| git-workflow | 128 | Bash, Read |
| push-to-cloud | 205 | Read, Write, Edit, Bash, Glob |
| remote-exec | ~230 | Bash, Read, Glob |
| ci-cd-setup | 241 | Read, Write, Edit |
| docker-composer | 241 | Bash, Read, Write, Edit |
| observability-setup | 242 | Bash, Read, Write, Edit, Glob |

### Data & Docs (5)
| Skill | Lines | Tools |
|-------|-------|-------|
| database-migrator | 302 | Bash, Read, Write, Edit |
| documentation-generator | 187 | Read, Write, Edit, Glob |
| secrets-vault-manager | 154 | Bash, Read, Write, Edit |
| secrets-sync | ~200 | Bash, Read, Write, Edit |
| oci-resources | ~200 | Bash, Read, Write, Edit |

### Communication (1)
| Skill | Lines | Tools |
|-------|-------|-------|
| the-audit | ~250 | Read, Write, Edit |

### Agent Bridge (1)
| Skill | Lines | Tools |
|-------|-------|-------|
| delegate-to-agent | ~180 | Task |

---

## Skill Chains

Common workflows that compose multiple skills:

```
New Project:
  oneshot-core → create-plan → implement-plan

Add Feature:
  create-plan → implement-plan → test-runner

Debug Issue:
  thinking-modes → debugger → test-runner

Deploy:
  code-reviewer → push-to-cloud → ci-cd-setup

Session Break:
  create-handoff → /clear → resume-handoff

Security Review (with agent):
  delegate-to-agent → security-auditor agent → report

Deep Research (with agent):
  delegate-to-agent → deep-research agent → findings
```

---

## When NOT to Use

| Skill | Skip When |
|-------|-----------|
| oneshot-core | Micro task, single file change |
| create-plan | Simple change, already have plan |
| thinking-modes | Quick question, obvious answer |
| api-designer | Internal function, no external API |
| database-migrator | No schema change, just data |
| ci-cd-setup | Local-only project |

---

## Tool Availability

| Tool | Skills Using It |
|------|-----------------|
| Read | All 27 |
| Write | 20 |
| Edit | 18 |
| Bash | 15 |
| Glob | 12 |
| Grep | 11 |
| Task | 6 |
