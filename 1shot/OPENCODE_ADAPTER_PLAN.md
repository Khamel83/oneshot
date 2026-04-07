# OpenCode Adapter Plan: Making OneShot Universal

> **Goal**: OpenCode becomes the universal harness. Same AGENTS.md, same routing, same dispatch.
> When Claude tokens run out, switch to OpenCode and keep working.
> **Date**: 2026-04-07
> **Status**: Draft — reviewed by Codex (see Review Notes below). Gemini CLI broken on this machine.
> **v2**: Updated based on Codex review corrections.

---

## Current State

### What Already Works

| Component | Status | Notes |
|-----------|--------|-------|
| `core/router/resolve.py` + `lane_policy.py` | Works | Pure Python, CLI-agnostic |
| `core/task_schema.py` | Works | Pure Python dataclasses + keyword matching |
| `core/dispatch/run.py` | Works | Subprocess dispatch to codex, gemini, claw_code, glm_claude |
| `config/lanes.yaml` + `workers.yaml` | Works | YAML-based routing, worker names are opaque strings |
| `AGENTS.md` (root) | Works | All three CLIs read it natively |
| `core/search/argus_client.py` | Works | Pure HTTP, no CLI deps |
| `.opencode/opencode.json` | Exists | Minimal — only configures anthropic provider |
| `.opencode/AGENTS.md` | Exists | Thin wrapper pointing to root AGENTS.md |
| `.opencode/commands/conduct.md` | Exists | Stub — simplified version |
| `.opencode/commands/research.md` | Exists | Uses raw curl instead of argus_client |
| `.opencode/agents/cheap-worker.md` | Exists | But has `bash: false` — can't dispatch |
| `.opencode/agents/reviewer.md` | Exists | Read-only agent, works for review |

### What's Broken in the OpenCode Adapter

1. **OpenCode agents have `bash: false`** — cheap-worker cannot run `python -m core.router.resolve` or dispatch to other CLIs. It can only read/write files. This makes it a standalone worker, not a dispatcher.

2. **No OpenCode primary agent with dispatch capability** — There's no agent definition that has bash enabled AND understands the dispatch protocol. The `build` agent (default) has full access but no OneShot-specific instructions.

3. **argus_client.py doesn't read config** — Hardcodes `localhost:8005` instead of reading `config/search.yaml`.

4. **research.md uses raw curl** — Bypasses argus_client.py entirely, creating a dual code path.

5. **No persistent task tracking** — OpenCode's `todowrite` is session-scoped (CASCADE deletes on session end).

6. **No session start context injection** — No equivalent of Claude Code's hooks that inject compressed project state.

7. **Janitor only works via Claude Code hooks** — `scripts/janitor-cron.sh` already exists but is marked deprecated. Needs to be updated and wired to a systemd timer.

8. **SSH dispatch not implemented** — `workers.yaml` declares `transport: ssh` for macmini/homelab but `dispatch/run.py` only runs local subprocesses.

9. **Provider config is Anthropic-only** — `.opencode/opencode.json` only configures `anthropic`. If the goal is "switch when Claude tokens run out," OpenRouter + OpenAI + Google must be configured first.

10. **AGENTS.md indirection doesn't work** — `.opencode/AGENTS.md` tells the model to "read root AGENTS.md" but OpenCode doesn't auto-follow cross-file references. Must reference `../AGENTS.md` directly in `instructions`.

---

## What We're NOT Changing

- All Claude Code skills, hooks, rules — keep working as-is
- CLAUDE.md, CLAUDE.local.md — keep working as-is
- `core/router/`, `core/task_schema.py`, `core/plan_schema.py` — CLI-agnostic, no changes needed
- `config/lanes.yaml`, `config/workers.yaml`, `config/models.yaml` — YAML configs, no changes needed
- AGENTS.md — the neutral operating contract stays the same
- Claude Code as primary harness — this is additive, not replacing

---

## Phase 0: Provider + Config Bootstrap (MUST come first)

> **Codex review correction**: Provider/model setup must be done before anything else. If the goal is "switch when Claude tokens run out," OpenCode must have alternative providers configured.

### 0A: Add providers to opencode.json

**File**: `.opencode/opencode.json`
**Change**: Add OpenRouter, OpenAI, Google providers. Reference existing env vars.
```json
{
  "provider": {
    "openrouter": {
      "options": { "apiKey": "{env:OPENROUTER_API_KEY}" }
    },
    "openai": {
      "options": { "apiKey": "{env:OPENAI_API_KEY}" }
    },
    "google": {
      "options": { "apiKey": "{env:GEMINI_API_KEY}" }
    }
  }
}
```

### 0B: Fix AGENTS.md reference

**File**: `.opencode/opencode.json`
**Change**: `instructions: ["../AGENTS.md"]` — direct reference, not indirection through `.opencode/AGENTS.md`

### 0C: Verify with smoke test

```bash
opencode -c "echo hello" --model openrouter/google/gemini-2.5-flash
opencode -c "echo hello" --model openai/gpt-5
```

---

## Phase 1: Fix the Foundation (no new features, just make existing stuff work)

### 1A: argus_client.py reads config

**File**: `core/search/argus_client.py`
**Change**: Import yaml, read `config/search.yaml` for `base_url` and mode defaults
**Why**: Currently hardcodes `localhost:8005`. Any config change requires code change.
**Lines**: ~10 lines added (import yaml + load_config helper)

### 1B: research.md uses argus_client instead of raw curl

**File**: `.opencode/commands/research.md`
**Change**: Replace raw `curl` calls with `python -c "from core.search.argus_client import search; ..."`
**Why**: Single code path for Argus. Config-driven, not hardcoded.

### 1C: Design decision — subagents should NOT dispatch

> **Codex review correction**: Subagents should stay bounded. The primary agent (or commands running on the primary agent) should dispatch to workers. Subagents shelling out to codex/gemini creates nested orchestrators, approval deadlocks, and unreadable traces.
>
> **Decision**: `cheap-worker` stays as a bounded file-only worker. The primary agent (via commands) handles dispatch through `core.dispatch.run`. Subagents are never given dispatch authority.

### 1D: Update cheap-worker permissions (bounded only)

**File**: `.opencode/agents/cheap-worker.md`
**Change**: Keep `bash: false`. This agent is a standalone Gemini Flash worker, not a dispatcher.
**Why**: Bounded agents are safer. The primary agent handles orchestration.

### 1E: Fix AGENTS.md reference in opencode.json

**File**: `.opencode/opencode.json`
**Change**: Set `instructions: ["../AGENTS.md"]` — direct file reference
**Why**: OpenCode doesn't auto-follow cross-file references in markdown. The `.opencode/AGENTS.md` indirection layer doesn't work.

---

## Phase 2: OpenCode Commands (the slash commands)

> **Codex review correction**: Commands run on the current agent unless `agent:` is set in frontmatter. If pointing at a subagent, OpenCode may invoke as subtask unless `subtask: false`. Every command must explicitly set `agent: build` to ensure the primary agent (with dispatch capability) runs them.

### 2A: Translate /short

**File**: `.opencode/commands/short.md`
**Frontmatter**: `agent: build` (ensures primary agent with bash access runs this)
**Content**: Same workflow as `.claude/skills/short/SKILL.md` but adapted for OpenCode tools:
- `TaskList` → `todowrite` tool (session-scoped, fine for a single session)
- `python -m core.router.resolve` → via bash
- `codex exec` / `gemini` → via bash via `core.dispatch.run`
- Provider detection → via bash

**Key difference from Claude Code**: No `AskUserQuestion` — use `question` tool instead (already exists in OpenCode).

### 2B: Translate /conduct

**File**: `.opencode/commands/conduct.md` (exists, needs rewrite)
**Content**: Same phases as Claude Code `/conduct` but adapted:
- Phase 0 intake: Use `question` tool instead of `AskUserQuestion`
- Phase 1 plan: `python -m core.router.resolve` via bash, `todowrite` for task tracking
- Phase 2 build: `python -m core.dispatch.run` via bash for actual dispatch
- Phase 3 verify: Run tests via bash
- Phase 4 challenge: `codex review` via bash, or reviewer agent
- Phase 5 learning: Write to `docs/instructions/learned/`

**Key difference**: TaskCreate/TaskUpdate → todowrite for session tasks. For persistent cross-session tasks, write to a JSON file (`1shot/tasks.json`) that survives sessions.

### 2C: Translate /handoff

**File**: `.opencode/commands/handoff.md`
**Content**: Pure markdown output, almost identical to Claude Code version.
**Change**: Minimal — just the invocation format.

### 2D: Translate /restore

**File**: `.opencode/commands/restore.md`
**Content**: Read handoff file, set context. Same as Claude Code version.

### 2E: Translate /freesearch

**File**: `.opencode/commands/freesearch.md`
**Content**: Uses argus_client in cheap mode. Already exists in Gemini CLI, translate to OpenCode command.

### 2F: Translate /doc

**File**: `.opencode/commands/doc.md`
**Content**: Cache external documentation. Pure bash + file I/O. Almost identical.

---

## Phase 3: Persistent Task Tracking Shim

### 3A: tasks.json — cross-session persistent tasks

**New file**: `1shot/tasks.json`
**Format**:
```json
{
  "version": 1,
  "tasks": [
    {
      "id": "1",
      "subject": "Fix auth bug",
      "description": "...",
      "status": "in_progress",
      "priority": "high",
      "created": "2026-04-07T10:00:00Z",
      "updated": "2026-04-07T10:30:00Z",
      "blocked_by": []
    }
  ]
}
```

**New file**: `scripts/tasks.py` — CLI for task CRUD
```bash
python scripts/tasks.py list          # list all tasks
python scripts/tasks.py add "title"   # add task
python scripts/tasks.py update 1 done # update status
python scripts/tasks.py blocked-by 1 2  # set dependency
```

**Integration**: OpenCode commands call `python scripts/tasks.py` via bash. Claude Code skills can optionally use it too (but native Tasks still work).

**Why not use todowrite?** Session-scoped only. Dies when session ends. The JSON file survives.

### 3B: Session start task loading

**Approach**: Instead of a hook (OpenCode doesn't have session hooks), add a line to the OpenCode commands that load tasks:
```
1. Load existing tasks: `python scripts/tasks.py list`
2. If no tasks, ask what you're working on
```

This is manual (run at session start) rather than automatic (hook fires on session start). Good enough for v1.

---

## Phase 4: Janitor as Cron

### 4A: janitor-cron.sh

**New file**: `scripts/janitor-cron.sh`
**What it runs**:
1. `detect_test_gaps` — find source files with no tests
2. `scan_code_smells` — find oversized files/functions
3. `detect_config_drift` — find uncommitted config changes
4. `build_dependency_map` — import graph
5. (Optional) `summarize_session` — if events.jsonl has new events, call openrouter/free
6. (Optional) `generate_onboarding` — regenerate `.oneshot/onboarding.md` or `CLAUDE.local.md`

**Output**: Writes to `.janitor/test-gaps.json`, `.janitor/code-smells.json`, `.janitor/config-drift.json`, `.janitor/dep-graph.json` (same as today)

### 4B: systemd timer

**New files**:
- `~/.config/systemd/user/oneshot-janitor.service`
- `~/.config/systemd/user/oneshot-janitor.timer`

**Schedule**: Every 15 minutes. `Persistent=true` so it runs missed intervals on boot.

### 4C: Keep Claude Code hooks for event recording

**What stays**: The Claude Code PostToolUse hook that records events to `.oneshot/events.jsonl`. This only fires in Claude Code sessions. OpenCode sessions won't have event recording (acceptable — the pure-compute janitor jobs don't depend on events).

---

## Phase 5: OpenCode Agent Definitions

### 5A: OneShot primary agent

**File**: `.opencode/agents/oneshot.md` (new) OR update `build` agent
**Purpose**: The default agent with OneShot operating contract + dispatch capability
**Tools**: bash (with restrictions), read, write, edit, glob, grep, question, todowrite, task
**Model**: User's choice (default to whatever they have tokens for)

### 5B: Update cheap-worker

**File**: `.opencode/agents/cheap-worker.md` (update)
**Changes**: Enable bash for dispatch, add dispatch protocol instructions
**Model**: `openrouter/google/gemini-2.5-flash` (or whatever's cheapest)

### 5C: Keep reviewer as-is

**File**: `.opencode/agents/reviewer.md` (no change)
**Why**: Read-only agent is correct for review. No changes needed.

---

## Phase 6: MCP Integration (Argus)

> **Codex review correction**: MCP config is NOT drop-in between CLIs. Auth, env wiring, enablement, and per-agent approvals differ. Treat MCP as optional integration, not as "same servers, same tools."

### 6A: Evaluate Argus as MCP server

**Decision point**: Does Argus expose an MCP interface? If yes, add to opencode.json. If no, keep using `argus_client.py` via bash (which already works).

### 6B: Add MCP servers individually (not bulk)

**File**: `.opencode/opencode.json`
**Approach**: Add MCP servers one at a time, verifying each works before adding the next. Don't assume Claude Code MCP config will just work.

---

## Review Notes

### Codex Review (2026-04-07)

**Accepted corrections:**
1. Permission syntax: `tools.bash: "ask"` is wrong. Use `permission.bash` with glob patterns.
2. Phase order: Agent/config before commands.
3. Provider bootstrap missing: Must be first.
4. AGENTS.md indirection: Use direct reference in `instructions`.
5. MCP section hand-wavy: Not drop-in, test individually.
6. Subagents should NOT dispatch: Primary agent only.
7. `janitor-cron.sh` already exists (was marked deprecated).

**Rejected corrections:**
- "todowrite doesn't CASCADE-delete" — Verified against actual SQLite schema: `FOREIGN KEY(session_id) REFERENCES session(id) ON DELETE CASCADE`. It does cascade.
- "tasks.json is unnecessary complexity" — Fair concern but todowrite genuinely doesn't persist across sessions. Defer to Phase 3 (after testing with todowrite alone).
- "core.dispatch.run needs an OpenCode runner" — Disagree for v1. OpenCode is the human-facing harness. Workers are still dispatched as subprocess CLIs via Python. No need for OpenCode-to-OpenCode dispatch.

### Gemini Review

Failed — Gemini CLI broken on this machine (Docker amd64/arm64 mismatch).

---

## What's NOT in This Plan (intentionally deferred)

| Feature | Why Deferred |
|---------|-------------|
| SSH dispatch to remote workers | macmini/homelab as OpenCode workers requires SSH + remote OpenCode setup. Complex, low priority. |
| OpenCode as MCP server | OpenCode can be an MCP server but we don't need this yet. |
| Plugin SDK (npm) | The plugin infrastructure exists but we don't need custom plugins yet. Shell commands + agents + commands cover everything. |
| Gemini CLI adapter | Gemini has Beads + hooks + extensions. Can be done later. |
| Codex CLI adapter | Codex has skills + plugins. Hooks are still under development. Can be done later. |
| Native subagent dispatch from OpenCode | Using `task` tool instead of `python -m core.dispatch.run` subprocess dispatch. The subprocess approach works and is simpler. |
| `update_plan` in Codex | Ephemeral. Not useful for cross-session persistence. |

---

## Files Changed Summary

### New Files
| File | Purpose |
|------|---------|
| `scripts/tasks.py` | Persistent task tracking CLI |
| `scripts/janitor-cron.sh` | Cron-based janitor runner |
| `~/.config/systemd/user/oneshot-janitor.service` | systemd service unit |
| `~/.config/systemd/user/oneshot-janitor.timer` | systemd timer unit |
| `.opencode/commands/short.md` | /short command |
| `.opencode/commands/handoff.md` | /handoff command |
| `.opencode/commands/restore.md` | /restore command |
| `.opencode/commands/freesearch.md` | /freesearch command |
| `.opencode/commands/doc.md` | /doc command |
| `1shot/tasks.json` | Persistent task store (created at runtime) |

### Modified Files
| File | Change |
|------|--------|
| `.opencode/opencode.json` | Add providers (openrouter, openai, google), fix AGENTS.md reference |
| `.opencode/agents/cheap-worker.md` | Keep bash:false, update as bounded-only worker |
| `.opencode/commands/conduct.md` | Rewrite with full dispatch protocol, add `agent: build` |
| `.opencode/commands/research.md` | Use argus_client instead of raw curl |
| `core/search/argus_client.py` | Read `config/search.yaml` for base_url |

### Unchanged Files
| File | Why |
|------|-----|
| `core/router/resolve.py` | CLI-agnostic |
| `core/router/lane_policy.py` | CLI-agnostic |
| `core/task_schema.py` | CLI-agnostic |
| `core/dispatch/run.py` | Already works via subprocess |
| `config/lanes.yaml` | String-based routing |
| `config/workers.yaml` | Machine placement |
| `AGENTS.md` | Neutral operating contract |
| `.claude/skills/*` | Claude Code-specific, keep as-is |
| `.claude/hooks/*` | Claude Code-specific, keep as-is |
| `.claude/rules/*` | Claude Code-specific, keep as-is |

---

## Execution Order

> **Codex review correction**: Agent/config must come before commands. Provider bootstrap is first.
>
> **Revised order (v2)**:
> 1. **Phase 0** — Provider bootstrap + AGENTS.md fix + smoke test
> 2. **Phase 5A** — Define the `oneshot` primary agent with correct permissions
> 3. **Phase 1** — Foundation fixes (argus_client, research.md, cheap-worker bounded)
> 4. **Phase 2** — Command translations (`/short`, `/conduct`, `/handoff`, `/restore`, `/freesearch`, `/doc`)
> 5. **Phase 3** — Persistent task tracking shim (if needed after testing with todowrite)
> 6. **Phase 4** — Janitor cron (independent, can be done anytime)
> 7. **Phase 6** — MCP integration (if needed, not assumed drop-in)

---

## Success Criteria

- [ ] `opencode` in the oneshot repo reads AGENTS.md and understands the operating contract
- [ ] `/short` command works in OpenCode — loads context, classifies, dispatches to workers
- [ ] `/conduct` command works in OpenCode — full intake → plan → build → verify loop
- [ ] `python -m core.router.resolve --class implement_small` returns correct routing
- [ ] `python -m core.dispatch.run --class implement_small --prompt "test"` dispatches to workers
- [ ] Argus search works via `/freesearch` command in OpenCode
- [ ] Task tracking survives session end (tasks.json persists)
- [ ] Janitor runs via cron, outputs to `.janitor/` (same format as today)
- [ ] Claude Code still works exactly as before (no regressions)
