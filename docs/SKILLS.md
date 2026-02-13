# ONE_SHOT Slash Commands Reference

A practical guide to all 21 slash commands - what they do and when to use them.

---

## Planning & Execution

### `/interview`
Triages your request by asking clarifying questions before coding. Classifies intent (new project, fix bug, continue work, modify existing, understand, quick task) and adjusts interview depth accordingly. Use this before starting any non-trivial work to avoid rework from unclear requirements. Outputs a spec file.

### `/cp` (Continuous Planner)
Creates a living plan stored in three files (`task_plan.md`, `findings.md`, `progress.md`) that survives `/clear`, context compression, and even switching between different AI models. Use for multi-session projects where you need persistent state. Each file has a specific purpose: plan holds decisions, findings holds research, progress holds the session log.

### `/run-plan`
Executes a continuous plan deterministically by reading the skill sequence from `task_plan.md` and running each skill step-by-step. Updates the plan files as it progresses. Use after `/cp` creates a plan. **Clear context first** with `/handoff` → `/clear` → `/restore` so the plan is fresh in context.

### `/implement`
Executes an approved plan with Beads task tracking. Breaks the plan into task groups, tracks progress via `bd` commands, commits after each task, and manages context thresholds. Use when you have a plan ready to execute. **Clear context first** for best results.

---

## Context Management

### `/handoff`
Saves a checkpoint of your current context before clearing. Captures what was done, what's in progress, key decisions, blockers, and next steps. Use before `/clear` or when context is getting full. Creates a file you can restore from.

### `/restore`
Resumes work from a handoff checkpoint. Checks Beads first for in-progress tasks (fast path), then falls back to reading the handoff file for full context restoration. Use after `/clear` to pick up exactly where you left off.

### `/sessions`
Views and searches encrypted session logs. All Claude Code sessions are auto-saved as encrypted markdown files. Use to find past conversations, decisions, or code from previous sessions. Different from `/restore` - this is for browsing history, not resuming work.

---

## Task Tracking

### `/beads`
Interface to the Beads task tracking system (`bd` CLI). Creates, updates, lists, and manages persistent tasks that survive across sessions. Use to track work in progress, see what's ready to work on next, and maintain task dependencies.

---

## Debugging & Quality

### `/diagnose`
Systematically debugs issues using hypothesis-based diagnosis. Starts with symptoms, isolates the problem layer (network → process → config → dependencies → data → code), checks past lessons, forms hypotheses, tests them, and applies minimal fixes. Use when something is broken or not working as expected.

### `/codereview`
Performs structured code reviews for quality and security. Checks OWASP Top 10, code quality patterns, accessibility (for frontend), and provides actionable feedback with severity levels. Use before merging, for security review, or when asking "is this safe?"

---

## Multi-File & Remote Operations

### `/batch`
Applies the same operation across many files using parallel background agents. Groups files into batches of 5, spawns an agent per batch, aggregates results, and handles failures with rollback. Use for pattern-based refactoring across 10+ files (renaming, adding imports, updating patterns). 10x faster than sequential.

### `/remote`
Executes commands on remote machines via SSH. Supports three workflows: sync-and-run (push code, execute on remote), data transfer (move files between machines for processing), and long-running jobs (tmux sessions). Routes to homelab for Docker/storage, macmini for GPU/transcription, oci-dev for APIs. Use when compute needs differ from current machine.

---

## Research & Documentation

### `/research`
Runs background research using Gemini CLI or search APIs. Investigates topics without blocking your main conversation. Use for gathering context on unfamiliar libraries, patterns, or domains.

### `/freesearch`
Zero-token web research via Exa API. Searches the web without consuming your context budget. Use before WebSearch to save tokens. Follows the docs-cache search order: local cache → freesearch → training data → WebSearch.

### `/doc`
Caches external documentation locally from a URL. Fetches via webReader MCP, saves to `~/github/docs-cache/`, and updates the index. Use to cache framework/library docs for offline reference. Run `/doc --list` to see what's cached.

### `/skill-discovery`
Automatically matches your goal to relevant skills. Searches local skills and suggests which ones to use. Use when you're not sure which skill applies to your task.

---

## Communication & Secrets

### `/audit`
Strategic communication filter that transforms raw emotional input into strategic output. Applies principles from negotiation experts (Chris Voss, Jim Camp) to strip emotional charge while preserving your position. Use before sending high-stakes communications to employers, clients, partners, or in any negotiation/conflict situation. Originally for divorce, but applicable to any difficult conversation.

### `/secrets`
Manages SOPS/Age encrypted secrets. Decrypts from `~/github/oneshot/secrets/` without exposing plaintext in chat. Use to access API keys, credentials, or any sensitive configuration.

---

## Thinking & Analysis

### `/think`
Multi-perspective analysis using expert personas. Applies different cognitive depths: "think" (quick check), "think hard" (trade-offs), "ultrathink" (exhaustive alternatives), "super think" (system-wide), "mega think" (paradigm questioning). Use for complex decisions where you want to see multiple angles.

---

## Stack & Updates

### `/stack-setup`
Configures a project with the standard Cloudflare + Postgres stack. Sets up Astro frontend, Cloudflare Workers for API, Better Auth, and Postgres on OCI via Hyperdrive. Use when starting a new web project that should follow the default stack.

### `/update`
Updates the ONE_SHOT framework itself and runs a health check. Syncs from the GitHub repo. Use to get the latest skills, rules, and fixes.

---

## Quick Reference by Intent

| I want to... | Use |
|--------------|-----|
| Plan a new feature | `/interview` → `/cp` |
| Execute a plan | `/handoff` → `/clear` → `/restore` → `/implement` or `/run-plan` |
| Continue after `/clear` | `/restore` |
| Save my place before clearing | `/handoff` |
| Find old conversations | `/sessions` |
| Track tasks across sessions | `/beads` |
| Debug something broken | `/diagnose` |
| Review code for security | `/codereview` |
| Edit 20+ files at once | `/batch` |
| Run on macmini/homelab | `/remote` |
| Research a topic | `/research` or `/freesearch` |
| Cache library docs | `/doc` |
| Filter a message before sending | `/audit` |
| Think through a complex decision | `/think` (or "think hard", "ultrathink", etc.) |
| Set up a new web project | `/stack-setup` |
| Update ONE_SHOT | `/update` |
