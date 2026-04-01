# Review & Delegation Rules

## Planner/Worker Split

This is the architectural line that all routing follows:

### Claude Code Owns (Planner)
- Planning and decomposition
- Repo synthesis and context gathering
- Task classification and lane selection
- Final review and integration
- Sensitive edits (auth, data mutation)

### Workers Own (Bounded Execution)
- Bounded implementation tasks
- Test generation
- Draft documentation
- Search-result summarization
- Isolated experiments

## Assessment Before Delegating

| Dimension | Low | High |
|-----------|-----|------|
| **Complexity** | Single tool call | Exploration + synthesis, 5+ calls |
| **Criticality** | Read-only, informational | Deployment, auth, data mutation |
| **Uncertainty** | Clear inputs, known approach | Open-ended, multiple valid paths |

**Routing:**
- Low complexity + low criticality → handle inline, skip delegation
- High criticality + high uncertainty → ask before proceeding
- High criticality → git checkpoint before delegating
- Low complexity + low cost → use cheapest available model

## Verification After Delegating

| Task Type | Method |
|-----------|--------|
| Code search | Spot-check 1-2 claims against actual files |
| Code changes | Read modified files, confirm diff matches intent |
| Build / test | Check exit code (0 = success) |
| Research | Confirm key claims have real sources |

## Fallback Chain (3 attempts max)

```
1. Original worker (from lane pool)
   ↓ fails
2. Escalate to fallback_lane (from config/lanes.yaml)
   ↓ fails
3. Main agent (Claude) handles inline with full context
```

If all 3 fail → log blocker, skip, continue.

## Quality Gate

For adversarial/challenge phases:
- Codex (if available): fresh perspective on diffs and plans
- Always: Claude performs final integration

## Circuit Breaker

If same task fails 3 times with different approaches:
1. Log to `BLOCKERS.md` or `1shot/ISSUES.md`
2. Skip to next unblocked task
3. Continue without it

## Credit Assignment

After multi-span sessions, evaluate which delegations contributed most:

| Signal | Credit | Blame |
|--------|--------|-------|
| Output reused by later steps | +credit | |
| Last delegation before failure | | +blame |
| Wasted compute (no output) | | +blame |
| Unblocked a stuck task | +credit | |
| Low-cost delegation that succeeded | +credit | |
