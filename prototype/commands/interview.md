# /interview — Intelligent Task Triage & Interview

Triage the user's request, then interview them to build a spec before coding.

## Process

### 1. Triage (30 seconds)

Classify intent:
| Intent | Signals | Action |
|--------|---------|--------|
| build_new | "new project", "build me" | Full interview → spec → /cp |
| fix_existing | "broken", "bug", "error" | Quick triage → /diagnose |
| continue_work | "continue", "resume" | → /restore |
| modify_existing | "add feature", "change" | Interview → /cp |
| understand | "explain", "how does" | Research only |
| quick_task | "just", "quickly" | One triage question → direct |

Output: `Intent: [type] | Scope: [micro/small/medium/large] | Flow: [Full/Mini/Direct]`

### 2. Bypass Check

Ask: "This seems straightforward — proceed directly or discuss first?"

Bypass ONLY if ALL apply: single file, <10 lines, explicit path given.
If user says `/interview` explicitly, never bypass.

### 3. Auto-Delegation During Interview

For modify_existing, fix_existing, or understand intents, spawn an Explore agent BEFORE interviewing:

```
Task:
  subagent_type: Explore
  description: "Map codebase for {intent}"
  prompt: |
    User wants to: {user_request}
    Find: relevant files (max 10), existing patterns, dependencies, test files.
    Return 500-token summary with file:line references. No file contents.
```

Start the interview while the agent explores. Inject findings when it returns.

### 4. Interview (iterative, using AskUserQuestion)

- 1-2 questions per round with options
- Show progress tracker: `✓ Requirements  ✓ UX  ○ Edge Cases  ○ Testing`
- Flag contradictions immediately
- Write spec incrementally to `~/.claude/plans/spec-{date}-{slug}.md`

**Depth control:**
| Mode | Questions | When |
|------|-----------|------|
| full | All 13+ | Greenfield, no existing code |
| smart | Auto-detect 5-13 | Default — full for greenfield, shorter for mods |
| quick | Q1, Q2, Q6, Q12 only | Micro tasks, <100 lines |

**Required questions:**
- Q1: What are you building?
- Q2: What problem does this solve?
- Q6: Project type (CLI / Web / API / Library / Service / Pipeline / Static)
- Q12: Done criteria / v1 scope

**Smart defaults by type:**
| Type | Stack | Storage |
|------|-------|---------|
| CLI | Python + Click | SQLite |
| Web App | Next.js + Convex + Clerk | Convex |
| Service/API | Python + systemd | SQLite |
| Library | Python + pytest | N/A |

### 5. Spec Output

Write to `~/.claude/plans/spec-YYYY-MM-DD-{slug}.md` with YAML frontmatter:
```yaml
---
project: feature-name
type: cli | web-app | api | library
created: YYYY-MM-DD
status: in-progress | complete
covered: [requirements, ux]
remaining: [edge-cases, testing]
---
```

### 6. Post-Interview Routing

| Classification | Route To |
|----------------|----------|
| New project (greenfield) | Suggest `/cp` for planning |
| Existing + complex | Suggest `/cp` for planning |
| Existing + simple | Direct implementation |

### 7. When User Gets Impatient

One gentle push: "Skipping discovery risks rework on [specific gaps]. Continue anyway?"
If they insist, proceed with assumptions documented.

## Resume Capability

If interrupted, spec file tracks `covered` vs `remaining`. On resume, pick up where you left off.
