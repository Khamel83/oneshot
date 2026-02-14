# ONE_SHOT v12: Intelligent Delegation Framework

**Based on**: "Intelligent AI Delegation" (Tomasev, Franklin, Osindero - Google DeepMind, Feb 2026)
**Paper**: arXiv:2602.11865
**Status**: PLAN - Pending validation and approval

---

## Executive Summary

ONE_SHOT v11 has solid foundations: skill routing, auto-delegation triggers, resilient execution via tmux, and context management. But it lacks the five properties Google DeepMind identifies as essential for real delegation: **dynamic assessment, adaptive execution, structural transparency, trust calibration, and systemic resilience**.

This plan adds those capabilities incrementally without rewriting ONE_SHOT. Each improvement is a concrete, implementable addition to the existing architecture.

---

## Gap Analysis: ONE_SHOT v11 vs. DeepMind Framework

| DeepMind Requirement | ONE_SHOT v11 Status | Gap |
|---------------------|---------------------|-----|
| **Dynamic Assessment** | Trigger-based (file count, duration, security signals) | No capability/risk/cost evaluation before delegation |
| **Adaptive Execution** | Manual failure-recovery skill | No mid-execution reassignment or automatic escalation |
| **Structural Transparency** | No audit trail | No verifiable completion, no attribution of delegated work |
| **Trust Calibration** | All agents treated equally | No performance tracking or trust scoring |
| **Systemic Resilience** | tmux survives disconnects | No protection against cascading agent failures |

---

## Proposed Changes (5 Modules)

### Module 1: Delegation Assessment Protocol

**What**: Before spawning a subagent, evaluate the task against four dimensions (from the paper): complexity, criticality, uncertainty, and cost.

**Where**: New file `.claude/rules/delegation.md` - loaded as a rule for all projects.

**How it works**:

```yaml
delegation_assessment:
  # Before spawning any Task agent, evaluate:
  dimensions:
    complexity:    # How many sub-steps? What reasoning depth?
      low: "Single tool call, direct answer"
      medium: "Multi-step, 2-5 tool calls"
      high: "Exploration + synthesis, 5+ tool calls"

    criticality:   # What happens if this fails?
      low: "Informational, no side effects"
      medium: "Code changes, reversible"
      high: "Deployment, auth, data mutation"

    uncertainty:   # How ambiguous is the task?
      low: "Clear inputs, known approach"
      medium: "Some unknowns, may need iteration"
      high: "Open-ended research, multiple valid approaches"

    cost:          # Token/compute budget
      low: "<5 tool calls, haiku-eligible"
      medium: "5-15 tool calls, sonnet"
      high: ">15 tool calls, opus required"

  # Decision matrix
  routing:
    - if: "complexity=low AND criticality=low"
      then: "Handle inline, no delegation"

    - if: "complexity=high OR criticality=high"
      then: "Delegate with monitoring checkpoint"

    - if: "criticality=high AND uncertainty=high"
      then: "Require human confirmation before proceeding"

    - if: "cost=low"
      then: "Use haiku model for subagent"
```

**Concrete deliverable**: A `delegation.md` rule file that codifies these assessment criteria. The AGENTS.md auto-delegation section gets updated to reference it.

---

### Module 2: Delegation Audit Log

**What**: Every delegated task gets logged with: what was delegated, to whom, what the result was, and whether it was verified.

**Where**: `.claude/delegation-log.jsonl` (append-only, one JSON line per delegation event)

**Schema**:

```json
{
  "timestamp": "2026-02-13T14:30:00Z",
  "session_id": "abc123",
  "delegator": "main-agent",
  "delegatee": "Explore-agent-xyz",
  "task_summary": "Find all error handling patterns in src/",
  "assessment": {
    "complexity": "medium",
    "criticality": "low",
    "uncertainty": "medium",
    "cost": "low"
  },
  "model_used": "haiku",
  "result": "success",
  "tool_calls": 8,
  "files_touched": ["src/errors.ts", "src/handler.ts"],
  "duration_ms": 12340,
  "verified": true,
  "verification_method": "output_review"
}
```

**Implementation**: A new skill `delegation-logger` that:
1. Is referenced in AGENTS.md auto-delegation section
2. Writes to the JSONL file after each delegation completes
3. Can be queried with `/delegation-log` to show recent delegations

**Why JSONL**: Append-only, survives crashes, easy to grep/jq, no database needed.

---

### Module 3: Adaptive Execution with Fallback Chains

**What**: When a delegated task fails or returns low-quality results, automatically retry with escalation rather than just failing.

**Where**: Update AGENTS.md `auto_delegation` section + new `delegation.md` rule.

**Fallback chain**:

```yaml
adaptive_execution:
  # Escalation chain for failed delegations
  chain:
    - attempt: 1
      strategy: "Original delegation (haiku if cost=low)"
      timeout: 120s

    - attempt: 2
      strategy: "Retry with sonnet, more context"
      timeout: 180s

    - attempt: 3
      strategy: "Escalate to main agent (opus), handle inline"
      timeout: 300s

    - attempt: 4
      strategy: "Ask human for guidance"
      action: "AskUserQuestion with failure context"

  # Mid-execution intervention triggers
  intervention:
    - signal: "Agent stuck in loop (>3 similar tool calls)"
      action: "Terminate and escalate"

    - signal: "Agent modifying files outside scope"
      action: "Terminate, revert, escalate"

    - signal: "Agent exceeded token budget by 2x"
      action: "Force completion, summarize partial results"
```

**Concrete deliverable**: Rules in `delegation.md` that define escalation behavior. The main agent checks delegation results before marking tasks complete.

---

### Module 4: Trust Calibration via Performance Tracking

**What**: Track which agent types and models succeed at which task types, and use that history to inform future delegation decisions.

**Where**: `.claude/delegation-stats.json` (updated periodically, not per-call)

**Schema**:

```json
{
  "agent_performance": {
    "Explore": {
      "tasks_delegated": 47,
      "success_rate": 0.89,
      "avg_tool_calls": 6.2,
      "best_at": ["codebase_search", "file_discovery"],
      "struggles_with": ["complex_synthesis", "cross_repo_analysis"]
    },
    "Bash": {
      "tasks_delegated": 23,
      "success_rate": 0.96,
      "avg_tool_calls": 1.8,
      "best_at": ["git_operations", "build_commands"],
      "struggles_with": []
    },
    "general-purpose": {
      "tasks_delegated": 31,
      "success_rate": 0.77,
      "avg_tool_calls": 12.1,
      "best_at": ["research", "multi_step_implementation"],
      "struggles_with": ["simple_lookups"]
    }
  },
  "model_performance": {
    "haiku": {
      "good_for": ["simple_search", "formatting", "single_file_edits"],
      "bad_for": ["architecture_decisions", "complex_debugging"]
    },
    "sonnet": {
      "good_for": ["most_tasks"],
      "bad_for": ["deep_architectural_reasoning"]
    }
  },
  "last_updated": "2026-02-13"
}
```

**Implementation**:
1. The delegation-logger (Module 2) feeds data into this
2. A periodic aggregation step (triggered by `/delegation-stats`) summarizes the log
3. The assessment protocol (Module 1) reads this to inform routing decisions

**Important constraint**: This starts as a manual/advisory system. The stats inform the human and the main agent, but don't autonomously override delegation decisions. Trust calibration should itself be calibrated gradually.

---

### Module 5: Resilience Against Cascading Failures

**What**: Prevent single-point-of-failure patterns in delegation chains.

**Where**: Updates to AGENTS.md resilience section + `delegation.md` rules.

**Rules**:

```yaml
resilience:
  # Prevent cascading failures
  max_delegation_depth: 2
  # An agent can delegate to a subagent, but that subagent
  # cannot delegate further. Prevents unbounded chains.

  max_parallel_delegations: 4
  # No more than 4 concurrent subagents. Prevents resource
  # exhaustion and makes monitoring feasible.

  delegation_timeout:
    default: 120s
    explore: 60s
    general_purpose: 180s
    bash: 30s

  # Circuit breaker
  circuit_breaker:
    threshold: 3  # consecutive failures
    cooldown: 300s  # 5 min before retrying same agent type
    action: "Log warning, switch to inline execution"

  # Scope boundaries
  scope_enforcement:
    - rule: "Delegated agents cannot modify files outside the task scope"
    - rule: "Delegated agents cannot make git commits"
    - rule: "Delegated agents cannot access secrets unless explicitly granted"
    - rule: "Delegated agents cannot spawn further subagents"
```

---

## Implementation Order

| Phase | Module | Effort | Dependencies |
|-------|--------|--------|--------------|
| 1 | Module 1: Assessment Protocol | Small | None |
| 2 | Module 5: Resilience Rules | Small | None |
| 3 | Module 2: Audit Log | Medium | Module 1 |
| 4 | Module 3: Adaptive Execution | Medium | Module 1, 2 |
| 5 | Module 4: Trust Calibration | Medium | Module 2, 3 |

Phases 1 and 2 can be done in parallel. They're just rule files. Phases 3-5 build on each other.

---

## What This Does NOT Do

- **No new external dependencies** - Everything is JSONL files and markdown rules
- **No complex orchestration framework** - Uses Claude Code's existing Task/subagent system
- **No autonomous decision-making changes** - Humans still approve critical actions
- **No breaking changes** - All additions are backward-compatible with v11
- **No over-engineering** - Starts simple (rules + logs), complexity added only when validated

---

## Validation Criteria

This plan succeeds if:

1. **Assessment**: Before delegating, the agent considers task dimensions (not just trigger patterns)
2. **Audit**: After delegation, there's a record of what happened and whether it worked
3. **Recovery**: Failed delegations escalate rather than just failing
4. **Learning**: Over time, delegation decisions improve based on tracked performance
5. **Safety**: No unbounded delegation chains, no scope violations, no cascading failures

---

## Relationship to Paper's Framework

| Paper Requirement | Our Implementation | Coverage |
|------------------|--------------------|----------|
| Dynamic Assessment | Module 1: 4-dimension evaluation | Full |
| Adaptive Execution | Module 3: Fallback chains + intervention | Full |
| Structural Transparency | Module 2: JSONL audit log | Full |
| Trust Calibration | Module 4: Performance tracking | Partial (advisory only) |
| Scalable Market Coordination | Not applicable | N/A (single-user system) |
| Systemic Resilience | Module 5: Circuit breakers + scope limits | Full |

**Market Coordination** is intentionally excluded - ONE_SHOT is a single-user framework, not a multi-tenant agent marketplace. If that changes, Module 4's trust data could feed into agent selection in a marketplace context.

---

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| **CREATE** | `.claude/rules/delegation.md` | Assessment protocol + resilience rules (Modules 1, 3, 5) |
| **CREATE** | `docs/research/ai-delegation-plan.md` | This document |
| **CREATE** | `docs/research/delegation-gap-analysis.md` | Detailed gap analysis |
| **MODIFY** | `AGENTS.md` | Update auto-delegation section to reference new rules |
| **MODIFY** | `.claude/rules/core.md` | Add delegation rule loading |
| **CREATE** | `.claude/commands/delegation-log.md` | `/delegation-log` slash command |
| **CREATE** | `.claude/commands/delegation-stats.md` | `/delegation-stats` slash command |

---

## Version Bump

This would be **ONE_SHOT v12: Intelligent Delegation**

Tag line: *"Delegation is a protocol, not a prompt."* (from the DeepMind paper's core thesis)
