# ONE_SHOT_CONTRACT (do not remove)
```yaml
oneshot:
  version: 1.8

  # NEW IN v1.8: This single file IS the complete reference
  # No external files needed - everything is consolidated here
  consolidation:
    purpose: "Single-file reference for AI/LLM to understand entire ONE_SHOT system"
    includes:
      - core_specification
      - all_skills_inline
      - secrets_management
      - llm_overview_standard
    replaces:
      - "Separate SKILL.md files (now inline)"
      - "CENTRAL_SECRETS.md (now Section 17)"
      - "SOPS_STANDALONE.md (now Section 17)"
      - "SHARING_ONESHOT.md (now Section 18)"

  # NEW IN v1.8: LLM-OVERVIEW standard
  llm_overview:
    purpose: "Every ONE_SHOT project gets an LLM-OVERVIEW.md file"
    content: "Complete project context for a blank-slate LLM"
    update_frequency: "During development milestones, not every commit"
    location: "PROJECT_ROOT/LLM-OVERVIEW.md"

  phases:
    - intake_core_questions
    - generate_prd
    - wait_for_prd_approval
    - autonomous_build

  modes:
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

oneshot_env:
  projects_root: "~/github"
  secrets_vault_repo: "git@github.com:Khamel83/secrets-vault.git"
  secrets_vault_path: "~/github/secrets-vault"
  default_os: "ubuntu-24.04"
  default_user: "ubuntu"
```

# ONE_SHOT: AI-Powered Autonomous Project Builder

**Version**: 1.8
**Philosophy**: Ask everything upfront, then execute autonomously
**Validated By**: 8 real-world projects (135K+ records, 29 services, $1-3/month AI costs)
**Deployment**: OCI Always Free Tier OR Homelab (i5, 16GB RAM, Ubuntu)
**Cost**: $0/month infra (AI optional, low-cost)

---

# TABLE OF CONTENTS

This single file contains EVERYTHING an AI needs to understand and use ONE_SHOT:

**PART I: CORE SPECIFICATION (Sections 0-16)**
- Section 0: How to Use This File
- Section 1: Core Ethos
- Section 2: Core Questions (Q0-Q13)
- Section 3: Defaults & Advanced Options
- Section 4: Optional Web Design & AI
- Section 5: Environment Validation
- Section 6: PRD Generation
- Section 7: Autonomous Execution Pipeline
- Section 8-10: Deployment, Ops, AI Integration
- Section 11-13: Examples, Goals, Anti-Patterns
- Section 14-16: Meta, Version History, Skills Integration

**PART II: LLM-OVERVIEW STANDARD (Section 17)** - NEW IN v1.8
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

## 0.2 What's New in v1.8: Consolidated Single File

**v1.8 consolidates EVERYTHING into this single file:**

- **Skills are inline** (Section 19) - No need to check `.claude/skills/` separately
- **Secrets management included** (Section 18) - SOPS, Age, vault setup all here
- **LLM-OVERVIEW standard** (Section 17) - Every project gets a file that explains itself to any LLM

**Why single file?**
- AI can read ONE file and understand the entire system
- No chasing references across multiple files
- Complete context in one place
- Easier to share and maintain

---

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

# 2. CORE QUESTIONS (REQUIRED FOR ANY PROJECT)

These are the Core 10+. Every project must answer them.

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

# 7. AUTONOMOUS EXECUTION PIPELINE

ONE_SHOT's build loop, assuming PRD is approved.

## 7.1 Phase 0: Repo & Skeleton

- Create GitHub repo with the name from Q13
- Clone into `~/github/[project]`
- Initialize project layout
- Add `.editorconfig`, `.gitignore`
- **Create LLM-OVERVIEW.md** (NEW in v1.8)

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

# 14. META: LIVING IDEA REPOSITORY

ONE_SHOT is also your idea sink for future improvements.

## 14.1 Rules for Updating This File

- **You don't hand-edit structure**
- Tell the agent: "Add this concept: [idea]"
- The agent integrates new ideas, keeps Core Questions compact, avoids duplication

---

# 15. VERSION HISTORY

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

# PART II: LLM-OVERVIEW STANDARD (NEW IN v1.8)

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

# PART IV: SKILLS REFERENCE

# 19. CLAUDE CODE SKILLS (INLINE)

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

# END OF ONE_SHOT v1.8

---

**ONE_SHOT v1.8: One file. Complete context. Infinite possibilities.**

**What's in this file**:
- Complete specification (Sections 0-16)
- LLM-OVERVIEW standard (Section 17)
- Secrets management (Section 18)
- All 8 skills inline (Section 19)

**100% Free & Open-Source** | **Deploy Anywhere** | **No Vendor Lock-in**

---

*This single file IS the complete ONE_SHOT reference. No external files needed.*
