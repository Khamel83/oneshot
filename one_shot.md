# ONE_SHOT_CONTRACT (do not remove)
```yaml
oneshot:
  version: 2.0

  # ============================================================================
  # PRIME DIRECTIVE: FRONT-LOAD EVERYTHING
  # ============================================================================
  # The user answers questions ONCE. Then the agent works autonomously.
  # The user should be able to walk away after PRD approval.
  # 5 minutes of questions → 5 hours of uninterrupted autonomous work.
  # ============================================================================

  prime_directive:
    philosophy: |
      ONE_SHOT exists to MINIMIZE user interruptions during development.
      All information gathering happens UPFRONT, before any code is written.
      Once the PRD is approved, the agent works autonomously until done.

    rules:
      - "Ask ALL questions before writing ANY code"
      - "NEVER interrupt the user mid-build for information you could have asked upfront"
      - "If you discover you need new information, BATCH questions together"
      - "Validate answers immediately - don't discover problems 2 hours into coding"
      - "The user's time is precious - your compute time is cheap"

    information_flow:
      intake_phase:
        duration: "5-15 minutes of user time"
        goal: "Gather EVERYTHING needed to build autonomously"
        output: "Complete PRD with no ambiguity"

      autonomous_phase:
        duration: "Minutes to hours of agent work"
        goal: "Build the entire project without interruption"
        user_involvement: "ZERO - user can walk away"
        interruption_allowed: "Only for hard_stops (see below)"

    anti_patterns:
      - "Asking one question at a time over multiple messages"
      - "Discovering missing requirements mid-implementation"
      - "Interrupting to ask 'should I also do X?'"
      - "Waiting for approval on obvious next steps"
      - "Asking the same question twice in different forms"

  # File architecture guidance
  architecture:
    current_size: "~13K tokens"
    growth_ceiling: "30-40K tokens before restructure needed"
    priority_order: |
      1. YAML header (always parsed first)
      2. Part I Sections 0-7 (core flow - agent keeps hot)
      3. Part I Sections 8-16 (supporting patterns)
      4. Part II-III (reference on demand)
      5. Part IV (appendix - skim only)
    growth_rules:
      - "Add new core patterns to Part I only if used in >50% of projects"
      - "Add new reference material to Part II-III"
      - "Skills and templates go in Part IV (appendix)"
      - "If Part IV exceeds 40% of file, consider SKILLS.md companion"

  # Single-file reference - everything consolidated here
  consolidation:
    purpose: "Single-file reference for AI/LLM to understand entire ONE_SHOT system"
    includes:
      - core_specification
      - all_skills_inline
      - secrets_management
      - llm_overview_standard
      - session_continuity
      - failure_recovery

  # LLM-OVERVIEW standard
  llm_overview:
    purpose: "Every ONE_SHOT project gets an LLM-OVERVIEW.md file"
    content: "Complete project context for a blank-slate LLM"
    update_frequency: "During development milestones, not every commit"
    location: "PROJECT_ROOT/LLM-OVERVIEW.md"

  phases:
    - intake_core_questions   # User present - gather everything
    - generate_prd            # User present - review and approve
    - wait_for_prd_approval   # User says "go"
    - autonomous_build        # User can leave - agent works alone

  modes:
    micro:
      description: "Single file, <100 lines, no project structure needed."
      trigger: "User says 'micro mode' or describes a tiny script"
      required_questions: [Q1, Q6, Q11]
      optional_questions: [Q12]
      skip_sections:
        - web_design
        - ai
        - agents
        - deployment
        - testing
        - health_endpoints
        - scripts_directory
        - llm_overview
      output: "Single script file with inline comments"
    tiny:
      description: "Single script/CLI, no services, no web, no AI."
      skip_sections:
        - web_design
        - ai
        - agents
        - heavy_deployment
    normal:
      description: "CLI or simple web/API on one box. Archon patterns, health checks, basic ops."
      skip_sections: []
    heavy:
      description: "Multi-service and/or AI/agents/MCP with full ops."
      skip_sections: []

  # Tiered questions for speed vs thoroughness
  question_tiers:
    must_answer:
      description: "Always required, no defaults possible"
      questions: [Q0, Q1, Q2, Q6, Q12]
      count: 5
    answer_if_non_default:
      description: "Has smart defaults - only ask if user's needs differ"
      questions: [Q2.5, Q3, Q4, Q5, Q7, Q8, Q9, Q10, Q11, Q13]
      behavior: "Agent proposes defaults, user confirms or overrides"
    yolo_mode:
      trigger: "User says 'yolo mode' or 'fast mode'"
      behavior: "Only ask must_answer questions, use defaults for rest"
      confirmation: "Show proposed defaults, proceed on 'yes'"

  core_questions:
    - { id: Q0,  key: mode,          type: enum,       required: true }
    - { id: Q1,  key: what_build,    type: text,       required: true }
    - { id: Q2,  key: problem,       type: text,       required: true }
    - { id: Q2.5,key: reality_check, type: structured, required: true }
    - { id: Q3,  key: philosophy,    type: text,       required: true }
    - { id: Q4,  key: features,      type: structured, required: true }
    - { id: Q5,  key: non_goals,     type: text,       required: true }
    - { id: Q6,  key: project_type,  type: enum,       required: true }
    - { id: Q7,  key: data_shape,    type: structured, required: true }
    - { id: Q8,  key: data_scale,    type: enum,       required: true }
    - { id: Q9,  key: storage,       type: enum,       required: true }
    - { id: Q10, key: deps,          type: text,       required: false }
    - { id: Q11, key: interface,     type: text,       required: true }
    - { id: Q12, key: done_v1,       type: structured, required: true }
    - { id: Q13, key: naming,        type: structured, required: true }

  variants:
    required_files:
      - ONE_SHOT.md
      - LLM-OVERVIEW.md  # NEW IN v1.8
      - README.md
      - scripts/setup.sh
      - scripts/start.sh
      - scripts/stop.sh
      - scripts/status.sh
    required_web_endpoints:
      - /health
      - /metrics
    storage_upgrade_path:
      - files
      - sqlite
      - postgres
    ai_defaults:
      default_provider: openrouter
      default_model: google/gemini-2.5-flash-lite
      monthly_cost_target_usd: 5

  enforcement:
    presence_rule: >
      If ONE_SHOT.md exists in a repo, agents MUST treat it as the governing
      spec for questions, PRD, implementation order, ops, and AI usage.
    prd_rule: >
      Any non-trivial change (new feature, storage change, deployment change)
      MUST go through PRD update before code changes.
    storage_rule: >
      Agents MUST NOT introduce PostgreSQL unless data_scale is Large (Q8 = C)
      or requirements clearly demand it AND user explicitly approves.
    mode_rule: >
      Agents MUST respect the selected mode's skip_sections when planning
      and implementing work.
    reality_check_rule: >
      If Q2.5 is answered "No, but I might someday" and the project is not
      explicitly marked as a learning project, agents MUST stop after PRD and
      only proceed if the user types the override phrase 'Override Reality Check'.
    llm_overview_rule: >
      Every ONE_SHOT project MUST have an LLM-OVERVIEW.md file that provides
      complete context for a blank-slate LLM to understand the project.
    front_load_rule: >
      Agents MUST gather ALL required information during intake phase.
      NEVER interrupt autonomous build phase for information that could
      have been gathered upfront. User's time is precious; compute is cheap.

  # Hard stops - agent MUST pause and get explicit approval
  hard_stops:
    description: "Agent MUST pause and get explicit user approval before proceeding"
    triggers:
      - id: storage_upgrade
        condition: "Upgrading storage tier (files→SQLite, SQLite→Postgres)"
        prompt: "Storage upgrade requires approval. Current: [X], Proposed: [Y]. Approve?"
      - id: new_major_dependency
        condition: "Adding dependency > 5MB or with native extensions"
        prompt: "Adding [dependency]. This requires [native deps/compilation]. Approve?"
      - id: auth_change
        condition: "Changing authentication method"
        prompt: "Changing auth from [X] to [Y]. This affects [scope]. Approve?"
      - id: production_deploy
        condition: "Any change to production deployment configuration"
        prompt: "Modifying production config. Change: [description]. Approve?"
      - id: reality_check_failed
        condition: "Q2.5 answered 'No, but I might someday' without learning flag"
        prompt: "Reality Check failed. Type 'Override Reality Check' to proceed."
      - id: external_api_integration
        condition: "Adding new external API integration"
        prompt: "Adding [API] integration. Cost: [estimate]. Rate limits: [limits]. Approve?"
      - id: data_deletion
        condition: "Any operation that deletes user data or database tables"
        prompt: "This will delete [description]. Type 'CONFIRM DELETE' to proceed."
      - id: schema_migration
        condition: "Database schema changes on existing data"
        prompt: "Schema migration: [description]. Backup recommended. Approve?"
    agent_behavior: |
      On trigger: STOP → Present prompt → Wait for approval → Log decision → Proceed only after approval
    override:
      pattern: "OVERRIDE: [stop_id]"
      example: "OVERRIDE: storage_upgrade"
      logging: "All overrides MUST be logged to .oneshot/decisions.log"
      format: |
        ## Override: [stop_id]
        **Date**: [ISO timestamp]
        **Reason**: [User's justification]
        **Risk accepted**: [What could go wrong]

  # Agent compatibility notes
  agent_compatibility:
    tested_with:
      - agent: "claude-code"
        model: "claude-opus-4"
        status: "Primary - follows sections literally"
      - agent: "claude-code"
        model: "claude-sonnet-4"
        status: "Good for routine tasks, may need section reminders"
      - agent: "cursor"
        model: "claude-3.5-sonnet"
        status: "May need reminders to check ONE_SHOT.md"
    tips:
      claude_code: "Reference specific sections: 'Follow Section 7.2'"
      cursor: "Start sessions with: 'Read ONE_SHOT.md first'"
    model_selection:
      opus: "Initial setup, complex architecture, multi-phase builds"
      sonnet: "Bug fixes, single features, documentation"
      haiku: "Quick edits, simple scripts"

  # Validation tracking
  validation:
    last_tested: "2024-12-06"
    test_projects:
      - name: "atlas-v2"
        type: "Heavy (AI-powered web app)"
        result: "Pass"
      - name: "divorce-finance"
        type: "Normal (CLI + SQLite)"
        result: "Pass - 135K records"
    primary_agent: "claude-code / claude-opus-4"
    spec_author: "Omar / Khamel83"
    oneshot_version: "2.0"

oneshot_env:
  projects_root: "~/github"
  secrets_vault_repo: "git@github.com:Khamel83/secrets-vault.git"
  secrets_vault_path: "~/github/secrets-vault"
  default_os: "ubuntu-24.04"
  default_user: "ubuntu"
```

# ONE_SHOT: AI-Powered Autonomous Project Builder

**Version**: 2.0
**Philosophy**: Front-load ALL questions → Execute AUTONOMOUSLY → User walks away
**Prime Directive**: User's time is precious. Agent compute is cheap.
**Validated By**: 8 real-world projects (135K+ records, 29 services, $1-3/month AI costs)
**Deployment**: OCI Always Free Tier OR Homelab (i5, 16GB RAM, Ubuntu)
**Cost**: $0/month infra (AI optional, low-cost)

---

# TABLE OF CONTENTS

This single file contains EVERYTHING an AI needs to understand and use ONE_SHOT:

**PRIME DIRECTIVE**: User's time is precious. Agent compute is cheap.
Ask ALL questions upfront → PRD → Autonomous build → User walks away.

**PART I: CORE SPECIFICATION (Sections 0-16)**
- Section 0: How to Use This File
- Section 1: Core Ethos
- Section 2: Core Questions (Q0-Q13) + **PRIME DIRECTIVE (2.0)** + **Tiered Questions**
- Section 3: Defaults & Advanced Options
- Section 4: Optional Web Design & AI
- Section 5: Environment Validation
- Section 6: PRD Generation
- Section 7: Autonomous Execution Pipeline + **Resume Protocol (7.6)** + **Handoff Protocol (7.7)**
- Section 8-10: Deployment, Ops, AI Integration
- Section 11-13: Examples, Goals, Anti-Patterns + **Failure Recovery (13.5)**
- Section 14-16: Meta, Version History, Skills Integration

**PART II: LLM-OVERVIEW STANDARD (Section 17)**
- What it is and why it exists
- Template for every project
- Update guidelines

**PART III: SECRETS MANAGEMENT (Section 18)**
- Central Secrets (SOPS + Age)
- Standalone SOPS Setup
- Sharing ONE_SHOT with others

**PART IV: SKILLS REFERENCE (Section 19)**
- All 8 skills documented inline
- When to use each skill
- Complete skill instructions

---

<!-- ONESHOT_CORE_START -->

# PART I: CORE SPECIFICATION

<!-- SECTION:0:HOW_TO_USE -->

# 0. HOW TO USE THIS FILE

This file is meant to be loaded into an IDE agent (Claude Code, Cursor, etc.) and used as the **single spec** for building projects.

## 0.1 Operational Flow (Human + AI)

1. **Put this file in your repo** as `ONE_SHOT.md`.
2. **Open your dev agent** (Claude Code / Cursor) on that repo.
3. Tell it:

   > "Use `ONE_SHOT.md` as the spec. Ask me all *Core Questions* (Section 2) first. Don't write any code until I say `PRD approved. Execute autonomous build.`"

4. Answer all Core Questions once.
5. Agent generates a PRD (Section 6).
6. You reply: `PRD approved. Execute autonomous build.`
7. Agent runs Section 7 (Autonomous Execution).

This is the contract: *questions once → PRD → autonomous build*.

## 0.2 PROJECT RECONNAISSANCE (Auto-Run on Session Start)

**Before asking ANY questions, the agent MUST run a quick reconnaissance to understand where the project is.**

### 0.2.1 Reconnaissance Checklist (30 seconds)

```yaml
reconnaissance:
  files_to_check:
    - ONE_SHOT.md: "Is this a ONE_SHOT project?"
    - .oneshot/checkpoint.yaml: "Is there a resume point?"
    - LLM-OVERVIEW.md: "What's the project context?"
    - PRD.md: "Is there an approved PRD?"
    - README.md: "What does this project do?"
    - .git: "Is this a git repo?"

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
      action: "Ask: 'Existing project. Apply ONE_SHOT patterns incrementally?'"
```

### 0.2.2 Quick State Detection Script

Agent should mentally run this on session start:

```bash
# What kind of project is this?
if [ -f "ONE_SHOT.md" ]; then
    if [ -f ".oneshot/checkpoint.yaml" ]; then
        echo "STATE: Resume from checkpoint"
    elif [ -f "PRD.md" ]; then
        echo "STATE: PRD exists, ready to build or modify"
    else
        echo "STATE: ONE_SHOT project, needs intake"
    fi
elif [ -d ".git" ] && [ -n "$(ls -A src/ 2>/dev/null)" ]; then
    echo "STATE: Brownfield - existing code, no ONE_SHOT"
else
    echo "STATE: Greenfield - new project"
fi
```

### 0.2.3 State-Dependent First Message

Based on reconnaissance, agent's FIRST message should be:

| State | First Message |
|-------|---------------|
| **Greenfield** | "New project. Let me ask the Core Questions..." |
| **ONE_SHOT Fresh** | "ONE_SHOT project detected. Let me continue intake..." |
| **ONE_SHOT + PRD** | "Found PRD.md. Ready to build, or need changes first?" |
| **Resume** | "[Checkpoint summary]. Ready to continue from [task]?" |
| **Brownfield** | "Existing codebase. Apply ONE_SHOT patterns, or specific task?" |

**This reconnaissance takes <30 seconds and prevents wasted questions.**

---

## 0.3 What's New in v1.9

**v1.9 is about MINIMIZING user time:**

- **PRIME DIRECTIVE** (Section 2.0) - User's time is precious, agent compute is cheap
- **Project Reconnaissance** (Section 0.2) - Auto-detect project state on session start
- **Tiered Questions** - Must-answer vs defaults, Yolo mode for speed
- **Session Continuity** (Sections 7.6-7.7) - Resume from checkpoint, handoff between agents
- **Failure Recovery** (Section 13.5) - Patterns for common problems
- **Hard Stops** (YAML header) - Explicit approval triggers
- **Micro Mode** - Single file, <100 lines, minimal questions

**The Goal**: 5-15 minutes of user time → Hours of autonomous agent work

Everything from v1.8 remains:
- Skills inline (Section 19)
- Secrets management (Section 18)
- LLM-OVERVIEW standard (Section 17)

---

<!-- SECTION:1:CORE_ETHOS -->

# 1. CORE ETHOS

ONE_SHOT is built on a small set of non-negotiable principles.

## 1.1 Ownership & FOSS

- 100% free & open-source stack where possible.
- No vendor lock-in. Everything runs on:
  - OCI Always Free Tier **or**
  - Your own homelab.
- All services deployable on any Linux box with Docker or systemd.

### 1.1.1 FOSS Stack (Canonical)

```text
Application:   Python / Node / Go / Rust
Web:          FastAPI, Flask, Express, etc.
DB:           PostgreSQL, SQLite, Redis
Web server:   Nginx Proxy Manager (web UI for SSL/reverse proxy)
              OR Caddy (if you prefer config files)
DNS:          Cloudflare (free tier, SSL cert management)
OS:           Ubuntu Server 24.04 LTS (or equivalent)
Network:      Tailscale (free tier, WireGuard based)
VC:           Git + GitHub (or self-hosted Gitea)
Containers:   Docker + Docker Compose (modular includes pattern)
Storage:      MergerFS (pooling) + SnapRAID (parity, optional)
Automation:   Ansible (infrastructure-as-code, optional)
```

**Philosophy borrowed from homelab community**:
- **Modular Docker Compose**: Each service in its own directory with dedicated compose file
  - Master `docker-compose.yml` uses `include` directive
  - Easy to add/remove services without touching monolithic files
- **Nginx Proxy Manager over Traefik/Caddy**: Web UI for SSL management
  - Easier for non-experts (Let's Encrypt auto-renewal via UI)
  - Still FOSS, just more accessible
- **Cloudflare DNS**: Free tier for DNS + SSL certificate management
- **Cloudflare Tunnel**: For selective public exposure (free, always useful)
- **MergerFS + SnapRAID over ZFS/RAID**: Works with mixed drive sizes, lower RAM overhead
- **Tailscale over VPNs**: Zero-config mesh networking
- **SOPS + Age for secrets management**: Single source of truth with encryption

### 1.1.2 Conscious Tradeoffs

- We choose FOSS even when it costs ops work
- We allow swappable proprietary options behind interfaces

## 1.2 Archon Principles (Always On)

These rules apply to every project ONE_SHOT builds:

- **Validate Before Create**: Check environment, dependencies, and connectivity before generating code or infra.
- **WHY Documentation**: For any non-trivial choice, document why, not just how.
- **Systematic Debugging**: Isolate layer → Check dependencies → Analyze logs → Verify health endpoints.
- **Health First**: Every long-running service exposes a `/health` endpoint.
- **Future-You Documentation**: Write docs and code for yourself in 6 months when you've forgotten everything.

### 1.2.1 Future-You Documentation Standards

**Every non-obvious decision needs documentation**:

#### In Code:
```python
# Good: Explains WHY
# Using SQLite instead of Postgres because:
# 1. Single-file portability (easy backup)
# 2. No server overhead
# 3. Handles our 100K records fine
# Will upgrade to Postgres if we hit 500K records or need multi-user
db = sqlite3.connect("project.db")

# Bad: Just states WHAT
db = sqlite3.connect("project.db")
```

#### In README:
**Required sections for all projects**:

1. **Architecture Decisions** - Why this stack?
2. **Upgrade Triggers** - When to change technology?
3. **Known Limitations** - What doesn't this do?
4. **Troubleshooting** - Issues you've actually hit and solutions

## 1.3 Simplicity First (Core Principle)

**Before building anything, ask: Does this already exist?**

- **Prefer existing solutions** over building from scratch
- If a library/tool does 80% of what you need:
  - Fork it (give credit, follow license)
  - Wrap it with a thin layer for your use case
  - Document what you're doing and why
- **Building from scratch is the last resort**, not the first

### 1.3.1 The Upgrade Path Principle

**Start with the simplest thing that works, upgrade only when you hit limits.**

**Storage progression**:
1. **Files (YAML/JSON)** → works for < 1K items
2. **SQLite** → works for < 100K items
3. **PostgreSQL** → only when you need multi-user or > 100K items with heavy writes

**Deployment progression**:
1. **Local script** → works for personal use
2. **systemd service** → works for 24/7 single-machine
3. **Docker Compose** → works for multi-service
4. **Kubernetes** → only if you need multi-machine orchestration (you probably don't)

### 1.3.2 The "Works on My Machine" is Actually Good

**ONE_SHOT projects run on**:
- Ubuntu 24.04 LTS (homelab standard)
- Mac (development)
- OCI Always Free Tier (cloud)

This is a feature, not a bug. You know these environments intimately.

## 1.4 Web & UX Philosophy (When Web Exists)

- Modern, clean, and responsive.
- Real typography (Google Fonts), no browser defaults.
- Thoughtful color palettes, no generic red/blue/green.
- Micro-interactions (hover, focus, transitions) without bloat.
- SEO basics: good titles, meta descriptions, semantic HTML.

## 1.5 AI & Agents Philosophy (Optional)

- AI is optional. No AI if you don't explicitly ask for it.
- When used:
  - **Default provider**: OpenRouter (unified API for multiple models)
  - **Default model**: Gemini 2.5 Flash Lite (`google/gemini-2.5-flash-lite`)
    - **Very cheap** (~$0.10-0.30/M tokens)
    - Ultra-low latency, fast token generation
    - **Use for 99% of AI tasks** - it's good enough
  - **Upgrade models** (only when Flash Lite genuinely fails):
    - `anthropic/claude-3-5-haiku`: When Flash Lite gives bad results (~$0.80/M tokens)
    - `anthropic/claude-3-5-sonnet`: Complex code generation (~$3/M tokens)
    - `anthropic/claude-3-opus`: Mission-critical code, rarely needed (~$15/M tokens)

### 1.5.1 Cost Philosophy

**Reality check**:
- Gemini 2.5 Flash Lite handles **99% of AI tasks** just fine
- Typical usage: $0.50-2/month
- Only upgrade if Flash Lite genuinely fails, not "just in case"
- **Total AI cost target**: $1-3/month for most projects

## 1.6 Project Invariants (MUSTs)

For every ONE_SHOT project, the agent MUST ensure:

- **Documentation**
  - [ ] A `README.md` with clear one-line description, Current Tier, Upgrade Trigger, Quick Start (≤5 commands)
  - [ ] An `LLM-OVERVIEW.md` (NEW in v1.8) - complete project context for any LLM
  - [ ] A PRD file in the repo (name can be `PRD.md` or similar)

- **Scripts**
  - [ ] `scripts/setup.sh`
  - [ ] `scripts/start.sh`
  - [ ] `scripts/stop.sh`
  - [ ] `scripts/status.sh`
  - [ ] `scripts/process.sh` if there is any recurring/batch work

- **Services** (if Web Application, AI-Powered Web Application, or Background Service)
  - [ ] A `/health` endpoint
  - [ ] A `/metrics` endpoint OR a documented reason why not
  - [ ] A clear deployment path documented in README

- **Storage Discipline**
  - [ ] Agent MUST NOT introduce PostgreSQL without explicit human approval if Data Scale is A or B
  - [ ] Storage tier and upgrade trigger MUST be explicitly documented

- **Complexity Control**
  - [ ] No abstract factories / deep inheritance trees unless there are ≥3 real implementations
  - [ ] For small CLIs, keep modules small and direct; no premature layering

---

<!-- SECTION:2:CORE_QUESTIONS -->

# 2. CORE QUESTIONS (REQUIRED FOR ANY PROJECT)

<!-- SECTION:2.0:PRIME_DIRECTIVE -->

## 2.0 THE PRIME DIRECTIVE: FRONT-LOAD EVERYTHING

**This is the most important principle in ONE_SHOT.**

```
┌─────────────────────────────────────────────────────────────────────┐
│  USER TIME IS PRECIOUS. AGENT COMPUTE TIME IS CHEAP.                │
│                                                                     │
│  Ask ALL questions ONCE, UPFRONT.                                   │
│  Get ALL information BEFORE writing ANY code.                       │
│  Then execute AUTONOMOUSLY for hours without interruption.          │
│                                                                     │
│  The user should be able to walk away after saying:                 │
│  "PRD approved. Execute autonomous build."                          │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.0.1 Information Gathering Rules

**Agent MUST**:
1. Ask ALL Core Questions in ONE message (or as few as possible)
2. Validate answers IMMEDIATELY - catch problems before coding starts
3. If answers are ambiguous, clarify NOW, not 2 hours into the build
4. If new information is needed mid-build, BATCH questions together
5. NEVER interrupt for something that could have been asked upfront

**Agent MUST NOT**:
- Ask one question, wait for answer, ask next question (drip-feed)
- Interrupt mid-build to ask "should I also do X?"
- Ask for approval on obvious next steps
- Ask the same question in different forms
- Discover missing requirements after starting implementation

### 2.0.2 Question Tiers (Speed vs Thoroughness)

| Tier | Questions | When to Ask |
|------|-----------|-------------|
| **Must Answer** | Q0, Q1, Q2, Q6, Q12 | Always - no defaults possible |
| **If Non-Default** | Q2.5, Q3-Q5, Q7-Q11, Q13 | Only if user's needs differ from smart defaults |

### 2.0.3 Yolo Mode (For Experienced Users)

**Trigger**: User says "yolo mode" or "fast mode"

**Flow**:
1. Ask only must-answer questions (Q0, Q1, Q2, Q6, Q12)
2. Propose smart defaults for everything else
3. Show summary: "Using these defaults: [list]. Proceed? (yes/override)"
4. On "yes" → Generate PRD immediately

**Smart Defaults by Project Type**:

| Q6 Type | Stack | Structure | Storage |
|---------|-------|-----------|---------|
| A. CLI Tool | Python, Click | Flat | SQLite |
| B. Library | Python, pytest | Modular | N/A |
| C. Web App | FastAPI, Jinja2 | Domain-driven | SQLite |
| D. Data Pipeline | Python, pandas | Flat | SQLite |
| E. Background Service | Python, APScheduler | Flat | SQLite |
| F. AI Web App | FastAPI, OpenRouter | Domain-driven | SQLite |
| G. Static Page | HTML/CSS/JS | Flat | N/A |

### 2.0.4 Quick Mode Reference

| Mode | Questions | User Time | Output |
|------|-----------|-----------|--------|
| **Micro** | Q1, Q6, Q11 only | 1-2 min | Single file |
| **Yolo** | 5 must-answer | 3-5 min | Full project |
| **Normal** | All Core Questions | 10-15 min | Full project |
| **Heavy** | All + AI/Agent Qs | 15-20 min | Full project + AI |

## 2.1 MICRO MODE: The Fast Path

**Trigger**: User says "micro mode" OR describes a script <100 lines

**Micro mode is for**:
- Single-file scripts
- Quick utilities
- One-off automation
- Learning exercises

### Micro Mode Flow (1-2 minutes total)

```yaml
micro_mode_flow:
  step_1_detect:
    trigger_phrases:
      - "micro mode"
      - "quick script"
      - "simple script that..."
      - "one-liner" / "one file"
    auto_detect: "Description implies <100 lines, no services"

  step_2_ask:
    questions:
      - "What should this script do? (Q1)"
      - "CLI with args, or just run it? (Q11 simplified)"
    skip_entirely:
      - Q0 (mode) - already micro
      - Q2 (problem) - implied by Q1
      - Q2.5 (reality check) - micro = low investment
      - Q3-Q5 (philosophy, features, non-goals) - overkill
      - Q6 (project type) - default to CLI Tool
      - Q7-Q10 (data, storage, deps) - inline decisions
      - Q12 (done) - "it runs without errors"
      - Q13 (naming) - derive from description

  step_3_defaults:
    Q6: "A (CLI Tool)"
    Q12: "Script runs without errors"
    naming: "Derived from description (e.g., 'rename_jpeg.py')"
    structure: "Single file, no directories"
    testing: "Manual run = test"
    documentation: "Inline comments only"

  step_4_output:
    deliverables:
      - "Single script file with shebang"
      - "Inline comments for non-obvious logic"
      - "Usage example in file header"
    skip_deliverables:
      - README.md
      - PRD.md
      - LLM-OVERVIEW.md
      - scripts/ directory
      - .oneshot/ directory
    optional:
      - ".oneshot/micro_log.txt for history tracking"
```

**Example Micro Interaction**:

```
User: "Micro mode. Script that renames all .jpeg files to .jpg in current dir."

Agent: "Got it. Two quick questions:
1. Should it be recursive (subdirectories)?
2. Dry-run option to preview changes?

Or just the basics?"

User: "Just basics, current dir only."

Agent: [Produces rename_jpeg.py - done in 30 seconds]
```

**Micro Output Template**:

```python
#!/usr/bin/env python3
"""
rename_jpeg.py - Renames .jpeg files to .jpg in current directory

Usage:
    python rename_jpeg.py

Created via ONE_SHOT micro mode.
"""

import os
from pathlib import Path

def main():
    for f in Path('.').glob('*.jpeg'):
        new_name = f.with_suffix('.jpg')
        f.rename(new_name)
        print(f"Renamed: {f} -> {new_name}")

if __name__ == "__main__":
    main()
```

### When to Upgrade from Micro

If any of these become true, upgrade to Tiny or Normal mode:
- Script exceeds 100 lines
- Need persistent storage
- Need to run as service
- Need tests
- Will be used by others

---

## Q0. Mode (Scope)

Choose ONE. This controls how much of ONE_SHOT the agent applies.

- **Tiny** – Single CLI/script, no services, no web, no AI.
- **Normal** – CLI or simple web/API on one box. Archon patterns, health checks, basic ops.
- **Heavy** – Multi-service and/or AI agents, MCP, full ops.

**Your choice**:
```
[Tiny / Normal / Heavy]
```

**Agent rules for Q0 (Mode)**:
- MUST ask Q0 first for any new ONE_SHOT project.
- MUST map the answer to `oneshot.modes[mode]` from the YAML header.
- MUST respect that mode's `skip_sections`.

Concretely:
- **Tiny** → skip Section 4 (Web & AI) and Sections 7.4–7.5 (AI & Deployment).
- **Normal** → apply Archon ops + health checks; AI optional.
- **Heavy** → enable AI, Agent SDK/MCP (if requested), AI cost tracking, and full ops patterns.

---

## Q1. What Are You Building?

One sentence: "A tool that does X for Y people."

**Your answer**:
```
[YOUR ANSWER HERE]
```

---

## Q2. What Problem Does This Solve?

Why does this exist? What is painful or impossible without it?

**Your answer**:
```
[YOUR ANSWER HERE]
```

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
[Describe exactly what you do manually now, including frequency and pain points]
```

**If you don't have a workaround, you might not have a real problem.**

### What's the simplest thing that would help?
```
[Describe the 20% solution that gives 80% of the value]
```

**Build this first. Everything else is v2+.**

### How will you know it's working?
```
[Observable outcome with measurable results, not "it exists"]
```

### The "Would I Use This Tomorrow?" Test

**Imagine the project is done. Tomorrow morning, you need to**:
```
[Describe a specific task you'd do with this tool]
```

**If you can't describe a specific task, stop and reconsider the project.**

### Project Validation Checklist

Before proceeding, ensure:
- [ ] Real problem with current painful workaround
- [ ] Specific, measurable success criteria
- [ ] Concrete "tomorrow morning" use case
- [ ] Learning projects explicitly marked as such

**Agent rules for Q2.5 (Reality Check)**:
- If the user selects "No, but I might someday" AND does **not** mark it as a learning project:
  - Agent MUST stop after PRD generation.
  - Agent MUST NOT proceed unless the user types: `Override Reality Check`

---

## Q3. Project Philosophy (3–6 bullets)

These drive architectural decisions.

Examples:
- Simplicity over features
- Local-first, no external cloud
- CLI only, no GUI
- Each module < 300 lines
- Works offline

**Your answer** (bullets):
```
- ...
- ...
- ...
```

---

## Q4. What Will It DO? (Features)

List 3–7 concrete capabilities.

**Your answer**:
```
1.
2.
3.
4.
5.
6.
7.
```

---

## Q5. What Will It NOT Do? (Non-Goals)

Explicitly exclude things to stop scope creep.

**Your answer**:
```
- ...
- ...
- ...
```

---

## Q6. Project Type

Choose one (this drives defaults):
- **A.** CLI Tool (commands, flags, local execution)
- **B.** Python Library (importable, reusable functions)
- **C.** Web Application (API + frontend + DB)
- **D.** Data Pipeline (ETL, scheduled jobs)
- **E.** Background Service (24/7 monitoring, alerts)
- **F.** AI-Powered Web Application
- **G.** Static / Landing Page (premium design, minimal backend)

**Your choice**: (letter)
```
[LETTER]
```

---

## Q7. Data Shape (Example Objects)

Give one or two realistic examples of the data this project manipulates.

Example:
```yaml
transaction:
  date: 2024-01-15
  description: "AMAZON.COM"
  amount: -42.99
  category: "shopping"
  account: "checking"
```

**Your examples**:
```
[YOUR DATA EXAMPLES HERE]
```

---

## Q8. Data Scale (Size)

- **A.** Small (< 1,000 items, < 1 GB)
- **B.** Medium (1K–100K items, 1–10 GB)
- **C.** Large (100K+ items, 10 GB+)

**Your choice**:
```
[LETTER]
```

---

## Q9. Storage Choice

- **A.** Files (YAML/JSON directories)
- **B.** SQLite (single file DB)
- **C.** PostgreSQL
- **D.** Mix (files for raw, SQLite/Postgres for processed)

If files, format: YAML / JSON / CSV / Other

**Your choice**:
```
[LETTER + FORMAT IF FILES]
```

---

## Q10. Dependencies (Python / Node Packages)

Either specify or say "you decide" and ONE_SHOT will pick minimal defaults.

**Your answer**:
```
[LIST PACKAGES OR "you decide"]
```

---

## Q11. User Interface Shape

Describe how humans call this thing.

**If CLI, list commands**:
```bash
yourtool init
yourtool import [source]
yourtool list [filters]
yourtool export [path]
```

**If Web/API, list routes**:
```
/            - Landing
/dashboard   - Main UI
/api/items   - CRUD
```

**If Library, public API**:
```python
from project import Parser
Parser().process(input)
```

**Your interface**:
```
[YOUR INTERFACE HERE]
```

---

## Q12. "Done" and v1 Scope

### Q12a. What Does "Done" Look Like?

Observable criteria.

**Your success criteria**:
```
- ...
- ...
- ...
```

### Q12b. What Is "Good Enough v1"?

The 80% you would actually use.

**Your v1 scope**:
```
- ...
- ...
- ...
```

---

## Q13. Naming

Pick names once.
- **Project name** (lowercase, hyphens OK):
- **GitHub repo name** (usually same as project):
- **Module name** (Python import name, no hyphens):

**Your names**:
```
Project: [NAME]
Repo: [NAME]
Module: [NAME]
```

---

# 3. DEFAULTS & ADVANCED OPTIONS

If you don't care, ONE_SHOT picks sane defaults based on Q6.

## 3.1 Directory Structure (Q16)

- **A.** Flat (`src/*.py`)
- **B.** Modular (`src/module1/`, `src/module2/`)
- **C.** Domain-driven (`src/models/`, `src/services/`, `src/api/`)
- **D.** Let ONE_SHOT choose based on project type

**Defaults**:
- CLI / small tools → A (Flat)
- Web apps / services → C (Domain-driven)

## 3.2 Testing Strategy (Q17)

- **A.** Minimal (critical paths)
- **B.** Thorough (~80% coverage target)
- **C.** Comprehensive (near 100%)
- **D.** ONE_SHOT decides based on complexity

**Defaults**:
- CLI: A/B depending on complexity
- Web apps / services: B

## 3.3 Deployment Preference (Q18)

- **A.** Local dev only
- **B.** Tailscale HTTPS (e.g. `https://project.your-tailnet.ts.net`)
- **C.** Systemd service (24/7)
- **D.** Both Tailscale + systemd

**Runtime**:
- OCI Always Free Tier VM
- Homelab (i5, 16GB, Ubuntu)
- Local only

## 3.4 Secrets & Env (Q19)

**Choose your secrets management approach**:

- **A.** No secrets needed
- **B.** Traditional `.env` file (unencrypted, for development only)
- **C.** SOPS + Age encryption (recommended for production/shared teams)

**See Section 18 for complete SOPS + Age setup.**

---

# 4. OPTIONAL: WEB DESIGN & AI

Skip entire Section 4 if you don't want web / AI.

## 4.1 Web Design (Q20–Q22)

Only relevant for Web / AI Web / Landing projects.

**Aesthetic**: Modern & Minimal / Bold & Vibrant / Dark & Sleek / Professional & Corporate / Creative & Playful / ONE_SHOT decides / N/A

**Color scheme**: Monochrome / Complementary / Analogous / ONE_SHOT decides / N/A

**Animation level**: Minimal / Moderate / Rich / N/A

## 4.2 AI Features (Q23)

**Do you want AI?**
- No AI
- Yes, with these capabilities: Content generation / Intelligent search / Recommendations / Chat UI / Data analysis / Other

**Budget**: Minimal ($0–5/month) / Moderate ($5–20/month) / Flexible ($20+/month)

## 4.3 Agent Architecture (Q24)

**Decision rule**:
- If AI is requested AND project has multi-step workflows with tools → Use **Agent SDK with MCP**
- Else → Use **simple API calls**

**MCP (Model Context Protocol)**:
- Open standard for connecting AI to tools
- Works with any model
- Pre-built servers: Filesystem, GitHub, Slack, PostgreSQL, Brave Search, Google Drive

---

<!-- SECTION:5:ENVIRONMENT_VALIDATION -->

# 5. ENVIRONMENT VALIDATION

ONE_SHOT always validates environment before building.

## 5.1 Validation Script

```bash
#!/usr/bin/env bash
# save as: scripts/oneshot_validate.sh
set -euo pipefail

echo "=== ONE_SHOT Environment Validation ==="

echo "[*] Python version:"
python3 --version || echo "Python not found"

echo "[*] Git config:"
git config user.name  || echo "user.name not set"
git config user.email || echo "user.email not set"

echo "[*] GitHub access (optional):"
if command -v gh >/dev/null 2>&1; then
  gh auth status || echo "gh auth not configured"
fi

echo "[*] Tailscale:"
if command -v tailscale >/dev/null 2>&1; then
  tailscale status || echo "tailscale not connected"
fi

echo "[*] Disk space:"
df -h /

echo "[*] Memory:"
free -h || echo "free command not available"

echo "=== Validation complete ==="
```

## 5.2 Validation-Before-Build Pattern

**ALWAYS validate before writing code**. This prevents wasted effort on invalid assumptions.

## 5.3 Project Health Check (oneshot_doctor.sh)

**Validates a project against ONE_SHOT spec. Run periodically or before major changes.**

```bash
#!/usr/bin/env bash
# scripts/oneshot_doctor.sh
# Validates project against ONE_SHOT v2.0 spec

set -euo pipefail

echo "=== ONE_SHOT Doctor v2.0 ==="
echo "Timestamp: $(date -Iseconds)"
echo ""

ERRORS=0
WARNINGS=0

# Helper functions
error() { echo "❌ ERROR: $1"; ((ERRORS++)) || true; }
warn() { echo "⚠️  WARN: $1"; ((WARNINGS++)) || true; }
ok() { echo "✅ OK: $1"; }

# Required files (all modes except micro)
echo "=== Required Files ==="
for f in ONE_SHOT.md README.md; do
  [ -f "$f" ] && ok "$f exists" || error "$f missing"
done

# Mode-dependent files
if [ -f "PRD.md" ]; then
  ok "PRD.md exists"
else
  warn "PRD.md missing (required for non-micro projects)"
fi

if [ -f "LLM-OVERVIEW.md" ]; then
  ok "LLM-OVERVIEW.md exists"
  # Check freshness
  if [[ "$OSTYPE" == "darwin"* ]]; then
    AGE=$(( ($(date +%s) - $(stat -f %m LLM-OVERVIEW.md)) / 86400 ))
  else
    AGE=$(( ($(date +%s) - $(stat -c %Y LLM-OVERVIEW.md)) / 86400 ))
  fi
  [ $AGE -gt 30 ] && warn "LLM-OVERVIEW.md is $AGE days old - consider updating"
else
  warn "LLM-OVERVIEW.md missing (required for non-micro projects)"
fi

# Scripts directory
echo ""
echo "=== Scripts ==="
if [ -d "scripts" ]; then
  for s in setup.sh start.sh stop.sh status.sh; do
    [ -f "scripts/$s" ] && ok "scripts/$s exists" || warn "scripts/$s missing"
  done
else
  warn "scripts/ directory missing (required for non-micro projects)"
fi

# Checkpoint directory
echo ""
echo "=== Session Continuity ==="
if [ -d ".oneshot" ]; then
  ok ".oneshot/ directory exists"
  [ -f ".oneshot/checkpoint.yaml" ] && ok "checkpoint.yaml exists" || warn "checkpoint.yaml missing"
else
  warn ".oneshot/ directory missing (no resume capability)"
fi

# Git status
echo ""
echo "=== Git Status ==="
if [ -d ".git" ]; then
  ok "Git repository initialized"
  # Check for uncommitted changes
  if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    warn "Uncommitted changes present"
  fi
else
  error "Not a git repository"
fi

# Secrets check
echo ""
echo "=== Secrets Safety ==="
if [ -f ".env" ]; then
  if grep -q "^.env$" .gitignore 2>/dev/null; then
    ok ".env exists and is gitignored"
  else
    error ".env exists but NOT in .gitignore!"
  fi
else
  ok "No .env file (or using SOPS)"
fi

# Summary
echo ""
echo "=== Summary ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [ $ERRORS -gt 0 ]; then
  echo ""
  echo "❌ Project has $ERRORS errors that should be fixed."
  exit 1
elif [ $WARNINGS -gt 0 ]; then
  echo ""
  echo "⚠️  Project has $WARNINGS warnings to review."
  exit 0
else
  echo ""
  echo "✅ Project passes all ONE_SHOT checks!"
  exit 0
fi
```

**Usage**: Run `./scripts/oneshot_doctor.sh` to validate project health.

## 5.5 Using ONE_SHOT with Existing Projects

ONE_SHOT isn't just for greenfield projects. You can apply its patterns incrementally.

### Progressive Adoption Approach

1. **Observability First** (Always): Add health/metrics endpoints, status scripts
2. **Documentation Upgrade**: Enhance README with current tier/upgrade triggers
3. **Secrets Management**: Add SOPS + Age for sensitive configs
4. **Scripts & Automation**: Add setup.sh if missing

### Agent Rules for Existing Projects

- **Don't recreate** - analyze existing architecture first
- **Respect current constraints** - databases, frameworks, deployment patterns
- **Focus on pain points** - apply ONE_SHOT patterns where they provide immediate value
- **Progressive enhancement** - start with observability, then documentation, then automation

---

<!-- SECTION:6:PRD_GENERATION -->

# 6. PRD GENERATION

Once Core Questions are answered, ONE_SHOT generates a **Project Requirements Document**.

## 6.0 Agent Rules for PRD-First Changes

When `ONE_SHOT.md` is present in a repo:

- Any non-trivial change MUST:
  1. Re-check relevant Core Questions
  2. Update the PRD
  3. Only then modify code/tests/scripts

## 6.1 PRD Schema (Required Shape)

Every ONE_SHOT PRD MUST follow this structure:

1. **Overview** - 3–8 sentences summarizing what, for whom, why now
2. **Problem & Reality Check** - Core problem, current workaround, 80/20 solution
3. **Philosophy & Constraints** - Project philosophy, non-goals, mode
4. **Features** - 3–7 capabilities, marked `v1` or `later`
5. **Data Model** - YAML examples, formal schema
6. **Storage & Upgrade Path** - Storage choice, scale, tier label, upgrade trigger
7. **Interfaces** - CLI commands, API routes, or library API
8. **Architecture & Deployment** - Project type, stack, where it runs, deployment path
9. **Testing Strategy** - Testing level, what gets tested
10. **AI & Agents** (if applicable) - Whether AI is used, provider/model, cost target
11. **v1 Scope vs Future Work** - v1 features, deferred work, "done when..."

## 6.2 PRD Approval

**You say**:
```
PRD approved. Execute autonomous build.
```

At that point the agent stops asking questions and moves to execution.

---

<!-- SECTION:7:AUTONOMOUS_EXECUTION -->

# 7. AUTONOMOUS EXECUTION PIPELINE

ONE_SHOT's build loop, assuming PRD is approved.

## 7.1 Phase 0: Repo & Skeleton

- Create GitHub repo with the name from Q13
- Clone into `~/github/[project]`
- Initialize project layout
- Add `.editorconfig`, `.gitignore`
- **Create LLM-OVERVIEW.md**
- **Initialize checkpoint tracking**:

### Initialize Checkpoint Tracking

```bash
# Create checkpoint directory structure
mkdir -p .oneshot/checkpoints
touch .oneshot/checkpoint.yaml
echo "# ONE_SHOT Decision Log - $(date -I)" > .oneshot/decisions.log
```

**Initial checkpoint.yaml**:
```yaml
checkpoint:
  oneshot_version: "2.0"      # Spec version this project uses
  checkpoint_schema: "1.0"    # Checkpoint format version
  project: [PROJECT_NAME]
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

### Required Initial Files

**README.md**:
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

**LLM-OVERVIEW.md** (NEW in v1.8):
```markdown
# LLM-OVERVIEW: [Project Name]

This file provides complete context for any LLM to understand this project.
Updated: [DATE]

## What This Project Is
[2-3 paragraph explanation]

## Current State
[What works, what's in progress, what's broken]

## Key Files and Their Purpose
[File: Purpose list]

## Architecture Decisions
[Why we chose X over Y]

## How to Contribute
[What an AI should know before making changes]
```

## 7.2 Phase 1: Core Implementation (Data-First Order)

**Implementation order is critical. Follow this sequence**:

1. **Define Data Models** - `models.py` with complete data structures
2. **Define Storage Schema** - Database schema or file format
3. **Implement Storage Layer** - CRUD operations
4. **Build Processing Logic** - Business logic
5. **Create Interface** - CLI, API, or UI

## 7.3 Phase 2: Tests

- Write tests for critical paths
- Run tests and fix failures
- Document test commands in README

## 7.4 Phase 3: Scripts

Create required automation scripts:

```bash
scripts/
├── setup.sh     # One-time setup (deps, DB, secrets)
├── start.sh     # Start the service
├── stop.sh      # Stop the service
├── status.sh    # Check service health
└── process.sh   # Batch/recurring work (if needed)
```

## 7.5 Phase 4: Deployment

- Create systemd unit file (if 24/7 service)
- Create Docker Compose (if containerized)
- Document deployment in README
- Test health endpoints

---

<!-- SECTION:7.6:RESUME_PROTOCOL -->

## 7.6 SESSION CONTINUITY: RESUME PROTOCOL

Sessions get interrupted. Context windows fill up. Machines crash. This section ensures work survives.

### 7.6.1 Checkpoint System

**Every ONE_SHOT project maintains a checkpoint file**:

```yaml
# .oneshot/checkpoint.yaml
checkpoint:
  oneshot_version: "1.9"      # Spec version this was created under
  checkpoint_schema: "1.0"    # Checkpoint format version
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
      - "Define storage schema"
    in_progress:
      - task: "Implement storage layer"
        status: "CRUD operations 3/5 done"
        files_modified:
          - src/storage.py
          - tests/test_storage.py
    pending:
      - "Build processing logic"
      - "Create CLI interface"
      - "Write tests"

  decisions_made:
    - decision: "Use SQLite over files"
      reason: "Need querying, expect 10K+ records"
      date: 2024-12-06

  blockers: []

  files_changed_this_session:
    - src/models.py
    - src/storage.py
```

### 7.6.2 When to Update Checkpoint

**Agent MUST update checkpoint**:
- After completing any task
- Before context window reaches 70% capacity
- When switching to a new phase
- When hitting a blocker
- At end of any session

### 7.6.3 Resume Command

**User says**: `Resume from checkpoint`

**Agent MUST**:
1. Read `.oneshot/checkpoint.yaml`
2. Read `LLM-OVERVIEW.md` for full context
3. Read the PRD for requirements
4. Summarize current state to user
5. Confirm next action before proceeding

**Resume summary format**:
```markdown
## Session Resume

**Project**: [name]
**Last checkpoint**: [timestamp]

**Completed**:
- [x] Task 1
- [x] Task 2

**In Progress**:
- [ ] Task 3 (50% - [status details])

**Next Action**: [exact next step]

Ready to continue?
```

### 7.6.4 Checkpoint Directory Structure

```
.oneshot/
├── checkpoint.yaml      # Current state
├── checkpoints/         # Historical checkpoints (optional)
│   └── YYYY-MM-DD.yaml
└── decisions.log        # Running log of decisions made
```

---

<!-- SECTION:7.7:HANDOFF_PROTOCOL -->

## 7.7 SESSION HANDOFF PROTOCOL

When switching agents (Claude Code → Cursor), models, or machines, use this standardized handoff.

### 7.7.1 Quick Handoff Template

When ending a session or switching contexts, generate this:

```markdown
## HANDOFF STATE
**Project**: [project-name]
**Timestamp**: [ISO timestamp]
**Agent**: [Claude Code / Cursor / etc.]

### Last Completed
- [Phase X, Task Y - specific description]

### Currently Blocked On (if any)
- [Issue description]
- [What was tried]
- [Why it failed]

### Next Action (BE SPECIFIC)
1. Open file: `[exact path]`
2. Find function: `[function name]`
3. Do: [exact change needed]

### Files Changed This Session
- `src/storage.py` - Added CRUD operations
- `tests/test_storage.py` - Added 5 test cases

### Decisions Made This Session
- Chose X over Y because Z

### Context the Next Agent Needs
- [Important detail 1]
- [Important detail 2]
```

### 7.7.2 Handoff Triggers

**Generate handoff when**:
- User says "handoff", "switch agent", "take a break"
- Context window exceeds 80%
- Agent detects it's looping or stuck
- Before any session end

### 7.7.3 Receiving a Handoff

**When starting with a handoff, agent MUST**:
1. Read the handoff document
2. Read `LLM-OVERVIEW.md`
3. Read the PRD
4. Verify "Next Action" is still valid
5. Confirm understanding before proceeding

### 7.7.4 Handoff vs LLM-OVERVIEW vs Checkpoint

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| LLM-OVERVIEW.md | Full project context | Milestones |
| Handoff | Session state transfer | Every session |
| Checkpoint | Machine-readable state | Continuous |

**Use together**: LLM-OVERVIEW for "what is this project", Handoff for "what was I just doing", Checkpoint for precise state recovery.

---

# 8-10. DEPLOYMENT, OPS, AI INTEGRATION

## 8. Health Endpoints

Every long-running service needs:

```python
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "dependencies": {
            "database": check_db(),
            "redis": check_redis() if REDIS_ENABLED else "disabled"
        }
    }

@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint."""
    return {
        "uptime_seconds": get_uptime(),
        "requests_total": REQUEST_COUNT,
        "errors_total": ERROR_COUNT
    }
```

## 9. Observability Patterns

### Status Script Template

```bash
#!/usr/bin/env bash
# scripts/status.sh

echo "=== [Project] Status ==="
echo "Timestamp: $(date -Iseconds)"

# Service status
if systemctl is-active --quiet project; then
    echo "Service: RUNNING"
else
    echo "Service: STOPPED"
fi

# Health check
if curl -sf http://localhost:8000/health > /dev/null; then
    echo "Health: HEALTHY"
else
    echo "Health: UNHEALTHY"
fi

# Resource usage
echo "Memory: $(free -h | awk '/Mem:/ {print $3 "/" $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2}')"
```

## 10. AI Cost Management

```python
import sqlite3
from datetime import datetime

class AIUsageTracker:
    def __init__(self, db_path: str = "ai_usage.db"):
        self.db = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                model TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                estimated_cost REAL
            )
        """)
        self.db.commit()

    def log(self, model: str, input_tokens: int, output_tokens: int):
        cost = self._estimate_cost(model, input_tokens, output_tokens)
        self.db.execute("""
            INSERT INTO usage (timestamp, model, input_tokens, output_tokens, estimated_cost)
            VALUES (?, ?, ?, ?, ?)
        """, (datetime.utcnow().isoformat(), model, input_tokens, output_tokens, cost))
        self.db.commit()

    def monthly_cost(self) -> float:
        result = self.db.execute("""
            SELECT SUM(estimated_cost) FROM usage
            WHERE timestamp >= date('now', 'start of month')
        """).fetchone()
        return result[0] or 0.0
```

---

# 11. CANONICAL EXAMPLES

## 11.1 Minimal: Local-Only CLI Finance Tracker

- **Type**: A (CLI Tool)
- **Storage**: SQLite
- **No AI, no web, local only**

```bash
finance import transactions.csv
finance categorize
finance report --month 2024-01
finance export --category groceries
```

## 11.2 Medium: Non-AI Web App Dashboard

- **Type**: C (Web Application)
- **Storage**: PostgreSQL
- **Web**: FastAPI backend + simple frontend
- **Deployment**: systemd + Tailscale

## 11.3 Complex: AI Code Review with Subagents

- **Type**: F (AI-Powered Web Application)
- **AI**: Yes, Agent SDK with MCP

---

# 12. GOAL VS BASELINE

## 12.1 Baseline Contract

For every ONE_SHOT project:
- A PRD is generated and kept in the repo
- An LLM-OVERVIEW.md exists (NEW in v1.8)
- Code compiles/runs for the v1 scope
- At least minimal test suite for critical paths
- Long-running services have `/health`
- README explains how to run and deploy

## 12.2 Goal State (Stretch)

- Fully autonomous build from PRD to deployed system
- Clean commits per milestone
- Integrated AI agents where appropriate
- Robust test coverage and CI

---

# 13. ANTI-PATTERNS (Learn from Past Mistakes)

## 13.1 Complexity Creep

**Anti-Pattern**: Adding abstraction layers "for flexibility"

```python
# Bad: Over-engineered (1,363 lines)
class AbstractDataProviderFactory:
    def create_provider(self, provider_type: str) -> AbstractDataProvider:
        ...

# Good: Simple and direct (104 lines)
def get_data(source: str) -> dict:
    if source.endswith('.json'):
        return json.load(open(source))
    elif source.endswith('.yaml'):
        return yaml.safe_load(open(source))
```

**Rule**: Only add abstraction when you have 3+ implementations

## 13.2 Building Before Validating

**Always**: Phase 0 (Validate) → Phase 1 (Build)

## 13.3 Over-Engineering Storage

**Anti-Pattern**: Use PostgreSQL for everything

**Better Pattern**: Files → SQLite → PostgreSQL (only when needed)

**Real-world validation**: Divorce project runs 135K records in SQLite with sub-second queries

## 13.4 No Rollback Plan

**Always have**: `scripts/rollback.sh` or equivalent

---

<!-- SECTION:13.5:FAILURE_RECOVERY -->

## 13.5 FAILURE MODES & RECOVERY

When things go wrong, follow these recovery patterns.

### 13.5.1 Build Failure Recovery

```yaml
recovery_build_failure:
  trigger: "Tests fail, build errors, runtime crashes"
  steps:
    1_isolate:
      action: "Identify failing component"
      commands:
        - "pytest tests/ -x --tb=short"  # Stop at first failure
        - "git diff HEAD~1"              # What changed?
    2_rollback:
      action: "Revert to last known good state"
      commands:
        - "git stash"                    # Save current changes
        - "git checkout HEAD~1"          # Go back one commit
        - "pytest tests/"                # Verify it works
    3_bisect:
      action: "Find the breaking change"
      commands:
        - "git bisect start"
        - "git bisect bad HEAD"
        - "git bisect good [last-good-commit]"
    4_fix:
      action: "Apply minimal fix"
      rule: "Fix the bug, don't refactor"
    5_verify:
      action: "Confirm fix works"
      commands:
        - "pytest tests/"
        - "git stash pop"  # Restore changes if any
```

### 13.5.2 Agent Confusion Recovery

```yaml
recovery_agent_confusion:
  trigger: "Agent loops, gives inconsistent answers, seems lost"
  symptoms:
    - "Repeating same action without progress"
    - "Contradicting previous statements"
    - "Asking questions already answered"
    - "Generating code that ignores existing patterns"
  steps:
    1_restate:
      prompt: |
        STOP. Let's reset.
        Current phase: [Phase X]
        Current task: [Task Y]
        Reference: ONE_SHOT.md Section [N]
    2_narrow:
      prompt: |
        Focus only on: src/storage.py
        Specific change needed: [exact change]
        Do not touch any other files.
    3_verify:
      prompt: |
        Before proceeding, tell me:
        1. What file are you editing?
        2. What specific change are you making?
        3. Why?
    4_checkpoint:
      prompt: "Update .oneshot/checkpoint.yaml with current state"
```

### 13.5.3 Context Window Exhaustion

```yaml
recovery_context_exhaustion:
  trigger: "Agent responses get shorter, misses context, forgets decisions"
  prevention:
    - "Use checkpoint.yaml for state"
    - "Keep LLM-OVERVIEW.md updated"
    - "Don't paste entire files - use line ranges"
  recovery:
    1_handoff:
      prompt: "Generate a HANDOFF STATE document for session transfer"
    2_new_session:
      prompt: |
        New session. Read these files in order:
        1. ONE_SHOT.md (skim, you know this)
        2. LLM-OVERVIEW.md (full read)
        3. .oneshot/checkpoint.yaml
        4. [handoff document]
        Then confirm your understanding.
```

### 13.5.4 Dependency Hell

```yaml
recovery_dependency_hell:
  trigger: "Package conflicts, version mismatches, missing deps"
  steps:
    1_isolate:
      action: "Create clean environment"
      commands:
        - "python -m venv .venv-clean"
        - "source .venv-clean/bin/activate"
    2_minimal:
      action: "Install only what PRD specifies"
      commands:
        - "pip install [core-deps-only]"
    3_add_incrementally:
      action: "Add deps one at a time, test after each"
    4_pin:
      action: "Pin working versions"
      commands:
        - "pip freeze > requirements.lock"
```

### 13.5.5 Recovery Decision Tree

```
Problem detected
    │
    ├─ Build/test failure?
    │   └─ → Section 13.5.1
    │
    ├─ Agent acting weird?
    │   └─ → Section 13.5.2
    │
    ├─ Responses degrading?
    │   └─ → Section 13.5.3
    │
    ├─ Dependency issues?
    │   └─ → Section 13.5.4
    │
    └─ Unknown?
        └─ → Generate handoff, start fresh session
```

---

# 14. META: LIVING IDEA REPOSITORY

ONE_SHOT is also your idea sink for future improvements.

## 14.1 Rules for Updating This File

- **You don't hand-edit structure**
- Tell the agent: "Add this concept: [idea]"
- The agent integrates new ideas, keeps Core Questions compact, avoids duplication

## 14.2 File Size & Growth Guidelines

**Current state**: ~13K tokens (~50K characters, ~3,000 lines)
**Growth ceiling**: 30-40K tokens before considering restructure

### Why Single File Works

1. **Agent loads once**: File is parsed at session start, not re-read constantly
2. **Context window is large**: 100K+ tokens available; we use ~10-15%
3. **Simplicity**: One file to clone, one file to update, one source of truth

### When Single File Breaks Down

Watch for these signals:
- Agent "forgets" later sections without explicit references
- Part IV (appendix) exceeds 40% of total file size
- You find yourself saying "see Section X" constantly
- New users are overwhelmed finding relevant sections

### Growth Rules

| Content Type | Where to Add | When to Add |
|--------------|--------------|-------------|
| Core patterns | Part I (Sections 0-7) | Used in >50% of projects |
| Supporting patterns | Part I (Sections 8-16) | Used in >25% of projects |
| Reference material | Part II-III | Needed but not core |
| Skills & templates | Part IV (Appendix) | Lookup only |

### If Restructure Needed (Future)

If file exceeds 40K tokens, consider:

```
ONE_SHOT.md          # Core spec (Parts I-III, ~25K tokens)
SKILLS_REFERENCE.md  # Part IV extracted (~15K tokens)
```

With ONE_SHOT.md containing:
```yaml
companion_files:
  skills: SKILLS_REFERENCE.md
  load: "On demand when skills needed"
```

**But not yet.** Current size is healthy. Revisit at 30K tokens.

---

# 15. VERSION HISTORY

- **v2.0** (2024-12-06)
  - **ARCHITECTURE**: File structure optimized for long-term growth
    - Added growth ceiling guidance (~30-40K tokens max)
    - Added priority ordering for agent attention
    - Marked Part IV as appendix (skim, don't memorize)
    - Added section markers for navigation (`<!-- SECTION:X:NAME -->`)
  - **NEW**: Micro mode explicit flow (Section 2.1)
    - Complete fast-path for <100 line scripts
    - 2 questions → single file output
  - **NEW**: oneshot_doctor.sh v2.0 (Section 5.3)
    - Project health validation script
    - Checks required files, git status, secrets safety
  - **NEW**: Checkpoint initialization in Phase 0
    - .oneshot/ directory created at project start
    - checkpoint.yaml includes oneshot_version field
  - **NEW**: Hard stop override pattern
    - Explicit `OVERRIDE: [stop_id]` syntax
    - All overrides logged to decisions.log
  - **ENHANCED**: Reference sections marked for on-demand loading
  - **RATIONALE**: Prepare ONE_SHOT for continued growth while maintaining single-file simplicity. Agent attention is finite; prioritize core flow.

- **v1.9** (2024-12-06)
  - **MAJOR**: PRIME DIRECTIVE - Front-load everything
    - New philosophy: User's time is precious, agent compute is cheap
    - All information gathering happens UPFRONT before any code
    - User can walk away after "PRD approved. Execute autonomous build."
  - **NEW**: Session Continuity (Section 7.6-7.7)
    - Resume Protocol with checkpoint.yaml
    - Handoff Protocol for switching agents/models
    - Recovery patterns for common failures
  - **NEW**: Tiered Questions (Section 2.0)
    - Must-answer vs defaults-available questions
    - Yolo mode for experienced users (5 questions → full project)
    - Micro mode for single-file scripts
  - **NEW**: Hard Stops in YAML header
    - Explicit triggers where agent MUST pause for approval
    - Storage upgrades, auth changes, production deploys
  - **NEW**: Agent Compatibility notes
    - Tested configurations (Claude Code, Cursor)
    - Model selection guidance (Opus vs Sonnet vs Haiku)
  - **NEW**: Failure Recovery (Section 13.5)
    - Build failure, agent confusion, context exhaustion, dependency hell
    - Decision tree for problem diagnosis
  - **RATIONALE**: Real-world sessions get interrupted. This version ensures work survives and users spend minimal time babysitting agents.

- **v1.8** (2024-12-06)
  - **MAJOR**: Consolidated everything into single file
    - All 8 skills now inline (Section 19)
    - Secrets management included (Section 18)
    - No more external file references
  - **NEW**: LLM-OVERVIEW standard (Section 17)
    - Every ONE_SHOT project gets `LLM-OVERVIEW.md`
    - Complete project context for any LLM
    - Enables off-site/independent AI conversations about the project
  - **NEW**: Consolidation philosophy in contract YAML
  - **ENHANCED**: Table of contents for navigation
  - **RATIONALE**: Single file means any AI can understand the entire system from one document

- **v1.7** (2024-12-02)
  - Added machine-readable `ONE_SHOT_CONTRACT` header
  - Promoted Q0 Mode and Q2.5 Reality Check to hard gates
  - Clarified PRD-first evolution
  - Added Section 5.5: Using ONE_SHOT with Existing Projects

- **v1.6** (2024-12-02)
  - Added Q0 Mode (Tiny / Normal / Heavy)
  - Project Invariants checklist
  - Rigid PRD Schema
  - Claude Code subagent support

- **v1.5** (2024-11-26)
  - Integrated patterns from 8 real-world projects
  - Added Reality Check questions (Q2.5)
  - Added Upgrade Path Principle
  - Added Anti-Patterns section

---

# 16. CLAUDE SKILLS INTEGRATION

ONE_SHOT serves as the **single reference document** for Claude Skills.

**In v1.8**: All skills are now documented inline in Section 19. No need to check separate files.

---

<!-- ONESHOT_CORE_END -->

---

# PART II: LLM-OVERVIEW STANDARD

<!-- SECTION:17:LLM_OVERVIEW -->

# 17. LLM-OVERVIEW: THE PROJECT CONTEXT FILE

## 17.1 What Is LLM-OVERVIEW.md?

**Every ONE_SHOT project MUST have an `LLM-OVERVIEW.md` file.**

This file exists to give ANY LLM (Claude, GPT, Gemini, etc.) complete context about the project without needing access to the full repository.

**Use cases**:
- Get a second opinion from a different AI
- Have an off-site conversation about the project
- Onboard a new AI assistant quickly
- Document project state at milestones
- Enable async/parallel AI assistance

## 17.2 LLM-OVERVIEW Template

```markdown
# LLM-OVERVIEW: [Project Name]

> This file provides complete context for any LLM to understand this project.
> **Last Updated**: [DATE]
> **Updated By**: [Human/AI name]
> **ONE_SHOT Version**: 1.8

---

## 1. WHAT IS THIS PROJECT?

### One-Line Description
[A tool that does X for Y people]

### The Problem It Solves
[What's painful or impossible without this? What's the workaround?]

### Current State
- **Status**: [In Development / Alpha / Beta / Production]
- **Version**: [X.Y.Z]
- **Last Milestone**: [What was accomplished]
- **Next Milestone**: [What's being worked on]

---

## 2. ARCHITECTURE OVERVIEW

### Project Type
[CLI Tool / Web App / Data Pipeline / etc.]

### Tech Stack
```
Language:    [Python 3.11 / Node 20 / etc.]
Framework:   [FastAPI / Express / etc.]
Database:    [SQLite / PostgreSQL / etc.]
Deployment:  [Local / systemd / Docker / etc.]
```

### Key Components
| Component | Purpose | Location |
|-----------|---------|----------|
| [Component 1] | [What it does] | [path/to/file] |
| [Component 2] | [What it does] | [path/to/file] |

### Data Flow
```
[Input] → [Processing] → [Storage] → [Output]
```

---

## 3. KEY FILES AND THEIR PURPOSE

### Core Files
- `src/main.py` - Entry point, CLI commands
- `src/models.py` - Data models
- `src/storage.py` - Database operations
- `src/processing.py` - Business logic

### Configuration
- `config.yaml` - Application settings
- `.env` - Secrets (from secrets-vault)

### Scripts
- `scripts/setup.sh` - One-time setup
- `scripts/start.sh` - Start service
- `scripts/stop.sh` - Stop service
- `scripts/status.sh` - Check health

---

## 4. CURRENT STATE OF DEVELOPMENT

### What Works
- [Feature 1 - fully implemented]
- [Feature 2 - fully implemented]

### What's In Progress
- [Feature 3 - 50% complete, blocked on X]
- [Feature 4 - design phase]

### What's Broken
- [Issue 1 - description and workaround]
- [Issue 2 - low priority, can ignore]

### Known Technical Debt
- [Debt 1 - why it exists, when to fix]
- [Debt 2 - why it exists, when to fix]

---

## 5. ARCHITECTURE DECISIONS

### Why [Major Choice 1]?
**Decision**: We use [X] instead of [Y]
**Reason**: [Explanation]
**Trade-offs**: [What we gave up]
**Upgrade Trigger**: [When we'd reconsider]

### Why [Major Choice 2]?
[Same format]

---

## 6. HOW TO WORK ON THIS PROJECT

### Getting Started
```bash
# Clone and setup
git clone [repo]
cd [project]
./scripts/setup.sh

# Run
./scripts/start.sh

# Test
pytest tests/
```

### Making Changes

**Before changing code**:
1. Check if PRD needs updating
2. Understand current architecture
3. Follow data-first implementation order

**Code conventions**:
- [Style guide reference]
- [Testing requirements]
- [Documentation requirements]

### Common Tasks

| Task | Command/Process |
|------|-----------------|
| Add new feature | Update PRD → Implement → Test → Document |
| Fix bug | Reproduce → Isolate → Fix → Test → Document |
| Deploy | Run tests → Build → Deploy → Verify health |

---

## 7. CONTEXT FOR AI ASSISTANTS

### When Helping With This Project

**DO**:
- Follow ONE_SHOT patterns (PRD-first, data-first implementation)
- Check existing code before suggesting changes
- Maintain current conventions
- Update documentation when changing code
- Use existing abstractions before creating new ones

**DON'T**:
- Introduce PostgreSQL without explicit approval (we use [current storage])
- Add abstraction layers "for flexibility"
- Ignore the Reality Check principle
- Skip validation before building

### Current Priorities
1. [Priority 1 - context]
2. [Priority 2 - context]
3. [Priority 3 - context]

### Off-Limits (Don't Touch)
- [Thing 1 - reason]
- [Thing 2 - reason]

---

## 8. REFERENCE LINKS

- **Repository**: [GitHub URL]
- **ONE_SHOT Spec**: ONE_SHOT.md in this repo
- **PRD**: PRD.md in this repo
- **External Docs**: [Links to relevant documentation]

---

## 9. RECENT CHANGES LOG

| Date | Change | Impact |
|------|--------|--------|
| [DATE] | [What changed] | [How it affects the project] |
| [DATE] | [What changed] | [How it affects the project] |

---

## 10. QUESTIONS AN AI MIGHT ASK

**Q: What's the main entry point?**
A: [Answer]

**Q: How is authentication handled?**
A: [Answer]

**Q: Where is data stored?**
A: [Answer]

**Q: How do I run tests?**
A: [Answer]

**Q: What's the deployment process?**
A: [Answer]

---

*This LLM-OVERVIEW was last verified against the actual codebase on [DATE].*
```

## 17.3 When to Update LLM-OVERVIEW.md

**Update during**:
- Major milestone completion
- Architecture changes
- Before seeking external AI help
- After significant refactoring
- When onboarding new contributors

**Don't update**:
- Every commit
- Minor bug fixes
- Typo corrections
- Test additions only

## 17.4 Agent Rules for LLM-OVERVIEW

- MUST create LLM-OVERVIEW.md during Phase 0 (Repo & Skeleton)
- MUST update when making architectural changes
- MUST keep accurate - outdated LLM-OVERVIEW is worse than none
- SHOULD include enough context that another AI could help without repo access

---

# PART III: SECRETS MANAGEMENT

<!-- SECTION:18:SECRETS_MANAGEMENT -->

> **📋 REFERENCE SECTION**: Load on demand.
> Only relevant when project needs secrets management.
> Skip if Q19 answer is "A. No secrets needed".

# 18. SECRETS MANAGEMENT (SOPS + Age)

## 18.1 Central Secrets Vault (Recommended)

**Philosophy**: Store ONE Age key in 1Password, get ALL secrets automatically.

### One-Time Setup

1. **Install tools**:
```bash
# Ubuntu/Debian
sudo apt install age sops

# Mac
brew install age sops
```

2. **Generate Age key** (or get from 1Password):
```bash
mkdir -p ~/.age
age-keygen -o ~/.age/key.txt
# Save the public key (starts with age1...) and store in 1Password
```

3. **Clone secrets vault**:
```bash
git clone git@github.com:Khamel83/secrets-vault.git ~/github/secrets-vault
```

4. **Create `.sops.yaml`** in secrets-vault:
```yaml
creation_rules:
  - path_regex: .*\.encrypted$
    age: 'age1your_public_key_here'
```

### Daily Usage

**Decrypt secrets to project**:
```bash
sops --decrypt ~/github/secrets-vault/secrets.env.encrypted > .env
source .env
```

**Update secrets**:
```bash
cd ~/github/secrets-vault
sops secrets.env.encrypted
# Edit in your editor, save, auto-encrypted
git add . && git commit -m "Update secrets" && git push
```

## 18.2 Standalone SOPS (Per-Project)

For work projects or isolated secrets:

```bash
# In your project directory
mkdir -p .sops
age-keygen -o .sops/key.txt

# Create .sops.yaml
cat > .sops.yaml << 'EOF'
creation_rules:
  - path_regex: \.encrypted$
    age: 'age1your_project_key_here'
EOF

# Create encrypted secrets
sops secrets.env.encrypted

# Decrypt for use
sops --decrypt secrets.env.encrypted > .env
```

## 18.3 Sharing ONE_SHOT with Others

### For Open Source

1. **Include `.env.example`** with all variable names (no values)
2. **Document SOPS setup** in README
3. **Never commit**: `.env`, `secrets.env`, `*.key`, `*_key`

### For Teams

1. **Share encrypted vault access** (add their public age key to `.sops.yaml`)
2. **Each person has their own Age key**
3. **Vault can be decrypted by any authorized key**

### .gitignore Template

```gitignore
# Secrets (NEVER commit)
.env
.env.local
.env.*.local
secrets.env
*.key
*_key
key.txt
.age/

# Allow examples
!.env.example
!secrets.env.example

# SOPS encrypted files ARE safe to commit
!*.encrypted
```

---

# PART IV: SKILLS REFERENCE (APPENDIX)

<!-- SECTION:19:SKILLS_REFERENCE -->

> **📋 APPENDIX NOTICE**: This section is REFERENCE MATERIAL.
>
> **Agent behavior**: Skim on initial load. Reference specific skills only when:
> - User explicitly mentions a skill by name
> - Task matches a skill's "When to Use" trigger
> - User asks "is there a skill for X?"
>
> **Do NOT** memorize all skill details. **DO** know they exist for lookup.

---

# 19. CLAUDE CODE SKILLS (INLINE REFERENCE)

All 8 ONE_SHOT skills are documented here for reference. These skills are also available in `.claude/skills/` as separate files, but this inline reference means any AI reading this file has complete context.

---

## 19.1 PROJECT-INITIALIZER

**Name**: `project-initializer`
**Purpose**: Bootstraps new projects with ONE_SHOT standards

### When to Use
- User says "initialize new project" or "start new project"
- User asks to "set up project with ONE_SHOT standards"
- Starting any new development effort

### What It Does

1. **Gathers project information**: Name, type, stack, purpose, scope
2. **Creates directory structure** based on project type
3. **Initializes git** with proper `.gitignore`
4. **Creates CLAUDE.md** with project-specific guidance
5. **Creates README.md** with Quick Start
6. **Creates LLM-OVERVIEW.md** (NEW in v1.8)
7. **Sets up secrets management** (SOPS integration)
8. **Configures quality tools** (linting, formatting, testing)
9. **Creates documentation structure** (`docs/architecture/`, ADR template)
10. **Makes initial commit**

### Directory Structures by Project Type

**Web Application**:
```
project-name/
├── .claude/
│   ├── CLAUDE.md
│   └── skills/
├── src/
│   ├── components/
│   ├── pages/
│   └── utils/
├── tests/
├── docs/
├── LLM-OVERVIEW.md
├── README.md
└── package.json
```

**CLI Tool**:
```
project-name/
├── .claude/
│   └── CLAUDE.md
├── cmd/
├── internal/
├── tests/
├── docs/
├── scripts/
├── LLM-OVERVIEW.md
├── README.md
└── Makefile
```

**API/Backend Service**:
```
project-name/
├── .claude/
│   └── CLAUDE.md
├── cmd/
├── internal/
├── api/
├── tests/
├── docs/
│   └── api/
├── LLM-OVERVIEW.md
├── README.md
└── docker-compose.yml
```

---

## 19.2 FEATURE-PLANNER

**Name**: `feature-planner`
**Purpose**: Breaks down feature requests into implementable plans

### When to Use
- User requests "plan this feature"
- User describes a new feature or enhancement
- Complex feature needs decomposition
- User says "break this down" or "create a plan"

### Planning Methodology

1. **Understand the feature**: What problem does it solve? Who uses it?
2. **Break down into components**: Frontend, backend, database, infrastructure, testing, documentation
3. **Create task list**: Ordered by dependencies
4. **Identify dependencies**: What must be done first?
5. **Estimate complexity**: Simple / Medium / Complex
6. **Risk assessment**: What could go wrong?
7. **Testing strategy**: How to verify it works?

### Output Format

```markdown
# Feature Plan: [Feature Name]

## Overview
[What this feature does and why]

## Components
1. [Component 1]
2. [Component 2]

## Tasks (ordered)
- [ ] Task 1 (prerequisite for 2, 3)
- [ ] Task 2 (depends on 1)
- [ ] Task 3 (depends on 1)

## Dependencies
- External: [APIs, libraries]
- Internal: [Other features, services]

## Risks
- Risk 1: [Description] → Mitigation: [How to handle]

## Testing Strategy
- Unit tests for [X]
- Integration tests for [Y]
- Manual testing for [Z]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

---

## 19.3 GIT-WORKFLOW

**Name**: `git-workflow`
**Purpose**: Automates git operations with conventional commits

### When to Use
- User asks to commit changes
- User wants to create a PR
- User mentions conventional commits
- Git workflow automation needed

### Conventional Commits Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code change without feature/fix
- `test`: Adding tests
- `chore`: Maintenance tasks
- `perf`: Performance improvement
- `ci`: CI/CD changes

### Commit Workflow

1. **Review changes**: `git status`, `git diff`
2. **Stage files**: `git add <files>` (be selective)
3. **Create commit**: Use conventional format
4. **Push changes**: `git push`

### Branch Naming

```
feature/[ticket-id]-short-description
fix/[ticket-id]-short-description
docs/update-readme
chore/update-dependencies
```

### PR Template

```markdown
## Summary
[2-3 bullet points]

## Changes
- Change 1
- Change 2

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing done

## Screenshots (if UI changes)
[Before/After]
```

---

## 19.4 CODE-REVIEWER

**Name**: `code-reviewer`
**Purpose**: Comprehensive code review including quality and security

### When to Use
- User asks to review code
- User mentions code review or PR review
- User asks about security issues
- Before merging significant changes

### Review Checklist

**Code Quality**:
- [ ] DRY - No repeated code blocks
- [ ] KISS - Simplest solution that works
- [ ] YAGNI - No speculative features

**Security (OWASP Top 10)**:
- [ ] A01: Broken Access Control
- [ ] A02: Cryptographic Failures
- [ ] A03: Injection (SQL, Command, XSS)
- [ ] A04: Insecure Design
- [ ] A05: Security Misconfiguration
- [ ] A06: Vulnerable Components
- [ ] A07: Authentication Failures
- [ ] A08: Software/Data Integrity Failures
- [ ] A09: Security Logging Failures
- [ ] A10: SSRF

**Best Practices**:
- [ ] Error handling is appropriate
- [ ] Logging is useful but not excessive
- [ ] Tests cover critical paths
- [ ] Documentation is updated

### Output Format

```markdown
## Code Review: [File/PR Name]

### Critical Issues
- **[Location]**: [Issue description]
  - **Why it matters**: [Impact]
  - **Fix**: [How to resolve]

### Important Suggestions
- **[Location]**: [Suggestion]
  - **Benefit**: [Why this helps]

### Minor Improvements
- [Improvement 1]
- [Improvement 2]

### What's Good
- [Positive observation 1]
- [Positive observation 2]
```

---

## 19.5 DOCUMENTATION-GENERATOR

**Name**: `documentation-generator`
**Purpose**: Generates READMEs, API docs, ADRs, and project guides

### When to Use
- User asks to generate documentation
- User mentions README, API docs, or ADR
- New project needs documentation structure
- Documentation updates needed after changes

### Documentation Types

1. **README.md**: User-facing, getting started
2. **LLM-OVERVIEW.md**: AI context file (NEW in v1.8)
3. **ADR (Architecture Decision Record)**: Why we chose X
4. **API Documentation**: Endpoints, request/response
5. **Developer Guide**: How to contribute
6. **CLAUDE.md**: AI assistant guidance

### ADR Template (Nygard Format)

```markdown
# ADR-[NUMBER]: [Title]

**Date**: YYYY-MM-DD
**Status**: [Proposed | Accepted | Deprecated | Superseded]

## Context
[What is the issue we're facing?]

## Decision
[What is the change we're proposing?]

## Rationale
[Why is this the best approach?]

## Consequences

### Positive
- [Benefit 1]

### Negative
- [Trade-off 1]

## Alternatives Considered
- Alternative 1: [Description] - Rejected because [reason]
```

---

## 19.6 SECRETS-VAULT-MANAGER

**Name**: `secrets-vault-manager`
**Purpose**: Automates secrets management with SOPS + Age

### When to Use
- User mentions secrets, environment variables, or API keys
- User asks to set up secrets-vault
- New project initialization needing secrets
- User mentions decrypting secrets

### Setup Workflow

1. **Verify Age key exists**: `~/.age/key.txt`
2. **Clone vault**: `git clone git@github.com:Khamel83/secrets-vault.git`
3. **Set up project**: Decrypt secrets to `.env`
4. **Add to .gitignore**: Ensure `.env` is ignored
5. **Verify setup**: Source `.env` and check variables
6. **Document usage**: Add secrets section to README

### Common Operations

**Initial setup**:
```bash
sops --decrypt ~/github/secrets-vault/secrets.env.encrypted > .env
source .env
```

**Refresh secrets**:
```bash
sops --decrypt ~/github/secrets-vault/secrets.env.encrypted > .env
```

**Add new secret**:
```bash
cd ~/github/secrets-vault
sops secrets.env.encrypted
# Add new line: NEW_SECRET=value
# Save and exit
git add . && git commit -m "Add NEW_SECRET" && git push
```

---

## 19.7 SKILL-CREATOR

**Name**: `skill-creator`
**Purpose**: Creates well-structured Claude Code skills

### When to Use
- User explicitly asks to create a skill
- User describes a repetitive workflow to automate
- User wants to package domain knowledge for reuse

### Skill Creation Workflow

1. **Gather requirements**: What should the skill do? When should it be used?
2. **Create directory structure**: `.claude/skills/skill-name/`
3. **Write SKILL.md**: YAML frontmatter + instructions
4. **Create supporting files**: Templates, examples, scripts
5. **Test the skill**: Verify it works as expected
6. **Document**: Keywords, examples, edge cases

### SKILL.md Structure

```markdown
---
name: skill-name
description: Brief description of what this skill does
version: "1.0.0"
allowed-tools: [Bash, Read, Write, Grep, Glob]
---

# Skill Name

You are an expert at [domain].

## When to Use This Skill
- Trigger condition 1
- Trigger condition 2

## Workflow
1. Step 1
2. Step 2
3. Step 3

## Output Format
[Expected output format]

## Keywords
keyword1, keyword2, keyword3
```

---

## 19.8 MARKETPLACE-BROWSER

**Name**: `marketplace-browser`
**Purpose**: Discovers and installs skills from community sources

### When to Use
- User asks to find or search for skills
- User wants to browse the marketplace
- User describes a task and asks "is there a skill for that?"

### Skill Discovery Sources

1. **skillsmp.com**: Official Skills Marketplace
2. **Anthropic official**: Built-in Claude Code skills
3. **Community repositories**:
   - obra/claude-code-skills
   - levnikolaevich/claude-code-skills
   - mhattingpete/claude-skills
   - OneRedOak/claude-code-prompt-repo
   - WSHobson/claude-skill-builder

### Installation Methods

**From marketplace**:
```bash
# Browse available skills
open https://skillsmp.com

# Download skill to local
curl -o .claude/skills/skill-name/SKILL.md https://skillsmp.com/skills/skill-name
```

**From GitHub**:
```bash
# Clone skill repository
git clone https://github.com/author/skill-repo
cp -r skill-repo/skills/* .claude/skills/
```

---

# END OF ONE_SHOT v2.0

---

**ONE_SHOT v2.0: Front-load everything. Execute autonomously. Scale sustainably.**

**Architecture**:
- **Part I (Sections 0-16)**: Core specification - agent keeps hot
- **Part II-III (Sections 17-18)**: Reference material - load on demand
- **Part IV (Section 19)**: Appendix - skim only, lookup when needed

**The Contract**:
```
Micro:  2 questions → single file (2 min)
Yolo:   5 questions → full project (5 min)
Normal: 14 questions → full project (15 min)
Heavy:  14+ questions → full project + AI (20 min)
```

**File Health**:
- Current: ~13K tokens ✅
- Ceiling: 30-40K tokens
- Status: Healthy, room to grow

**100% Free & Open-Source** | **Deploy Anywhere** | **No Vendor Lock-in**

---

*ONE_SHOT v2.0 - Single file. Priority ordered. Built to last.*
