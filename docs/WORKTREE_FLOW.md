# Worktree Flow

## Why Worktrees

Git worktrees provide **filesystem-level isolation** between the planner (Claude Code) and workers:

- Each dispatched task gets its own directory at `../oneshot-worktrees/<task-id>/`
- Workers cannot modify the main working tree — they're on a separate branch in a separate directory
- `git status` in the main tree is unaffected by worker activity
- No merge conflicts — diffs are collected and reviewed, not auto-merged

## Path Layout

```
~/github/oneshot/                    ← main working tree (planner)
  .oneshot/tasks/<task-id>/          ← task metadata (task.md, status.json, etc.)

~/github/oneshot-worktrees/          ← worker sandbox (outside repo)
  <task-id>/                         ← full repo checkout on worker/<task-id> branch
```

`oneshot-worktrees/` lives **outside** the repo at `~/github/`, so it's invisible to `git status` in the main tree.

## Branch Naming

- Worker branches: `worker/<task-id>` (e.g., `worker/routine_coder-20260427-185805-dsl0`)
- Created from `HEAD` of the main working tree at dispatch time
- Deleted on `oneshot worktree remove <task-id>`

## Task ID Format

`<lane>-<YYYYMMDD-HHMMSS>-<rand4>`

- Sortable by date
- Lane prefix for quick visual filtering
- 4-char random suffix for collision resistance

## Lifecycle

### 1. Create (dispatch)

```
./bin/oneshot dispatch --lane routine_coder --task "fix the auth bug"
```

- Pre-flight: checks `git status --porcelain` is empty (unless `--allow-dirty`)
- Creates `../oneshot-worktrees/<id>` via `git worktree add`
- Writes `task.md`, `status.json`, `worker.md`, `worker.log`
- Resolves the selected runner template and executes it immediately in the worktree
- Branch: `worker/<id>` from current HEAD

### 2. Work (worker)

- Worker operates in the worktree directory
- Makes commits on the `worker/<id>` branch
- Main tree is unaffected

### 3. Collect

```
./bin/oneshot collect <id>
```

- Reads `HEAD` from the worktree
- Computes `git diff <base_sha>..<head_sha>`
- Writes `diff.patch`, `result.md`, `test.log`
- Updates `status.json` to `collected`

### 4. Review

```
./bin/oneshot review <id>
```

- Prints absolute paths to the review bundle
- Claude Code reads `task.md`, `result.md`, `diff.patch`, `test.log`
- Verdict: accept / reject / escalate

### 5. Cleanup

```
./bin/oneshot worktree remove <id>
```

- Removes the worktree directory
- Deletes the `worker/<id>` branch
- Task metadata in `.oneshot/tasks/` is preserved

## Dirty Tree Refusal

If the main working tree has uncommitted changes, dispatch fails with a clear error:

```
Error: main working tree is dirty; use --allow-dirty to override
```

This prevents dispatching from an inconsistent state. Use `--allow-dirty` only when you're sure the uncommitted changes are unrelated to the task.

## Execution Note

Dispatch is a live runner, not a dry-run. The worker command is executed immediately in the worktree and `worker.log` captures the execution transcript, including the exit code and stdout/stderr.

If you want to inspect or reproduce the run manually, use the task's recorded worktree path and branch from `status.json`.
