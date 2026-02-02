# ONE_SHOT v9 Design: The "Play Calling" System

**Created:** 2026-02-02
**Status:** Design Draft
**Branch:** v9-refactor

---

## The Vision: Offensive Coordinator Model

> "Coding is going to stop being writing code and start being executing plays. I'm the offensive coordinator, not the quarterback. Claude Code is the quarterback, models are the players. I call a play, the play runs, I see the outcome, I call the next play."

**User** = Offensive Coordinator (calls plays)
**Front-door** = Play caller (identifies which skills to run)
**Create-plan/Continuous-planner** = Playbook designer (links skills together)
**Implement-plan** = Execution engine (runs the plays)
**Skills** = Players (execute specific actions)
**Beads** = Scorekeeper (tracks progress)

---

## Current State (v8.3)

```
User says: "Build a REST API with auth"
  ↓
/front-door interviews (Q1, Q2, Q6, Q12...)
  ↓
User answers questions
  ↓
/create-plan creates plan.md
  ↓
User reviews and approves
  ↓
/implement-plan executes steps
  ↓
/beads tracks progress
```

**Problems:**
1. Skills are implicit in plans (not explicitly listed)
2. No skill inventory check before planning
3. Skills are executed manually, not automatically
4. No deterministic skill→skill handoff
5. Plans don't survive /clear well

---

## v9 Design: Make "Play Calling" First-Class

### Core Insight: Plans ARE Skill Sequences

A plan should be:
```yaml
goal: "Build a REST API with auth"
skills_required:
  - front-door (for triage)
  - api-designer (for endpoint design)
  - convex-resources (for backend)
  - create-plan (for planning)
  - implement-plan (for execution)
steps:
  - skill: front-door
    action: interview_requirements
  - skill: api-designer
    action: design_endpoints
    input_from: front-door.requirements
  - skill: create-plan
    action: create_implementation_plan
    input_from: api-designer.endpoints
  - skill: implement-plan
    action: execute_deterministically
    input_from: create-plan.plan
```

### Key Change: Skills Become First-Class Citizens

**Old way (v8):**
- Plans list file changes and bash commands
- Skills are invoked implicitly
- No skill inventory or dependency checking

**New way (v9):**
- Plans list SKILLS to invoke
- Each skill has INPUT and OUTPUT contracts
- Skills can call other skills (deterministic chaining)
- Skill inventory is checked before planning

---

## v9 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OFFENSIVE COORDINATOR                     │
│                         (User)                              │
└────────────────────────┬────────────────────────────────────┘
                         │ "Build X"
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FRONT-DOOR                              │
│  • Interview requirements                                    │
│  • Check skill inventory (what's available?)                 │
│  • Triage: can we do this with available skills?            │
└────────────────────────┬────────────────────────────────────┘
                         │ requirements + skill_inventory
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   CONTINUOUS PLANNER                         │
│  • Create 3-file plan (task_plan.md, findings.md, progress.md)│
│  • List REQUIRED skills (check inventory)                   │
│  • Define skill INPUT/OUTPUT contracts                      │
│  • Plan for skill handoffs                                  │
└────────────────────────┬────────────────────────────────────┘
                         │ plan with skill sequence
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       USER APPROVAL                          │
│  • Review the play sequence                                 │
│  • Verify skills are available                              │
│  • Approve or modify                                        │
└────────────────────────┬────────────────────────────────────┘
                         │ approved plan
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    IMPLEMENT-PLAN                            │
│  • Execute skills DETERMINISTICALLY                          │
│  • Pass outputs between skills                              │
│  • Track progress with beads                                │
│  • Handle failures with recovery protocols                  │
└────────────────────────┬────────────────────────────────────┘
                         │ completed
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                         BEADS                                │
│  • Mark plan complete                                        │
│  • Update skill usage stats                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Skill Contracts (New Concept)

Each skill defines:

```markdown
---
name: api-designer
description: Design RESTful or GraphQL APIs with proper conventions
version: "1.0"

# INPUT CONTRACT
expects:
  - requirements: "User requirements from front-door"
  - tech_stack: "Preferred technologies (from CLAUDE.md)"

# OUTPUT CONTRACT
produces:
  - api_spec: "OpenAPI/Swagger spec"
  - endpoints: "List of endpoints with methods"
  - data_models: "Data structures"

# DEPENDENCIES
requires_skills:
  - front-door "for requirements gathering"

# COMPATIBILITY
works_with:
  - convex-resources "for backend"
  - docker-composer "for deployment"
---
```

**This enables:**
1. **Skill inventory checking** before planning
2. **Deterministic skill chaining** (output → input)
3. **Skill discovery** from SkillsMP based on contracts
4. **Automatic skill selection** based on what's needed

---

## Skill Inventory (New Component)

```bash
# List all available skills
/skills list

# Show skill details
/skills show api-designer

# Find skills by contract
/skills find --produces "api_spec"
/skills find --expects "requirements"

# Install from SkillsMP
/skills install skillsmp/anthropics/frontend-design

# Sync with SkillsMP
/skills sync --marketplace
```

**The inventory tracks:**
- Local skills (~20 unique ONE_SHOT skills)
- SkillsMP skills (installed favorites)
- Skill contracts (input/output)
- Skill dependencies
- Skill usage statistics

---

## Continuous Plan Format (Enhanced)

### task_plan.md (v9 format)

```markdown
# Task Plan: REST API with Auth

## Goal
Build a RESTful API with authentication

## Skill Sequence (The Playbook)

1. **front-door** → requirements
   - Input: User request
   - Output: requirements.yaml
   - Status: ✅ Complete

2. **api-designer** → api_spec
   - Input: requirements.yaml
   - Output: openapi.yaml, endpoints.md
   - Status: ⏳ In Progress

3. **convex-resources** → backend_setup
   - Input: openapi.yaml
   - Output: convex/
   - Status: ⏸️ Waiting

4. **create-plan** → implementation_steps
   - Input: api_spec + backend_setup
   - Output: task_plan.md (this file)
   - Status: ⏸️ Waiting

## Skill Inventory Check
| Skill | Available? | Version | Source |
|-------|------------|---------|--------|
| front-door | ✅ | 1.0 | local |
| api-designer | ✅ | 1.0 | local |
| convex-resources | ✅ | 1.0 | local |
| create-plan | ✅ | 1.0 | local |
| implement-plan | ✅ | 1.0 | local |
```

---

## Deterministic Execution (The "Run Play" Command)

```bash
# Execute plan deterministically
/run-plan task_plan.md

# What happens:
1. Load plan and skill sequence
2. For each skill:
   a. Check skill is available
   b. Load skill's input from previous skill's output
   c. Execute skill
   d. Save output to findings.md
   e. Update progress.md
   f. Mark bead complete
3. If any skill fails: invoke failure-recovery
4. On completion: mark plan bead complete
```

**This is the "execute play" button.**

---

## SkillsMP Integration ( Seamless Discovery)

```bash
# Search SkillsMP for skills that produce "api_spec"
/skillsmp find --produces "api_spec"

# Install a skill from SkillsMP
/skillsmp install anthropics/frontend-design

# The skill becomes part of local inventory
/skills list

# Use in plans just like local skills
```

**Key: SkillsMP skills have contracts too, so they integrate seamlessly.**

---

## v9 Components Summary

| Component | Purpose | Unique? | Status |
|-----------|---------|---------|--------|
| **Skill Contracts** | Define input/output | ✅ NEW | Design |
| **Skill Inventory** | Track available skills | ✅ NEW | Design |
| **Front-door v9** | Interview + inventory check | ✅ ENHANCED | Design |
| **Continuous Planner v9** | Plans with skill sequences | ✅ ENHANCED | Design |
| **Implement-plan v9** | Deterministic execution | ✅ ENHANCED | Design |
| **Beads v9** | Track skill execution | ✅ ENHANCED | Existing |
| **SkillsMP Integration** | Discover/install external skills | ✅ NEW | Design |

---

## What v9 Achieves

### For the User (Offensive Coordinator)
- ✅ See exactly which skills will run
- ✅ Verify skills are available before approving
- ✅ Execute plans deterministically with one command
- ✅ Discover new skills from SkillsMP based on contracts

### For the System (Quarterback)
- ✅ Clear input/output contracts between skills
- ✅ Deterministic skill chaining
- ✅ Better error handling (knows what each skill produces)
- ✅ Can substitute SkillsMP skills seamlessly

### For Less Sophisticated Models
- ✅ Well-defined skills with clear contracts
- ✅ Execution is deterministic (follow the plan)
- ✅ Can execute any skill regardless of model capability

---

## Migration Path: v8.3 → v9

### Phase 1: Add Contracts (Non-breaking)
- Add contract sections to existing skills
- Create skill inventory system
- Keep existing behavior

### Phase 2: Enhance Planning
- Update continuous-planner to include skill sequences
- Add skill inventory checking
- Maintain backward compatibility

### Phase 3: Deterministic Execution
- Implement /run-plan command
- Add skill chaining (output → input)
- Failure recovery integration

### Phase 4: SkillsMP Integration
- Add contract-based search
- One-click install from SkillsMP
- Seamless local + external skill mixing

---

## Next Steps

1. ✅ Design skill contract format
2. ✅ Create skill inventory system
3. ✅ Implement contract-based skill search
4. ✅ Enhance continuous-planner with skill sequences
5. ✅ Implement deterministic /run-plan
6. ✅ Add SkillsMP integration

---

## The v9 Question Answered

> **"Can v9 allow me to get back to the original vision?"**

**YES.**

v9 makes the "play calling" explicit:
1. **Front-door** identifies the play (which skills to run)
2. **Continuous-planner** designs the playbook (skill sequence with contracts)
3. **User approves** the play sequence
4. **Implement-plan** executes deterministically (skill by skill)
5. **Beads** tracks the score

**SkillsMP provides additional players. ONE_SHOT v9 provides the playbook.**

---

**Status:** Ready for feedback and iteration
