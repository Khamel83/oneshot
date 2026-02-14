# Plan: Integrate Agent Lightning Concepts into ONE_SHOT

**Branch**: `claude/integrate-agent-lightning-QXAKk`
**Depends on**: PR #5 (`claude/ai-delegation-research-3HdfP`) — AI Delegation v12.1
**Sequence**: This merges AFTER PR #5

---

## Context

**PR #5** added Intelligent Delegation (v12.1) based on DeepMind's paper:
- Assessment protocol (complexity, criticality, uncertainty)
- Verification after delegation
- Fallback chains (3 attempts, escalate to human)
- Audit logging via SubagentStop hook → `.claude/delegation-log.jsonl`
- Trust calibration (Module 4, advisory — planned but not fully built)

**Agent Lightning** (Microsoft) is an RL training framework for AI agents. Its core ideas:
- **Spans**: Structured execution traces capturing prompts, completions, tool calls, rewards
- **Trajectories**: Complete execution paths assembled from spans
- **Credit assignment**: Evaluating which step contributed to outcome (hierarchical RL)
- **LightningStore**: Central data exchange between execution and learning
- **Training loop**: Continuous cycle of execute → trace → learn → improve

**The bridge**: PR #5 gives us *assessment + logging*. Agent Lightning gives us *structured traces + learning*. Together they create a system that doesn't just log delegation events — it learns from them.

---

## What We Take From Agent Lightning (Concepts, Not Dependencies)

We are NOT adding `pip install agentlightning` or building RL training. We're borrowing the conceptual architecture and applying it to ONE_SHOT's prompt-based system.

| Agent Lightning Concept | ONE_SHOT Adaptation |
|------------------------|---------------------|
| **Spans** | Enrich delegation-log.jsonl entries with structured trace data (input context, output, tool sequence) |
| **Trajectories** | Chain spans into session-level execution paths for pattern analysis |
| **Credit assignment** | Per-step success scoring in delegation log → feeds trust calibration |
| **LightningStore** | The `.claude/delegation-log.jsonl` + `.claude/delegation-stats.json` combo from PR #5 |
| **Training loop** | `/delegation-stats` aggregation → rules update → better future decisions (prompt-level "training") |

---

## Implementation Steps

### Step 1: Rebase on PR #5

Before any work, rebase this branch on `claude/ai-delegation-research-3HdfP` so we have:
- `.claude/rules/delegation.md`
- `.claude/hooks/delegation-log-hook.sh`
- `.claude/commands/delegation-log.md`
- Updated AGENTS.md (v12.1)

### Step 2: Enrich Span Format in Delegation Log

Upgrade the delegation-log-hook.sh to capture richer span data inspired by Agent Lightning:

**Current schema** (from PR #5):
```json
{"timestamp", "agent_type", "model", "result", "tool_calls_count", "duration_ms", "summary"}
```

**Enhanced schema** (Agent Lightning-inspired):
```json
{
  "timestamp": "...",
  "span_id": "uuid",
  "session_id": "from-env",
  "agent_type": "Explore",
  "model": "haiku",
  "task_input": "first 200 chars of task prompt",
  "task_output": "first 200 chars of result",
  "tool_sequence": ["Glob", "Read", "Read", "Grep"],
  "tool_calls_count": 4,
  "duration_ms": 12340,
  "result": "success",
  "assessment": {
    "complexity": "medium",
    "criticality": "low"
  },
  "reward": 1.0
}
```

Key additions:
- `span_id` — unique ID for chaining into trajectories
- `session_id` — groups spans into session-level trajectories
- `task_input` / `task_output` — the prompt and result (truncated)
- `tool_sequence` — ordered list of tools used (the "action sequence" in RL terms)
- `reward` — heuristic success score (1.0=success, 0.5=partial, 0.0=failure)

**File**: Update `.claude/hooks/delegation-log-hook.sh`

### Step 3: Add Trajectory Assembly

Create a `/delegation-trajectory` command that chains spans by session_id into a full execution path. This shows:
- The sequence of delegations in a session
- Which succeeded/failed
- Total tool calls and duration
- The "critical path" (longest chain of dependent delegations)

**File**: Create `.claude/commands/delegation-trajectory.md`

### Step 4: Add Credit Assignment Heuristics

Update `.claude/rules/delegation.md` to include credit assignment guidance:
- When a multi-step task succeeds, which delegation was most valuable?
- When it fails, which delegation was the bottleneck?
- Simple heuristics: last-delegation-before-failure gets blame, delegations that produced reused outputs get credit

This feeds into Module 4 (Trust Calibration) from PR #5 — the performance stats become reward-weighted rather than just success/fail counts.

**File**: Update `.claude/rules/delegation.md` (add credit assignment section)

### Step 5: Enhance Trust Calibration with Reward Signals

Upgrade the planned `/delegation-stats` to use reward-weighted metrics:
- Instead of just "Explore: 89% success rate", show "Explore: avg reward 0.82, best at codebase_search (0.94), worst at synthesis (0.61)"
- This is the Agent Lightning "training loop" expressed as prompt-level learning

**File**: Create/update `.claude/commands/delegation-stats.md`

### Step 6: Document the Conceptual Bridge

Create a research doc explaining how Agent Lightning concepts map to ONE_SHOT, why we adapted rather than adopted, and what this enables for future versions.

**File**: Create `docs/research/agent-lightning-integration.md`

### Step 7: Version Bump AGENTS.md to v12.2

Update AGENTS.md to reference the new span format, trajectory assembly, and credit assignment. Tag as v12.2 (building on v12.1 from PR #5).

**File**: Update `AGENTS.md`

---

## Files Changed Summary

| Action | File | Step |
|--------|------|------|
| REBASE | Branch onto PR #5 | 1 |
| UPDATE | `.claude/hooks/delegation-log-hook.sh` | 2 |
| CREATE | `.claude/commands/delegation-trajectory.md` | 3 |
| UPDATE | `.claude/rules/delegation.md` | 4 |
| CREATE/UPDATE | `.claude/commands/delegation-stats.md` | 5 |
| CREATE | `docs/research/agent-lightning-integration.md` | 6 |
| UPDATE | `AGENTS.md` | 7 |

---

## What This Does NOT Do

- No `pip install agentlightning` — we borrow concepts, not the library
- No actual RL training — ONE_SHOT is a prompt framework, not a training framework
- No GPU requirements — everything stays as JSONL + markdown rules
- No breaking changes to PR #5 — purely additive
- No new external dependencies of any kind

---

## Why This Matters

PR #5 asks: "Should I delegate this? Did it work?"
This branch asks: "What can I learn from how it went?"

Together they create a delegation system that:
1. **Assesses** before delegating (PR #5)
2. **Traces** execution with structured spans (this branch)
3. **Assigns credit** to individual steps (this branch)
4. **Learns** from accumulated experience (this branch + PR #5 Module 4)
5. **Verifies and escalates** on failure (PR #5)

---

## Sources

- [Microsoft Agent Lightning (GitHub)](https://github.com/microsoft/agent-lightning)
- [Agent Lightning: Adding RL to AI Agents (Microsoft Research Blog)](https://www.microsoft.com/en-us/research/blog/agent-lightning-adding-reinforcement-learning-to-ai-agents-without-code-rewrites/)
- [Agent Lightning Documentation](https://microsoft.github.io/agent-lightning/latest/)
- PR #5: AI Delegation Research (`claude/ai-delegation-research-3HdfP`)
