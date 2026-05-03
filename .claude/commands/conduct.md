# /conduct — Lane-Based Orchestrator

Classifies tasks by type, routes to lanes, dispatches to workers, reviews with Claude. Loops until done.

## CRITICAL: Dispatch Is Mandatory

This operator REQUIRES external worker dispatch. Claude is the planner and reviewer ONLY.
Implementation tasks MUST go to opencode_go workers via `./bin/oneshot dispatch` or `./bin/oneshot dispatch-many`.
**There is no "do it inline" fallback. If dispatch fails, log a blocker and escalate.**

## Usage

```
/conduct
/conduct <idea or goal>
```

## Behavior

### Phase 0: Intake (BLOCKING — nothing else runs until complete)

1. **Detect providers and verify routing works**
   ```bash
   ./bin/oneshot lanes
   ```
   The router MUST return a valid lane with workers. If it fails, stop and tell the user.
   `.oneshot/config/models.yaml` MUST exist. If it doesn't, stop and tell the user.

2. **Ask 5 required questions** using AskUserQuestion — do NOT proceed until answered:
   1. What is the goal / deliverable?
   2. What does done look like? (acceptance criteria — be specific)
   3. What is in scope? What is explicitly out of scope?
   4. Any constraints? (tech stack, time, things to avoid)
   5. What is the riskiest / most uncertain part?

3. **Initialize `1shot/`** in the project root (create if missing):
   - Create dated subdirectory: `1shot/{YYYY-MM-DD}-{session-slug}/`
   - Write intake answers to `1shot/{session-dir}/PROJECT.md`
   - Update `1shot/{session-dir}/STATE.md`: phase = "intake → plan"
   - Create `1shot/{session-dir}/skills/` directory
   - NEVER clobber an existing session directory — each /conduct run gets its own folder

4. **Show PROJECT.md** to user and confirm before proceeding.

### Phase 1: Plan

1. **Explore codebase** (Explore subagent) — identify impacted files
2. **Persist exploration artifact** — Write structured output to `1shot/explore.json`:
   ```json
   {
     "goal": "[from PROJECT.md]",
     "candidate_files": ["list of relevant files"],
     "commands_to_run": ["test commands", "lint commands"],
     "constraints": ["architectural constraints discovered"],
     "unknowns": ["open questions to resolve"],
     "risk_assessment": {"level": "low|medium|high", "reasoning": "..."},
     "existing_patterns": ["patterns found in relevant files"]
   }
   ```
3. **Docs Check** — `cat ~/github/docs-cache/docs/cache/.index.md` → cache missing docs via `/doc`
4. **Write `1shot/ROADMAP.md`** — phases and success criteria
5. **Task specs for non-trivial work**: Generate TASK_SPEC.md from `templates/TASK_SPEC.md`
6. **Generate machine-readable plan** — Create `1shot/plan.json` from `core/plan_schema.py`
7. **Create native tasks** — one TaskCreate per deliverable
8. **Classify each task**: `python -m core.router.resolve --class <task_class> --category <category>`
9. **Update STATE.md**: phase = "plan → build"

### Phase 2: Build Loop (ALL implementation via dispatch)

Repeat until no unblocked tasks remain:

1. Pick next unblocked task (`TaskList` → lowest ID pending)
2. `TaskUpdate` → in_progress
3. **Select methodology** (automatic — based on task description):
   - **Bug fix** → `/debug` protocol (investigate → analyze → hypothesize → fix)
   - **New feature** → `/tdd` protocol (RED-GREEN-REFACTOR)
   - **Doc edit, config change, refactor**: no special methodology needed
4. **Classify and dispatch** (MANDATORY — no exceptions):
   - Determine task class (see task-classes.md)
   - Resolve lane: `python -m core.router.resolve --class <class> --category <category>`
   - **If lane is NOT premium**: Build self-contained prompt → dispatch to worker:
      ```bash
      ./bin/oneshot dispatch \
        --lane <lane> \
        --task-file /tmp/task-spec.md \
        --allow-dirty
      ```
   - **If lane IS premium**: Claude handles inline (planning, review, integration only)
   - **For parallel tasks**:
      ```bash
      ./bin/oneshot dispatch-many --lane <lane> \
        --task-file /tmp/task-a.md \
        --task-file /tmp/task-b.md \
        --task-file /tmp/task-c.md
      ```
   - **CRITICAL: Use subprocess dispatch, NOT Agent tool subagents.**
     `core.dispatch.run` spawns lightweight CLI processes.
     Agent tool spawns full Claude Code sessions — never use Agent for dispatch.
   - If NO workers are available: **log blocker, stop, tell user**
5. **Review**: If task requires review, dispatch review to reviewer
6. **Scope check** — `git diff --name-only` against TASK_SPEC "Files Involved"
7. **Verify**: Run Phase 3 verification checklist
8. `TaskUpdate` → completed (only after verification passes)
9. Update `1shot/STATE.md`
10. **Circuit breaker**: if same task failed 3x → log blocker → skip → continue

If 3 consecutive tasks hit circuit breaker → stop, surface to user.

### Phase 3: Verify (MANDATORY — evidence required)

**No verification, no completion. Assertions don't count — show the output.**

1. **Run targeted tests** — if test files exist for the changed files, run them.
2. **Run lint/static analysis** — shellcheck, prettier, ruff, or whatever the project uses.
3. **Run type check** — tsc, pyright, or equivalent.
4. **Check acceptance criteria** — go through each criterion, cite evidence.
5. **Review diff** — `git diff` and confirm changed files match plan scope.

If any check fails:
- `TaskUpdate` back to **pending** — never mark as completed with failing checks
- Loop back to Phase 2
- Document persistent failures in `1shot/BLOCKERS.md`

### Phase 4: Challenge (two-stage review)

#### Stage A: Spec Compliance
Re-read `1shot/PROJECT.md`. For each acceptance criterion: cite evidence. Check scope violations.
**Stage A fail** → do not run Stage B. Create tasks to address gaps.

#### Stage B: Code Quality
```bash
# Dispatch a single task
./bin/oneshot dispatch --lane routine_coder --task-file /tmp/task.md

# Dispatch multiple tasks in parallel
./bin/oneshot dispatch-many --lane routine_coder \
  --task-file /tmp/task-a.md \
  --task-file /tmp/task-b.md
```

### Phase 5: Session-End Learning

If any correction was given 2+ times during this session:
- Write proposal to `docs/instructions/learned/{date}-{topic}.md`

### Done

```
Conduct Complete
├─ Tasks: X/Y completed
├─ Lanes used: [list]
├─ Workers used: [list with counts]
├─ Files changed: Z
├─ Commits: N
└─ Blockers: M (see 1shot/ISSUES.md)
```

---

## Routing Reference

See `docs/instructions/task-classes.md` for full classification guide.
See `.claude/commands/dispatch.md` for the /dispatch skill and `./bin/oneshot --help` for CLI reference.
See `~/.claude/skills/_shared/providers.md` for provider detection and commands.

**Key rule**: Route by task class, not provider name. Use lane policy from config.
