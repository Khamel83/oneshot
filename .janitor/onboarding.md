# Project Status  
Oneshot is a mature Python package with extensive code but limited test coverage; several very large source files and stale documentation indicate technical‑debt hotspots.

# Recent Activity  
- `.oneshot/config/models.yaml` was opened 5 times by “Test User”.  
- `CLAUDE.md` edited 4 times by Khamel83.  
- `.claude/skills/_shared/providers.md` edited 3 times by “Test User”.  
- `docs/ZAI_TO_OPENCODE_GO_MIGRATION.md` edited 3 times by “Test User”.  
- `README.md` edited 3 times by Khamel83.  
- The most recent focus files were `.claude/skills/conduct/SKILL.md` (twice) and two memory notes in `/home/ubuntu/.claude/projects/.../memory/`.

# Attention Items  
1. **Test Gaps (high urgency)** – No tests for:  
   - `core/dispatch/direct_api.py`  
   - `oneshot_cli/__main__.py`  
   - `scripts/validate-oneshot-config.py`  
2. **Knowledge Risk (high urgency)** – Sole‑author files with limited review:  
   - `.claude/skills/conduct/SKILL.md` (11 edits, Test User)  
   - `.claude/skills/_shared/providers.md` (10 edits, Test User)  
   - `.claude/skills/full/SKILL.md` (10 edits, Test User)  
3. **Oversized Files (medium urgency)** – Files >600 lines that are hard to maintain:  
   - `core/janitor/jobs.py` (1,834 lines)  
   - `oneshot_cli/doctor_cmd.py` (791 lines)  
   - `core/dispatch/run.py` (675 lines)  
4. **Config Drift (medium urgency)** – Frequently edited YAML configs suggest drift:  
   - `.oneshot/config/models.yaml` (36 sessions)  
   - `oneshot_cli/tasks.py` (17 sessions)  
   - `.opencode/opencode.json` (15 sessions)  

# Recommended Next Steps  
1. Add unit tests for `core/dispatch/direct_api.py`, `oneshot_cli/__main__.py`, and `scripts/validate-oneshot-config.py`.  
2. Conduct a peer review of the three sole‑author skill files (`.claude/skills/conduct/SKILL.md`, `.claude/skills/_shared/providers.md`, `.claude/skills/full/SKILL.md`) and document any missing edge cases.  
3. Refactor `core/janitor/jobs.py` into smaller modules (e.g., split `generate_onboarding` and `run_session_start` into separate files).  
4. Split `oneshot_cli/doctor_cmd.py` and `core/dispatch/run.py` into logical sub‑components to bring each below 400 lines.  
5. Freeze the current state of `models.yaml`, `tasks.py`, and `opencode.json`, then create a linting/validation script to detect unintended changes in future commits.