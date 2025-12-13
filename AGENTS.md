# ONE_SHOT Orchestrator

> **FOR AI AGENTS**: This file contains orchestration rules. Parse the YAML config, route to skills based on user intent, and follow the build loop.

<!-- ONE_SHOT_CONTRACT v5.0 -->

## YAML CONFIG (Always Parse First)

```yaml
oneshot:
  version: 5.0

  prime_directive: |
    USER TIME IS PRECIOUS. AGENT COMPUTE IS CHEAP.
    Ask ALL questions UPFRONT. Get ALL info BEFORE coding.
    User walks away after: "PRD approved. Execute autonomous build."

  file_hierarchy:
    - CLAUDE.md        # Read first (project-specific)
    - AGENTS.md        # This file (orchestration)
    - TODO.md          # Track progress (always update)
    - LLM-OVERVIEW.md  # Project context (update on major changes)

  infrastructure:
    priority: ["homelab ($0)", "OCI free tier ($0)", "GitHub Actions ($0)"]
    oci_dev:
      ip: "100.126.13.70"
      limits: "4 OCPU, 24GB RAM, 200GB disk (Always Free ARM)"

  modes:
    micro: { trigger: "'micro mode' OR <100 lines", questions: [Q1, Q11] }
    tiny: { trigger: "Single CLI, no services" }
    normal: { trigger: "CLI or simple web/API" }
    heavy: { trigger: "Multi-service, AI agents" }

  hard_stops:
    - "Storage upgrade (files->SQLite->Postgres)"
    - "Auth method changes"
    - "Production deployment"
    action: "STOP -> Present options -> Wait for approval"

  build_loop: |
    for each task in PRD:
      implement -> test -> commit -> update TODO.md

  required_files: [TODO.md, CLAUDE.md, LLM-OVERVIEW.md, PRD.md]
```

---

## TRIAGE (First 30 Seconds)

Classify user intent and route to appropriate skill chain:

| Intent | Signals | Primary Skill | Chain |
|--------|---------|---------------|-------|
| **build_new** | "new project", "build me" | `oneshot-core` | → create-plan → implement-plan |
| **fix_existing** | "broken", "bug", "error" | `debugger` | → thinking-modes → test-runner |
| **continue_work** | "resume", "checkpoint" | `oneshot-resume` | → resume-handoff |
| **add_feature** | "add feature", "extend" | `feature-planner` | → create-plan → implement-plan |
| **deploy** | "deploy", "push to cloud" | `push-to-cloud` | → ci-cd-setup |
| **stuck** | "looping", "confused" | `failure-recovery` | → create-handoff |
| **deep_analysis** | "think", "ultrathink" | `thinking-modes` | (standalone) |

---

## SKILL CHAINS

Skills compose together. Use appropriate chains for complex tasks:

```yaml
skill_chains:
  # New project: questions → plan → build
  new_project:
    - oneshot-core        # Ask questions, generate PRD
    - create-plan         # Structure implementation
    - implement-plan      # Execute with commits

  # Add feature to existing project
  add_feature:
    - feature-planner     # Break down feature
    - create-plan         # Structure approach
    - implement-plan      # Build it
    - test-runner         # Verify

  # Debug an issue
  debug:
    - thinking-modes      # Analyze deeply (ultrathink)
    - debugger            # Systematic debugging
    - test-runner         # Verify fix

  # Deploy to production
  deploy:
    - code-reviewer       # Pre-deploy review
    - push-to-cloud       # Deploy
    - ci-cd-setup         # Set up automation

  # Context management
  session_end:
    - create-handoff      # Preserve context
    # After /clear:
    - resume-handoff      # Continue seamlessly
```

---

## THINKING MODES

Activate extended thinking by level. Deeper = more expert perspectives simulated.

| Level | Trigger | Use Case |
|-------|---------|----------|
| **Think** | "think", "consider" | Quick sanity checks |
| **Think Hard** | "think hard", "really think" | Trade-off analysis |
| **Ultrathink** | "ultrathink" | Architecture, debugging |
| **Super Think** | "super think" | System-wide design |
| **Mega Think** | "mega think", "super mega think" | Strategic decisions |

> **Pro tip**: "ultrathink please do a good job" activates deep analysis.

---

## PLAN WORKFLOW

Structured workflow for complex implementations:

```
/create_plan [idea]      → thoughts/shared/plans/YYYY-MM-DD-description.md
  └─ answer questions, get approval

/implement_plan @[plan]  → systematic execution with commits
  └─ context getting low?

/create_handoff          → thoughts/shared/handoffs/YYYY-MM-DD-handoff.md
  └─ /clear

/resume_handoff @[file]  → continue exactly where you left off
```

**Why handoffs > auto-compact**: Explicit control, versioned, shareable, no context loss.

---

## CORE QUESTIONS

Ask these upfront before any implementation:

| ID | Question | Required |
|----|----------|----------|
| **Q0** | Mode (micro/tiny/normal/heavy) | Yes |
| **Q1** | What are you building? | Yes |
| **Q2** | What problem does this solve? | Yes |
| **Q4** | Features (3-7 items) | Yes |
| **Q6** | Project type (CLI/Web/API) | Yes |
| **Q12** | Done criteria / v1 scope | Yes |

Full details in `oneshot-core` skill.

---

## AVAILABLE SKILLS (28)

**Core**: `oneshot-core`, `oneshot-resume`, `failure-recovery`

**Thinking**: `thinking-modes`

**Planning**: `project-initializer`, `feature-planner`, `api-designer`, `designer`, `create-plan`, `implement-plan`

**Context**: `create-handoff`, `resume-handoff`

**Development**: `debugger`, `test-runner`, `code-reviewer`, `refactorer`, `database-migrator`, `performance-optimizer`

**Operations**: `git-workflow`, `ci-cd-setup`, `docker-composer`, `push-to-cloud`, `dependency-manager`

**Docs & Secrets**: `documentation-generator`, `secrets-vault-manager`

**Content**: `content-enricher`

**Meta**: `skill-creator`, `marketplace-browser`

---

## BUILD LOOP

After PRD approval, execute this loop:

```
for each task in TODO.md:
  1. Mark task "In Progress"
  2. Implement (use appropriate skills)
  3. Test (run tests, verify)
  4. Commit (clear message referencing task)
  5. Mark task "Done ✓"
  6. Update LLM-OVERVIEW.md if major change
```

---

## ALWAYS UPDATE

| File | When to Update |
|------|----------------|
| **TODO.md** | Every task state change |
| **LLM-OVERVIEW.md** | Major architectural changes |
| **CLAUDE.md** | New project conventions |

---

## STORAGE PROGRESSION

| Tier | When | Upgrade Trigger |
|------|------|-----------------|
| Files | Default | Need querying |
| SQLite | Most projects | Multi-user |
| PostgreSQL | Only when needed | **HARD STOP** - get approval |

---

## PROJECT INVARIANTS

Every project should have:
- `CLAUDE.md` - project instructions
- `TODO.md` - task tracking (todo.md format)
- `LLM-OVERVIEW.md` - context for any LLM
- `PRD.md` - approved requirements (after planning)
- `scripts/` - setup, start, stop, status
- `/health` endpoint (if service)

---

## SECRETS

```bash
# Pull from central vault
sops -d ~/github/secrets-vault/secrets.env.encrypted | grep KEY_NAME >> .env

# Encrypt project secrets
sops -e .env > .env.encrypted && rm .env

# Decrypt when needed
sops -d .env.encrypted > .env
```

---

## RESET

Say `(ONE_SHOT)` anytime to re-anchor to these orchestration rules.

---

## CORE ETHOS

- **$0 Infrastructure**: Homelab, OCI Free Tier, no lock-in
- **Simplicity First**: Files → SQLite → Postgres only when needed
- **Skills Over Scripts**: Predetermined workflows, not reinvention
- **User Time is Precious**: 5 min questions → autonomous build → done
- **Non-Destructive**: Always add, never overwrite existing work

---

**Version**: 5.0 | **Skills**: 28 | **Cost**: $0

Compatible: Claude Code, Cursor, Aider, Gemini CLI
