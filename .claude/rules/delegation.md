# Intelligent Delegation Rules (v12)

Based on: "Intelligent AI Delegation" (Tomasev et al., Google DeepMind, 2026)

---

## Assessment Protocol

Before spawning any Task/subagent, the main agent MUST assess the task against five dimensions.
This is a reasoning step — the agent evaluates these mentally, not via a runtime engine.

### Five Dimensions

| Dimension | Low | Medium | High |
|-----------|-----|--------|------|
| **Complexity** | Single tool call, direct answer | Multi-step, 2-5 tool calls | Exploration + synthesis, 5+ calls |
| **Criticality** | Informational, no side effects | Code changes, reversible | Deployment, auth, data mutation |
| **Uncertainty** | Clear inputs, known approach | Some unknowns, may iterate | Open-ended, multiple valid approaches |
| **Cost** | <5 tool calls, haiku-eligible | 5-15 tool calls, sonnet | >15 tool calls, opus required |
| **Reversibility** | Read-only (trivial to undo) | Git-revertable changes | Deployment, external mutations (hard to undo) |

### Routing Decisions

Based on assessment:

- **complexity=low AND criticality=low** → Handle inline, no delegation needed
- **complexity=high OR criticality=high** → Delegate, but review result before acting on it
- **criticality=high AND uncertainty=high** → Require human confirmation (AskUserQuestion) before proceeding
- **criticality=high AND reversibility=hard** → Create git checkpoint before delegating
- **cost=low AND complexity=low** → Use haiku model for subagent

---

## Delegation Audit Log

After every Task agent completes, log the delegation event.

### Log Location

`.claude/delegation-log.jsonl` — append-only, one JSON line per event.

### What to Log

```
- timestamp
- task_summary (what was delegated)
- agent_type (Explore, Bash, general-purpose, Plan)
- model_used (haiku, sonnet, opus)
- assessment (the 5 dimensions above)
- result (success | partial | failure)
- tool_calls_count
- files_read or files_modified (list)
- duration_ms (approximate)
- verification (method + result, see below)
```

### Verification Methods

After a delegated task completes, verify the result using the appropriate method:

| Task Type | Verification Method | How |
|-----------|-------------------|-----|
| Code search / exploration | **Output sampling** | Spot-check 1-2 claims against actual files |
| Code changes | **Diff review** | Read the modified files, confirm changes match intent |
| Build / test execution | **Exit code check** | Verify command succeeded (exit 0) |
| Research / synthesis | **Source check** | Confirm key claims have cited sources |

If verification fails, the result should be logged as `partial` or `failure` and the fallback chain triggered.

### Querying the Log

Use `/delegation-log` to view recent delegation events. The log can be filtered with jq:
- `jq 'select(.result == "failure")' .claude/delegation-log.jsonl` — show failures
- `jq 'select(.agent_type == "Explore")' .claude/delegation-log.jsonl` — show Explore delegations
- `jq '{agent_type, result}' .claude/delegation-log.jsonl | sort | uniq -c` — success rates by agent type

---

## Fallback Chain

When a delegated task fails or returns a `partial` result:

```
Attempt 1: Original delegation (selected model based on assessment)
    ↓ if fails
Attempt 2: Main agent handles inline (opus, full context)
    ↓ if fails
Attempt 3: Ask human for guidance (AskUserQuestion with failure context)
```

Rules:
- Do NOT retry with the same approach. If attempt 1 failed, attempt 2 must change strategy (different prompt, different scope, or handle inline).
- Log each attempt in the audit log.
- If the task was badly decomposed (not that the agent was too weak), restructure the task before retrying.

---

## Resilience Rules

### Delegation Depth
- **Max depth: 2** — A subagent cannot delegate to another subagent. This prevents unbounded delegation chains.

### Parallelism
- **Max parallel delegations: 4** — No more than 4 concurrent subagents. Makes monitoring feasible and prevents API rate limit exhaustion.

### Timeouts (per agent type)
| Agent Type | Timeout |
|------------|---------|
| Bash | 30s |
| Explore | 60s |
| general-purpose | 180s |
| Plan | 120s |

### Circuit Breaker
- **Threshold**: 3 consecutive failures from the same agent type
- **Action**: Log warning, switch to inline execution for that task type
- **Cooldown**: 5 minutes before retrying that agent type

### Scope Guidelines

These are prompt-level guidelines, not technical sandboxing. They depend on model instruction-following:

- Delegated agents should not modify files outside the stated task scope
- Delegated agents should not make git commits (only the main agent commits)
- Delegated agents should not access secrets unless the delegation explicitly grants access
- If a delegated agent violates scope, log the violation and review the result carefully

---

## When NOT to Delegate

Not every task benefits from delegation. Handle inline when:

- The task is a single tool call (read a file, run a command)
- The answer is already in context (no search needed)
- The task requires full conversation history (subagents don't have it unless you provide it)
- The task is security-sensitive and you need full control
