---
name: update
description: Pull latest oneshot from GitHub and sync skills/agents to all downstream projects.
---

# /update — Sync OneShot to All Projects

Pull the latest oneshot and propagate skills, agents, and AGENTS.md to every downstream project.

## Usage

```
/update           # pull + sync all projects
/update --dry-run # preview what would change without touching anything
/update --self    # pull oneshot only, skip project sync
```

## Steps

1. **Pull latest oneshot**
   ```bash
   cd ~/github/oneshot && git pull --rebase
   ```
   If this fails (local changes), stash first:
   ```bash
   git stash && git pull --rebase && git stash pop
   ```

2. **Sync to all projects** (skip if `--self`)
   ```bash
   bash ~/github/oneshot/scripts/sync-all-projects.sh
   ```
   With `--dry-run`:
   ```bash
   bash ~/github/oneshot/scripts/sync-all-projects.sh --dry-run
   ```

3. **Fix any push failures**
   For each failed project, the likely cause is remote ahead of local. Fix with:
   ```bash
   cd ~/github/<project>
   git stash
   git pull --rebase
   git push
   git stash pop
   ```
   Do this for every project listed in `FAILED:` — don't leave them behind.

4. **Report results**
   ```
   OneShot update complete
   ├─ oneshot: <old-sha> → <new-sha>  (or "already up to date")
   ├─ synced: N projects
   ├─ skipped: N (no .claude/ dir or oneshot itself)
   ├─ failed: N
   └─ fixed: [list of projects that needed manual push]
   ```

## What Gets Synced

| What | Where | Notes |
|------|-------|-------|
| Skills | `.claude/skills/` | `--delete` removes obsolete skills |
| Agents | `.claude/agents/` | Only if project already has the dir |
| AGENTS.md | `AGENTS.md` | Only if file exists in the project |

Project-local files (`CLAUDE.md`, `CLAUDE.local.md`, `config/`, `1shot/`) are never touched.

## Notes

- The auto-updater pulls oneshot once per day on session start — `/update` is for forcing it now
- `sync-all-projects.sh` auto-discovers every repo under `~/github/` with a `.claude/` dir
- Each synced project gets a `chore: sync oneshot framework` commit and is pushed
- Run from any directory — scripts use absolute paths
