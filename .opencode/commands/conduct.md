---
description: Multi-model orchestration with lane-based routing
agent: build
---

# /conduct — Lane-Based Orchestrator

Classifies tasks by type, routes to lanes, dispatches to workers, reviews. Loops until done.

## Usage

`/conduct` or `/conduct <idea or goal>`

## Behavior

### Phase 0: Intake (BLOCKING)

1. **Detect providers**:
   ```bash
   command -v codex >/dev/null 2>&1 && echo "codex: yes" || echo "codex: no"
   command -v gemini >/dev/null 2>&1 && echo "gemini: yes" || echo "gemini: no"
   python3 -c "from core.search.argus_client import is_available; print('argus:', is_available())" 2>/dev/null || echo "argus: no"
   ```

2. **Ask 5 questions** using `question` tool (do NOT proceed until answered):
   1. What is the goal / deliverable?
   2. What does done look like? (acceptance criteria)
   3. What is in scope? What is out of scope?
   4. Any constraints? (tech stack, things to avoid)
   5. What is the riskiest / most uncertain part?

3. **Initialize `1shot/`**:
   - Write intake to `1shot/PROJECT.md`
   - Create `1shot/STATE.md`: phase = "intake → plan"
   - Load persistent tasks: `python3 scripts/tasks.py list`

### Phase 1: Plan

1. **Explore codebase** — identify impacted files
2. **Write `1shot/ROADMAP.md`** — phases and success criteria
3. **Create tasks** using `todowrite`:
   - One item per deliverable with clear acceptance criteria
4. **Classify each task**:
   ```bash
   cd ~/github/oneshot && python3 -m core.router.resolve --class <task_class>
   ```
5. **Update STATE.md**: phase = "plan → build"

### Phase 2: Build Loop

Repeat until no unblocked tasks remain:

1. Pick next unblocked task (lowest ID)
2. **Select methodology** (automatic — based on task description):
   - **Bug fix** (fix, bug, broken, error, crash, failing, wrong, unexpected, regression,
     investigate, troubleshoot, not working, incorrect) → apply `/debug` protocol: investigate →
     analyze → hypothesize → fix. Phases 1-3 are read-only.
   - **New feature / implementation** (implement, add, create, build, new endpoint,
     new function) → apply `/tdd` protocol: RED-GREEN-REFACTOR.
     No production code without a failing test shown first.
3. **Classify and dispatch**:
   ```bash
   cd ~/github/oneshot && python3 -m core.router.resolve --class <task_class>
   ~/github/oneshot/bin/dispatch --class <task_class> --prompt "task description"
   ```
   - For premium lane tasks → execute inline
   - For worker tasks → dispatch via `core.dispatch.run`
3. **Review**: If task requires review, use the `reviewer` subagent
4. **Verify** (MANDATORY — non-negotiable):
   - Run tests: `./scripts/ci.sh` or appropriate test command
   - Check acceptance criteria from PROJECT.md
   - If fails → loop back, never mark completed with failing checks
5. **Scope check**: `git diff --name-only` — flag out-of-scope changes
6. **Update STATE.md**: increment loop count
7. **Circuit breaker**: if same task fails 3x → log to `1shot/BLOCKERS.md` → skip

If 3 consecutive tasks hit circuit breaker → stop and surface to user.

### Phase 3: Verify (MANDATORY — evidence required)

**Assertions don't count — show the output.** No exceptions. Each step requires actual command output as evidence.

For each completed task:
1. Run targeted tests — show the output. No test files? State explicitly.
2. Run lint/typecheck — show the output (or lack of errors). No linter? State what was tried.
3. Check acceptance criteria — go through each criterion from PROJECT.md one by one.
   Cite evidence (file changed, output shown) for each. No evidence = unverified.
4. Review diff against plan — confirm changed files match scope

If any check fails → loop back to Phase 2. Never mark completed with failing checks.

### Phase 4: Challenge (two-stage review)

Stage A (spec compliance) must pass before Stage B (code quality) runs.

#### Stage A: Spec Compliance

Did we build what PROJECT.md asked for?
1. Re-read PROJECT.md — every acceptance criterion and scope constraint
2. For each criterion: cite evidence (file changed, test output, behavior confirmed)
3. Check scope: any changes to out-of-scope files?
4. Fail → create tasks, loop to Phase 2. Do not run Stage B.

#### Stage B: Code Quality

1. Full diff: `git diff $(git merge-base HEAD main)..HEAD`
2. If codex available:
   ```bash
   unset OPENAI_API_KEY && codex exec --sandbox danger-full-access "Review this diff for code quality: (1) what could break in production, (2) edge cases, (3) security concerns, (4) pattern adherence. Diff: [content]"
   ```
3. New issues → create tasks → loop to Phase 2
4. Clean pass → update STATE.md: phase = "complete"

### Phase 5: Session-End Learning

If any correction was given 2+ times:
- Write proposal to `docs/instructions/learned/{date}-{topic}.md`

### Done

```
Conduct Complete
├─ Tasks: X/Y completed
├─ Files changed: Z
├─ Commits: N
└─ Blockers: M (see 1shot/BLOCKERS.md)
```

## Routing

See `docs/instructions/task-classes.md` for classification.
See `config/lanes.yaml` for lane definitions.
**Route by task class, not provider name.**

## Decision Defaults

| Ambiguity | Default |
|-----------|---------|
| Multiple implementations | Simplest |
| Naming | Follow existing pattern |
| Lane selection | Use task class routing |
| Stack | Follow AGENTS.md defaults |

## Auto-Approved

- Reading/writing files
- Running tests and linters
- Creating/updating `1shot/` files
- Git commit (not push)

## Requires Confirmation

- Destructive operations
- Git push
- External API calls that cost money
- Deploying to production
