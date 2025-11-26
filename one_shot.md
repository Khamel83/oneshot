# ONE_SHOT: AI-Powered Autonomous Project Builder

**Version**: 1.3
**Philosophy**: Ask everything upfront, then execute autonomously
**Deployment**: OCI Always Free Tier OR Homelab (i5, 16GB RAM, Ubuntu)
**Cost**: $0/month infrastructure (AI features optional, low-cost)
**Core Ethos**: 
- **Free & Open-Source**: Everything built uses FOSS tools
- **Flexible Deployment**: Works on cloud VMs or home hardware
- **No Vendor Lock-in**: Portable across any Linux environment
- **Validate Before Create**: Check dependencies before building
- **WHY Documentation**: Explain decisions, not just code

---

## META: HOW THIS DOCUMENT WORKS

**ONE_SHOT is a living idea repository.**

### The Workflow

```
You (User) → Feed ideas and concepts
     ↓
Claude → Refines, integrates, organizes
     ↓
ONE_SHOT → Grows and evolves
     ↓
You → Use it to build projects autonomously
```

### Rules for This Document

1. **You Don't Edit**: You share ideas, I integrate them
2. **Continuous Refinement**: Every concept you share gets woven into the framework
3. **No Redundancy**: I consolidate overlapping ideas
4. **Maintain Harmony**: New ideas must work with existing components
5. **Version Tracking**: Every major addition gets documented

### How to Contribute Ideas

**Just tell me**:
- "Add this concept: [idea]"
- "I saw this pattern: [link/description]"
- "What if we could: [feature]"
- "This should also handle: [use case]"

**I will**:
- Analyze how it fits with existing framework
- Integrate it into the right section
- Update examples if needed
- Ensure no conflicts
- Document the addition

### What Makes This Special

This isn't just documentation - it's a **self-evolving framework**:
- ✅ Captures your vision across time
- ✅ Integrates new learnings automatically
- ✅ Maintains consistency as it grows
- ✅ Stays practical and actionable
- ✅ Never loses previous insights

**You focus on ideas. I focus on integration.**

---

## CORE ETHOS: FREE & OPEN-SOURCE EVERYTHING

ONE_SHOT is built on the principle that **you should own your infrastructure and tools**. No vendor lock-in, no proprietary dependencies, no monthly fees (except optional AI features).

### The FOSS Stack

**Every project built with ONE_SHOT uses 100% free and open-source software**:

```
┌─────────────────────────────────────────────┐
│           APPLICATION LAYER                  │
│  Python, Node.js, Go, Rust (your choice)    │
│  FastAPI, Flask, Express, etc.              │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│           DATABASE LAYER                     │
│  PostgreSQL, SQLite, Redis (all FOSS)       │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         WEB SERVER LAYER                     │
│  Caddy, Nginx (FOSS reverse proxies)        │
│  Automatic HTTPS via Tailscale certs        │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│        INFRASTRUCTURE LAYER                  │
│  OCI Always Free Tier (cloud)               │
│  OR Homelab (your hardware)                 │
│  Ubuntu 22.04 LTS (FOSS OS)                 │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         NETWORKING LAYER                     │
│  Tailscale (free tier, 100 devices)         │
│  WireGuard-based mesh network               │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│        VERSION CONTROL LAYER                 │
│  GitHub Free (or self-hosted Gitea)         │
│  Git (FOSS)                                 │
└─────────────────────────────────────────────┘
```

### Deployment Flexibility

**Option A: OCI Always Free Tier** (Cloud)
- **Cost**: $0/month forever
- **Specs**: 1-4 ARM cores, 6-24GB RAM
- **Bandwidth**: 10TB/month outbound
- **Storage**: 200GB block storage
- **Perfect for**: Always-on services, public-facing apps

**Option B: Homelab Server** (Your Hardware)
- **Cost**: Electricity only (~$5-15/month)
- **Specs**: Whatever you have (i5, 16GB RAM works great)
- **Control**: 100% ownership, no cloud provider
- **Perfect for**: Privacy-focused apps, local services, learning

**Both work identically** - ONE_SHOT generates the same code regardless of where it runs.

### Why This Matters

**Portability**:
```bash
# Move from OCI to homelab? Just:
git clone your-repo
cd your-repo
docker compose up -d  # or systemd service
# Done. Everything works.
```

**No Lock-in**:
- Don't like OCI? Use AWS, Azure, DigitalOcean, or your homelab
- Don't like GitHub? Use GitLab, Gitea, or any Git host
- Don't like Tailscale? Use WireGuard directly
- **You're never trapped**

**Self-Hosting**:
- Every component can be self-hosted
- No external dependencies required (except optional AI)
- Your data stays on your infrastructure

### The Only Paid Component (Optional)

**Claude API** (for AI features):
- **Cost**: ~$1-20/month for typical usage
- **Optional**: Only if you want AI features
- **Alternatives**: Use local LLMs (Ollama, LM Studio) for $0
- **You choose**: Pay for convenience or self-host for free

### Philosophy in Practice

When ONE_SHOT builds a project, it **always**:
- ✅ Uses FOSS databases (PostgreSQL, SQLite, Redis)
- ✅ Uses FOSS web servers (Caddy, Nginx)
- ✅ Uses FOSS languages (Python, Node.js, Go, Rust)
- ✅ Uses FOSS frameworks (FastAPI, Express, etc.)
- ✅ Generates portable code (works anywhere)
- ✅ Includes Docker configs (easy deployment)
- ✅ Documents self-hosting options

**Never**:
- ❌ Requires proprietary software
- ❌ Locks you into a specific cloud provider
- ❌ Uses paid-only services
- ❌ Creates vendor dependencies

---

## HOW THIS WORKS

This single file is your complete project builder. Here's the workflow:

```
1. INTERACTIVE PHASE (5-15 minutes, you + Claude)
   ├─ Answer project questions
   ├─ Validate connections (GitHub, Tailscale)
   ├─ Make all architectural decisions
   └─ Generate complete PRD

2. AUTONOMOUS PHASE (hours to days, Claude Code alone)
   ├─ Create repo structure
   ├─ Implement all features
   ├─ Write tests
   ├─ Commit + push automatically
   └─ Deploy to Tailscale HTTPS

3. DONE
   └─ Working project at https://[project].deer-panga.ts.net
```

**You answer questions once. Claude Code does the rest.**

---

## STEP 1: INTERACTIVE SETUP

### **Current Environment Check**

**Deployment Options** (choose one):

**Option A: OCI Always Free Tier VM**
- Host: Your OCI VM (e.g., `oci-dev-public`)
- Specs: 1-4 ARM cores, 6-24GB RAM (always free)
- OS: Ubuntu 22.04 LTS
- Tailscale: Connected to your tailnet
- Python: 3.11+ installed

**Option B: Homelab Server**
- Hardware: i5 CPU, 16GB RAM (or similar)
- OS: Ubuntu 22.04 LTS (or any Linux)
- Uptime: Usually always-on
- Tailscale: Connected to your tailnet
- Python: 3.11+ installed

**Both options work identically** - ONE_SHOT doesn't care where it runs.

**Let's validate connections...**

Run these commands on your VM:

```bash
# Check Python
python3 --version

# Check git + GitHub auth
git config --global user.name
git config --global user.email
gh auth status  # or just try: git ls-remote https://github.com/yourusername/test.git

# Check Tailscale
tailscale status | grep deer-panga

# Check if logged into GitHub CLI (optional but helpful)
gh auth status
```

**Paste results here, or just confirm:**
- [ ] Python 3.11+ installed
- [ ] Git configured with your name/email
- [ ] GitHub authentication works (SSH or HTTPS)
- [ ] Tailscale connected to deer-panga.ts.net
- [ ] SSH to oci-dev-public works

---

### PROJECT QUESTIONNAIRE

**I'll ask you questions to generate the complete PRD. Answer each one.**

#### Core Project Definition

**Q1: What are you building?**
(One sentence: "A tool that does X for Y people")

**Example**: "A personal knowledge manager that converts newsletters/podcasts into searchable YAML files for developers who consume lots of content"

**Your answer**:
```
[YOUR ANSWER HERE]
```

---

**Q2: What's the core problem this solves?**
(Why does this need to exist? What's painful without it?)

**Your answer**:
```
[YOUR ANSWER HERE]
```

---

**Q3: What's your philosophy for this project?**
(3-5 bullet points - these guide ALL decisions)

**Example**:
- Simplicity over features
- Local-first, no cloud dependencies
- CLI-only, no web UI needed
- < 300 lines per module
- Works offline

**Your answer**:
```
[YOUR ANSWER HERE]
```

---

#### Project Scope

**Q4: What will this project DO?** 
(List 3-7 concrete features, be specific)

**Example**:
1. Import newsletter from URL, save as YAML
2. Extract podcast transcript, save as YAML  
3. Search all content by keyword
4. Export filtered content as markdown
5. CLI with simple commands

**Your answer**:
```
1. [FEATURE 1]
2. [FEATURE 2]
3. [FEATURE 3]
4. [etc...]
```

---

**Q5: What will this project NOT do?**
(Explicitly exclude things to prevent scope creep)

**Example**:
- No web interface (CLI only)
- No real-time sync (batch processing)
- No multi-user support (single user)
- No AI processing (just storage/search)

**Your answer**:
```
[YOUR ANSWER HERE]
```

---

**Q6: What type of project is this?**
(Pick one - affects structure and patterns)

- [ ] A. CLI Tool (commands, flags, local execution)
- [ ] B. Python Library (importable, reusable functions)
- [ ] C. Web Application (FastAPI, frontend, database)
- [ ] D. Data Pipeline (ETL, scheduled jobs, transformations)
- [ ] E. Background Service (runs 24/7, monitoring, alerts)
- [ ] F. AI-Powered Web Application (web app + Claude API integration)
- [ ] G. Premium Landing Page / Portfolio (stunning design, minimal backend)

**Your choice**: [LETTER]

---

#### Data & Storage

**Q7: What data does this project work with?**
(Give me an example of each data type)

**Example**:
```yaml
# Newsletter content
type: newsletter
title: "Weekly AI Digest #42"
url: "https://example.com/digest/42"
content: "Full text of newsletter..."
published: 2024-10-01
word_count: 3420
```

**Your data examples**:
```
[PASTE EXAMPLE DATA HERE]
```

---

**Q8: How much data will this handle?**

- [ ] A. Small (< 1000 items, < 1GB)
- [ ] B. Medium (1K-100K items, 1-10GB)
- [ ] C. Large (100K+ items, 10GB+)

**Your choice**: [LETTER]

---

**Q9: Where should data be stored?**

- [ ] A. Local files (YAML/JSON in directories)
- [ ] B. SQLite database (single file DB)
- [ ] C. PostgreSQL (needs setup)
- [ ] D. Mix (files for raw, SQLite for processed)

**Your choice**: [LETTER]

**If files, what format?**
- [ ] YAML (human-readable, comments)
- [ ] JSON (standard, parseable)
- [ ] CSV (tabular data)
- [ ] Other: [specify]

---

#### External Dependencies

**Q10: Does this project need external APIs?**

- [ ] No external APIs (all local)
- [ ] Yes, free APIs (list them):
  ```
  - API 1: [name, what for, free tier limits]
  - API 2: [name, what for, free tier limits]
  ```

**If yes, do you already have API keys?**
- [ ] Yes, I'll provide them as environment variables
- [ ] No, I'll get them during setup
- [ ] No API keys needed (public APIs)

---

**Q11: What Python packages does this need?**
(Or say "you decide" and I'll pick minimal dependencies)

**Example**:
```
pyyaml - YAML parsing
click - CLI framework  
requests - HTTP calls
pytest - testing
```

**Your answer**:
```
[LIST PACKAGES OR "you decide"]
```

---

#### User Interface

**Q12: How will users interact with this?**

If CLI tool:
```bash
# What commands should exist?
project init
project import [source]
project search [query]
project export [filter]
```

If web app:
```
# What pages/routes?
/ - Homepage
/dashboard - Main interface
/api/items - REST API
```

If library:
```python
# What's the main API?
from project import Parser
parser = Parser()
data = parser.process(input)
```

**Your interface design**:
```
[PASTE YOUR COMMANDS/ROUTES/API HERE]
```

---

#### Success Criteria

**Q13: What does "done" look like?**
(How do you know this project is complete and working?)

**Example**:
- Can import 100 newsletters without errors
- Can search and find content in < 1 second
- All tests passing
- CLI help shows all commands
- Running on Tailscale HTTPS at https://project.deer-panga.ts.net

**Your success criteria**:
```
[YOUR ANSWER HERE]
```

---

**Q14: What's a "good enough" first version?**
(What's the 80% solution you'd actually use?)

**Example**:
- Import newsletters (skip podcasts for v1)
- Basic search (full-text, no fuzzy)
- Manual export (no auto-sync)
- CLI only (web later)

**Your v1 scope**:
```
[YOUR ANSWER HERE]
```

---

### Technical Decisions

**Q15: Naming**

**Project name** (lowercase, hyphens ok): [name]
**GitHub repo name** (same as project name usually): [name]
**Module name** (Python import name, no hyphens): [name]

**Example**:
- Project: "newsletter-archive"
- Repo: "newsletter-archive"  
- Module: "newsletter_archive"

**Your names**:
- Project: [YOUR PROJECT NAME]
- Repo: [YOUR REPO NAME]
- Module: [YOUR MODULE NAME]

---

**Q16: Directory Structure Preference**

- [ ] A. Flat (src/ with all .py files)
- [ ] B. Modular (src/module1/, src/module2/)
- [ ] C. Domain-driven (src/models/, src/services/, src/api/)
- [ ] D. You decide based on project type

**Your choice**: [LETTER]

---

**Q17: Testing Strategy**

- [ ] A. Minimal (test critical paths only)
- [ ] B. Thorough (aim for 80%+ coverage)
- [ ] C. Comprehensive (test everything, 100% coverage)
- [ ] D. You decide based on complexity

**Your choice**: [LETTER]

---

**Q18: Deployment Preference**

- [ ] A. Local dev only (no deployment needed)
- [ ] B. Tailscale HTTPS (https://[project].your-tailnet.ts.net)
- [ ] C. Systemd service (runs 24/7 on VM/homelab)
- [ ] D. Both Tailscale + systemd (recommended for web apps)

**Where will this run?**
- [ ] OCI Always Free Tier VM
- [ ] Homelab server (i5, 16GB RAM, Ubuntu)
- [ ] Either (I'll decide later)
- [ ] Local only

**Your choice**: [LETTER] + [WHERE]

---

### Environment Variables / Secrets

**Q19: Does this project need secrets?**

- [ ] No secrets needed
- [ ] Yes, list them:
  ```
  SECRET_NAME_1=description of what this is
  SECRET_NAME_2=description of what this is
  ```

**Will you provide these now or later?**
- [ ] Now (I'll paste them)
- [ ] Later (I'll add to .env before running)

---

### Web Design & AI Features (for web projects)

**Q20: What's your design aesthetic preference?**
(Skip if not a web project)

- [ ] A. Modern & Minimal (clean, lots of whitespace, simple)
- [ ] B. Bold & Vibrant (bright colors, strong contrasts, energetic)
- [ ] C. Dark & Sleek (dark mode, glassmorphism, premium feel)
- [ ] D. Professional & Corporate (conservative, trustworthy, clean)
- [ ] E. Creative & Playful (unique, fun, experimental)
- [ ] F. You decide based on project purpose
- [ ] N/A (not a web project)

**Your choice**: [LETTER]

---

**Q21: Color scheme preference?**
(Skip if not a web project)

- [ ] A. Monochrome (single color + neutrals)
- [ ] B. Complementary (two contrasting colors)
- [ ] C. Analogous (harmonious color range)
- [ ] D. You decide (provide curated palette)
- [ ] N/A (not a web project)

**Your choice**: [LETTER]

---

**Q22: Animation level?**
(Skip if not a web project)

- [ ] A. Minimal (subtle hover effects only)
- [ ] B. Moderate (smooth transitions, micro-interactions)
- [ ] C. Rich (dynamic animations, parallax, complex effects)
- [ ] N/A (not a web project)

**Your choice**: [LETTER]

---

**Q23: Does this project need AI features?**

- [ ] No AI features needed
- [ ] Yes, specify which:
  - [ ] Content generation (summaries, descriptions, writing)
  - [ ] Intelligent search (semantic, natural language)
  - [ ] Recommendations (personalized suggestions)
  - [ ] Natural language interface (chat, conversational UI)
  - [ ] Image generation (custom graphics, illustrations)
  - [ ] Data analysis (insights, pattern detection)
  - [ ] Other: [specify]

**If yes, what's your AI budget?**
- [ ] Minimal ($0-5/month - use Haiku, cache aggressively)
- [ ] Moderate ($5-20/month - Sonnet for key features)
- [ ] Flexible ($20+/month - Sonnet everywhere, no limits)
- [ ] N/A (no AI features)

**Do you have an Anthropic API key?**
- [ ] Yes, I'll provide it
- [ ] No, I'll get one (https://console.anthropic.com)
- [ ] N/A (no AI features)

---

**Q24: Should this use Agent Architecture (Claude Agent SDK)?**
(Only relevant if you answered "Yes" to AI features)

**Use Agent SDK if**:
- Task requires multiple steps with iteration
- Need to search/process large amounts of data
- Want parallel execution (multiple specialist agents)
- Context management is critical
- Task benefits from self-correction loops

**Use Simple API if**:
- One-off text generation
- Simple categorization/summarization
- No iteration needed
- Small, manageable context

**Your choice**:
- [ ] Agent SDK (full agent loop with subagents, MCP, verification)
- [ ] Simple API (basic Claude API calls)
- [ ] N/A (no AI features)

**If Agent SDK, describe your agent architecture**:
(Example: "Orchestrator + 3 specialist subagents: research, analysis, writing")
```
[YOUR AGENT ARCHITECTURE HERE]
```

**If Agent SDK, which MCP servers do you need?**
(See available servers: https://github.com/modelcontextprotocol/servers)
- [ ] None needed
- [ ] Yes, specify:
  - [ ] Slack (team communication)
  - [ ] GitHub (code/issues)
  - [ ] Google Drive (documents)
  - [ ] PostgreSQL (database)
  - [ ] Brave Search (web search)
  - [ ] Filesystem (local files)
  - [ ] Other: [specify]

---

### Final Confirmation

**Q25: Review and confirm**

Based on your answers, here's what I'll build:

**Project**: [name from Q15]
**Type**: [type from Q6]
**Philosophy**: [bullets from Q3]

**Features**:
[list from Q4]

**Storage**: [choice from Q9]
**Interface**: [CLI/Web/Library from Q12]
**Deployment**: [choice from Q18]

**Dependencies**:
- Python 3.12
- [packages from Q11 or minimal set I choose]
- No external paid services

**Success looks like**:
[criteria from Q13]

**Is this correct?**
- [ ] Yes, build this exactly
- [ ] No, let me change: [what to change]

---

## STEP 2: CONNECTION VALIDATION

**I'll validate your environment before building anything.**

### Archon Methodology: Validate Before Create

Run this validation script on `oci-dev-public`:

```bash
#!/bin/bash
# Save as validate.sh and run: bash validate.sh

echo "=== Environment Validation ==="

# Python version
python3 --version || echo "❌ Python not found"

# Git config
git config user.name || echo "❌ Git user.name not set"
git config user.email || echo "❌ Git user.email not set"

# GitHub access (test by listing repos)
gh repo list --limit 1 2>/dev/null || git ls-remote https://github.com/$(git config user.name)/test.git 2>/dev/null || echo "❌ GitHub auth failed"

# Tailscale
tailscale status | grep -q "deer-panga" && echo "✅ Tailscale connected" || echo "❌ Tailscale not connected"

# Disk space
df -h / | grep -v Filesystem

# Memory
free -h

echo ""
echo "=== Validation Complete ==="
```

**Paste the output here**:
```
[VALIDATION OUTPUT]
```

**Or just confirm all passed**:
- [ ] All checks passed, ready to build

---

## STEP 3: PRD GENERATION

**Based on your answers, I'll generate the complete PRD.**

This PRD will include:
1. Project overview (from Q1-Q3)
2. Features (from Q4)
3. Non-goals (from Q5)
4. Data models (from Q7, expanded)
5. Storage structure (from Q9)
6. Dependencies (from Q11)
7. CLI/API design (from Q12)
8. Error handling (auto-generated)
9. Testing strategy (from Q17)
10. Deployment plan (from Q18)

**I'll show you the PRD for final approval.**

---

## STEP 4: AUTONOMOUS EXECUTION

**After you approve the PRD, here's what happens automatically:**

### Phase 0: Setup (5 min)
- Create GitHub repo: `https://github.com/[your-username]/[repo-name]`
- Clone to VM: `~/[project-name]`
- Initialize project structure
- Set up git hooks for auto-commit
- Configure Tailscale cert (if deployment chosen)

### Phase 1: Core Implementation (30min - 6hrs depending on complexity)
- Implement data models
- Build storage layer
- Add validation logic
- Create CLI/API (based on project type)
- Write unit tests

### Archon Integration (if applicable)
- Set up Caddy for SSL/reverse proxy (if web service)
- Implement microservices communication (HTTP APIs only)
- Add health endpoints (`/health`) for all services
- Set up proper logging and error handling

### Phase 2: Integration (1-3hrs)
- End-to-end workflows
- Integration tests
- Error handling
- Logging

### Phase 3: Deployment (30min)
- Set up systemd service (if chosen)
- Configure Tailscale HTTPS (if chosen)
- Create README with usage
- Final testing

### Caddy/Web Configuration (if applicable)
```
# Add domain to /etc/caddy/Caddyfile
your-project.ts.net {
    reverse_proxy localhost:8080
    encode gzip
}
# Validate: sudo caddy validate --config /etc/caddy/Caddyfile
# Reload: sudo systemctl reload caddy
```

### Phase 4: Validation (15min)
- Run all tests
- Verify deployment
- Check GitHub repo
- Confirm Tailscale URL works

**Claude Code will show progress every 5-10 tasks and commit after each working piece.**

**You can check progress anytime**:
```bash
ssh oci-dev-public
cd ~/[project-name]
git log --oneline  # See what's been built
pytest             # Run tests
```

---

## STEP 5: HANDOFF

**When complete, you'll get:**

1. **GitHub repo**: `https://github.com/[username]/[repo-name]`
   - Complete source code
   - Tests
   - README with usage instructions
   - Git history showing build process

2. **Running project** (if deployed):
   - Tailscale URL: `https://[project].deer-panga.ts.net`
   - Systemd service (if chosen): `sudo systemctl status [project]`

3. **Documentation**:
   - README.md with installation and usage
   - ARCHITECTURE.md explaining design decisions (WHY not just HOW)
   - API.md (if library/web app)

4. **Operations Guide**:
   ```bash
   # Standard Archon workflow
   git add . && git commit -m "description" && git push
   docker compose up --build -d  # if containerized
   make dev  # if Makefile exists
   ```

5. **Troubleshooting Principles**:
   - Isolate Layer → Check Dependencies → Analyze Logs → Verify Health
   - Always check `/health` endpoints before debugging code
   - Use systematic debugging patterns

4. **Next steps guide**:
   - How to extend
   - How to deploy elsewhere
   - How to contribute

---

## READY TO START?

**Once you've answered all questions above and validated connections, tell me:**

```
I've answered all questions. Validation passed. Generate PRD and show me for approval.
```

**I'll create the complete PRD based on your answers.**

**After you approve it, I'll say:**

```
PRD approved. Execute autonomous build.
```

**Then I'll build the entire project while you go do other things.**

### Archon Workflow Integration

**Standard commands you'll see during build:**
- `docker compose up --build -d` (if containerized)
- `make dev` (if Makefile exists)
- `git add . && git commit -m 'description' && git push` (after each milestone)

**Core principles applied:**
- Document the WHY, not just the HOW
- Single responsibility for each module
- Dependency awareness and circular prevention

---

## EXAMPLE WALKTHROUGHS

**To show you how this works, here are detailed examples:**

---

### Example 1: Personal Finance Tracker (Original Example)

**User Answers**:

Q1: "A personal finance tracker that imports transactions from CSV and categorizes spending"
Q2: "Mint.com is shutting down, need free alternative for tracking spending"
Q3: 
- Local-first (no cloud)
- Privacy-focused (data never leaves machine)
- Simple CSV in/out
- CLI only

Q4:
1. Import transactions from bank CSV
2. Auto-categorize transactions
3. Generate spending reports
4. Export filtered transactions

Q5: 
- No bank API integration (manual CSV only)
- No mobile app
- No multi-currency

Q6: A (CLI Tool)

Q7:
```yaml
transaction:
  date: 2024-01-15
  description: "AMAZON.COM"
  amount: -42.99
  category: shopping
  account: checking
```

Q8: A (< 1000 transactions)
Q9: B (SQLite)
Q11: "you decide"
Q12:
```bash
finance import transactions.csv
finance categorize
finance report --month 2024-01
finance export --category food
```

Q13:
- Can import 1000 transactions in < 5 seconds
- Auto-categorizes 80%+ correctly
- Reports show spending by category
- All tests passing

Q14:
- Import + manual categorization only
- Skip auto-categorize for v1
- Basic reports only

Q15:
- Project: finance-tracker
- Repo: finance-tracker
- Module: finance_tracker

Q17: B (Thorough)
Q18: A (Local only)
Q23: No AI features

**Validation**: All passed

**Generated PRD (Condensed)**:

```markdown
# Finance Tracker PRD

## Overview
Local-first personal finance tracker for CSV transaction management.

## Philosophy
- Local-first, no cloud
- Privacy-focused
- Simple CSV in/out
- CLI only

## Features
1. Import from CSV → SQLite
2. Manual categorization
3. Spending reports
4. Filtered exports

## Data Model
[Complete schema with examples]

## Storage
SQLite database: `~/.finance-tracker/transactions.db`

## CLI Commands
[All commands with full specifications]

## Testing
Aim for 80% coverage, focus on import/export

## Success Criteria
- Import 1000 transactions < 5s
- All tests passing
- CLI help functional
```

**Autonomous Build**:

**Phase 0**: Create repo, clone, structure ✅
**Phase 1**: Data models, SQLite, CLI skeleton ✅
**Phase 2**: Import/export, tests ✅
**Phase 3**: Reports, documentation ✅

**Result**: Working finance tracker at `~/finance-tracker`, all code on GitHub

---

### Example 2: AI-Powered Portfolio Site

**User Answers**:

Q1: "A personal portfolio website that showcases my projects with AI-generated descriptions and summaries"

Q2: "Need a stunning portfolio to showcase my work to potential clients, but writing project descriptions is time-consuming"

Q3:
- Visual excellence (must wow visitors)
- AI-assisted content (save time on writing)
- Fast and responsive
- Easy to update (just add project data)
- SEO optimized

Q4:
1. Beautiful landing page with hero section
2. Projects showcase with dynamic grid layout
3. AI-generated project descriptions and summaries
4. Skills section with visual indicators
5. Contact form with AI spam detection
6. Blog section with AI writing assistance

Q5:
- No CMS (static data files)
- No user accounts (single portfolio owner)
- No e-commerce (just showcase)
- No real-time features

Q6: F (AI-Powered Web Application)

Q7:
```yaml
project:
  id: "portfolio-redesign"
  title: "Portfolio Website Redesign"
  category: "Web Development"
  technologies: ["Next.js", "Tailwind", "Vercel"]
  image: "/projects/portfolio.jpg"
  github: "https://github.com/user/portfolio"
  live_url: "https://portfolio.example.com"
  raw_notes: "Redesigned my portfolio using Next.js with focus on performance and modern design"
  # AI will generate:
  # - description (2-3 paragraphs)
  # - summary (1 sentence)
  # - key_highlights (3-5 bullets)
```

Q8: A (< 50 projects)
Q9: A (YAML files in directories)
Q11: "you decide" (but include anthropic SDK)

Q12:
```
Web Routes:
/ - Landing page with hero
/projects - Project showcase grid
/projects/[id] - Individual project page
/blog - Blog listing
/blog/[slug] - Blog post
/contact - Contact form
```

Q13:
- Site loads in < 2 seconds
- All projects display with AI descriptions
- Contact form works with spam detection
- Responsive on mobile/tablet/desktop
- Deployed to Tailscale HTTPS
- All tests passing

Q14 (v1 scope):
- Landing + projects showcase
- AI descriptions for projects
- Basic contact form
- Skip blog for v1
- Static deployment (no backend needed initially)

Q15:
- Project: ai-portfolio
- Repo: ai-portfolio
- Module: portfolio

Q17: B (Thorough testing)
Q18: B (Tailscale HTTPS)

**Web Design Questions**:
Q20: C (Dark & Sleek - glassmorphism, premium feel)
Q21: D (You decide - curated palette)
Q22: B (Moderate animations - smooth, professional)

**AI Features**:
Q23: Yes
- Content generation (project descriptions, summaries)
- AI spam detection for contact form

AI Budget: Minimal ($0-5/month - Haiku for descriptions)
API Key: Yes, will provide

**Generated PRD**:

```markdown
# AI-Powered Portfolio PRD

## Overview
Premium portfolio website with AI-generated content, dark sleek design, and glassmorphism effects.

## Philosophy
- Visual excellence (wow factor)
- AI-assisted content generation
- Fast, responsive, SEO-optimized
- Easy to maintain

## Tech Stack
- Vite + vanilla JS (lightweight, fast)
- Vanilla CSS with design system
- Claude API (Haiku for cost efficiency)
- FastAPI backend for AI features
- Tailscale HTTPS deployment

## Design System
**Aesthetic**: Dark & Sleek
**Colors**:
- Primary: hsl(280, 100%, 70%) - Vibrant purple
- Secondary: hsl(180, 100%, 60%) - Cyan accent
- Background: hsl(240, 10%, 8%) - Deep dark
- Surface: hsl(240, 10%, 12%) with backdrop-blur
- Text: hsl(0, 0%, 95%)

**Typography**: Inter (Google Fonts)
**Animations**: Moderate (300ms transitions, hover effects, smooth scrolling)

## Features
1. Hero section with animated gradient background
2. Projects grid with glassmorphism cards
3. AI-generated descriptions (cached for cost)
4. Smooth page transitions
5. Contact form with AI spam detection
6. Responsive design (mobile-first)

## AI Integration
- Generate project descriptions on build (cache results)
- Spam detection on contact form submission
- Budget: ~$2-3/month (Haiku model)

## Data Structure
Projects stored in `/data/projects/*.yaml`
AI-generated content cached in `/data/cache/*.json`

## Deployment
- Build static assets
- FastAPI backend for AI endpoints
- Caddy reverse proxy
- Tailscale HTTPS: https://portfolio.deer-panga.ts.net

## Success Criteria
- Page load < 2s
- All projects have AI descriptions
- Spam detection > 95% accurate
- Responsive on all devices
- Deployed and accessible via Tailscale
```

**Autonomous Build**:

**Phase 0**: Setup ✅
- Create repo
- Initialize Vite project
- Set up project structure

**Phase 1**: Design System ✅
- Create `index.css` with dark theme
- Define color palette and typography
- Build glassmorphism utilities
- Set up animation system

**Phase 2**: Components ✅
- Hero section with gradient
- Project card component
- Navigation with smooth scroll
- Contact form
- Footer

**Phase 3**: AI Integration ✅
- Claude API setup
- Description generator
- Caching system
- Spam detector

**Phase 4**: Pages ✅
- Landing page assembly
- Projects showcase
- Individual project pages
- Contact page

**Phase 5**: Deployment ✅
- Build optimization
- FastAPI backend
- Caddy configuration
- Tailscale setup

**Result**: Stunning portfolio at `https://portfolio.deer-panga.ts.net`

---

### Example 3: Smart Note-Taking App with AI

**User Answers**:

Q1: "A note-taking web app with AI-powered organization, tagging, and semantic search"

Q2: "Existing note apps are dumb - they can't understand context or help me find related notes. I want AI to organize my thoughts."

Q3:
- AI-first (intelligent by default)
- Fast and responsive
- Privacy-conscious (data stays on my server)
- Beautiful, modern UI
- Works offline (progressive web app)

Q4:
1. Rich text note editor
2. AI-powered automatic tagging
3. Semantic search (understand meaning, not just keywords)
4. AI-generated summaries for long notes
5. Related notes suggestions
6. Folder organization with AI suggestions
7. Export to markdown

Q5:
- No mobile app (PWA only)
- No collaboration (single user)
- No sync across devices (single server)
- No third-party integrations

Q6: F (AI-Powered Web Application)

Q7:
```yaml
note:
  id: "note-123"
  title: "Meeting Notes - Q4 Planning"
  content: "Full markdown content..."
  created: 2024-11-26T10:30:00Z
  updated: 2024-11-26T14:20:00Z
  tags: ["meetings", "planning", "Q4"]  # AI-generated
  summary: "Discussion of Q4 goals..."  # AI-generated
  folder: "work/meetings"
  word_count: 450
```

Q8: B (1K-10K notes, ~5GB)
Q9: C (PostgreSQL - need full-text search)
Q11: "you decide" (but include anthropic, fastapi, postgres)

Q12:
```
Web Routes:
/ - Note list/grid view
/note/[id] - Note editor
/search - Semantic search interface
/tags - Tag browser
/settings - App settings

API:
POST /api/notes - Create note
GET /api/notes/[id] - Get note
PUT /api/notes/[id] - Update note
POST /api/ai/tag - Generate tags
POST /api/ai/summarize - Generate summary
POST /api/ai/search - Semantic search
GET /api/ai/related/[id] - Get related notes
```

Q13:
- Can create/edit notes instantly
- AI tagging works in < 2 seconds
- Semantic search returns relevant results
- Related notes are actually related
- Works offline (PWA)
- All tests passing
- Deployed on Tailscale

Q14 (v1):
- Core editor + AI tagging
- Semantic search
- Basic folder organization
- Skip related notes for v1
- Skip offline mode for v1

Q15:
- Project: smart-notes
- Repo: smart-notes
- Module: smart_notes

Q17: B (Thorough)
Q18: D (Tailscale + systemd service)

**Web Design**:
Q20: A (Modern & Minimal - focus on content)
Q21: D (You decide)
Q22: B (Moderate animations)

**AI Features**:
Q23: Yes
- Content generation (summaries, tags)
- Intelligent search (semantic understanding)
- Recommendations (related notes)

AI Budget: Moderate ($10-15/month - Sonnet for search quality)
API Key: Will get one

**Generated PRD**:

```markdown
# Smart Notes PRD

## Overview
AI-powered note-taking app with semantic search and intelligent organization.

## Tech Stack
- Next.js (React framework)
- PostgreSQL (full-text search + vector embeddings)
- FastAPI (AI backend)
- Claude API (Sonnet for search, Haiku for tagging)
- Tailscale deployment

## Design
**Aesthetic**: Modern & Minimal
**Colors**: Clean, content-focused palette
**Animations**: Subtle, smooth transitions

## AI Features
1. **Auto-tagging**: Haiku analyzes note, suggests 3-5 tags
2. **Summarization**: Haiku creates 1-2 sentence summary
3. **Semantic Search**: Sonnet understands query intent, finds relevant notes
4. **Cost**: ~$10-15/month (mostly search queries)

## Architecture
- Frontend: Next.js (port 3000)
- API: FastAPI (port 8000)
- Database: PostgreSQL (port 5432)
- AI: Claude API (external)

## Success Criteria
- Create note: instant
- AI tag generation: < 2s
- Search: < 1s response
- 95%+ search relevance
- Deployed and running 24/7
```

**Result**: Intelligent note-taking app at `https://notes.deer-panga.ts.net`

---

## PHILOSOPHY OF ONE_SHOT + ARCHON INTEGRATION

This file embodies a specific philosophy enhanced with Archon principles:

### Front-Load All Decisions
- No "we'll figure it out later"
- No "TBD" or "TODO"
- All architectural decisions made upfront
- All questions asked before building

### Document the WHY, Not Just the HOW
- WHY this database choice (not just HOW to use it)
- WHY this architecture pattern (not just HOW to implement)
- HOW changes, WHY remains constant

### Validate Before Create
- Always check task validity before creation
- Dependency awareness and resolution
- Circular dependency prevention
- Environment validation before building

### Microservices When Appropriate
- Single responsibility per module
- Independent scaling possible
- HTTP communication between services (no direct imports)
- True separation of concerns

### Trust the Builder
- You provide vision and constraints
- AI handles implementation details
- No hand-holding after approval
- Autonomous execution once started

### Simplicity Default
- Minimal dependencies
- Small modules (< 300 lines)
- Local-first when possible
- No frameworks when tools suffice

### Free & Open-Source Everything
- **Infrastructure**: OCI Always Free Tier OR homelab hardware you own
- **Version Control**: GitHub Free (or self-hosted Gitea)
- **Networking**: Tailscale Free (100 devices, 3 users)
- **Software Stack**: 100% FOSS (Python, FastAPI, PostgreSQL, Caddy, etc.)
- **No Proprietary Dependencies**: Everything can be self-hosted
- **Runtime Cost**: $0/month (AI features optional, ~$1-20/month if used)

### Progressive Enhancement
- Build v1 that works
- Iterate to v2 when needed
- Don't over-engineer upfront
- Ship, learn, improve

---

## WEB DESIGN EXCELLENCE WITH CLAUDE

When building web applications with ONE_SHOT, we don't just make them work - we make them **stunning**. This section guides you in creating premium, beautiful web experiences that wow users at first glance.

### Philosophy: Visual Excellence

**Core Principles**:
1. **Prioritize Visual Impact**: Designs should impress immediately with modern aesthetics
2. **Modern Design Language**: Vibrant colors, dark modes, glassmorphism, smooth animations
3. **Responsive & Accessible**: Beautiful on all devices, works for everyone
4. **Performance Matters**: Fast load times, smooth interactions
5. **No Placeholders**: Use real content and generated assets

### Technology Stack for Web Projects

**Core Technologies**:
- **HTML**: Semantic HTML5 for structure and SEO
- **CSS**: Vanilla CSS for maximum flexibility (Tailwind if explicitly requested)
- **JavaScript**: Modern ES6+, frameworks when complexity demands it

**Frameworks (when needed)**:
- **Vite**: Fast, modern build tool for SPAs
- **Next.js**: Full-stack React applications with SSR
- **FastAPI**: Python backend for APIs

**Typography**:
- Google Fonts: Inter, Roboto, Outfit, Poppins
- Never use browser defaults

**Icons & Assets**:
- Lucide Icons, Heroicons, Font Awesome
- Generate custom images with AI when needed

### Design Aesthetics Guide

**Color Palettes** (avoid generic red/blue/green):
```css
/* Example: Modern Dark Mode */
--primary: hsl(260, 100%, 65%);      /* Vibrant purple */
--secondary: hsl(200, 100%, 60%);    /* Bright cyan */
--background: hsl(240, 10%, 8%);     /* Deep dark */
--surface: hsl(240, 10%, 12%);       /* Card background */
--text: hsl(0, 0%, 95%);             /* Off-white */

/* Example: Vibrant Light Mode */
--primary: hsl(340, 82%, 52%);       /* Energetic pink */
--secondary: hsl(45, 100%, 51%);     /* Golden yellow */
--background: hsl(0, 0%, 98%);       /* Soft white */
--surface: hsl(0, 0%, 100%);         /* Pure white */
--text: hsl(240, 10%, 15%);          /* Dark gray */
```

**Modern Effects**:
- **Glassmorphism**: `backdrop-filter: blur(10px)` with semi-transparent backgrounds
- **Smooth Gradients**: Multi-stop gradients, not harsh transitions
- **Shadows**: Layered shadows for depth (`box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)`)
- **Animations**: Smooth transitions (200-300ms), micro-interactions on hover

**Typography Scale**:
```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
```

### Implementation Workflow for Web Projects

**1. Plan and Understand**:
- Understand user requirements fully
- Draw inspiration from modern, beautiful web designs
- Outline features for v1

**2. Build the Foundation**:
- Create `index.css` with complete design system
- Define all CSS custom properties (colors, spacing, typography)
- Set up base styles and utilities

**3. Create Components**:
- Build reusable components using the design system
- Ensure all components use predefined styles
- Keep components focused and modular

**4. Assemble Pages**:
- Update main application with design and components
- Implement responsive layouts (mobile-first)
- Add proper routing and navigation

**5. Polish and Optimize**:
- Add smooth interactions and transitions
- Optimize performance (lazy loading, code splitting)
- Test across devices and browsers

### SEO Best Practices (Auto-Applied)

Every web page should include:
- **Title Tags**: Descriptive, unique per page
- **Meta Descriptions**: Compelling summaries (150-160 chars)
- **Heading Structure**: Single `<h1>`, proper hierarchy
- **Semantic HTML**: `<header>`, `<nav>`, `<main>`, `<article>`, `<footer>`
- **Unique IDs**: All interactive elements for testing
- **Performance**: Fast load times, optimized assets

### Critical Design Rules

**Do**:
- Use curated, harmonious color palettes
- Implement smooth micro-animations
- Choose modern typography (Google Fonts)
- Create responsive designs (mobile-first)
- Generate real assets (no placeholders)
- Make designs feel premium and state-of-the-art

**Don't**:
- Use generic colors (plain red, blue, green)
- Use browser default fonts
- Create static, lifeless interfaces
- Build simple MVPs without polish
- Use placeholder images or "Lorem ipsum"

---

## CLAUDE AGENT SDK: BUILDING AUTONOMOUS AGENTS

ONE_SHOT can build projects using the **Claude Agent SDK** - the same framework that powers Claude Code. This enables you to create autonomous agents that can work independently, manage their own context, and collaborate through subagents.

### Understanding Agent Architecture

**What's the difference between Claude API and Claude Agent SDK?**

- **Claude API**: Simple request/response. You send a prompt, get a response. Good for one-off tasks.
- **Claude Agent SDK**: Full agent loop. Agents gather context, take actions, verify work, and iterate autonomously.

**The Agent Loop**:
```
1. GATHER CONTEXT
   ├─ Search files and data
   ├─ Query external APIs (via MCP)
   ├─ Use subagents for parallel research
   └─ Load relevant information

2. TAKE ACTION
   ├─ Use tools (custom functions)
   ├─ Run bash commands
   ├─ Generate and execute code
   └─ Call external services (via MCP)

3. VERIFY WORK
   ├─ Check against defined rules
   ├─ Visual feedback (screenshots)
   ├─ LLM-as-judge evaluation
   └─ Iterate if needed

4. REPEAT until task complete
```

### When to Use Agent Architecture

**Use Agents When**:
- Task requires multiple steps with verification
- Need to search through large amounts of data
- Want parallel execution (multiple subagents)
- Context management is critical (avoid hitting limits)
- Task benefits from iteration and self-correction

**Use Simple API When**:
- One-off text generation
- Simple categorization or summarization
- No iteration needed
- Context is small and manageable

### Subagents: Parallel Work + Context Isolation

**Why Subagents Matter**:
1. **Context Isolation**: Each subagent has its own 200k context window
2. **Parallel Execution**: Multiple subagents work simultaneously
3. **Specialization**: Each subagent can have specific instructions and tools
4. **Context Efficiency**: Only final results return to orchestrator, not full context

**Example: Research Agent with Subagents**:
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Orchestrator agent
def research_topic(topic: str) -> dict:
    """
    Main agent that coordinates subagents for comprehensive research.
    """
    # Spawn 3 subagents in parallel
    subagents = [
        {"role": "academic_search", "query": f"academic papers on {topic}"},
        {"role": "news_search", "query": f"recent news about {topic}"},
        {"role": "code_search", "query": f"code examples for {topic}"}
    ]
    
    results = []
    for agent in subagents:
        # Each subagent processes independently
        result = run_subagent(agent["role"], agent["query"])
        results.append(result)
    
    # Orchestrator synthesizes results
    synthesis = synthesize_research(results)
    return synthesis

def run_subagent(role: str, query: str) -> str:
    """
    Subagent with specialized instructions and tools.
    """
    system_prompt = get_role_prompt(role)  # Specialized instructions
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": query}]
    )
    
    # Only return relevant findings, not full context
    return extract_key_findings(message.content[0].text)
```

**Subagent Best Practices**:
- **Specialized Instructions**: Each subagent should have clear, focused role
- **Limited Tools**: Only give subagents tools they need (reduces context)
- **Compact Returns**: Return summaries, not full context
- **Parallel When Possible**: Independent tasks can run simultaneously

### Model Context Protocol (MCP)

**What is MCP?**
MCP provides standardized integrations to external services. Instead of writing custom API code, you get pre-built "servers" that handle authentication and API calls.

**Available MCP Servers** (examples):
- **Slack**: Search messages, post updates
- **GitHub**: Search code, create issues, manage PRs
- **Google Drive**: Search files, read documents
- **Asana**: Get tasks, update status
- **Brave Search**: Web search
- **PostgreSQL**: Database queries
- **Filesystem**: Local file operations

**Using MCP in Your Agent**:
```python
# Example: Agent that searches Slack and GitHub
import mcp

# Initialize MCP servers
slack_server = mcp.SlackServer(token=os.environ["SLACK_TOKEN"])
github_server = mcp.GitHubServer(token=os.environ["GITHUB_TOKEN"])

def investigate_bug(bug_description: str) -> str:
    """
    Agent uses MCP to search Slack discussions and GitHub issues.
    """
    # Search Slack for related discussions
    slack_results = slack_server.search_messages(
        query=bug_description,
        limit=10
    )
    
    # Search GitHub for similar issues
    github_results = github_server.search_issues(
        query=bug_description,
        state="all",
        limit=10
    )
    
    # Agent synthesizes findings
    context = f"""
    Slack discussions: {slack_results}
    GitHub issues: {github_results}
    """
    
    # Use Claude to analyze and provide insights
    analysis = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"Analyze this bug based on context:\n{context}\n\nBug: {bug_description}"
        }]
    )
    
    return analysis.content[0].text
```

**MCP Benefits**:
- No custom OAuth flows
- Standardized tool interface
- Growing ecosystem of integrations
- Works seamlessly with Claude Agent SDK

### Agent Context Management

**The Context Problem**:
- Claude has 200k token context limit
- As context fills, performance degrades
- Long-running agents hit limits quickly

**Solutions**:

**1. Agentic Search** (File System as Context):
```python
# Instead of loading entire files, search strategically
def search_logs(error_pattern: str) -> list[str]:
    """
    Agent uses bash to search efficiently.
    """
    # Use grep instead of loading full log file
    result = subprocess.run(
        ["grep", "-n", error_pattern, "/var/log/app.log"],
        capture_output=True,
        text=True
    )
    return result.stdout.split("\n")[:10]  # Only top 10 matches
```

**2. Compaction** (Automatic Summarization):
```python
# When context approaches limit, summarize previous work
def compact_context(messages: list) -> list:
    """
    Summarize old messages to free context.
    """
    if len(messages) > 50:
        # Summarize first 30 messages
        old_messages = messages[:30]
        summary = summarize_messages(old_messages)
        
        # Replace with summary
        return [{"role": "user", "content": f"Previous work summary: {summary}"}] + messages[30:]
    return messages
```

**3. Subagents for Heavy Lifting**:
```python
# Offload data processing to subagent
def analyze_large_dataset(data_path: str) -> str:
    """
    Subagent processes data, returns only insights.
    """
    # Subagent has its own 200k context
    subagent_result = run_subagent(
        role="data_analyst",
        task=f"Analyze {data_path} and return top 5 insights"
    )
    
    # Only insights added to main context, not raw data
    return subagent_result
```

### Verification Patterns

**1. Rules-Based Verification**:
```python
def verify_email_format(email_html: str) -> dict:
    """
    Check email against defined rules.
    """
    errors = []
    warnings = []
    
    # Rule 1: Valid email address
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', extract_recipient(email_html)):
        errors.append("Invalid email address format")
    
    # Rule 2: Has subject line
    if not extract_subject(email_html):
        errors.append("Missing subject line")
    
    # Rule 3: Check if recipient is known
    if not is_known_contact(extract_recipient(email_html)):
        warnings.append("First time emailing this contact")
    
    return {"errors": errors, "warnings": warnings}
```

**2. Visual Verification** (for UI/HTML):
```python
import playwright

def verify_ui_visually(html_path: str) -> str:
    """
    Screenshot and verify visual output.
    """
    # Render HTML and screenshot
    screenshot = render_and_screenshot(html_path)
    
    # Send to Claude for visual verification
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "data": screenshot}},
                {"type": "text", "text": "Does this UI match requirements? Check layout, colors, spacing."}
            ]
        }]
    )
    
    return message.content[0].text
```

**3. LLM-as-Judge**:
```python
def verify_tone(email_draft: str, user_history: list[str]) -> dict:
    """
    Use separate LLM to judge output quality.
    """
    message = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Cheaper model for judging
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"""
            Previous emails from user:
            {user_history}
            
            New draft:
            {email_draft}
            
            Does the tone match the user's previous emails? Rate 1-10 and explain.
            """
        }]
    )
    
    return parse_judge_response(message.content[0].text)
```

### Agent Architecture Patterns

**Pattern 1: Specialist Subagents**
```python
# Orchestrator coordinates specialists
agents = {
    "database": DatabaseAgent(),      # Handles all DB operations
    "api": APIAgent(),                # Manages external API calls
    "frontend": FrontendAgent(),      # Builds UI components
    "testing": TestingAgent(),        # Writes and runs tests
    "reviewer": CodeReviewAgent()     # Reviews all code changes
}

# Each specialist has focused instructions and tools
```

**Pattern 2: Pipeline Agents**
```python
# Sequential processing with verification
def process_content(raw_content: str) -> str:
    # Stage 1: Extract and structure
    structured = extraction_agent.process(raw_content)
    
    # Stage 2: Enhance with AI
    enhanced = enhancement_agent.process(structured)
    
    # Stage 3: Review and verify
    verified = review_agent.verify(enhanced)
    
    # Stage 4: Format for output
    final = formatting_agent.format(verified)
    
    return final
```

**Pattern 3: Parallel Research + Synthesis**
```python
# Multiple agents research in parallel, orchestrator synthesizes
def comprehensive_research(topic: str) -> str:
    # Spawn parallel subagents
    results = parallel_execute([
        ("academic", search_academic_papers, topic),
        ("news", search_news, topic),
        ("code", search_code_examples, topic),
        ("community", search_forums, topic)
    ])
    
    # Orchestrator synthesizes all findings
    synthesis = orchestrator.synthesize(results)
    return synthesis
```

### Cost Implications of Agents

**Token Usage**:
- **Single-threaded**: 1x token usage
- **With subagents**: 3-4x token usage (typical)
- **Heavy parallelization**: Up to 15x token usage

**Why the increase?**
- Each subagent has its own context
- Orchestrator processes subagent outputs
- More verification loops = more tokens

**Cost Management**:
```python
# 1. Use appropriate models
subagent_configs = {
    "simple_tasks": "claude-3-5-haiku-20241022",    # Cheap
    "complex_tasks": "claude-3-5-sonnet-20241022",  # Balanced
    "critical_tasks": "claude-3-opus-20240229"      # Expensive
}

# 2. Limit subagent context
max_tokens_per_subagent = 2048  # Don't let them run wild

# 3. Cache system prompts
# System prompts are often repeated - cache them

# 4. Monitor usage
import anthropic

response = client.messages.create(...)
print(f"Tokens used: {response.usage.input_tokens + response.usage.output_tokens}")
```

### ONE_SHOT + Agent SDK Integration

**How This Fits Together**:

1. **ONE_SHOT Philosophy**: Ask everything upfront, execute autonomously
2. **Agent SDK**: Provides the execution framework (agent loop, subagents, MCP)
3. **Result**: Projects that build themselves using agent architecture

**Example Flow**:
```
User answers ONE_SHOT questionnaire
  ↓
ONE_SHOT generates PRD
  ↓
Agent SDK builds the project:
  ├─ Planning Agent: Breaks down PRD into tasks
  ├─ Implementation Agents (parallel):
  │   ├─ Backend Agent: Builds API
  │   ├─ Frontend Agent: Builds UI
  │   └─ Database Agent: Sets up schema
  ├─ Testing Agent: Writes and runs tests
  └─ Review Agent: Verifies everything works
  ↓
Deployed project on Tailscale
```

**Key Principle**: Agents work **with** ONE_SHOT, not against it. The questionnaire defines **what** to build, agents handle **how** to build it autonomously.

---

## AI-POWERED FEATURES WITH CLAUDE

ONE_SHOT can now build projects with intelligent AI capabilities using the Claude API. This section covers when to use AI, how to integrate it, and how to manage costs.

### When to Add AI Features

**Good Use Cases**:
- **Content Generation**: Summaries, descriptions, suggestions, writing assistance
- **Intelligent Search**: Semantic search, natural language queries
- **Recommendations**: Personalized suggestions based on user behavior
- **Natural Language Interfaces**: Chat interfaces, conversational UIs
- **Data Analysis**: Insights, pattern detection, anomaly detection
- **Image Generation**: Custom graphics, illustrations, UI mockups

**Not Recommended**:
- Simple CRUD operations (overkill)
- Real-time requirements (API latency ~1-3 seconds)
- High-volume batch processing (costs add up)
- When deterministic logic suffices

### Claude API Integration Patterns

**Setup and Authentication**:
```python
import anthropic
import os

# Initialize client (API key from environment)
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

def get_ai_response(prompt: str, model: str = "claude-3-5-haiku-20241022") -> str:
    """Get response from Claude API with error handling."""
    try:
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except anthropic.APIError as e:
        print(f"API Error: {e}")
        return None
```

**Model Selection**:
- **Haiku** (`claude-3-5-haiku-20241022`): Fast, cheap, good for simple tasks
  - Use for: Summaries, categorization, simple Q&A
  - Cost: ~$0.80 per million input tokens
- **Sonnet** (`claude-3-5-sonnet-20241022`): Balanced, most versatile
  - Use for: Complex analysis, creative writing, code generation
  - Cost: ~$3 per million input tokens
- **Opus** (`claude-3-opus-20240229`): Most capable, expensive
  - Use for: Critical tasks requiring highest quality
  - Cost: ~$15 per million input tokens

**Cost Management Best Practices**:
```python
# 1. Cache system prompts (reduces repeat costs)
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(prompt: str) -> str:
    return get_ai_response(prompt)

# 2. Set appropriate max_tokens
message = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=256,  # Limit output length
    messages=[{"role": "user", "content": prompt}]
)

# 3. Use streaming for long responses
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# 4. Batch requests when possible
prompts = ["Summarize: " + text for text in documents]
# Process in batches to avoid rate limits
```

**Error Handling Pattern**:
```python
import logging
from anthropic import APIError, RateLimitError

logger = logging.getLogger(__name__)

def safe_ai_call(prompt: str, retries: int = 3) -> str:
    """Call Claude API with retry logic and error handling."""
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        except RateLimitError:
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Rate limited, waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                logger.error("Rate limit exceeded after retries")
                return None
        
        except APIError as e:
            logger.error(f"API error: {e}")
            return None
    
    return None
```

### Cost Estimation Guide

**Typical Usage Costs** (approximate):

| Project Type | Monthly Usage | Model | Est. Cost |
|--------------|---------------|-------|-----------|
| Personal blog with AI summaries | 1,000 articles | Haiku | $0.50 |
| Note-taking app with AI tagging | 10,000 notes | Haiku | $2.00 |
| Smart search (100 queries/day) | 3,000 queries | Sonnet | $5.00 |
| AI writing assistant | 500 generations | Sonnet | $8.00 |
| Content recommendation engine | 50,000 items | Haiku | $10.00 |

**Free Tier**: Claude API has no free tier, but:
- First $5 of usage is often credited for new accounts
- Costs are very low for personal projects ($1-10/month typical)
- You can set spending limits in the Anthropic Console

**Budget Levels**:
- **Minimal** ($0-5/month): Use Haiku, cache aggressively, limit features
- **Moderate** ($5-20/month): Sonnet for key features, Haiku for bulk
- **Flexible** ($20+/month): Sonnet everywhere, no artificial limits

### Example AI Features

**1. Intelligent Content Summarization**:
```python
def summarize_article(article_text: str) -> str:
    """Generate concise summary of article."""
    prompt = f"""Summarize this article in 2-3 sentences:

{article_text}

Focus on the main points and key takeaways."""
    
    return get_ai_response(prompt, model="claude-3-5-haiku-20241022")
```

**2. Smart Categorization**:
```python
def categorize_item(item: str, categories: list[str]) -> str:
    """Categorize item into one of the provided categories."""
    prompt = f"""Categorize this item into ONE of these categories: {', '.join(categories)}

Item: {item}

Respond with only the category name, nothing else."""
    
    return get_ai_response(prompt, model="claude-3-5-haiku-20241022").strip()
```

**3. Natural Language Search**:
```python
def semantic_search(query: str, documents: list[dict]) -> list[dict]:
    """Find relevant documents using semantic understanding."""
    # Create document summaries
    doc_summaries = "\n".join([
        f"{i}. {doc['title']}: {doc['summary']}" 
        for i, doc in enumerate(documents)
    ])
    
    prompt = f"""Given this search query: "{query}"

Which of these documents are most relevant? Return the numbers of the top 3 most relevant documents.

Documents:
{doc_summaries}

Respond with just the numbers, comma-separated (e.g., "2,5,7")."""
    
    response = get_ai_response(prompt, model="claude-3-5-sonnet-20241022")
    indices = [int(i.strip()) for i in response.split(",")]
    return [documents[i] for i in indices]
```

### Choosing Between API and Agent SDK

**Decision Matrix**:

| Feature | Claude API | Claude Agent SDK |
|---------|-----------|------------------|
| **Use Case** | Simple tasks | Complex, multi-step tasks |
| **Context** | Single conversation | Multiple contexts (subagents) |
| **Iteration** | Manual | Automatic (agent loop) |
| **Parallelization** | No | Yes (subagents) |
| **Cost** | Lower | Higher (3-15x) |
| **Complexity** | Simple | Advanced |
| **Best For** | Content generation, categorization | Research, code generation, workflows |

**Example Projects**:

**API-Based** (Simple):
- Blog post summarizer
- Product description generator
- Email categorizer
- Simple chatbot

**Agent SDK-Based** (Complex):
- Code review system with multiple specialist agents
- Research assistant that searches multiple sources
- Content pipeline with extraction → enhancement → review
- Customer support system with context tracking

### Environment Variables for AI Projects

When using Claude API, add to your `.env`:
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Optional (for cost control)
MAX_TOKENS_DEFAULT=1024
AI_MODEL_DEFAULT=claude-3-5-haiku-20241022
ENABLE_AI_CACHING=true
```

---

## TROUBLESHOOTING (Archon Systematic Approach)

**Core Debugging Methodology**:
1. **Isolate Layer**: Test each component independently (network → app → database)
2. **Check Dependencies**: Verify required services are running before testing
3. **Analyze Logs**: Always check logs before code changes
4. **Verify Health**: Use `/health` endpoints to verify service status

**If validation fails:**

```bash
# Python missing/wrong version
sudo apt install python3.12 python3.12-venv

# Git not configured
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# GitHub auth failing
gh auth login  # If you have GitHub CLI
# or set up SSH keys

# Tailscale not connected
sudo tailscale up
```

**If build gets stuck:**

```bash
# Check what's running
ps aux | grep python

# Archon: Check service status
systemctl status caddy docker tailscale

# See recent commits
cd ~/[project]
git log --oneline -10

# Check tests
pytest -v

# Check logs (systematic approach)
journalctl -u [service-name] --since "1 hour ago"
tail -100 [project].log

# Port conflicts
lsof -i :PORT

# Docker issues
docker compose logs -f [service-name]
```

**If you need to restart:**
- All code is on GitHub
- All progress committed
- Just continue from where it stopped
- No work is lost

---

## ANTI-PATTERNS TO AVOID (Archon Enhanced)

**Don't:**
- Answer questions vaguely ("make it configurable")
- Skip the validation step
- Change requirements mid-build
- Over-scope v1 (keep it simple)
- Implement services without health endpoints
- Create tight coupling between modules
- Ignore the WHY (focus only on HOW)

**Do:**
- Be specific in answers
- Provide concrete examples
- Start small (can expand later)
- Trust the autonomous process
- Add `/health` endpoints to all services
- Document WHY choices were made
- Follow Validate Before Create principle

---

## ADVANCED PATTERNS (Archon Integration)

### Microservices Communication
```python
# Service A (example)
import requests

def call_service_b(data):
    response = requests.post("http://localhost:8052/api/process", json=data)
    return response.json()
```

### Health Endpoint Pattern
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

### Caddy Configuration Templates
```caddy
# API service
api.project.ts.net {
    reverse_proxy localhost:8000
    encode gzip
}

# Static site
project.ts.net {
    root * /path/to/files
    file_server
    encode gzip
}

# Mixed (API + Static)
app.project.ts.net {
    handle /api/* {
        reverse_proxy localhost:8000
    }
    handle /* {
        root * /path/to/app
        file_server
        try_files {path} /index.html
    }
    encode gzip
}
```

### Docker Compose Structure
```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Error Handling Pattern
```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    try:
        # Main logic
        result = transform(data)
        logger.info(f"Successfully processed {len(data)} items")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        # Always log before raising
        raise
```

## NEXT STEPS AFTER FIRST PROJECT

**Once you've built one project with ONE_SHOT:**

1. **Iterate on ONE_SHOT itself**
   - What questions were unclear?
   - What should be asked differently?
   - What defaults could be smarter?

2. **Build your second project**
   - It'll be faster (you know the questions)
   - PRD generation improves
   - Patterns emerge

3. **Create project templates**
   - Save answered questionnaires for project types
   - CLI tool template
   - Web app template
   - Data pipeline template

4. **Contribute improvements**
   - Better questions
   - More project types
   - Smarter defaults

---

## READY?

**Start by answering Q1 above and work through all questions.**

**Once done, say: "Questions complete, run validation"**

**Then we build your project autonomously.**

---

## HOW IT ALL WORKS TOGETHER HARMONIOUSLY

This section explains how **ONE_SHOT + Archon + Web Design + AI + Agent SDK** work together as a unified system, not competing approaches.

### The Complete Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      ONE_SHOT FRAMEWORK                      │
│  Philosophy: Ask everything upfront, execute autonomously    │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
    ┌────▼────┐                 ┌────▼────┐
    │ ARCHON  │                 │ CLAUDE  │
    │ METHODS │                 │ SKILLS  │
    └────┬────┘                 └────┬────┘
         │                           │
         │  ┌────────────────────────┤
         │  │                        │
    ┌────▼──▼────┐            ┌─────▼──────┐
    │ Systematic  │            │ Web Design │
    │ Debugging   │            │ Excellence │
    │ WHY Docs    │            │ AI/Agents  │
    │ Validation  │            │ MCP Tools  │
    └─────────────┘            └────────────┘
```

### Principle 1: ONE_SHOT Orchestrates Everything

**ONE_SHOT is the conductor**. It:
- Asks all questions upfront (no TBD)
- Generates complete PRD
- Decides which tools to use (Archon methods, AI, agents, web design)
- Executes autonomously

**Example**:
```
User: "Build me an AI-powered code review system"

ONE_SHOT asks:
- Q6: Type? → F (AI-Powered Web Application)
- Q20: Design? → C (Dark & Sleek)
- Q23: AI features? → Yes (code analysis, suggestions)
- Q24: Agent SDK? → Yes (need specialist agents)

ONE_SHOT decides:
✓ Use Archon validation patterns
✓ Use web design excellence (dark theme, glassmorphism)
✓ Use Agent SDK (orchestrator + specialist subagents)
✓ Use MCP (GitHub integration)
✓ Deploy to Tailscale HTTPS
```

### Principle 2: Archon Provides the Foundation

**Archon methods are always active**. They provide:
- **Validate Before Create**: Check dependencies before building
- **WHY Documentation**: Explain decisions, not just code
- **Systematic Debugging**: Isolate → Dependencies → Logs → Health
- **Health Endpoints**: All services expose `/health`
- **Dependency Awareness**: Prevent circular dependencies

**These work with everything**:
- Web apps get health endpoints
- AI agents document WHY they chose specific models
- Deployment validates Tailscale before deploying
- All errors follow systematic debugging

### Principle 3: Web Design Enhances User-Facing Projects

**Web design excellence activates for web projects** (types C, F, G):

```python
if project_type in ["Web Application", "AI-Powered Web App", "Landing Page"]:
    apply_web_design_excellence()
    # - Curated color palettes
    # - Modern typography (Google Fonts)
    # - Smooth animations
    # - Responsive design
    # - SEO best practices
```

**Non-web projects skip this** (CLI tools don't need glassmorphism).

### Principle 4: AI Adds Intelligence Where Needed

**AI integration is selective**:

```python
if user_wants_ai_features:
    if task_is_complex:
        use_agent_sdk()  # Full agent loop
    else:
        use_simple_api()  # Basic Claude calls
```

**AI doesn't replace logic**:
- Use AI for: content generation, semantic search, recommendations
- Use code for: CRUD operations, calculations, data validation

### Principle 5: Agent SDK Handles Complex Workflows

**Agent SDK activates for complex AI tasks**:

```python
if using_agent_sdk:
    # Orchestrator coordinates specialists
    agents = {
        "planning": PlanningAgent(),      # Breaks down tasks
        "backend": BackendAgent(),        # Builds API
        "frontend": FrontendAgent(),      # Builds UI
        "testing": TestingAgent(),        # Writes tests
        "review": ReviewAgent()           # Verifies work
    }
    
    # Each agent follows Archon principles
    for agent in agents.values():
        agent.add_health_endpoint()
        agent.document_why()
        agent.validate_before_create()
```

### Real-World Example: AI Code Review System

**User Answers**:
- Q1: "AI-powered code review system with automated suggestions"
- Q6: F (AI-Powered Web Application)
- Q20: C (Dark & Sleek design)
- Q23: Yes (code analysis, suggestions, pattern detection)
- Q24: Agent SDK (orchestrator + specialists)
- MCP: GitHub, Slack

**ONE_SHOT Generates This Architecture**:

```
┌─────────────────────────────────────────────────────┐
│              ORCHESTRATOR AGENT                      │
│  - Receives code review requests                    │
│  - Coordinates specialist agents                    │
│  - Synthesizes final review                         │
│  - Follows Archon validation patterns               │
└──────────────┬──────────────────────────────────────┘
               │
      ┌────────┼────────┬────────┐
      │        │        │        │
┌─────▼───┐ ┌─▼────┐ ┌─▼─────┐ ┌▼──────┐
│ Pattern │ │ Style│ │ Logic │ │ Docs  │
│ Agent   │ │ Agent│ │ Agent │ │ Agent │
└─────────┘ └──────┘ └───────┘ └───────┘
     │          │         │         │
     └──────────┴─────────┴─────────┘
                 │
         ┌───────▼────────┐
         │  WEB INTERFACE │
         │  - Dark theme  │
         │  - Glassmorphism│
         │  - Real-time UI│
         │  - SEO optimized│
         └────────────────┘
```

**How Components Work Together**:

1. **Archon Foundation**:
   - Validates GitHub MCP connection before starting
   - All agents expose `/health` endpoints
   - Documents WHY each agent specializes in its area
   - Systematic debugging if agents fail

2. **Web Design Excellence**:
   - Dark & sleek theme with glassmorphism
   - Smooth animations for code diffs
   - Responsive design (works on mobile)
   - Modern typography (Inter font)

3. **Agent SDK**:
   - **Orchestrator**: Coordinates review process
   - **Pattern Agent**: Detects anti-patterns (uses Sonnet)
   - **Style Agent**: Checks code style (uses Haiku)
   - **Logic Agent**: Analyzes logic errors (uses Sonnet)
   - **Docs Agent**: Verifies documentation (uses Haiku)
   - All agents work in parallel, return compact results

4. **MCP Integration**:
   - GitHub MCP: Fetch code, create review comments
   - Slack MCP: Notify team when review complete

5. **Verification Loop**:
   - Each agent verifies its own work
   - Orchestrator runs final validation
   - Visual feedback (screenshot of review UI)
   - LLM-as-judge checks review quality

**Result**: A production-ready AI code review system that:
- ✅ Looks stunning (web design excellence)
- ✅ Works reliably (Archon validation)
- ✅ Scales efficiently (agent SDK with subagents)
- ✅ Integrates seamlessly (MCP for GitHub/Slack)
- ✅ Self-corrects (verification loops)
- ✅ Costs ~$15-20/month (optimized model usage)

### Key Principles for Harmony

**1. Layered Architecture**:
```
ONE_SHOT (orchestration layer)
  ↓
Archon (foundation layer - always active)
  ↓
Specialized layers (activated as needed):
  - Web Design (for web projects)
  - AI/Agents (for intelligent features)
  - MCP (for integrations)
```

**2. No Conflicts**:
- Archon validation doesn't conflict with AI agents (agents also validate)
- Web design doesn't conflict with Archon (health endpoints work in web apps)
- Agent SDK doesn't conflict with ONE_SHOT (ONE_SHOT decides when to use it)

**3. Additive, Not Competitive**:
- Each component **adds** capabilities
- Nothing is **replaced** or **overridden**
- Simple projects use fewer components
- Complex projects use more components

**4. Decision Tree**:
```
Is it a web project?
  Yes → Apply web design excellence
  No → Skip web design

Does it need AI?
  Yes → Is it complex?
    Yes → Use Agent SDK
    No → Use simple API
  No → Skip AI

Does it need integrations?
  Yes → Use MCP servers
  No → Skip MCP

Always apply:
  - Archon validation
  - WHY documentation
  - Systematic debugging
  - Health endpoints (if service)
```

### Testing the Harmony

**Simple CLI Tool** (uses minimal components):
```
✓ ONE_SHOT questionnaire
✓ Archon validation
✗ Web design (not needed)
✗ AI (not needed)
✗ Agent SDK (not needed)
✗ MCP (not needed)

Result: Clean, validated CLI tool
```

**AI-Powered Web App** (uses all components):
```
✓ ONE_SHOT questionnaire
✓ Archon validation + WHY docs
✓ Web design excellence
✓ AI with Agent SDK
✓ MCP integrations

Result: Premium, intelligent, integrated web app
```

**The system scales from simple to complex without conflicts.**

---

**Version History**
- v1.3 (2024-11-26): **Claude Skills + FOSS Ethos** - Added web design excellence, AI-powered features, Claude Agent SDK (subagents, MCP, agent loops), comprehensive FOSS philosophy, flexible deployment (OCI or homelab), harmonious integration guide, and meta-documentation for living idea repository
- v1.2 (2024-11-21): Complete Archon integration - systematic debugging, health endpoints, microservices patterns, Caddy templates, Docker best practices
- v1.1 (2024-11-21): Added Archon methodology integration - Validate Before Create, Dependency Awareness, WHY documentation
- v1.0 (2024-11-21): Initial ONE_SHOT framework based on RelayQ, OOS, FrugalOS patterns

---

*This is ONE_SHOT: One file. One workflow. Infinite possibilities.*

**100% Free & Open-Source** • **Deploy Anywhere** • **No Vendor Lock-in**

*Build anything from simple CLI tools to AI-powered web applications with autonomous agents - on your terms, with your infrastructure.*

