# ONE_SHOT: The $0 AI Build System
<!-- ONE_SHOT_CONTRACT v3.1 -->

**Version**: 3.1 | **Philosophy**: 5 min questions → PRD → autonomous build → done
**Compatible With**: Claude Code, Cursor, Aider, Gemini CLI, any LLM agent

---

## HOW TO READ THIS FILE (CRITICAL FOR AGENTS)

This file is ~3000 lines. **DO NOT read it all at once.**

```yaml
reading_strategy:
  session_start:
    read: "Lines 1-500 (HOT PATH)"
    contains: "Config, triage, questions list, build loop"

  on_demand:
    method: "Grep for section markers, read specific sections"
    markers:
      - "<!-- REF:TRIAGE -->"        # Full triage protocol
      - "<!-- REF:QUESTIONS -->"     # Question details + examples
      - "<!-- REF:EXECUTION -->"     # Build pipeline details
      - "<!-- REF:RESUME -->"        # Checkpoint/resume protocol
      - "<!-- REF:HANDOFF -->"       # Session handoff
      - "<!-- REF:RECOVERY -->"      # Failure recovery
      - "<!-- REF:LLM_OVERVIEW -->"  # LLM-OVERVIEW template
      - "<!-- REF:SECRETS -->"       # SOPS + Age setup
      - "<!-- REF:SKILLS -->"        # Skills reference

  example:
    user_says: "Resume from checkpoint"
    agent_does: "grep 'REF:RESUME' AGENTS.md → read that section"
```

---

## YAML CONFIG (ALWAYS PARSED)

```yaml
oneshot:
  version: 3.1

  prime_directive: |
    USER TIME IS PRECIOUS. AGENT COMPUTE IS CHEAP.
    Ask ALL questions UPFRONT. Get ALL info BEFORE coding.
    User walks away after: "PRD approved. Execute autonomous build."

  infrastructure:
    priority: ["homelab ($0)", "OCI free tier ($0)", "GitHub Actions ($0)", "Supabase ($0)"]
    decision: "Homelab unless needs 24/7 public access"

  cost:
    default_model: "google/gemini-2.5-flash-lite"  # ~$0.02/million tokens
    complex_model: "claude-sonnet-4"
    monthly_target: "$0-5"

  modes:
    micro:
      trigger: "'micro mode' OR <100 lines"
      questions: [Q1, Q11]
      output: "Single file, inline comments"
      skip: [PRD, README, scripts/, .oneshot/]
    tiny:
      trigger: "Single CLI, no services"
      skip: [web_design, ai, agents]
    normal:
      trigger: "CLI or simple web/API"
      skip: []
    heavy:
      trigger: "Multi-service, AI agents"
      skip: []

  question_tiers:
    must_answer: [Q0, Q1, Q2, Q6, Q12]   # Always ask
    if_non_default: [Q2.5, Q3-Q5, Q7-Q11, Q13]  # Smart defaults available
    yolo_mode: "Ask must_answer only → propose defaults → proceed"

  hard_stops:
    - "Storage upgrade (files→SQLite→Postgres)"
    - "Auth method changes"
    - "Production deployment changes"
    - "External API integration"
    - "Data deletion operations"
    - "Schema migrations"
    action: "STOP → Present prompt → Wait for approval → Log decision"

  build_loop: |
    for each task in PRD:
      1. implement(task)
      2. test(task)        # Auto-run tests
      3. if fails: fix → retry (max 3)
      4. commit(task)      # Conventional commits
      5. update_checkpoint()

  required_files:
    all: [ONE_SHOT.md, README.md, LLM-OVERVIEW.md, PRD.md]
    scripts: [setup.sh, start.sh, stop.sh, status.sh]
    services: ["/health endpoint", "/metrics endpoint"]

  supplements:
    skills_md:
      url: "https://raw.githubusercontent.com/Khamel83/secrets-vault/master/SKILLS.md"
      local: "~/github/secrets-vault/SKILLS.md"
      fetch: "On-demand when skill triggered"
```

---

## TRIAGE (First 30 Seconds of Every Session)

**Before doing ANYTHING, classify the user's intent:**

| Intent | Signals | Action |
|--------|---------|--------|
| **build_new** | "new project", "build me", "create" | Full ONE_SHOT → Questions → PRD → Build |
| **fix_existing** | "broken", "bug", "error", "fix" | Diagnostic Mode (no full flow) |
| **continue_work** | "continue", "resume", "pick up" | Load checkpoint → Summarize → Resume |
| **modify_existing** | "add feature", "change", "update" | Scope check → Mini-PRD if needed |
| **understand** | "explain", "how does", "what is" | Research only, no code changes |
| **quick_task** | "just", "quickly", "simple" | Check if micro mode applies |

**Decision Tree:**
```
READ USER MESSAGE
    ↓
CLASSIFY INTENT (above table)
    ↓
├─ build_new     → Section: Core Questions (below)
├─ fix_existing  → grep REF:TRIAGE → Diagnostic Mode
├─ continue_work → grep REF:RESUME → Load checkpoint
├─ modify        → grep REF:TRIAGE → Scope Assessment
├─ understand    → Research mode, no ONE_SHOT flow
└─ quick_task    → Check micro mode, maybe skip flow
```

**Triage Output:**
```
Intent: [type] | Scope: [micro/small/medium/large] | Flow: [Full/Mini/Direct/Research]
Next: [specific next step]
```

---

## CORE QUESTIONS (Quick Reference)

Ask these UPFRONT in ONE message (or batched). Don't drip-feed.

| ID | Key | Required | Smart Default |
|----|-----|----------|---------------|
| **Q0** | Mode | Yes | - |
| **Q1** | What are you building? | Yes | - |
| **Q2** | What problem does this solve? | Yes | - |
| Q2.5 | Reality check | If non-default | - |
| Q3 | Philosophy (3-6 bullets) | If non-default | "Simplicity first" |
| **Q4** | Features (3-7 items) | Yes | - |
| Q5 | Non-goals | If non-default | - |
| **Q6** | Project type (A-G) | Yes | - |
| Q7 | Data shape (examples) | If non-default | From Q1 context |
| Q8 | Data scale (A/B/C) | If non-default | A (Small) |
| Q9 | Storage (files/SQLite/Postgres) | If non-default | SQLite |
| Q10 | Dependencies | If non-default | "You decide" |
| Q11 | Interface (CLI commands/API routes) | If non-default | From Q6 |
| **Q12** | Done criteria / v1 scope | Yes | - |
| Q13 | Naming (project/repo/module) | If non-default | From Q1 |

**Project Types (Q6):**
- A. CLI Tool
- B. Python Library
- C. Web Application
- D. Data Pipeline
- E. Background Service
- F. AI-Powered Web App
- G. Static/Landing Page

**Mode Rules (Q0):**
- **Micro**: Skip all but Q1, Q11 → Single file output
- **Tiny**: Skip web/AI sections
- **Normal**: Full questions, standard project
- **Heavy**: Full questions + AI/agent questions

---

## BUILD LOOP (After PRD Approved)

```
Phase 0: Repo & Skeleton
  ├─ Create repo, .gitignore, .editorconfig
  ├─ Initialize .oneshot/checkpoint.yaml
  └─ Create LLM-OVERVIEW.md

Phase 1: Core Implementation (DATA-FIRST ORDER)
  1. Define data models
  2. Define storage schema
  3. Implement storage layer (CRUD)
  4. Build processing logic
  5. Create interface (CLI/API/UI)

Phase 2: Tests
  └─ Critical paths, run tests, fix failures

Phase 3: Scripts
  └─ setup.sh, start.sh, stop.sh, status.sh

Phase 4: Deployment
  └─ systemd/Docker, health endpoints, README
```

**Checkpoint after each task.** Update `.oneshot/checkpoint.yaml`.

---

## QUICK REFERENCE TABLES

### Storage Progression
| Tier | When | Records | Upgrade Trigger |
|------|------|---------|-----------------|
| Files (YAML/JSON) | Default | <1K | Need querying |
| SQLite | Most projects | <100K | Multi-user or heavy writes |
| PostgreSQL | Only when needed | 100K+ | Explicit approval required |

### Deployment Progression
| Tier | When |
|------|------|
| Local script | Personal use |
| systemd service | 24/7 single-machine |
| Docker Compose | Multi-service |
| Kubernetes | Multi-machine (you probably don't need this) |

### Cost by Mode
| Mode | Questions | User Time | Token Cost |
|------|-----------|-----------|------------|
| Micro | 2 | 1-2 min | $0.00 |
| Yolo | 5 | 3-5 min | $0.01 |
| Normal | 14 | 10-15 min | $0.05 |
| Heavy | 14+ | 15-20 min | $0.10 |

---

## PROJECT INVARIANTS (Every Project MUST Have)

- [ ] `README.md` with: one-line description, current tier, upgrade trigger, quick start (≤5 commands)
- [ ] `LLM-OVERVIEW.md` - complete project context for any LLM
- [ ] `PRD.md` - approved requirements document
- [ ] `scripts/` - setup.sh, start.sh, stop.sh, status.sh
- [ ] `/health` endpoint (if service)
- [ ] Storage tier documented with upgrade trigger
- [ ] No PostgreSQL without explicit approval for small/medium data

---

## PRD APPROVAL

**User says**: `PRD approved. Execute autonomous build.`

**Agent behavior**: Stop asking questions. Execute build loop autonomously.
Only interrupt for hard_stops (storage upgrade, auth change, etc.)

---

## RESUME FROM CHECKPOINT

**User says**: `Resume from checkpoint`

**Agent MUST**:
1. Read `.oneshot/checkpoint.yaml`
2. Read `LLM-OVERVIEW.md`
3. Read `PRD.md`
4. Summarize state to user
5. Confirm next action before proceeding

```markdown
## Session Resume
**Project**: [name]
**Last checkpoint**: [timestamp]
**Completed**: [list]
**In Progress**: [task + status]
**Next Action**: [exact next step]
Ready to continue?
```

---

<!-- ============================================================== -->
<!-- HOT PATH ENDS HERE (~Line 280)                                 -->
<!-- Everything below is REFERENCE - read on-demand via grep        -->
<!-- ============================================================== -->

---
---
---

# REFERENCE SECTIONS (Read On-Demand)

**Agent instructions**: Grep for section markers when needed. Don't load all at once.

---

<!-- REF:TRIAGE -->
# FULL TRIAGE PROTOCOL

## Intent Classification

```yaml
intent_classification:
  build_new:
    signals: ["new project", "build me", "create", "start fresh", "greenfield"]
    action: "Full ONE_SHOT flow → Reconnaissance → Core Questions → PRD → Build"

  fix_existing:
    signals: ["broken", "not working", "bug", "error", "fix", "debug"]
    action: "Diagnostic Mode → Gather symptoms → Isolate → Fix → Verify"

  continue_work:
    signals: ["continue", "resume", "pick up where", "last session"]
    action: "Context Recovery → Load checkpoint → Summarize state → Resume"

  modify_existing:
    signals: ["add feature", "change", "update", "modify", "extend"]
    action: "Scope Assessment → Impact analysis → Mini-PRD → Implement"

  understand:
    signals: ["explain", "how does", "what is", "show me", "walk through"]
    action: "Research Mode → Read code → Explain → No code changes"

  quick_task:
    signals: ["just", "quickly", "simple", "one-liner", "script"]
    action: "Micro Mode check → If truly micro, skip to minimal questions"
```

## Diagnostic Mode (For "It's Broken" Scenarios)

```yaml
diagnostic_protocol:
  step_1_symptoms:
    ask: "What behavior are you seeing vs what you expected?"
    gather:
      - "What error message (if any)?"
      - "When did it last work?"
      - "What changed since then?"

  step_2_reproduce:
    action: "Try to reproduce the issue yourself"
    commands:
      - "Run the failing command/action"
      - "Check logs: docker logs, journalctl, app logs"
      - "Check health endpoints if applicable"

  step_3_isolate:
    layers:
      - "Network: Can you reach the service?"
      - "Process: Is it running?"
      - "Config: Any recent changes?"
      - "Dependencies: All services up?"
      - "Data: Database accessible?"

  step_4_fix:
    approach: "Smallest change that fixes the issue"
    avoid: "Do NOT refactor while debugging"

  step_5_verify:
    action: "Confirm fix, document what broke and why"

  anti_pattern: |
    DO NOT run the full ONE_SHOT flow for a bug fix.
    User said "it's broken" - they want it fixed, not rebuilt.
```

## Scope Assessment (For Modifications)

```yaml
scope_assessment:
  step_1_understand_request:
    ask: "What feature/change do you want?"

  step_2_impact_analysis:
    check:
      - "Which files will change?"
      - "Any database changes needed?"
      - "Any new dependencies?"
      - "Does this affect other features?"

  step_3_size_classification:
    micro:
      criteria: "<10 lines, single file, no new deps"
      action: "Just do it, no PRD update"
    small:
      criteria: "<100 lines, 1-3 files, no arch changes"
      action: "Document in LLM-OVERVIEW.md, implement"
    medium:
      criteria: "New feature, multiple files, possible deps"
      action: "Mini-PRD → Approval → Implement"
    large:
      criteria: "Architecture change, new service, major refactor"
      action: "Full PRD update → Approval → Phased implementation"

  step_4_propose:
    output: |
      "This looks like a [size] change. My plan:
      1. [step]
      2. [step]
      Should I proceed, or want to discuss first?"
```

## Graceful Degradation

```yaml
graceful_degradation:
  one_shot_overkill_signals:
    - "Just add a comment"
    - "Rename this variable"
    - "Quick script to..."
    - "Help me understand..."

  degradation_levels:
    full_oneshot:
      when: "New project, major feature, architectural change"
      flow: "Core Questions → PRD → Autonomous Build"

    mini_oneshot:
      when: "Medium feature, some complexity"
      flow: "Quick scope check → Mini-PRD → Implement"

    direct_action:
      when: "Micro task, clear request, minimal risk"
      flow: "Understand → Do → Verify → Done"

    research_only:
      when: "User wants to understand, not change"
      flow: "Read → Explain → No code changes"

  agent_judgment: |
    Use judgment. A 5-line fix doesn't need 13 Core Questions.
    But a "quick" feature that touches auth definitely does.
```

## "I'm Lost" Recovery

```yaml
lost_recovery:
  symptoms:
    - "User request doesn't match any intent category"
    - "Project state is inconsistent"
    - "Previous context is missing or contradictory"

  recovery_protocol:
    step_1: "STOP. Don't guess or hallucinate."
    step_2: |
      Ask the user directly:
      "I want to make sure I help you correctly. Can you tell me:
      1. What's the end goal you're trying to achieve?
      2. Is this a new project, existing project, or continuation?
      3. What's the most important thing to get right?"
    step_3: "Based on answers, re-run triage"

  anti_pattern: |
    DO NOT pretend to understand when confused.
    DO NOT make up context that wasn't provided.
```

## Project Reconnaissance (Auto-Run on Session Start)

```yaml
reconnaissance:
  files_to_check:
    - ONE_SHOT.md: "Is this a ONE_SHOT project?"
    - .oneshot/checkpoint.yaml: "Is there a resume point?"
    - LLM-OVERVIEW.md: "What's the project context?"
    - PRD.md: "Is there an approved PRD?"
    - README.md: "What does this project do?"

  state_detection:
    new_project:
      indicators: ["No ONE_SHOT.md", "Empty or minimal repo"]
      action: "Start fresh - ask Core Questions"

    existing_oneshot_fresh:
      indicators: ["ONE_SHOT.md exists", "No checkpoint", "No PRD"]
      action: "Resume intake - check which questions answered"

    existing_oneshot_prd:
      indicators: ["ONE_SHOT.md exists", "PRD.md exists", "No checkpoint"]
      action: "Ask: 'PRD exists. Resume build or modify PRD?'"

    existing_oneshot_in_progress:
      indicators: ["checkpoint.yaml exists"]
      action: "Resume from checkpoint - show state summary"

    brownfield_no_oneshot:
      indicators: ["Code exists", "No ONE_SHOT.md"]
      action: "Ask: 'Existing project. Apply ONE_SHOT patterns?'"
```

---

<!-- REF:QUESTIONS -->
# CORE QUESTIONS (Full Details)

## Q0. Mode (Scope)

Choose ONE. This controls how much of ONE_SHOT the agent applies.

- **Micro** – Single file, <100 lines
- **Tiny** – Single CLI/script, no services, no web, no AI
- **Normal** – CLI or simple web/API on one box
- **Heavy** – Multi-service and/or AI agents, MCP, full ops

**Agent rules**:
- Micro → skip PRD, README, scripts/
- Tiny → skip Section 4 (Web & AI)
- Normal → apply Archon ops + health checks
- Heavy → enable AI, Agent SDK/MCP, full ops

---

## Q1. What Are You Building?

One sentence: "A tool that does X for Y people."

---

## Q2. What Problem Does This Solve?

Why does this exist? What is painful or impossible without it?

---

## Q2.5 The Reality Check

**Before building anything, validate you have a real problem.**

### Do you actually have this problem right now?
- [ ] Yes, I hit this issue **weekly** (strong build signal)
- [ ] Yes, I hit this issue **monthly** (moderate build signal)
- [ ] No, but I might someday (**WARNING**: Don't build it)
- [ ] No, this is a learning project (**Mark as such in README**)

### What's your current painful workaround?
```
[Describe exactly what you do manually now]
```

**If you don't have a workaround, you might not have a real problem.**

### What's the simplest thing that would help?
```
[Describe the 20% solution that gives 80% of the value]
```

**Build this first. Everything else is v2+.**

### The "Would I Use This Tomorrow?" Test
```
[Describe a specific task you'd do with this tool tomorrow]
```

**If you can't describe a specific task, stop and reconsider.**

**Agent rules for Q2.5**:
- If "No, but I might someday" AND not marked as learning project:
  - Agent MUST stop after PRD generation
  - Agent MUST NOT proceed unless user types: `Override Reality Check`

---

## Q3. Project Philosophy (3–6 bullets)

Examples:
- Simplicity over features
- Local-first, no external cloud
- CLI only, no GUI
- Works offline

---

## Q4. What Will It DO? (Features)

List 3–7 concrete capabilities.

---

## Q5. What Will It NOT Do? (Non-Goals)

Explicitly exclude things to stop scope creep.

---

## Q6. Project Type

- **A.** CLI Tool
- **B.** Python Library
- **C.** Web Application
- **D.** Data Pipeline
- **E.** Background Service
- **F.** AI-Powered Web Application
- **G.** Static / Landing Page

---

## Q7. Data Shape (Example Objects)

```yaml
example:
  date: 2024-01-15
  description: "AMAZON.COM"
  amount: -42.99
  category: "shopping"
```

---

## Q8. Data Scale (Size)

- **A.** Small (< 1,000 items, < 1 GB)
- **B.** Medium (1K–100K items, 1–10 GB)
- **C.** Large (100K+ items, 10 GB+)

---

## Q9. Storage Choice

- **A.** Files (YAML/JSON)
- **B.** SQLite
- **C.** PostgreSQL (needs explicit approval for A/B scale)
- **D.** Mix

---

## Q10. Dependencies

Specify or "you decide" for minimal defaults.

---

## Q11. User Interface Shape

**CLI**: List commands
```bash
yourtool init
yourtool import [source]
yourtool list [filters]
```

**Web/API**: List routes
```
/            - Landing
/dashboard   - Main UI
/api/items   - CRUD
```

---

## Q12. "Done" and v1 Scope

### Q12a. What Does "Done" Look Like?
Observable criteria.

### Q12b. What Is "Good Enough v1"?
The 80% you would actually use.

---

## Q13. Naming

- **Project name** (lowercase, hyphens OK)
- **GitHub repo name** (usually same)
- **Module name** (Python import, no hyphens)

---

## Yolo Mode Flow

**Trigger**: User says "yolo mode" or "fast mode"

1. Ask only: Q0, Q1, Q2, Q6, Q12
2. Propose smart defaults for rest
3. Show summary: "Using these defaults: [list]. Proceed?"
4. On "yes" → Generate PRD immediately

**Smart Defaults by Type**:
| Q6 Type | Stack | Storage |
|---------|-------|---------|
| A. CLI | Python, Click | SQLite |
| B. Library | Python, pytest | N/A |
| C. Web | FastAPI, Jinja2 | SQLite |
| D. Pipeline | Python, pandas | SQLite |
| E. Service | Python, APScheduler | SQLite |
| F. AI Web | FastAPI, OpenRouter | SQLite |
| G. Static | HTML/CSS/JS | N/A |

---

## Micro Mode Flow

**Trigger**: "micro mode" OR describes <100 line script

**Questions**: Only Q1 (what) and Q11 (interface)

**Skip**: PRD, README, LLM-OVERVIEW, scripts/, .oneshot/

**Output**: Single file with shebang, inline comments, usage in header

```python
#!/usr/bin/env python3
"""
rename_jpeg.py - Renames .jpeg files to .jpg

Usage:
    python rename_jpeg.py

Created via ONE_SHOT micro mode.
"""

from pathlib import Path

def main():
    for f in Path('.').glob('*.jpeg'):
        f.rename(f.with_suffix('.jpg'))
        print(f"Renamed: {f}")

if __name__ == "__main__":
    main()
```

**Upgrade from Micro when**:
- Script exceeds 100 lines
- Needs persistent storage
- Needs to run as service
- Needs tests
- Will be used by others

---

<!-- REF:EXECUTION -->
# AUTONOMOUS EXECUTION PIPELINE

## Phase 0: Repo & Skeleton

- Create GitHub repo (name from Q13)
- Clone to `~/github/[project]`
- Initialize: `.editorconfig`, `.gitignore`
- Create `LLM-OVERVIEW.md`
- Initialize checkpoint:

```bash
mkdir -p .oneshot/checkpoints
touch .oneshot/checkpoint.yaml
echo "# ONE_SHOT Decision Log - $(date -I)" > .oneshot/decisions.log
```

**Initial checkpoint.yaml**:
```yaml
checkpoint:
  oneshot_version: "3.1"
  project: [NAME]
  created: [ISO_TIMESTAMP]
  last_updated: [ISO_TIMESTAMP]

  session:
    current_phase: "Phase 0: Repo & Skeleton"
    current_task: "Initial setup"
    completion_percentage: 0

  progress:
    completed: []
    in_progress: []
    pending:
      - "Phase 1: Core Implementation"
      - "Phase 2: Tests"
      - "Phase 3: Scripts"
      - "Phase 4: Deployment"

  decisions_made: []
  blockers: []
```

**Required README.md**:
```markdown
# [Project Name] - [One-line description]

**Status**: In Development
**Current Tier**: [Storage/Deployment tier]
**Upgrade Trigger**: [When to upgrade]

## What This Does
[Problem → Solution in 2-3 sentences]

## Quick Start
[≤5 commands to get running]
```

---

## Phase 1: Core Implementation

**DATA-FIRST ORDER (critical)**:

1. **Define Data Models** - `models.py`
2. **Define Storage Schema** - Database schema or file format
3. **Implement Storage Layer** - CRUD operations
4. **Build Processing Logic** - Business logic
5. **Create Interface** - CLI, API, or UI

---

## Phase 2: Tests

- Write tests for critical paths
- Run tests, fix failures
- Document test commands in README

---

## Phase 3: Scripts

```bash
scripts/
├── setup.sh     # One-time setup
├── start.sh     # Start service
├── stop.sh      # Stop service
├── status.sh    # Check health
└── process.sh   # Batch work (if needed)
```

---

## Phase 4: Deployment

- systemd unit file (if 24/7 service)
- Docker Compose (if containerized)
- Health endpoints verified
- Deployment documented in README

---

## Health Endpoints (Required for Services)

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "dependencies": {
            "database": check_db()
        }
    }

@app.get("/metrics")
async def metrics():
    return {
        "uptime_seconds": get_uptime(),
        "requests_total": REQUEST_COUNT
    }
```

---

<!-- REF:RESUME -->
# SESSION CONTINUITY: RESUME PROTOCOL

## Checkpoint System

**Every project maintains `.oneshot/checkpoint.yaml`**:

```yaml
checkpoint:
  oneshot_version: "3.1"
  checkpoint_schema: "1.0"
  project: project-name
  last_updated: 2024-12-06T14:32:00Z

  session:
    current_phase: "Phase 1: Core Implementation"
    current_task: "Implement storage layer"
    completion_percentage: 45

  progress:
    completed:
      - "Phase 0: Repo & Skeleton"
      - "Define data models"
    in_progress:
      - task: "Implement storage layer"
        status: "CRUD operations 3/5 done"
        files_modified:
          - src/storage.py
    pending:
      - "Build processing logic"
      - "Create CLI interface"

  decisions_made:
    - decision: "Use SQLite over files"
      reason: "Need querying, expect 10K+ records"
      date: 2024-12-06

  blockers: []
  files_changed_this_session: []
```

## When to Update Checkpoint

- After completing any task
- Before context window reaches 70%
- When switching phases
- When hitting a blocker
- At end of any session

## Resume Command

**User says**: `Resume from checkpoint`

**Agent MUST**:
1. Read `.oneshot/checkpoint.yaml`
2. Read `LLM-OVERVIEW.md`
3. Read PRD
4. Summarize state
5. Confirm next action

**Resume format**:
```markdown
## Session Resume

**Project**: [name]
**Last checkpoint**: [timestamp]

**Completed**:
- [x] Task 1
- [x] Task 2

**In Progress**:
- [ ] Task 3 (50% - [status])

**Next Action**: [exact next step]

Ready to continue?
```

---

<!-- REF:HANDOFF -->
# SESSION HANDOFF PROTOCOL

## Handoff Template

When ending session or switching contexts:

```markdown
## HANDOFF STATE
**Project**: [project-name]
**Timestamp**: [ISO timestamp]
**Agent**: [Claude Code / Cursor / etc.]

### Last Completed
- [Phase X, Task Y - description]

### Currently Blocked On (if any)
- [Issue]
- [What was tried]
- [Why it failed]

### Next Action (BE SPECIFIC)
1. Open file: `[exact path]`
2. Find function: `[function name]`
3. Do: [exact change needed]

### Files Changed This Session
- `src/storage.py` - Added CRUD operations

### Decisions Made This Session
- Chose X over Y because Z

### Context the Next Agent Needs
- [Important detail 1]
- [Important detail 2]
```

## Handoff Triggers

Generate handoff when:
- User says "handoff", "switch agent", "take a break"
- Context window exceeds 80%
- Agent is looping or stuck
- Before any session end

## Receiving a Handoff

**Agent MUST**:
1. Read handoff document
2. Read `LLM-OVERVIEW.md`
3. Read PRD
4. Verify "Next Action" is still valid
5. Confirm understanding before proceeding

## Document Purposes

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| LLM-OVERVIEW.md | Full project context | Milestones |
| Handoff | Session state transfer | Every session |
| checkpoint.yaml | Machine-readable state | Continuous |

---

<!-- REF:RECOVERY -->
# FAILURE MODES & RECOVERY

## Build Failure Recovery

```yaml
recovery_build_failure:
  trigger: "Tests fail, build errors, runtime crashes"
  steps:
    1_isolate:
      - "pytest tests/ -x --tb=short"  # Stop at first failure
      - "git diff HEAD~1"              # What changed?
    2_rollback:
      - "git stash"
      - "git checkout HEAD~1"
      - "pytest tests/"                # Verify it works
    3_bisect:
      - "git bisect start"
      - "git bisect bad HEAD"
      - "git bisect good [last-good]"
    4_fix:
      rule: "Fix the bug, don't refactor"
    5_verify:
      - "pytest tests/"
```

## Agent Confusion Recovery

```yaml
recovery_agent_confusion:
  trigger: "Agent loops, gives inconsistent answers"
  symptoms:
    - "Repeating same action without progress"
    - "Contradicting previous statements"
    - "Asking questions already answered"
  steps:
    1_restate: |
      STOP. Let's reset.
      Current phase: [Phase X]
      Current task: [Task Y]
    2_narrow: |
      Focus only on: src/storage.py
      Specific change: [exact change]
      Do not touch other files.
    3_verify: |
      Before proceeding, tell me:
      1. What file?
      2. What change?
      3. Why?
    4_checkpoint:
      "Update .oneshot/checkpoint.yaml"
```

## Context Window Exhaustion

```yaml
recovery_context_exhaustion:
  trigger: "Responses get shorter, misses context"
  prevention:
    - "Use checkpoint.yaml for state"
    - "Keep LLM-OVERVIEW.md updated"
    - "Don't paste entire files"
  recovery:
    1_handoff: "Generate HANDOFF STATE document"
    2_new_session: |
      New session. Read in order:
      1. LLM-OVERVIEW.md
      2. .oneshot/checkpoint.yaml
      3. [handoff document]
      Confirm understanding.
```

## Dependency Hell

```yaml
recovery_dependency_hell:
  trigger: "Package conflicts, version mismatches"
  steps:
    1_isolate:
      - "python -m venv .venv-clean"
      - "source .venv-clean/bin/activate"
    2_minimal:
      - "pip install [core-deps-only]"
    3_add_incrementally:
      - "Add deps one at a time, test after each"
    4_pin:
      - "pip freeze > requirements.lock"
```

## Recovery Decision Tree

```
Problem detected
    ├─ Build/test failure?     → Build Failure Recovery
    ├─ Agent acting weird?     → Agent Confusion Recovery
    ├─ Responses degrading?    → Context Window Exhaustion
    ├─ Dependency issues?      → Dependency Hell
    └─ Unknown?                → Generate handoff, start fresh
```

---

<!-- REF:LLM_OVERVIEW -->
# LLM-OVERVIEW TEMPLATE

Every ONE_SHOT project MUST have `LLM-OVERVIEW.md`.

```markdown
# LLM-OVERVIEW: [Project Name]

> Complete context for any LLM to understand this project.
> **Last Updated**: [DATE]
> **ONE_SHOT Version**: 3.1

---

## 1. WHAT IS THIS PROJECT?

### One-Line Description
[A tool that does X for Y people]

### The Problem It Solves
[What's painful without this?]

### Current State
- **Status**: [In Development / Alpha / Beta / Production]
- **Version**: [X.Y.Z]
- **Last Milestone**: [What was accomplished]
- **Next Milestone**: [What's being worked on]

---

## 2. ARCHITECTURE OVERVIEW

### Tech Stack
```
Language:    [Python 3.11 / Node 20 / etc.]
Framework:   [FastAPI / Express / etc.]
Database:    [SQLite / PostgreSQL / etc.]
Deployment:  [Local / systemd / Docker]
```

### Key Components
| Component | Purpose | Location |
|-----------|---------|----------|
| [Component] | [What it does] | [path] |

---

## 3. KEY FILES

- `src/main.py` - Entry point
- `src/models.py` - Data models
- `src/storage.py` - Database operations
- `scripts/` - Automation scripts

---

## 4. CURRENT STATE

### What Works
- [Feature 1]

### What's In Progress
- [Feature 2 - 50%]

### What's Broken
- [Issue 1 - workaround]

---

## 5. ARCHITECTURE DECISIONS

### Why [Choice]?
**Decision**: Use [X] instead of [Y]
**Reason**: [Explanation]
**Upgrade Trigger**: [When we'd reconsider]

---

## 6. HOW TO WORK ON THIS PROJECT

```bash
git clone [repo]
cd [project]
./scripts/setup.sh
./scripts/start.sh
pytest tests/
```

---

## 7. CONTEXT FOR AI ASSISTANTS

**DO**:
- Follow ONE_SHOT patterns
- Check existing code first
- Update docs when changing code

**DON'T**:
- Add PostgreSQL without approval
- Add abstraction "for flexibility"
- Skip validation

---

## 8. RECENT CHANGES

| Date | Change | Impact |
|------|--------|--------|
| [DATE] | [What] | [How it affects project] |
```

---

<!-- REF:SECRETS -->
# SECRETS MANAGEMENT (SOPS + Age)

## Central Secrets Vault (Recommended)

**Philosophy**: One Age key in 1Password → ALL secrets.

### Setup

```bash
# Install
sudo apt install age sops  # Ubuntu
brew install age sops      # Mac

# Generate key
mkdir -p ~/.age
age-keygen -o ~/.age/key.txt
# Save public key (age1...) to 1Password

# Clone vault
git clone git@github.com:Khamel83/secrets-vault.git ~/github/secrets-vault
```

### Create `.sops.yaml`

```yaml
creation_rules:
  - path_regex: .*\.encrypted$
    age: 'age1your_public_key_here'
```

### Daily Usage

```bash
# Decrypt to project
sops --decrypt ~/github/secrets-vault/secrets.env.encrypted > .env
source .env

# Update secrets
cd ~/github/secrets-vault
sops secrets.env.encrypted
# Edit, save, auto-encrypted
git add . && git commit -m "Update secrets" && git push
```

## Standalone SOPS (Per-Project)

```bash
mkdir -p .sops
age-keygen -o .sops/key.txt

cat > .sops.yaml << 'EOF'
creation_rules:
  - path_regex: \.encrypted$
    age: 'age1your_key'
EOF

sops secrets.env.encrypted
sops --decrypt secrets.env.encrypted > .env
```

## .gitignore Template

```gitignore
# Secrets (NEVER commit)
.env
.env.local
secrets.env
*.key
key.txt
.age/

# Allow examples
!.env.example

# SOPS encrypted ARE safe
!*.encrypted
```

---

<!-- REF:SKILLS -->
# SKILLS REFERENCE

**Full skills in external file** - fetch on-demand.

```yaml
skills_reference:
  url: "https://raw.githubusercontent.com/Khamel83/secrets-vault/master/SKILLS.md"
  local: "~/github/secrets-vault/SKILLS.md"
```

## Available Skills

| Skill | Purpose | Trigger |
|-------|---------|---------|
| **project-initializer** | Bootstrap projects | "new project", "initialize" |
| **feature-planner** | Break down features | "plan feature", "break down" |
| **git-workflow** | Conventional commits | "commit", "PR" |
| **code-reviewer** | Quality & security | "review code", "PR review" |
| **documentation-generator** | READMEs, ADRs | "generate docs", "README" |
| **secrets-vault-manager** | SOPS + Age | "secrets", "API keys" |
| **skill-creator** | Create new skills | "create skill" |
| **marketplace-browser** | Find skills | "find skill", "browse" |
| **designer** | Web designs | "design", "website", "UI" |

## How to Use

```bash
# Local
cat ~/github/secrets-vault/SKILLS.md

# Or fetch
curl -s https://raw.githubusercontent.com/Khamel83/secrets-vault/master/SKILLS.md
```

---

# CORE ETHOS (Reference)

## Ownership & FOSS

- 100% free & open-source where possible
- No vendor lock-in
- Runs on: OCI Free Tier, homelab, any Linux box

## FOSS Stack

```
Application:  Python / Node / Go / Rust
Web:          FastAPI, Flask, Express
DB:           PostgreSQL, SQLite, Redis
Web server:   Nginx Proxy Manager / Caddy
DNS:          Cloudflare (free tier)
Network:      Tailscale (free tier)
Containers:   Docker + Docker Compose
```

## Archon Principles

- **Validate Before Create**: Check environment first
- **WHY Documentation**: Document why, not just how
- **Health First**: Every service has `/health`
- **Future-You Documentation**: Write for yourself in 6 months

## Simplicity First

- Prefer existing solutions over building
- Start with simplest thing that works
- Upgrade only when you hit limits

## The Upgrade Path Principle

**Storage**: Files → SQLite → PostgreSQL (only when needed)
**Deployment**: Local → systemd → Docker → Kubernetes (probably never)

---

# ANTI-PATTERNS

## Complexity Creep

```python
# Bad: Over-engineered
class AbstractDataProviderFactory:
    def create_provider(self, type: str) -> AbstractDataProvider: ...

# Good: Simple and direct
def get_data(source: str) -> dict:
    if source.endswith('.json'):
        return json.load(open(source))
```

**Rule**: Only add abstraction with 3+ implementations

## Over-Engineering Storage

**Anti-Pattern**: PostgreSQL for everything
**Better**: Files → SQLite → PostgreSQL when needed
**Validation**: 135K records in SQLite with sub-second queries

## No Rollback Plan

**Always have**: `scripts/rollback.sh`

---

# VERSION HISTORY

- **v3.1** (2024-12-06)
  - **RESTRUCTURED**: File now has HOT PATH (~300 lines) + REFERENCE sections
  - Agent reads ~300 lines at start, greps for reference sections on-demand
  - Same content, better consumption pattern for LLMs

- **v3.0** (2024-12-06)
  - ONE_SHOT is "The $0 AI Build System"
  - AGENTS.md compatibility
  - Cost optimization, build loop
  - Standalone vs Supplemented pattern

- **v2.1** (2024-12-06)
  - TRIAGE LAYER - First Contact Protocol
  - Skills extracted to secrets-vault

- **v2.0** (2024-12-06)
  - File structure optimized
  - Micro mode, oneshot_doctor.sh
  - Hard stop override pattern

---

# END OF ONE_SHOT v3.1

**Single file. Works standalone. Builds anything. Costs nothing.**

```
HOT PATH: Lines 1-280 (always read)
REFERENCE: Lines 280+ (grep on-demand)
```

Compatible: Claude Code, Cursor, Aider, Gemini CLI, any LLM agent
