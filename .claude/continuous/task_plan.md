# Task Plan: ONE_SHOT v9 Refactor - "Play Calling" System

**Created**: 2026-02-02
**Status**: In Progress
**Last Updated**: 2026-02-02 12:04

## Summary
Refactor ONE_SHOT to implement the "offensive coordinator" model where user calls plays (skills), and the system executes them deterministically. Focus on reducing context bloat and making skill orchestration explicit.

## Problem Statement
- **Context bloat**: v8.3 loads 15K chars of skill descriptions at startup (20% of context)
- **Implicit skill usage**: Skills are invoked implicitly, plans don't explicitly list which skills to use
- **No automatic skill discovery**: User must manually know which skills exist
- **Running in circles**: Previous refactor attempts added complexity without clear value

## Goals
- [ ] Reduce context bloat from 15K to ~3K chars (skill names + descriptions only)
- [ ] Make skill usage explicit in plans
- [ ] Add automatic skill discovery (local + SkillsMP)
- [ ] Implement deterministic skill execution (`/run-plan`)
- [ ] Track all work in beads
- [ ] Maintain continuous plan throughout refactor

## Non-Goals
- Replacing skills with SkillsMP equivalents (unless better)
- Rewriting entire system
- Losing any existing functionality
- Breaking changes without clear benefit

## Decisions
| # | Question | Options | Decision | Rationale |
|---|----------|---------|----------|-----------|
| 1 | How to reduce context bloat? | Load less, compress, lazy-load | Lazy-load full skills | Only load descriptions, full content on invoke |
| 2 | Should we replace skills with SkillsMP? | Yes, No, Hybrid | No - keep unique skills | Skills are secondary to orchestration |
| 3 | Make skill discovery automatic or manual? | Auto, Manual, Both | Automatic | System should find skills, not user |

## Technical Approach

### Architecture
```
User says "Build X"
  ↓
Front-door: Check skill inventory (what do we have?)
  ↓
Continuous-planner: Create plan with explicit skill list
  ↓
User approves
  ↓
Implement-plan: Execute skills deterministically
  ↓
Beads: Track progress
```

### Key Components
1. **skills_inventory.json**: Names + descriptions only (~3K chars vs 15K)
2. **Lazy-loading**: Full skill content loaded only when invoked
3. **Skill contracts**: Input/output definitions (later phase)
4. **Automatic SkillsMP lookup**: When planning, check SkillsMP for gaps (later phase)
5. **`/run-plan`**: Execute skill sequences deterministically (later phase)

## Implementation Phases

### Phase 1: Fix Context Bloat (Status: ✅ Complete)
- [x] 1.1: Create skills_inventory.json with names + descriptions
- [ ] 1.2: Modify skill loading to lazy-load full content (DEFERRED - not needed)
- [x] 1.3: Measure context before/after (Skills only 2.2K/1.1% - not a problem)
- [x] 1.4: Test with real workflows

**Bead**: oneshot-5kd ✅ Closed

### Phase 2: Make Skills Explicit in Plans (Status: ✅ Complete)
- [x] 2.1: Enhance create-plan to list required skills
- [x] 2.2: Enhance continuous-planner to show skill sequences
- [x] 2.3: Update implement-plan to follow skill list
- [x] 2.4: Test deterministic execution

**Result**: Skill Sequence table added to task_plan.md template

### Phase 3: SkillsMP Integration (Status: ✅ Complete)
- [x] 3.1: Create SkillsMP API wrapper
- [x] 3.2: Add automatic skill lookup during planning
- [x] 3.3: Install SkillsMP skills on-demand
- [x] 3.4: Test with real scenarios

**Result**: skill_discovery.py with --skillsmp flag, skillsmp-search skill created

**Note**: API key intermittently returns 401 - may need verification from skillsmp.com

## Dependencies
- Continuous planner skill (already created)
- Beads system (already exists)
- v9-refactor branch (already created)

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing workflows | Low | High | Test each phase, maintain backward compat |
| SkillsMP API changes | Med | Low | Cache locally, handle failures gracefully |
| Context doesn't reduce enough | Low | Med | Measure early, iterate if needed |
| Adding complexity without value | Med | High | One change at a time, measure impact |

## Success Metrics
- Context at startup: < 5K chars (down from 15K)
- Plans explicitly list skills: Yes
- Skills discoverable without manual search: Yes
- Beads tracking all work: Yes
- Continuous plan maintained: Yes

## Beads Integration
- **Epic**: oneshot-5kd (Fix context bloat)
- **Phase tasks**: Created as needed
- **Sync**: After each phase completion

## MCP Tools Available
- Vision MCP: ui_to_artifact, diagnose_error_screenshot
- Web Search MCP: webSearchPrime for research
- Zread MCP: search_doc, get_repo_structure, read_file

---
## Revision History
| Date | Changed By | Summary |
|------|------------|---------|
| 2026-02-02 | claude | Initial plan - context bloat fix |
