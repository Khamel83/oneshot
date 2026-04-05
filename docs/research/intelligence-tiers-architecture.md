# Intelligence Tiers & Cost Cascade Architecture

**Date**: 2026-04-04
**Status**: Design document — describes how every model invocation decision is made across all slash commands

---

## The Core Principle

**Claude plans. Free models execute. Paid models fill gaps. Claude reviews.**

Every slash command follows this pattern:
1. **One concentrated burst of Claude tokens** — plan, decompose, classify tasks
2. **Save plan to disk** — context can be cleared without losing work
3. **Dispatch tasks to free models in parallel** — gemini, codex, zai
4. **Claude reviews results** — quality gate, catches mistakes
5. **Only when free models fail or are exhausted** → cascade to paid OpenRouter via `or`
6. **Only when that fails** → Claude handles inline

---

## The Cost Cascade (ordered cheapest-first)

### Tier 0: Free Unlimited (no tokens, no quota)
| Tool | What | Cost | Expiry |
|------|------|------|--------|
| Argus | Search (SearXNG, Brave, Exa) | $0 | indefinite |
| Bash, Read, Write, Edit, Glob, Grep | Native Claude Code tools | $0 | indefinite |

These aren't "intelligence" — they're tools. But they're free and Claude Code always has them.

### Tier 1: Free Subscription Workers (already paying, no extra cost)
| Worker | Backend | What it's good at | Quota | Expiry |
|--------|---------|-------------------|-------|--------|
| `gemini_cli` | Google AI Pro | Research, coding, writing, long context | Generous | EOY 2026 |
| `codex` | ChatGPT Plus $20/mo | Coding, adversarial review, tasks | Monthly | Perpetual |

**These go first. Always.** If either is available, it handles the task. No API tokens spent.

### Tier 2: Free Provider (ZAI GLM Coding Plan)
| Worker | Backend | Model | Quota | Expiry |
|--------|---------|-------|-------|--------|
| `glm_claude` | ZAI via Claude CLI | glm-5-turbo | Plan limit | **2026-05-02** |
| `claw_code` | ZAI via claw-code-agent | glm-5-turbo | Plan limit | **2026-05-02** |

`glm_claude` is preferred — it runs the full Claude Code toolchain with GLM as the model brain.
`claw_code` is ~71% parity and only used for parallel dispatch.

### Tier 3: Paid OpenRouter via `or` function (Claude Code, non-Claude model)
| Model | Input/M | Output/M | Best for |
|-------|---------|----------|----------|
| `deepseek/deepseek-v3.2` | $0.26 | $0.38 | General work (default) |
| `google/gemini-2.5-flash-lite` | $0.10 | $0.40 | Throughput, cheap |
| `qwen/qwen3-coder:free` | $0 | $0 | Coding tasks (`or --code`) |
| `minimax/minimax-m2.7` | $0.30 | $1.20 | Long context |
| `moonshotai/kimi-k2.5` | $0.38 | $1.72 | Agentic tasks |

Full Claude Code session — same tools, CLAUDE.md, hooks. Just a different model thinking.
Used when tier 0-2 are unavailable or exhausted. Uses $20+ in existing OpenRouter credits.

### Tier 4: Claude Native (Sonnet/Opus)
| Model | Cost | Used for |
|-------|------|----------|
| Sonnet | Subscription tokens | Planning, decomposition, review gates |
| Opus | Subscription tokens (more expensive) | Complex planning, hard problems |

**Minimized.** Only used when cheaper models can't do the job.

---

## How Each Slash Command Uses This Cascade

### `/conduct` — Full Multi-Model Orchestration

**Phase 1: Plan (Claude Sonnet — tier 4)**
- Claude reads repo context, classifies tasks, creates plan
- Parallel subagents (gemini_cli, codex) research simultaneously — tier 1
- Claude synthesizes all subagent results into a structured plan
- **Plan saved to TASK_SPEC.md or PLAN.md**
- Context cleared or compacted

**Phase 2: Execute (free models — tiers 1-2)**
- New session loads just the plan
- Tasks dispatched to worker pool in parallel:
  ```
  gemini_cli → coding tasks
  codex      → coding tasks, adversarial review
  glm_claude → anything that needs full Claude Code toolchain
  claw_code  → parallel bounded tasks (when gemini/codex busy)
  ```
- Claude reviews each result — tier 4 (small, focused review calls)

**Phase 3: Cascade (when free models fail)**
- Worker fails 3x → lane escalation → next tier
- `cheap` lane exhaustion → `or` function kicks in (tier 3)
- `or` exhaustion → Claude handles inline (tier 4)

### `/short` — Quick Iteration

- Load context, check TaskList, ask what you're working on
- Small tasks → handle inline with Claude (tier 4, but minimal tokens)
- Medium tasks → dispatch to gemini_cli or codex (tier 1)
- Only if task requires heavy editing → Claude handles directly

### `/full` — Structured Work

**Phase 1: Intake (Claude — tier 4)**
- Goals, scope, architecture, constraints
- One Claude burst to understand the problem

**Phase 2: Plan (Claude + parallel research — tiers 4 + 1)**
- Subagents research in parallel (gemini, codex)
- Claude synthesizes into IMPLEMENTATION_CONTEXT.md
- Context checkpoint at 50% (suggest handoff)

**Phase 3: Execute (tiers 1-2, escalating to 3-4)**
- Tasks dispatched to free workers
- Claude reviews at milestones

### `/research` — Background Research

- **Argus does the search** — tier 0 (free, local)
- **Subagent summarizes** — gemini_cli (tier 1) or codex (tier 1)
- **Claude synthesizes final** — tier 4 (one call, results saved to .md)
- Total Claude cost: one synthesis call

### `/freesearch` — Zero-Token Research

- Argus in `cheap` mode (SearXNG only) — tier 0
- Returns results directly
- Claude cost: $0 (unless you ask follow-up questions)

---

## Task Classification → Model Selection

Every task gets a class and a category. The class determines the lane.
The category determines which model within the lane is preferred.

### Task Categories

| Category | Examples | Best Tier 1 Worker | Best Tier 3 Fallback |
|----------|----------|---------------------|----------------------|
| **coding** | Implement feature, fix bug, refactor | codex | `or --code` (qwen3-coder) |
| **research** | Investigate, gather info, compare options | gemini_cli | `or` (deepseek-v3.2) |
| **writing** | Docs, summaries, emails, reports | gemini_cli | `or` (deepseek-v3.2) |
| **review** | Code review, quality gate | codex (adversarial) | Claude inline (tier 4) |
| **general** | Project management, planning, analysis | gemini_cli | `or` (deepseek-v3.2) |

### Task Classes → Lane → Worker Flow

```
plan              → premium  → Claude only (tier 4, one burst)
research          → research → gemini_cli (tier 1) + argus (tier 0)
search_sweep      → research → argus only (tier 0)
implement_small   → cheap    → gemini_cli → codex → glm_claude → claw_code → `or`
implement_medium  → balanced → codex → gemini_cli → (escalate to premium)
test_write        → cheap    → gemini_cli → codex → glm_claude → claw_code
review_diff       → premium  → Claude only (tier 4)
doc_draft         → cheap    → gemini_cli → codex → glm_claude
summarize_findings→ cheap    → gemini_cli → codex
```

### When Claude Gets Used (Tier 4)

Claude is expensive — it should only appear when:
1. **Planning** — needs to understand full repo context and make judgment calls
2. **Reviewing** — quality gate, catches what free models miss
3. **High-risk tasks** — auth, security, deployment, production changes
4. **Complex orchestration** — tasks that require repo-wide synthesis
5. **Fallback** — when all cheaper options have failed

---

## The Ideal Session Flow (Your Requested Pattern)

```
You: /conduct "build a payment system"

1. CLAUDE (one burst)
   ├── Spawn 3 parallel subagents (gemini_cli, codex, argus)
   │   ├── Subagent A: Research payment providers
   │   ├── Subagent B: Explore existing codebase for patterns
   │   └── Subagent C: Search docs for Stripe/Vercel integration
   └── Synthesize into PLAN.md (saved to disk)

2. CONTEXT CLEAR / COMPACT
   └── Claude reads PLAN.md (minimal tokens to reload)

3. EXECUTE (free models, parallel)
   ├── gemini_cli: "Implement Stripe checkout handler" (coding)
   ├── codex: "Write tests for payment module" (test_write)
   ├── glm_claude: "Add payment schema migration" (coding)
   └── argus: "Search for PCI compliance requirements" (research)

4. REVIEW (Claude, one burst per result)
   ├── Review Stripe handler diff
   ├── Review test coverage
   ├── Review migration SQL
   └── Synthesize PCI findings

5. CASCADE (only if needed)
   └── gemini_cli fails → codex fails → `or` deepseek-v3.2

Total Claude cost: Plan (1 burst) + 4 reviews (4 small bursts) = ~5 bursts
Total free model cost: $0 (within quotas)
```

---

## Shell Functions (Your Direct Controls)

| Command | Model | Cost | When |
|---------|-------|------|------|
| `cc` | Claude Sonnet/Opus | Subscription | Normal session |
| `zai` | GLM-5-turbo | Free (until May 2) | Claude rate-limited |
| `or` | deepseek-v3.2 | $0.26/$0.38/M | Rate-limited + ZAI expired |
| `or --code` | qwen3-coder:free | Free | Coding tasks on OpenRouter |
| `OR_MODEL=x/y or` | Any OR model | Varies | Specific model needed |

All three (`cc`, `zai`, `or`) are identical Claude Code sessions. Same tools, same CLAUDE.md.

---

## What Still Needs To Be Done

1. **Task class → category mapping** — currently task-classes.md only has lane routing, not the category (coding/research/writing/general) that determines model preference within a lane
2. **Auto-detect rate limits** — detect when Claude subscription is exhausted and auto-suggest `or` or `zai`
3. **ZAI expiry handling** — when 2026-05-02 hits, glm models should drop out of the cascade automatically
4. **claw-code-agent deprecation path** — once `or` is proven for fallback sessions, claw-code-agent only serves parallel dispatch. Consider whether that's worth keeping.

---

## Key Files

| File | What it controls |
|------|-----------------|
| `config/lanes.yaml` | Task class → lane → worker pool order |
| `config/models.yaml` | Model metadata, pricing, capabilities |
| `config/workers.yaml` | Worker definitions, harness types |
| `config/providers.yaml` | API keys, endpoints per provider |
| `.claude/skills/_shared/providers.md` | Skill-level routing reference |
| `docs/instructions/task-classes.md` | Task classification rules |
| `core/dispatch/run.py` | Worker command builder + first_available logic |
| `~/.bashrc` (cc, zai, or) | Direct session launch functions |

---

## Billing Deadlines

| What | Expires | Action needed |
|------|---------|---------------|
| ZAI GLM Coding Plan | **2026-05-02** | Renew or glm drops to tier 3 (paid) |
| Google AI Pro | EOY 2026 | Renew before January 2027 |
| ChatGPT Plus | Perpetual ($20/mo) | None |
| OpenRouter credits | $20+ remaining | Top up when low |
| Claude subscription | Monthly/5hr | N/A — this is what we're minimizing |
