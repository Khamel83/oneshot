# Documentation Audit

## Pass A — README Accuracy

**Status:** Complete

**What changed in README.md:**
- Removed aspirational/marketing language ("operator framework centered on", "combines skills, routing policies...")
- Removed stale terminal shortcuts (`shot`, `zai`, `oc`, `or`) — `install.sh` does not create these
- Removed claim that `AGENTS.md` is written to current project (not in current `install.sh`)
- Updated worker table to reflect actual workers in `config/workers.yaml` (removed `claw_code` as primary option; added `free`, `ocg_minimax`, `ocg_api`)
- Fixed lane table to match `config/lanes.yaml` exactly (added `janitor` lane)
- Updated skill count from 10 to 15 to match `.claude/skills/INDEX.md`
- Fixed project structure (`templates/` not `.templates/`, added `oneshot_cli/`)
- Added honest **Known Limitations** section (GLM expiry, OpenCode Go key requirement, `oc` wrapper conditional, cross-repo memory degraded mode, janitor OPENROUTER_API_KEY dependency)
- Trimmed length from 223 lines to ~176 lines

---

## Other Doc Files (Brief Inventory)

Full content audit deferred to Pass B–E.

### Root-level docs

| File | Purpose |
|---|---|
| `CHANGELOG.md` | Version history (current v14.3) |
| `CLAUDE.md` | Project instructions for Claude Code |
| `CLAUDE.local.md` | Auto-generated onboarding summary |
| `CENTRAL_SECRETS.md` | Central secrets vault reference |
| `one_shot.md` | ⚠️ Unclear — appears to be an older project overview |
| `QUICKSTART.md` | Quick start guide |
| `SHARING_ONESHOT.md` | How to share OneShot with others |
| `SOPS_STANDALONE.md` | Standalone SOPS/Age usage guide |
| `worker.md` | ⚠️ Worker-related documentation (content unverified) |
| `llms.txt` | ⚠️ LLM context file |

### `docs/` directory

| File | Purpose |
|---|---|
| `docs/instructions/core.md` | Core operator rules |
| `docs/instructions/workflow.md` | Workflow instructions |
| `docs/instructions/coding.md` | Coding guidelines |
| `docs/instructions/review.md` | Review process |
| `docs/instructions/search.md` | Search policy |
| `docs/instructions/secrets.md` | Secrets management |
| `docs/instructions/secrets-reference.md` | Secrets reference |
| `docs/instructions/task-classes.md` | Task classification guide |
| `docs/instructions/oneshot.md` | OneShot-specific instructions |
| `docs/DELEGATION_MODEL.md` | Delegation model architecture |
| `docs/SEARCH_POLICY.md` | Search provider policy |
| `docs/SKILLS.md` | Skills overview |
| `docs/WORKER_LANES.md` | Worker lane documentation |
| `docs/WORKTREE_FLOW.md` | Git worktree flow documentation |
| `docs/LLM-OVERVIEW.md` | LLM overview |
| `docs/MACHINE_READINESS.md` | Machine readiness checklist |
| `docs/public-access.md` | Public access notes |
| `docs/ZAI_TO_OPENCODE_GO_MIGRATION.md` | Migration guide from ZAI to OpenCode Go |
| `docs/meta-harness/eval_framework.md` | Evaluation framework |
| `docs/meta-harness/trace_architecture.md` | Trace architecture |
| `docs/meta-harness/outer_loop_plan.md` | Outer loop planning |
| `docs/meta-harness/refactor_plan.md` | Refactor plan |
| `docs/meta-harness/repo_xray.md` | Repo x-ray analysis |
| `docs/external/codex/` | Codex external documentation cache |
| `docs/external/gemini/` | Gemini external documentation cache |
| `docs/external/opencode/` | OpenCode external documentation cache |
| `docs/research/` | Research documents and background intelligence |
| `docs/migration/baseline/` | Baseline migration docs (legacy skills/rules) |
| `docs/sessions/` | Session records |

### `.claude/` directory

| File | Purpose |
|---|---|
| `.claude/skills/INDEX.md` | Canonical skill index (15 skills) |
| `.claude/skills/SKILLS_REFERENCE.md` | Skill reference |
| `.claude/rules/khamel-mode.md` | Khamel mode rules |
| `.claude/rules/core.md` | Core rules import |
| `.claude/rules/delegation-enforcement.md` | Delegation enforcement |
| `.claude/rules/codex.md` | Codex setup/auth |
| `.claude/agents/INDEX.md` | Agent index |
| `.claude/memory/memory.md` | Memory documentation |

### `templates/` directory

| File | Purpose |
|---|---|
| `templates/TASK_SPEC.md` | Task specification template |
| `templates/AGENTS.md.j2` | AGENTS.md Jinja template |
| `templates/CLAUDE.md.j2` | CLAUDE.md Jinja template |
| `templates/LLM-OVERVIEW.md` | LLM overview template |

### `plans/` and `1shot/` directories

| File | Purpose |
|---|---|
| `plans/community-starter/` | Community starter plan tasks |
| `1shot/PROJECT.md` | Current project plan |
| `1shot/ROADMAP.md` | Current roadmap |
| `1shot/STATE.md` | Current state |
| `1shot/BLOCKERS.md` | Current blockers |

---

## Pass B — Core Instructions Audit

**Status:** Pending

Focus: `docs/instructions/*.md` — accuracy, stale content, missing sections.

---

## Pass C — Skill Documentation Audit

**Status:** Pending

Focus: `.claude/skills/*/SKILL.md` — do they match implementation? Are shared imports correct?

---

## Pass D — External / Cached Docs Audit

**Status:** Pending

Focus: `docs/external/`, `docs/research/` — stale caches, broken links, outdated provider docs.

---

## Pass E — Template & Plan Docs Audit

**Status:** Pending

Focus: `templates/`, `plans/`, `1shot/` — do templates reflect current structure? Are plans current?
