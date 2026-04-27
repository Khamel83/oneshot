# Project Status  
Oneshot is a Python package with extensive core logic but suffers from several test coverage gaps and a few very large modules that hinder maintainability.

# Recent Activity  
The most recent edits touched core/janitor/jobs.py (large function additions), core/janitor/recorder.py, core/janitor/worker.py, and core/task_schema.py (all flagged as test gaps). Documentation updates were made to .claude/skills/update/SKILL.md (3 edits) and docs/instructions/search.md (2 edits).

# Attention Items  
1. **Test Gaps (4 files)** – core/janitor/jobs.py, core/janitor/recorder.py, core/janitor/worker.py, core/task_schema.py have no associated tests.  
2. **Knowledge Risk (3 files)** – .claude/skills/conduct/SKILL.md (9 edits, single author), .claude/skills/full/SKILL.md (9 edits, single author), .claude/skills/_shared/providers.md (8 edits, single author) are sole‑contributor and could become single points of failure.  
3. **Oversized Files** – core/janitor/jobs.py is 1,834 lines; core/dispatch/run.py is 675 lines; core/janitor/jobs.py functions generate_onboarding (242 lines), run_session_start (202 lines), evaluate_task_sufficiency (166 lines) are each >150 lines, indicating high complexity.  
4. **Doc Staleness** – archive/v7-high-token/README.md and docs/public-access.md have not been updated in 84 days.

# Recommended Next Steps  
1. Add unit tests for core/janitor/jobs.py, core/janitor/recorder.py, core/janitor/worker.py, and core/task_schema.py (target ≥80% coverage).  
2. Refactor core/janitor/jobs.py: split generate_onboarding, run_session_start, and evaluate_task_sufficiency into smaller helper modules (e.g., core/janitor/onboarding.py, core/janitor/session.py).  
3. Review and duplicate knowledge for .claude/skills/conduct/SKILL.md, .claude/skills/full/SKILL.md, and .claude/skills/_shared/providers.md by adding a second reviewer or extracting key logic into shared libraries.  
4. Trim core/dispatch/run.py by extracting helper functions into core/dispatch/helpers.py to reduce the 675‑line file.  
5. Update archive/v7-high-token/README.md and docs/public-access.md to reflect current usage and APIs.