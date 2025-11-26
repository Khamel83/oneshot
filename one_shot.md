# ONE_SHOT: AI-Powered Autonomous Project Builder

**Version**: 1.4  
**Philosophy**: Ask everything upfront, then execute autonomously  
**Deployment**: OCI Always Free Tier OR Homelab (i5, 16GB RAM, Ubuntu)  
**Cost**: $0/month infra (AI optional, low-cost)  

---

# 0. HOW TO USE THIS FILE

This file is meant to be loaded into an IDE agent (Claude Code, Cursor, etc.) and used as the **single spec** for building projects.

## 0.1 Operational Flow (Human + AI)

1. **Put this file in your repo** as `ONE_SHOT.md`.
2. **Open your dev agent** (Claude Code / Cursor) on that repo.
3. Tell it:

   > "Use `ONE_SHOT.md` as the spec. Ask me all *Core Questions* (Section 2) first. Don't write any code until I say `PRD approved. Execute autonomous build.`"

4. Answer all Core Questions once.
5. Agent generates a PRD (Section 5).
6. You reply: `PRD approved. Execute autonomous build.`  
7. Agent runs Section 6 (Autonomous Execution) and Section 7 (Architecture & Ops).

This is the contract: *questions once → PRD → autonomous build*.

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
Web server:   Caddy or Nginx
OS:           Ubuntu 22.04 LTS (or equivalent)
Network:      Tailscale (free tier, WireGuard based)
VC:           Git + GitHub (or self-hosted Gitea)
```

### 1.1.2 Conscious Tradeoffs

- We choose FOSS even when it costs ops work:
  - Self-hosted DB instead of fully managed RDS.
  - Tailscale instead of proprietary tunneling.
- We allow swappable proprietary options behind interfaces:
  - Claude API (AI), but behind a provider abstraction.
  - GitHub vs Gitea via Git remote.

## 1.2 Archon Principles (Always On)

These rules apply to every project ONE_SHOT builds:

- **Validate Before Create**
  - Check environment, dependencies, and connectivity before generating code or infra.
- **WHY Documentation**
  - For any non-trivial choice, document why, not just how.
- **Systematic Debugging**
  - Isolate layer → Check dependencies → Analyze logs → Verify health endpoints.
- **Health First**
  - Every long-running service exposes a `/health` endpoint.

## 1.3 Simplicity First (Core Principle)

**Before building anything, ask: Does this already exist?**

- **Prefer existing solutions** over building from scratch
- If a library/tool does 80% of what you need:
  - Fork it (give credit, follow license)
  - Wrap it with a thin layer for your use case
  - Document what you're doing and why
- **Building from scratch is the last resort**, not the first

**Examples**:
- Need a CLI? Use `click` or `typer`, don't write argument parsing
- Need a web server? Use FastAPI or Flask, don't write HTTP handling
- Need a database? Use SQLite or PostgreSQL, don't write storage
- Need auth? Use existing auth libraries, don't roll your own crypto

**When to build from scratch**:
- The existing solution is more complex than building it yourself
- You need something so specific that wrapping would be harder
- Learning is the goal (but document this as a learning project)

**Documentation requirement**:
- If using/forking existing code, document it clearly in README
- Credit original authors
- Explain what you added/changed and why
- Follow licenses (prefer MIT/Apache/BSD)

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
    - Summaries, categorization, analysis, content generation, simple code, reviews
  - **Upgrade models** (only when Flash Lite genuinely fails):
    - `anthropic/claude-3-5-haiku`: When Flash Lite gives bad results (~$0.80/M tokens)
    - `anthropic/claude-3-5-sonnet`: Complex code generation, critical decisions (~$3/M tokens)
    - `anthropic/claude-3-opus`: Mission-critical code, rarely needed (~$15/M tokens)
  - **Agent SDK**: Only when tasks are multi-step, iterative, or need tool orchestration.

### 1.5.1 Cost Philosophy

**Reality check**:
- Gemini 2.5 Flash Lite handles **99% of AI tasks** just fine
- Typical usage: $0.50-2/month
- Only upgrade if Flash Lite genuinely fails, not "just in case"
- **Total AI cost target**: $1-3/month for most projects

**Decision tree**:
1. Try Flash Lite first (always)
2. If it fails, try again with better prompting
3. If it still fails, consider `anthropic/claude-3-5-haiku`
4. Only use Sonnet/Opus if absolutely necessary

---

# 2. CORE QUESTIONS (REQUIRED FOR ANY PROJECT)

These are the Core 10. Every project must answer them.

## Q1. What Are You Building?

One sentence:

"A tool that does X for Y people."

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

Examples:
- No web UI (CLI only)
- No multi-user support
- No real-time sync

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

If files, format:
- YAML
- JSON
- CSV
- Other: ______

**Your choice**:
```
[LETTER + FORMAT IF FILES]
```

---

## Q10. Dependencies (Python / Node Packages)

Either specify or say "you decide" and ONE_SHOT will pick minimal defaults.

Example:

```
pyyaml  - YAML parsing
click   - CLI
requests - HTTP
pytest  - testing
```

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

Example:
- Project: `newsletter-archive`
- Repo: `newsletter-archive`
- Module: `newsletter_archive`

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

**Your choice** (optional):
```
[LETTER OR BLANK FOR DEFAULT]
```

**Defaults**:
- CLI / small tools → A (Flat)
- Web apps / services → C (Domain-driven)

---

## 3.2 Testing Strategy (Q17)

- **A.** Minimal (critical paths)
- **B.** Thorough (~80% coverage target)
- **C.** Comprehensive (near 100%)
- **D.** ONE_SHOT decides based on complexity

**Your choice** (optional):
```
[LETTER OR BLANK FOR DEFAULT]
```

**Defaults**:
- CLI: A/B depending on complexity
- Web apps / services: B

---

## 3.3 Deployment Preference (Q18)

- **A.** Local dev only
- **B.** Tailscale HTTPS (e.g. `https://project.your-tailnet.ts.net`)
- **C.** Systemd service (24/7)
- **D.** Both Tailscale + systemd

**Runtime**:
- OCI Always Free Tier VM
- Homelab (i5, 16GB, Ubuntu)
- Local only

**Your choice** (optional):
```
[LETTER] + [RUNTIME]
```

**Defaults**:
- Web apps / services → D (Tailscale + systemd) on your preferred host.
- CLI / pipelines → A (local only) unless otherwise stated.

---

## 3.4 Secrets & Env (Q19)

- No secrets needed
- Yes (list):

```
SECRET_NAME_1 = what it is
SECRET_NAME_2 = what it is
```

Provide values later in `.env`, not here.

**Your answer** (optional):
```
[LIST SECRETS OR "none"]
```

---

# 4. OPTIONAL: WEB DESIGN & AI

Skip entire Section 4 if you don't want web / AI.

---

## 4.1 Web Design (Q20–Q22)

Only relevant for Web / AI Web / Landing projects.

**Aesthetic**:
- **A.** Modern & Minimal
- **B.** Bold & Vibrant
- **C.** Dark & Sleek
- **D.** Professional & Corporate
- **E.** Creative & Playful
- **F.** ONE_SHOT decides
- **N/A**

**Color scheme**:
- **A.** Monochrome
- **B.** Complementary
- **C.** Analogous
- **D.** ONE_SHOT decides
- **N/A**

**Animation level**:
- **A.** Minimal
- **B.** Moderate
- **C.** Rich
- **N/A**

**Your choices** (optional):
```
Aesthetic: [LETTER OR N/A]
Color: [LETTER OR N/A]
Animation: [LETTER OR N/A]
```

---

## 4.2 AI Features (Q23)

Only if you actually want AI.

**Do you want AI?**
- No AI
- Yes, with these capabilities:
  - Content generation (summaries, descriptions, text)
  - Intelligent search (semantic / NL search)
  - Recommendations
  - Chat / conversational UI
  - Data analysis / pattern detection
  - Other: ______

**Budget**:
- Minimal ($0–5/month, Haiku + caching)
- Moderate ($5–20/month, Sonnet where it matters)
- Flexible ($20+/month, no strict constraints)

**OpenRouter API key**:
- Yes, will provide in `.env`
- No, not yet (get one at https://openrouter.ai/keys)
- N/A (no AI)

**Your answers** (optional):
```
AI: [YES/NO]
Capabilities: [LIST]
Budget: [LEVEL]
API Key: [STATUS]
```

---

## 4.3 Agents vs Simple API (Q24)

**Decision rule** (ONE_SHOT uses this):
- **If**:
  - AI is requested and
  - Project has multi-step workflows with tools (files, DB, GitHub, Slack, web search) and
  - You want it to operate semi-autonomously
  
  → Use **Claude Agent SDK** (or equivalent agent loop).

- **Else**:
  
  → Use **simple Claude API calls**.

**You can override**:
- Agent SDK (orchestrator + subagents, MCP tooling)
- Simple API only (no agent loop)
- N/A (no AI)

**Optionally describe agent architecture**:

```
If Agent SDK:
- Orchestrator + subagents:
  - ...
  - ...
  - ...
MCP servers needed:
- Filesystem
- GitHub
- Slack
- PostgreSQL
- Web search (Brave)
- Other: ...
```

**Your answer** (optional):
```
[AGENT SDK / SIMPLE API / N/A]
[ARCHITECTURE IF AGENT SDK]
```

---

# 5. ENVIRONMENT VALIDATION

ONE_SHOT always validates environment before building.

## 5.1 Validation Script

Run on your VM / homelab:

```bash
#!/usr/bin/env bash
# save as: scripts/oneshot_validate.sh
set -euo pipefail

echo "=== ONE_SHOT Environment Validation ==="

echo "[*] Python version:"
python3 --version || echo "❌ Python not found"

echo "[*] Git config:"
git config user.name  || echo "❌ user.name not set"
git config user.email || echo "❌ user.email not set"

echo "[*] GitHub access (optional, but recommended):"
if command -v gh >/dev/null 2>&1; then
  gh auth status || echo "❌ gh auth not configured"
else
  echo "gh not installed (ok if you use SSH remotes)"
fi

echo "[*] Tailscale:"
if command -v tailscale >/dev/null 2>&1; then
  tailscale status || echo "❌ tailscale not connected"
else
  echo "tailscale not installed (ok if no Tailscale deploy)"
fi

echo "[*] Disk space:"
df -h /

echo "[*] Memory:"
free -h || echo "free command not available"

echo "=== Validation complete ==="
```

You can either paste output into your agent or just confirm:

```
- [ ] All checks passed.
```

---

# 6. PRD GENERATION (WHAT THE AGENT DOES)

Once Core Questions are answered, ONE_SHOT generates a **Project Requirements Document** with:

1. **Overview**
   - Q1–Q3 summarized.
2. **Features & Non-Goals**
   - From Q4–Q5.
3. **Architecture**
   - Stack, storage, deployment from Q6–Q9, Q18.
4. **Data Models**
   - From Q7, expanded.
5. **Interfaces**
   - CLI/API/Library from Q11.
6. **AI/Web Design**
   - If Section 4 is used.
7. **Testing & Ops**
   - From Q16–Q17 and Archon defaults.
8. **Success Criteria**
   - From Q12.

**You say**:

```
PRD approved. Execute autonomous build.
```

At that point the agent stops asking questions and moves to execution.

---

# 7. AUTONOMOUS EXECUTION PIPELINE

ONE_SHOT's build loop, assuming PRD is approved.

## 7.1 Phase 0: Repo & Skeleton

- Create GitHub repo (if desired) with the name from Q13.
- Clone into VM/homelab under `~/projects/[project]` or similar.
- Initialize project layout (based on Q6 and Q16).
- Add `.editorconfig`, `.gitignore`, basic `README.md`.
- Configure pre-commit hooks (optional) for formatting/linting.

## 7.2 Phase 1: Core Implementation

- Implement data models (Q7).
- Implement storage layer (Q9).
- Implement main interface:
  - **CLI**: commands + argument parsing.
  - **Web**: FastAPI or equivalent + routes.
  - **Library**: public functions/classes.
- Implement critical paths first:
  - The minimum for v1 (Q12b).

## 7.3 Phase 2: Tests & Validation

- Create tests for:
  - Core data transformations.
  - Storage layer interactions.
  - CLI/API happy paths.
- Run tests; fix failures.
- Ensure tests can be run via:

```bash
pytest      # or equivalent
```

## 7.4 Phase 3: AI & Agents (If Enabled)

- Wire AI provider (Claude API) behind an abstraction:
  - `ai_client.py` (or equivalent).
- **For simple AI**:
  - Implement functions like `summarize(text)` or `tag(item)`.
- **For Agent SDK**:
  - Implement:
    - Orchestrator agent (task decomposition, synthesis).
    - Specialist subagents (research, analysis, writing, code, etc.).
    - MCP connections (GitHub, filesystem, DB, Slack) if requested.
  - Use context-efficient patterns (summaries instead of full logs).

AI config lives in `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-...
AI_MODEL_DEFAULT=claude-3-5-haiku-20241022
MAX_TOKENS_DEFAULT=1024
```

## 7.5 Phase 4: Deployment (If Chosen)

### 7.5.1 systemd service

For background services / APIs:

- Unit file: `/etc/systemd/system/[project].service`:

```ini
[Unit]
Description=[project] service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/projects/[project]
ExecStart=/usr/bin/python3 -m [module].main
Restart=always
EnvironmentFile=/home/ubuntu/projects/[project]/.env

[Install]
WantedBy=multi-user.target
```

- Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable [project]
sudo systemctl start [project]
sudo systemctl status [project]
```

### 7.5.2 Tailscale + Caddy

If web UI / API is exposed:

`/etc/caddy/Caddyfile`:

```caddy
project.your-tailnet.ts.net {
    reverse_proxy 127.0.0.1:8000
    encode gzip
}
```

Then:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

The app is then accessible via Tailscale HTTPS.

---

# 8. ARCHON OPS PATTERNS (CONDENSED)

ONE_SHOT assumes these patterns by default.

## 8.1 Health Endpoints

For any HTTP service, add:

```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
```

Make health checks part of Docker/systemd health mechanisms.

## 8.2 Systematic Debugging

When something breaks, the sequence is:

1. **Check systemd / container**:

```bash
systemctl status [project]
journalctl -u [project] --since "1 hour ago"

docker compose ps
docker compose logs [service]
```

2. **Check `/health` endpoint**.
3. **Check logs from the app itself**.
4. **Only then change code**.

## 8.3 Docker Compose Pattern (If Used)

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

# 9. AI INTEGRATION (SINGLE SOURCE OF TRUTH)

Short, unified guidance.

## 9.1 Provider & Model Choices

**Default Stack**:
- **Provider**: OpenRouter (https://openrouter.ai)
  - Unified API for 100+ models
  - Pay-as-you-go, no subscriptions
  - Very affordable models available
- **Default Model**: `google/gemini-2.5-flash-lite`
  - **Very cheap** (~$0.10-0.30 per million tokens)
  - Ultra-low latency, fast token generation
  - Good enough for 80% of tasks

**Model Selection Guide**:

| Task Type | Model | Cost | When to Use |
|-----------|-------|------|-------------|
| Summaries, tags, categorization | `google/gemini-2.5-flash-lite` | ~$0.10-0.30/M | Default for all tasks |
| Simple code (refactors, reviews) | `google/gemini-2.5-flash-lite` | ~$0.10-0.30/M | Default for coding |
| Complex code generation | `anthropic/claude-3-5-haiku` | ~$0.80/M | When Flash Lite fails |
| Architecture, critical code | `anthropic/claude-3-5-sonnet` | ~$3/M | When quality critical |
| Mission-critical code | `anthropic/claude-3-opus` | ~$15/M | Rarely needed |

**Cost Reality Check**:
- Gemini 2.5 Flash Lite: ~$0.50-2/month for typical usage
- Typical project: $1-3/month
- With occasional upgrades: $2-5/month
- Heavy usage: $5-10/month

## 9.2 Usage Pattern (Python with OpenRouter)

```python
import os
import requests

# OpenRouter API (works with any model)
def ai_call(
    prompt: str,
    model: str = "google/gemini-2.5-flash-lite",
    max_tokens: int = 512
) -> str | None:
    """
    Call AI via OpenRouter.
    
    Models:
    - google/gemini-2.5-flash-lite (default, free)
    - anthropic/claude-3-5-haiku (when Flash isn't enough)
    - anthropic/claude-3-5-sonnet (critical code)
    """
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException:
        return None


# Example usage
def summarize_text(text: str) -> str:
    """Summarize using free Google Flash."""
    prompt = f"Summarize this in 2-3 sentences:\n\n{text}"
    return ai_call(prompt, model="google/gemini-2.5-flash-lite")


def generate_code(description: str) -> str:
    """Generate code using claude-3-5-sonnet (when quality matters)."""
    prompt = f"Write Python code for: {description}"
    return ai_call(prompt, model="anthropic/claude-3-5-sonnet", max_tokens=2048)
```

## 9.3 Environment Variables

```bash
# .env file
OPENROUTER_API_KEY=sk-or-v1-xxxxx  # Get from https://openrouter.ai/keys

# Optional: Set default model
AI_MODEL_DEFAULT=google/gemini-2.5-flash-lite
MAX_TOKENS_DEFAULT=512

## 9.4 When to Use Which Model

**Use Gemini 2.5 Flash Lite for 99% of tasks**:
- Content summarization
- Tagging and categorization
- Simple text transformations
- Data extraction from text
- Basic Q&A
- Code reviews and refactors
- Simple code generation
- **Default for everything**

**Only upgrade when Flash Lite genuinely fails**:

**`anthropic/claude-3-5-haiku`** (~$0.80/M tokens):
- Flash Lite gives inconsistent results
- Need better code understanding
- More complex reasoning required

**`anthropic/claude-3-5-sonnet`** (~$3/M tokens):
- Generating complex code
- Architecture decisions
- Critical business logic

**`anthropic/claude-3-opus`** (~$15/M tokens):
- Mission-critical code that cannot fail
- Rarely needed

## 9.5 Cost Management

```python
# Track usage
import logging

logger = logging.getLogger(__name__)

def ai_call_with_tracking(prompt: str, model: str, max_tokens: int = 512):
    """AI call with cost tracking."""
    result = ai_call(prompt, model, max_tokens)
    
    # Estimate cost (rough)
    input_tokens = len(prompt.split()) * 1.3  # rough estimate
    output_tokens = len(result.split()) * 1.3 if result else 0
    
    logger.info(f"AI call: model={model}, in={input_tokens:.0f}, out={output_tokens:.0f}")
    return result


# Use caching for repeated queries
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_ai_call(prompt: str, model: str = "google/gemini-2.5-flash-lite"):
    """Cache results for identical prompts."""
    return ai_call(prompt, model)
```

## 9.6 Why OpenRouter?

**Benefits**:
- **Unified API**: One API key for 100+ models
- **Easy switching**: Change models with one line of code
- **Unified billing**: One bill for all AI usage
- **No lock-in**: Switch providers anytime
- **Fallbacks**: Automatic failover if a model is down

**When you might use direct APIs**:
- Provider-specific features (e.g., Claude prompt caching)
- Absolute latest model versions
- Enterprise contracts with specific providers

**Recommendation**: Use OpenRouter unless you have a specific reason not to.

---

# 10. CANONICAL EXAMPLES (CONDENSED)

These are patterns, not something to memorize.

## 10.1 Minimal: Local-Only CLI Finance Tracker

- **Type**: A (CLI Tool)
- **Storage**: SQLite
- **No AI, no web, local only**.
- **Commands**:

```bash
finance import transactions.csv
finance categorize
finance report --month 2024-01
finance export --category groceries
```

Shows the simplest path: Core Questions → PRD → single binary CLI.

---

## 10.2 Medium: Non-AI Web App Dashboard

Example: Headcount dashboard pulling from a Postgres DB.

- **Type**: C (Web Application)
- **Storage**: PostgreSQL
- **Web**: FastAPI backend + simple frontend.
- **Deployment**: systemd + Tailscale.

Shows web design, DB, health endpoints, Tailscale, but no AI.

---

## 10.3 Complex: AI Code Review with Subagents

- **Type**: F (AI-Powered Web Application)
- **AI**: Yes, Agent SDK.
- **MCP**: GitHub, filesystem, maybe Slack.

**Architecture**:
- **Orchestrator agent**:
  - Receives a PR or diff.
  - Calls:
    - Pattern agent (anti-patterns, smells).
    - Style agent (consistency, formatting).
    - Logic agent (edge cases, bugs).
  - Synthesizes final review.
- **Web UI**:
  - Dark & sleek.
  - Shows diffs + AI comments.
- **Ops**:
  - `/health` endpoint.
  - systemd + Tailscale.
  - Logs + systematic debugging.

Shows where Agent SDK actually makes sense.

---

# 11. GOAL VS BASELINE

To keep expectations aligned:

## 11.1 Baseline Contract

For every ONE_SHOT project:
- A PRD is generated and kept in the repo.
- Code compiles / runs for the v1 scope.
- There is at least a minimal test suite for critical paths.
- Long-running services have `/health`.
- README explains how to run and deploy.

## 11.2 Goal State (Stretch)

- Fully autonomous build from PRD to deployed system.
- Clean commits per milestone, descriptive messages.
- Integrated AI agents where appropriate.
- Robust test coverage and CI.

**Reality**: depending on complexity and tool limits, some manual nudging may still be needed. The design assumes that and keeps everything documented and recoverable.

---

# 12. META: LIVING IDEA REPOSITORY

ONE_SHOT is also your idea sink for future improvements.

## 12.1 Rules for Updating This File

- **You don't hand-edit structure**.

Instead, you tell the agent:
- "Add this concept: [idea]"
- "Incorporate this pattern: [link/description]"
- "Adjust the defaults so that X happens for web projects."

- **The agent**:
  - Integrates new idea into the right section.
  - Keeps Core Questions compact.
  - Avoids duplication (one source of truth per concept).
  - Updates version history (Section 13).

---

# 13. VERSION HISTORY

- **v1.4** (2024-11-26)
  - Single-file layout but hierarchically structured.
  - Clear Core Questions vs Advanced vs Optional AI/Web.
  - Unified AI section; Archon ops condensed.
  - Added "Baseline vs Goal" clarifications and explicit usage instructions for IDE agents.
- **v1.3** (2024-11-26)
  - Added detailed AI & Agent SDK patterns, MCP integration, web design excellence, and FOSS deployment philosophy.
- **v1.2** (2024-11-21)
  - Archon integration: validation, health endpoints, microservices, Caddy, Docker best practices.
- **v1.1** (2024-11-21)
  - Introduced Validate Before Create, dependency awareness, WHY documentation.
- **v1.0** (2024-11-21)
  - Initial ONE_SHOT framework: front-loaded questionnaire, PRD → autonomous build loop.

---

**ONE_SHOT: One file. One workflow. Infinite possibilities.**

**100% Free & Open-Source** • **Deploy Anywhere** • **No Vendor Lock-in**
