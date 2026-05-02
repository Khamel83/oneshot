# Project Status  
Oneshoot is a medium‑size Python package with heavy churn on core dispatch logic; several files exceed 800 lines and documentation is noticeably stale.

# Recent Activity  
- `core/dispatch/run.py` was edited in the last 2 sessions (36 total sessions).  
- `.oneshot/config/models.yaml` saw 36 sessions of access.  
- `oneshot_cli/tasks.py` recorded 17 sessions.  
- Memory notes (`/home/ubuntu/.claude/projects/-home-ubuntu-github-oneshot/memory/manus-credits.md`) were revisited twice.

# Attention Items  
1. **Test Gap** – No tests cover `core/dispatch/run.py` (910 LOC).  
2. **Knowledge Risk** – Solo‑author files: `.claude/skills/_shared/providers.md` (12 edits by Test User), `.claude/skills/conduct/SKILL.md` (11 edits), `.claude/skills/full/SKILL.md` (10 edits).  
3. **Oversized Files** – `core/janitor/jobs.py` (1 834 LOC), `core/dispatch/run.py` (910 LOC), `oneshot_cli/doctor_cmd.py` (791 LOC).  
4. **Config Drift** – Multiple config files (`models.yaml`, `workers.yaml`, `lanes.yaml`, `providers.yaml`) are accessed frequently but have no version‑control diff summary; potential drift.

# Recommended Next Steps  
1. Add unit tests for `core/dispatch/run.py` focusing on its main entry points (e.g., `run_dispatch`, `handle_task`).  
2. Refactor `core/janitor/jobs.py` to extract logical modules (< 500 LOC each) and introduce tests for each new module.  
3. Pair‑program on one of the solo‑author skill docs (e.g., `.claude/skills/_shared/providers.md`) to broaden ownership and add inline documentation.  
4. Audit the four config files for consistency: run a diff against the latest committed versions, update any out‑of‑sync keys, and commit the reconciled versions.  
5. Schedule a documentation sprint to update stale docs (`docs/public-access.md`, `archive/v7-high-token/README.md`, `archive/SKILL_LOG.md`).  