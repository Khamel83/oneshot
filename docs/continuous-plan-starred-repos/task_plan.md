# ONE_SHOT v11 - Starred Repos Integration Plan

## Goal
Incorporate validated recommendations from starred repos analysis into ONE_SHOT.

## Scope
All recommendations from research/starred-repos-analysis/COMPREHENSIVE_REVIEW.md

## Validation Phase (Before Execution)

### 1. claude-sneakpeek Validation
- [ ] Install claude-sneakpeek: `npx @realmikekelly/claude-sneakpeek quick --name claudesp`
- [ ] Test swarm mode and TeammateTool
- [ ] Document how it differs from ONE_SHOT v10 approach
- [ ] Validate if native features make custom orchestration obsolete

### 2. openclaw Validation (penny project)
- [ ] Check how openclaw is used in penny project
- [ ] Identify patterns that could apply to ONE_SHOT
- [ ] Compare openclaw's personal AI assistant approach to ONE_SHOT

### 3. cc-mirror Task Tools Evaluation
- [ ] Compare CC-MIRROR's task tools (TaskCreate/Get/Update/List) to beads
- [ ] Test which approach feels more natural
- [ ] Document pros/cons of each

### 4. Gemini CLI CTO Validation
- [ ] Create detailed continuous plan document
- [ ] Prompt Gemini as CTO: "You're a CTO being asked to approve this plan. How does it sound? What would you change or keep? Save detailed report to MD."
- [ ] Incorporate CTO feedback into final plan

## Execution Phase (After Validation)

### Phase 1: Critical (claude-sneakpeek findings)
- [ ] Document ONE_SHOT v11 stance on native Claude features
- [ ] Update docs to reflect "wait for native" approach
- [ ] Remove any custom orchestration that duplicates native features

### Phase 2: High Priority (task tools)
- [ ] Decide: native task tools vs beads vs hybrid
- [ ] Implement chosen approach
- [ ] Update /beads command if needed

### Phase 3: Medium Priority (progressive disclosure)
- [ ] Design rule loading by project type
- [ ] Implement contextual rule loading
- [ ] Test token savings

### Phase 4: Documentation
- [ ] Update README with findings
- [ ] Document decision rationale
- [ ] Create migration guide from v10 to v11

## Success Criteria
- Validated claude-sneakpeek's swarm mode
- Compared task tools approaches
- Got CTO approval from Gemini CLI
- Clear execution path for v11
- All tracked in beads
