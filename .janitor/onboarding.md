# Project Status  
Oneshot is a mature Python package with heavy focus on the core dispatch system; however, several files are extremely large and a critical test gap exists, indicating technical debt that could affect stability.

# Recent Activity  
- `core/dispatch/run.py` was edited in 36 sessions (most recent focus).  
- `.oneshot/config/models.yaml` was edited in 36 sessions (critical config).  
- `oneshot_cli/tasks.py` saw 17 sessions of work.  
- Memory notes were added to `.claude/projects/-home-ubuntu-github-oneshot/memory/manus-credits.md` (twice).  

# Attention Items  
1. **Test Gap** – No tests cover `core/dispatch/run.py` (910 LOC).  
2. **Knowledge Risk** – `.claude/skills/_shared/providers.md` (12 edits by a single contributor) and the two plan docs `1shot/2026-04-27-plan-l-hardening-PROJECT.md` / `...-STATE.md` (5 edits each by Test User) have sole‑author concentration.  
3. **Oversized Files** – `core/janitor/jobs.py` (1,834 LOC), `core/dispatch/run.py` (910 LOC), `oneshot_cli/doctor_cmd.py` (791 LOC) and its autofix sub‑function (271 LOC) exceed typical module size, increasing maintenance risk.  
4. **Config Drift** – `.oneshot/config/models.yaml` is a high‑traffic config (36 sessions) but has no recorded dependencies, suggesting possible undocumented changes.

# Recommended Next Steps  
1. Add unit tests for `core/dispatch/run.py` covering its main execution paths.  
2. Split `core/janitor/jobs.py` into logical sub‑modules (e.g., onboarding, cleanup) to bring each below 500 LOC.  
3. Review and document the contents of `.oneshot/config/models.yaml`; add schema validation to catch unintended edits.  
4. Conduct a knowledge‑transfer audit on `.claude/skills/_shared/providers.md` and the two hardening plan docs; add at least one reviewer or backup author.  
5. Refactor `oneshot_cli/doctor_cmd.py` by extracting the 271‑line autofix routine into a separate helper module.