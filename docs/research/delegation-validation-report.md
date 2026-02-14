# Validation Report: ONE_SHOT v12 → v12.1

**Validator**: Opus-class agent (independent review)
**Date**: 2026-02-13 (original), 2026-02-14 (v12.1 revision)
**Verdict**: PASS — slimmed to remove Claude Code native overlap

---

## v12 → v12.1 Changes

### Dropped (now native to Claude Code)

| v12 Rule | Claude Code Native Feature |
|----------|---------------------------|
| Max delegation depth: 2 | Subagents cannot spawn subagents (built-in) |
| Max parallel delegations: 4 | Managed internally by Claude Code |
| Per-agent-type timeouts | `max_turns` param on Task tool |
| Scope enforcement guidelines | Tool-access scoping per subagent type |
| Circuit breaker (3 failures) | Moved to SubagentStop hook (deterministic) |
| Cost dimension (5th) | Redundant — model routing via `model` param |
| Reversibility dimension (5th) | Folded into criticality assessment |

### Kept (genuine value-add)

| Rule | Why |
|------|-----|
| 3-dimension assessment (complexity, criticality, uncertainty) | Claude doesn't natively assess before delegating |
| Verification protocol (4 methods) | Claude trusts subagent results without checking |
| Fallback chain (3 attempts) | No built-in escalation path |
| When NOT to delegate | Prevents over-delegation of trivial tasks |

### Changed (prompt → hook)

| Before | After |
|--------|-------|
| Prompt instruction: "log to JSONL after delegation" | SubagentStop hook: deterministic logging, fires every time |

---

## Token Impact

| Version | delegation.md tokens | AGENTS.md delegation section |
|---------|---------------------|------------------------------|
| v12 | ~400 | ~200 |
| v12.1 | ~150 | ~100 |
| Saved | ~350 tokens/session | |

---

## Sources Used for Decision

- [Claude Code Subagents Docs](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
- [Claude Code Agent Teams](https://code.claude.com/docs/en/agent-teams)
- SubagentStop hook event type (v1.0.41+)
