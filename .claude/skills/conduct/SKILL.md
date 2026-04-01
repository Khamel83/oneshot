---
name: conduct
description: Multi-model orchestration with lane-based routing. Classifies tasks, routes to appropriate lanes (premium/balanced/cheap/research), and loops until the goal is met. Use when the task is non-trivial and you want it to run until done. Trigger keywords: orchestrate, PMO, keep working, until done, multi-model, conduct.
---

# /conduct — Lane-Based Orchestrator

Classifies tasks by type, routes to lanes, dispatches to workers, reviews with Claude. Loops until done.

## Usage

```
/conduct
/conduct <idea or goal>
```

## Behavior

### Phase 0: Intake (BLOCKING — nothing else runs until complete)

1. **Detect providers and config**
   ```bash
   command -v codex >/dev/null 2>&1 && echo "codex: yes" || echo "codex: no"
   command -v gemini >/dev/null 2>&1 && echo "gemini: yes" || echo "gemini: no"
   python -c "from core.search.argus_client import is_available; print('argus:', is_available())" 2>/dev/null || echo "argus: no"
   ```
   Read `config/lanes.yaml` and `config/workers.yaml` for available routing.

2. **Ask 5 required questions** using AskUserQuestion — do NOT proceed until answered:
   1. What is the goal / deliverable?
   2. What does done look like? (acceptance criteria — be specific)
   3. What is in scope? What is explicitly out of scope?
   4. Any constraints? (tech stack, time, things to avoid)
   5. What is the riskiest / most uncertain part?

3. **Initialize `1shot/`** in the project root (create if missing):
   - Write intake answers to `1shot/PROJECT.md`
   - Update `1shot/STATE.md`: phase = "intake → plan"
   - Create `1shot/skills/` directory

4. **Show PROJECT.md** to user and confirm before proceeding.

### Phase 1: Plan

1. **Explore codebase** (Explore subagent) — identify impacted files
2. **Docs Check**
   - Check cache: `cat ~/github/docs-cache/docs/cache/.index.md`
   - For anything missing → run `/doc <name> <url>` before assigning build tasks
3. **Write `1shot/ROADMAP.md`** — phases and success criteria
4. **Create native tasks** — one TaskCreate per deliverable:
   - subject: deliverable title
   - description: acceptance criteria, files to touch
   - Set addBlockedBy for dependencies
5. **Classify each task** using `docs/instructions/task-classes.md`:
   ```bash
   python -m core.router.resolve --class <task_class>
   ```
   This returns: lane, workers, reviewer, search_backend, fallback_lane
6. **Update STATE.md**: phase = "plan → build"

### Phase 2: Build Loop

Repeat until no unblocked tasks remain:

1. Pick next unblocked task (`TaskList` → lowest ID pending)
2. `TaskUpdate` → in_progress
3. **Classify and route**:
   - Determine task class (see task-classes.md)
   - Resolve lane: `python -m core.router.resolve --class <class>`
   - Route to worker pool for that lane
4. Execute fully, commit: `git add <files> && git commit -m "feat: <task>"`
5. **Review**: If task requires review (see task-classes.md), route to reviewer
6. `TaskUpdate` → completed
7. Update `1shot/STATE.md`: increment loop count, log action
8. **Circuit breaker**: if same task failed 3x → log blocker → skip → continue

If 3 consecutive tasks hit circuit breaker → stop, surface to user.

### Phase 3: Verify

For each completed task:
1. Check acceptance criteria from `1shot/PROJECT.md`
2. Run tests: `./scripts/ci.sh` if present, else appropriate test command
3. Failed tasks → `TaskUpdate` back to pending → loop to Phase 2

### Phase 4: Challenge (adversarial pass)

1. `git diff $(git merge-base HEAD main)..HEAD` — full diff since conduct started
2. If Codex available:
   ```bash
   unset OPENAI_API_KEY && codex exec --sandbox danger-full-access "Review this diff: (1) what could break, (2) what was missed, (3) edge cases. Diff: [content]"
   ```
   If Codex unavailable: Claude performs adversarial review inline.
3. New issues → create Tasks → loop to Phase 2
4. Clean pass → update STATE.md: phase = "complete"

### Phase 5: Session-End Learning

If any correction was given 2+ times during this session:
- Write proposal to `docs/instructions/learned/{date}-{topic}.md`
- Never auto-edit `CLAUDE.md` or rules

### Done

```
Conduct Complete
├─ Tasks: X/Y completed
├─ Lanes used: [list]
├─ Files changed: Z
├─ Commits: N
└─ Blockers: M (see 1shot/ISSUES.md)
```

---

## Routing Reference

See `docs/instructions/task-classes.md` for full classification guide.
See `~/.claude/skills/_shared/providers.md` for dispatch commands.

**Key rule**: Route by task class, not provider name. Use lane policy from config.

---

## Decision Defaults

| Ambiguity | Default |
|-----------|---------|
| Multiple implementations | Simplest one |
| Naming | Follow existing pattern |
| Lane selection | Use task class routing |
| Stack | Follow CLAUDE.md defaults |

---

## Auto-Approved Actions

- Reading any file
- Writing to scope-matched files
- Creating / updating `1shot/` files
- Running tests and linters
- Git commit (not push)
- Creating and updating native tasks

## Requires Confirmation

- Destructive operations (rm -rf, DROP TABLE, reset --hard)
- Git push to shared branches
- External API calls that cost money
- Deploying to production
