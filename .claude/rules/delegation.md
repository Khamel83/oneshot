# Delegation Rules (v12.1)

Informed by: "Intelligent AI Delegation" (Tomasev et al., Google DeepMind, 2026)

Claude Code already enforces: subagent depth limits, tool-access scoping, model routing, max_turns.
These rules cover what Claude Code does NOT do natively: assessment, verification, fallback, and restraint.

---

## Assess Before Delegating

Before spawning a Task/subagent, evaluate mentally (not a runtime check):

| Dimension | Low | High |
|-----------|-----|------|
| **Complexity** | Single tool call | Exploration + synthesis, 5+ calls |
| **Criticality** | Read-only, informational | Deployment, auth, data mutation |
| **Uncertainty** | Clear inputs, known approach | Open-ended, multiple valid paths |

**Routing:**
- Low complexity + low criticality → handle inline, skip delegation
- High criticality + high uncertainty → `AskUserQuestion` before proceeding
- High criticality → `git add -A && git commit` checkpoint before delegating
- Low complexity + low cost → use `model: "haiku"` on the Task call

---

## Verify After Delegating

Claude does not auto-verify subagent results. Always verify:

| Task Type | Method |
|-----------|--------|
| Code search | Spot-check 1-2 claims against actual files |
| Code changes | Read modified files, confirm diff matches intent |
| Build / test | Check exit code (0 = success) |
| Research | Confirm key claims have real sources |

If verification fails → trigger fallback chain.

---

## Fallback Chain (3 attempts max)

```
1. Original delegation (assessed model)
   ↓ fails
2. Main agent handles inline (full context)
   ↓ fails
3. AskUserQuestion with failure context
```

Never retry with the same approach. Change strategy between attempts.

---

## When NOT to Delegate

- Single tool call (just do it)
- Answer already in context
- Task needs full conversation history
- Security-sensitive work needing full control
- Trivial tasks — delegation overhead > task cost

---

## Audit Log

Delegation events are logged automatically via SubagentStop hook to `.claude/delegation-log.jsonl`.
Query with `/delegation-log` or `jq` directly.
