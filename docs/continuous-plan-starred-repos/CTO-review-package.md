# ONE_SHOT v11 - CTO Review Package

**Date**: 2026-02-06
**Reviewer**: Gemini CLI (as CTO)
**Author**: Claude Code

---

## Executive Summary

We analyzed 10 starred GitHub repos to identify opportunities for ONE_SHOT v11. **3 critical findings** emerged that significantly impact our roadmap.

### TL;DR for CTO Review

1. **claude-sneakpeek validation** ✅ - Confirms v10's "back to basics" was correct
2. **Native task tools exist** - Beads should be bridge, not long-term
3. **OpenClaw is orthogonal** - Different problem, no direct integration needed

---

## Context: ONE_SHOT v10 Changes

ONE_SHOT v10 recently simplified from framework → personal kit:
- **Removed**: Custom orchestration, /diagnose, /implement commands
- **Kept**: Skills system, AGENTS.md orchestration, /beads for tracking
- **Result**: 93% token reduction

**Question**: Did we simplify too much? Are we missing capabilities?

---

## Finding 1: claude-sneakpeek Validates v10 ⭐⭐⭐

### What We Tested
```bash
npx @realmikekelly/claude-sneakpeek quick --name claudesp
claudesp -p "List your available tools"
```

### What We Found
**Anthropic has built native multi-agent orchestration**:

| Native Tool | Purpose |
|-------------|---------|
| `TeammateTool.spawnTeam` | Create a new team |
| `TeammateTool.discoverTeams` | List available teams |
| `Task(subagent_type)` | Spawn specialized agents (bash, explore, plan...) |
| `TaskCreate/Update/Delete` | Built-in task management |

### Implication for ONE_SHOT
**v10's simplification was 100% correct.** Anthropic is building native orchestration. We should:
- ✅ Remove custom orchestration (done)
- ✅ Wait for native features to mature
- ✅ Document how to use native features with ONE_SHOT

**CTO Question**: Does this validate our "wait for native" stance?

---

## Finding 2: Task Management Decision ⭐⭐

### Options Compared

| Option | Pros | Cons |
|--------|------|------|
| **Native TaskCreate** | Built-in, Claude-aware | Requires swarm mode (unreleased) |
| **Beads (/beads)** | Git-backed, works everywhere | External tool, not Claude-aware |
| **CC-MIRROR tasks** | Project-scoped, proven | Requires legacy Claude 1.6.3 |

### Recommendation
```yaml
task_management:
  preferred: "native"  # Use Claude's TaskCreate when available
  fallback: "beads"    # Use /beads when native unavailable
  timeline: "Deprecate beads when native tools ship stable"
```

**CTO Question**: Is this hybrid approach sound, or should we invest differently?

---

## Finding 3: OpenClaw is Orthogonal ⭐

### Analysis
OpenClaw = Standalone personal AI assistant (15+ messaging channels, apps, voice)
ONE_SHOT = Dev productivity kit (terminal-based)

### Conclusion
**No integration needed.** Different problem spaces.

**CTO Question**: Agree with scope boundary?

---

## Proposed ONE_SHOT v11 Roadmap

### Phase 1: Documentation (Immediate)
- [ ] Update CLAUDE.md with "wait for native" stance
- [ ] Document native TaskCreate/Update usage
- [ ] Add deprecation notice to /beads command

### Phase 2: Progressive Disclosure (This Week)
- [ ] Load rules contextually by project type (web, cli, service)
- [ ] Reduce token usage for large rule sets
- [ ] Test token savings

### Phase 3: Task Tools Transition (When Native Ships)
- [ ] Detect native tool availability
- [ ] Auto-switch from beads to native
- [ ] Migration guide for existing users

### Phase 4: Clean Up (Future)
- [ ] Remove /beads command (after native stable)
- [ ] Remove legacy v9 code
- [ ] Update docs to reflect native-only approach

---

## CTO Review Questions

### Strategic Questions
1. **Does "wait for native" align with your vision?** Or should ONE_SHOT provide its own orchestration?

2. **Task management strategy** - Native first, beads fallback, or invest in beads?

3. **Progressive disclosure** - Worth implementing for token savings?

4. **OpenClaw scope** - Agree that we stay dev-focused and don't expand to channels/voice?

### Technical Questions
1. **Hybrid task detection** - How to reliably detect if native tools are available?

2. **Beads deprecation timeline** - When to start warning users?

3. **Token optimization** - Is progressive disclosure worth the complexity?

### Risk Assessment
1. **Native tools delayed** - What if Anthropic delays swarm mode release?
2. **Beads abandonment** - Risk of deprecating beads too early?
3. **Scope creep** - Risk of expanding beyond dev productivity?

---

## Validation Tasks Completed

✅ claude-sneakpeek installed and tested
✅ Native TaskCreate/Update/Delete documented
✅ TeammateTool operations documented
✅ OpenClaw analyzed (low synergy)
✅ CC-MIRROR vs Beads compared
✅ Task management recommendation drafted

---

## Appendix: Key Files

- `research/starred-repos-analysis/COMPREHENSIVE_REVIEW.md` - All 10 repos analyzed
- `docs/continuous-plan-starred-repos/claude-sneakpeek-validation.md` - Native tools findings
- `docs/continuous-plan-starred-repos/cc-mirror-vs-beads.md` - Task tools comparison
- `docs/continuous-plan-starred-repos/CTO-review-package.md` - This document

---

## CTO Instructions

Please review this plan and provide:
1. **Strategic feedback** - Does this direction make sense?
2. **Priority adjustments** - What should we do first/last?
3. **Risk concerns** - What are we missing?
4. **Approval** - Should we proceed with Phase 1?

Save your response to `docs/continuous-plan-starred-repos/CTO-feedback.md`
