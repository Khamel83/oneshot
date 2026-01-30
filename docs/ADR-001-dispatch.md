# ADR-001: Multi-Model CLI Orchestration (/dispatch)

**Date**: 2025-01-29
**Status**: Accepted
**Deciders**: @Khamel83

---

## Context

### Problem

Claude Code tokens are expensive (~$3-15 per million depending on plan). When using ONE_SHOT for:
- Research tasks (literature review, API docs, best practices)
- Code generation (writing functions, boilerplate)
- Quick Q&A (what is X, how does Y work)

We were burning expensive Claude tokens on tasks that other AI models could handle equally well or better.

### Existing Approaches

1. **Use Claude for everything** - Expensive, hits token limits
2. **Manually switch CLIs** - Disrupts flow, no coordination
3. **Penny's service_router.py** - Works but Penny-specific, not portable

### Observations

- User already has multiple AI CLIs installed: claude, codex, gemini, qwen
- Each CLI is authenticated and ready to use
- Each CLI has strengths: claude (reasoning), codex (code), gemini (research+free), qwen (general+free)
- No unified way to route tasks to the best CLI

---

## Decision

### Create `/dispatch` Skill

A multi-model CLI orchestrator that:
1. **Auto-selects** the best CLI based on task keywords
2. **Accepts explicit** CLI selection (e.g., `/dispatch codex "..."`)
3. **Runs via Bash** - 0 Claude tokens for the actual work
4. **Saves output** to `~/github/oneshot/dispatch/` for reference
5. **Integrates with beads** for task tracking

### Model Selection Matrix

| Task Pattern | Routes To | Rationale |
|--------------|-----------|-----------|
| "research", "explain", "what is" | `gemini` | Free tier, has web search |
| "write code", "implement", "refactor" | `codex` | Optimized for code generation |
| "plan", "design", "architect" | `claude` | Best at complex reasoning |
| Ambiguous (no match) | Ask user OR default to `gemini` | Cheapest option |

### CLI Invocation Patterns

```bash
# Claude (reasoning)
claude -p "prompt" --output-format json

# Codex (code)
codex exec "prompt"

# Gemini (research, free)
gemini --yolo "prompt"

# Qwen (general, 2K free/day)
qwen "prompt"
```

### Output Structure

```
~/github/oneshot/dispatch/
└── <timestamp>-<cli>/
    ├── prompt.txt      # Original prompt
    ├── output.txt      # Raw CLI output
    └── summary.md      # Key findings (optional)
```

---

## Rationale

### Why This Approach?

1. **Zero API keys needed** - All CLIs are pre-authenticated
2. **Minimal Claude tokens** - Only for coordination/summary
3. **Leverages existing tools** - User already has these CLIs
4. **Standalone in ONE_SHOT** - No dependency on Penny or other projects
5. **Extensible** - Easy to add more CLIs (e.g., aider, cursor)

### Why Standalone vs. Penny Integration?

**Chose: Standalone in ONE_SHOT**

| Option | Pros | Cons |
|--------|------|------|
| **Standalone** | ✅ No cross-project dependency<br>✅ Works everywhere ONE_SHOT is installed<br>✅ Simpler | ❌ Duplicates some pattern logic |
| **Call Penny** | ✅ Reuses existing code | ❌ Requires Penny to be installed<br>❌ Creates tight coupling |

**Decision**: Standalone. The pattern is simple enough to duplicate, and portability matters more than DRY here.

### Why Add Qwen?

User's machines already have multiple AI CLIs. Qwen offers 2,000 free requests/day - perfect for overflow when other free tiers (Gemini) are exhausted.

---

## Consequences

### Positive

- ✅ **Token savings**: Research tasks use 0 Claude tokens
- ✅ **Best tool for job**: Code → codex, research → gemini, planning → claude
- ✅ **Extensible**: Easy to add more CLIs
- ✅ **Portable**: Works anywhere ONE_SHOT is installed

### Negative

- ⚠️ **Context split**: Output is in files, not Claude context
- ⚠️ **Latency**: CLI calls take time (30-90 seconds)
- ⚠️ **Maintenance**: New CLI versions may break invocation patterns

### Mitigations

- Output files are summarized back to Claude context
- Run in background for long tasks
- Test CLIs during installation/upgrade

---

## Alternatives Considered

### Alternative 1: Use Only Claude
**Rejected because**: Too expensive for routine tasks

### Alternative 2: Cloud API Calls
**Rejected because**: Requires API keys, less secure, not aligned with "local CLI" philosophy

### Alternative 3: Penny Integration Only
**Rejected because**: Creates tight coupling, Penny may not be installed

### Alternative 4: Sub-Agent Delegation
**Rejected because**: Still burns Claude tokens, negates the benefit

---

## Implementation

### Files Created/Modified

1. **Created**: `.claude/skills/dispatch/SKILL.md` - Main skill definition
2. **Modified**: `AGENTS.md` - Added to skill router + slash commands
3. **Modified**: `.claude/skills/INDEX.md` - Added to Free Research section
4. **Created**: `~/github/oneshot/dispatch/` - Output directory

### Testing

```bash
# Test gemini route
/dispatch "Research WebSocket best practices"

# Test codex route
/dispatch codex "Write a Python rate limiter"

# Test auto-selection
/dispatch "Implement a binary search tree"  # Should route to codex
```

### Installation

Qwen CLI installed via:
```bash
npm install -g @qwen-code/qwen-code
# Binary is named 'qwen', not 'qwen-code'
```

---

## Future Considerations

### Potential Enhancements

1. **Multi-step plans**: Execute TODO.md with different CLIs per step
2. **Confidence scoring**: Auto-select based on task complexity
3. **Fallback chain**: Try gemini → codex → qwen if one fails
4. **Output parsing**: Extract structured data from CLI responses

### Deprecation Criteria

Deprecate `/dispatch` if:
- Claude Code adds native multi-model support
- Token costs become negligible
- All external CLIs require API keys (losing the "pre-authenticated" advantage)

---

## References

- [ClawdBot Documentation](https://docs.openclaw.ai) - Inspiration for multi-model orchestration
- [Penny service_router.py](https://github.com/Khamel83/penny) - Existing implementation pattern
- [Gemini CLI](https://www.npmjs.com/package/@google/gemini-cli) - Free research
- [Qwen Code](https://www.npmjs.com/package/@qwen-code/qwen-code) - 2K free requests/day

---

**Document Version**: 1.0
**Status**: Implemented (v8.1)
