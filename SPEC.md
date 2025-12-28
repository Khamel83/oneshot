# front-door Skill Specification (ONE_SHOT v6.0)

## Overview

**Name:** `front-door`
**Version:** 6.0
**Replaces:** `oneshot-core` (immediate deprecation)
**Purpose:** Intelligent entry point that interviews users, classifies projects, and routes to appropriate downstream skills

## Core Concept

front-door is the new **orchestration hub** for the ONE_SHOT system. It:
1. Auto-detects when ambiguity requires deeper discovery
2. Conducts thorough, iterative interviews using AskUserQuestion
3. Writes incremental spec files with confidence scores
4. Routes to appropriate skills based on classification

## Activation & Triggers

### Auto-Detection Signals (any triggers interview mode)
- **Vague scope**: User says "build me X" without specifics
- **Multi-domain request**: Spans UI + backend + infra
- **Missing context**: References things not found in codebase
- **High-stakes change**: Refactors, migrations, >5 files

### Smart Bypass for Trivial Tasks
- Single triage question: "This seems straightforward - proceed directly or discuss first?"
- Keyword hints: "typo", "rename", "single file" suggest bypass
- User can always force interview with `/front-door` or `/interview`

## Interview Mechanics

### Core Tool: AskUserQuestion
front-door is built on **AskUserQuestion** - Claude Code's native multi-choice question tool.

**Usage pattern:**
```
AskUserQuestion({
  questions: [
    {
      question: "What problem are you solving?",
      header: "Problem",
      options: [
        { label: "Option A", description: "Details..." },
        { label: "Option B", description: "Details..." }
      ],
      multiSelect: false
    }
  ]
})
```

**Best practices:**
- 1-2 questions per call (quick iterations)
- Use `multiSelect: true` when choices aren't mutually exclusive
- Header should be ≤12 chars (displays as chip)
- 2-4 options per question (users can always pick "Other")

### Question Strategy
- **1-2 questions per round** (quick focused iterations)
- **Visible progress tracker** after each round:
  ```
  ✓ Requirements ✓ UX ○ Edge Cases ○ Testing
  ```
- **Flag contradictions immediately**: "Earlier you said X, but now Y - which is correct?"

### Topic Exhaustion Detection
Full coverage required before suggesting completion:
- Requirements & success criteria
- UX & user flows
- Edge cases & error handling
- Testing strategy
- Technical constraints

### When User Gets Impatient
**One gentle push with stakes:**
> "Skipping discovery risks rework on [specific gaps]. Continue anyway?"

If user insists, proceed with assumptions documented.

## Project Type Templates

### Auto-Detection
Scan for package.json, go.mod, Dockerfile, etc. to infer type before asking.

### CLI Tool Categories
- Requirements, Success Criteria
- Shell integration (completion, aliases, piping)
- Configuration (config files, env vars, precedence)
- Testing strategy

### Web App Categories
- Requirements, Success Criteria
- State management, Auth/permissions
- Responsive/mobile design
- Error handling (loading states, boundaries)

### API/Backend Categories
- Requirements, Success Criteria
- Data modeling & migrations
- Auth & rate limits, Versioning
- Observability (logs, metrics, health)

### Library/SDK Categories
- Requirements, Success Criteria
- Public API surface
- Documentation strategy

## Output Artifacts

### Spec File
- **Location:** `~/.claude/plans/spec-YYYY-MM-DD-{slug}.md`
- **Format:** YAML frontmatter + markdown body
- **Written incrementally** (enables resume)
- **Confidence scores per section:** [HIGH/MED/LOW]

### Spec File Structure
```yaml
---
project: feature-name
type: web-app | cli | api | library
created: 2025-01-15
status: in-progress | complete
covered: [requirements, ux]
remaining: [edge-cases, testing]
---

# Feature Name Specification

## Requirements [HIGH]
- ...

## UX & User Flows [MED]
- ...

## Edge Cases [TBD]
- Not yet explored

## Testing Strategy [TBD]
- Not yet explored
```

## Visual Iteration Loop (Web Apps)

When building web UIs, front-door can enable a **self-scoring visual feedback loop**:

### Requires
- Playwright MCP server configured
- Web app with dev server running

### Workflow
```
1. Implement UI change
2. Take full-page screenshot via Playwright
3. Self-assess: "Rate this design 1-10 for [criteria from spec]"
4. If < 10/10: identify specific issues, iterate
5. Repeat until 10/10 or user-defined threshold
```

### Assessment Criteria (from interview)
- Visual hierarchy & whitespace
- Consistency with design system
- Accessibility (contrast, text size)
- Responsive behavior
- User flow clarity

### Usage
Claude can invoke this loop during build phase when spec indicates:
- `visual_polish: true`
- Project type is web app (C or F)
- User requests "make it look good" or "polish the UI"

### Example
```
> Screenshot taken: /tmp/page-screenshot.png
> Self-assessment: 6/10
> Issues:
>   - Header too cramped (spacing)
>   - CTA button doesn't stand out (contrast)
>   - Mobile nav not visible
> Iterating...
```

## Routing Logic (Post-Interview)

Based on interview results:
| Classification | Route To |
|----------------|----------|
| New project (greenfield) | `create-plan` → implementation |
| Existing + complex | `create-plan` → implementation |
| Existing + simple | Direct implementation |

**Intelligent complexity detection:**
- Multi-file changes → create-plan
- Single-file, clear requirements → direct implement

## Integration with Plan Mode

front-door becomes **Phase 0** of plan mode:
1. **Phase 0 (NEW):** Interview & spec writing
2. Phase 1: Exploration (existing)
3. Phase 2: Design (existing)
4. Phase 3: Review (existing)
5. Phase 4: Final plan (existing)
6. Phase 5: Exit (existing)

## Resume Capability

If interview is interrupted (/clear, context exhaustion):
- Spec file tracks `covered` vs `remaining` categories
- On resume, Claude reads spec file and picks up where left off
- User sees: "Resuming from partial spec. Already covered: X, Y. Now exploring: Z"

## Anti-Patterns to Guard Against

1. **Under-interviewing**: Missing critical requirements → rework
   - Mitigation: Full product coverage required

2. **Analysis paralysis**: Never moving to implementation
   - Mitigation: Topic exhaustion detection, visible progress

## Skill File Structure

```yaml
---
name: front-door
description: "Intelligent entry point for all tasks. Interviews, triages, and routes. Use when starting any non-trivial work."
allowed-tools: Read, Glob, Grep, AskUserQuestion, Write, Task
---
```

## Absorbed from oneshot-core

### Prime Directive (KEEP)
> USER TIME IS PRECIOUS. AGENT COMPUTE IS CHEAP.
> Ask ALL questions UPFRONT. Get ALL info BEFORE coding.

### Triage Table (ENHANCED)
front-door extends the original triage with interview-first approach:

| Intent | Signals | Action |
|--------|---------|--------|
| **build_new** | "new project", "build me" | Interview → PRD → Build |
| **fix_existing** | "broken", "bug" | Quick triage → debugger skill |
| **continue_work** | "continue", "resume" | resume-handoff skill |
| **modify_existing** | "add feature", "change" | Interview → create-plan |
| **understand** | "explain", "how does" | Research only (bypass) |
| **quick_task** | "just", "quickly" | Quick triage question → bypass |

### Mode Selection (KEEP)
| Mode | Trigger | Interview Depth |
|------|---------|-----------------|
| Micro | <100 lines | Q1, Q11 only |
| Tiny | Single CLI | Skip web/AI categories |
| Normal | CLI/web/API | Full project-type template |
| Heavy | Multi-service, AI | Full + AI questions |

### Core Questions Structure (INTEGRATE)
front-door's interview templates should produce answers for:
- Q0: Mode
- Q1: What building
- Q2: Problem solved
- Q4: Features (3-7)
- Q6: Project type (A-G)
- Q12: Done criteria

Smart defaults handle the rest.

### Project Invariants (KEEP)
Every project from front-door MUST include:
- README.md, TODO.md, LLM-OVERVIEW.md
- PRD.md (generated from spec)
- scripts/ (setup, start, stop, status)
- /health endpoint for services

### Hard Stops (KEEP)
front-door must flag these for explicit approval:
- Storage tier upgrade
- Auth method changes
- Production deployment
- External API integration
- Data deletion
- Schema migrations

### Storage & Deployment Progressions (KEEP)
Preserve entire storage decision matrix and deployment progression from oneshot-core.

### Yolo Mode (KEEP as "Quick Mode")
Trigger: "yolo", "fast mode", "just do it"
- Ask only essential questions
- Propose smart defaults
- Show summary before proceeding

### Micro Mode (KEEP)
For <100 line scripts - minimal interview, single file output.

## Keywords
front-door, interview, triage, spec, discovery, requirements, build me, new project, help me, oneshot, yolo, micro

---

# Implementation Plan

## Files to Create/Modify

### New Files
1. `~/.claude/skills/oneshot/front-door/SKILL.md` - Main skill file

### Files to Delete
2. `~/.claude/skills/oneshot/oneshot-core/` - Entire directory (replaced)

### Files to Update
3. `AGENTS.md` - Update skill router to reference front-door
4. `~/.claude/skills/oneshot/INDEX.md` - Add front-door, remove oneshot-core
5. `oneshot.sh` - Update SKILLS array if applicable

## Implementation Steps

### Step 1: Create front-door Skill
Write `~/.claude/skills/oneshot/front-door/SKILL.md` with:
- Frontmatter (name, description, allowed-tools)
- Expert claim
- When To Use section with triggers
- Interview workflow (Phase 0)
- Project type templates
- Routing logic
- Anti-patterns
- Keywords

### Step 2: Delete oneshot-core
Remove `~/.claude/skills/oneshot/oneshot-core/` directory entirely.

### Step 3: Update AGENTS.md
- Update skill router table
- Update available skills list
- Update version to v6.0

### Step 4: Update INDEX.md
- Add front-door entry
- Remove oneshot-core entry
- Update skill count

### Step 5: Test
- Test trivial task bypass
- Test full interview flow
- Test resume from partial spec
- Test routing to downstream skills
