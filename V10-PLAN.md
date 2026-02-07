# ONE_SHOT v10 Plan

## What v10 IS

Your personal Claude Code configuration. Not a framework, not distributable, not a
skill marketplace. Just makes Claude Code work the way you want it to across all your
projects.

## Architecture

```
~/.claude/
├── CLAUDE.md                    # Identity (< 200 bytes)
├── rules/                       # Auto-loaded contextually (~1.5KB total)
│   ├── infra-routing.md         # 3 machines + Tailscale IPs
│   ├── stack-defaults.md        # SQLite→Convex→OCI progression
│   ├── anti-patterns.md         # Flag wrong tools (nginx, postgres, AWS)
│   ├── docs-first.md            # Check docs before coding
│   ├── secrets.md               # SOPS/Age workflow rules
│   └── lessons.md               # Check lessons DB on session start
├── commands/                    # Loaded ONLY when invoked via /command
│   ├── interview.md             # /interview — front-door triage + interview
│   ├── cp.md                    # /cp — continuous planner (3-file system)
│   ├── implement.md             # /implement — execute plan with beads tracking
│   ├── freesearch.md            # /freesearch — Exa API, zero Claude tokens
│   ├── research.md              # /research — Gemini CLI background research
│   ├── think.md                 # /think — multi-perspective analysis
│   ├── diagnose.md              # /diagnose — structured hypothesis debugging
│   ├── codereview.md            # /codereview — OWASP + quality review
│   ├── deploy.md                # /deploy — rsync + systemd to oci-dev
│   ├── remote.md                # /remote — SSH execute on homelab/macmini
│   ├── audit.md                 # /audit — strategic communication filter
│   ├── beads.md                 # /beads — persistent task tracking
│   ├── handoff.md               # /handoff — save context before /clear
│   ├── restore.md               # /restore — resume from handoff
│   ├── secrets.md               # /secrets — SOPS/Age sync and management
│   └── batch.md                 # /batch — parallel multi-file operations
└── settings.json                # Hook registrations (if any survive)

~/github/oneshot/
├── V10-PLAN.md                  # This file
├── prototype/                   # v10 files (rules + commands)
├── archive/v9/                  # Full v9 preserved for reference
│   ├── .claude/skills/          # All 52 skills
│   ├── .claude/hooks/           # All hooks
│   ├── .claude/agents/          # All agent definitions
│   ├── AGENTS.md                # v9 routing table
│   └── CLAUDE.md                # v9 config
├── scripts/
│   └── migrate-v10.sh           # Migration script for existing projects
├── secrets/                     # SOPS/Age encrypted (unchanged)
└── CLAUDE.md                    # Oneshot repo-specific config
```

## Command Inventory (16 commands)

### Naming: Conflicts with Native Claude Code

These native commands exist and CANNOT be used:
- `/plan` — native plan mode toggle
- `/debug` — native troubleshooting
- `/resume` — native session resume
- `/review` — native code review

### Command Details

| Command | Source Skill(s) | What it does | Token cost |
|---------|----------------|--------------|------------|
| `/interview` | front-door | Triage → interview → spec → route to plan/build | On-demand |
| `/cp` | continuous-planner + create-plan | 3-file living plan (task_plan.md, findings.md, progress.md) | On-demand |
| `/implement` | implement-plan | Execute plan with beads task tracking | On-demand |
| `/freesearch` | freesearch | Exa API research, zero Claude tokens | Zero |
| `/research` | deep-research + dispatch + search-fallback | Gemini CLI or fallback APIs, background sub-agent | Minimal |
| `/think` | thinking-modes | Multi-perspective analysis (architect, security, perf, user) | On-demand |
| `/diagnose` | debugger | Hypothesis → isolation → test → fix workflow | On-demand |
| `/codereview` | code-reviewer | OWASP top 10 + quality + actionable feedback | On-demand |
| `/deploy` | push-to-cloud | rsync + systemd to oci-dev (100.126.13.70) | On-demand |
| `/remote` | remote-exec | SSH to homelab/macmini, sync, execute, stream | On-demand |
| `/audit` | the-audit | Voss/Camp communication filter for high-stakes messages | On-demand |
| `/beads` | beads | Persistent task tracking, dependencies, session close | On-demand |
| `/handoff` | create-handoff | Structured context save before /clear | On-demand |
| `/restore` | resume-handoff | Resume from handoff file + sync beads | On-demand |
| `/secrets` | secrets-vault-manager + secrets-sync | SOPS/Age decrypt, encrypt, sync, rotate | On-demand |
| `/batch` | batch-processor | Parallel multi-file operations via sub-agents | On-demand |

### Commands NOT included (native coverage)

| Old Skill | Why dropped | Native equivalent |
|-----------|------------|-------------------|
| debugger (basic) | Claude debugs natively | Just describe the bug |
| refactorer | Claude refactors natively | Just ask for refactoring |
| test-runner | Claude runs tests natively | "run the tests" |
| code-reviewer (basic) | Native `/review` exists | `/review` |
| thinking-modes (basic) | Extended thinking is native | "think carefully about this" |
| auto-updater | Nothing to auto-update | Manual git pull |
| skills-browser | No skills to browse | ls .claude/commands/ |
| skill-analytics | No skills to analyze | — |
| skillsmp-browser | Marketplace deferred | — |
| failure-recovery | Claude recovers natively | — |
| front-door routing | Replaced by user invoking commands directly | — |

## Rules Inventory (6 rules)

Rules are always loaded (contextually by Claude Code when relevant files are touched).
Total overhead: ~1.5KB (~375 tokens).

| Rule | What it does | Size |
|------|-------------|------|
| `infra-routing.md` | Machine IPs, roles, routing logic | ~250 bytes |
| `stack-defaults.md` | Default stacks per project type | ~300 bytes |
| `anti-patterns.md` | Flag wrong tools, suggest alternatives | ~300 bytes |
| `docs-first.md` | Check current docs before coding | ~200 bytes |
| `secrets.md` | SOPS/Age rules, never commit plaintext | ~200 bytes |
| `lessons.md` | Check ~/.claude/.beads/ for lessons on start | ~200 bytes |

## What Hooks Become

| v9 Hook | v10 Replacement | Why |
|---------|----------------|-----|
| `context-v8.py` | Rules files | Rules ARE the context — no compression needed at 1.5KB |
| `beads-v8.py` | `/beads` command | Session close workflow lives in the command |
| `lessons-inject.sh` | `lessons.md` rule | Rule tells Claude to check lessons DB |
| Heartbeat metadata | Dropped | Was for tracking, not functionality |

## Migration: Existing Projects

Projects currently using ONE_SHOT have some combination of:
- AGENTS.md (curled from oneshot repo)
- CLAUDE.md with ONE_SHOT boilerplate
- .beads/ directory
- Hooks configured in .claude/settings.json

### Migration script (`scripts/migrate-v10.sh`) will:

1. **Detect ONE_SHOT version** — check for AGENTS.md, skill references, CTX: pattern
2. **Remove AGENTS.md** — no longer needed (routing is gone)
3. **Clean CLAUDE.md** — strip ONE_SHOT boilerplate, keep project-specific content
4. **Preserve .beads/** — task data survives, `/beads` command reads it
5. **Update .claude/settings.json** — remove old hook registrations
6. **Report** — show what was changed, what was kept

### What the script does NOT touch:
- Project-specific CLAUDE.md content (your project rules)
- .beads/ data (your tasks)
- secrets/ (your encrypted files)
- Any project source code

## Token Budget Comparison

| Component | v9 (tokens) | v10 (tokens) | Savings |
|-----------|-------------|--------------|---------|
| CLAUDE.md | ~2,500 | ~50 | 98% |
| AGENTS.md | ~2,800 | 0 | 100% |
| Hook context injection | ~500 | 0 | 100% |
| Rules (always loaded) | 0 | ~375 | New |
| Commands (on demand) | ~200 per skill | ~200 per command | Same |
| **Total always-on** | **~5,800** | **~425** | **93%** |

## The /interview Command (Front Door Preserved)

The front-door interview system stays intact as `/interview`. Key behaviors:

1. **Triage first** (30 seconds): Classify intent as build_new, fix_existing,
   continue_work, modify_existing, understand, or quick_task
2. **Auto-spawn Explore agent** while interviewing (parallel, non-blocking)
3. **Depth control**: Full (all questions), Smart (auto-detect), Quick (4 questions)
4. **Iterative AskUserQuestion**: 1-2 questions per round with options
5. **Incremental spec writing**: Saves to ~/.claude/plans/spec-{date}-{slug}.md
6. **Post-interview routing**: Suggests `/cp` for planning, direct build for simple tasks

What changes: It no longer auto-triggers on "build me". You type `/interview` when you
want the structured interview. For simple requests, just tell Claude what you want.

## The /cp Command (Continuous Planner)

The 3-file living plan system stays intact. Key behaviors:

1. **Creates/updates three files** that survive /clear and context compression:
   - `task_plan.md` — decisions made, requirements locked
   - `findings.md` — research results, API docs, constraints discovered
   - `progress.md` — what's done, what's in progress, what's blocked
2. **Reads files before each response** to stay grounded against context drift
3. **Writes decisions to disk immediately** so they're never lost to rolling context

This is the core solution to the "we already decided not to use FastAPI" problem.

## The /freesearch and /research Commands (Token Conservation)

Two separate commands for different use cases:

- `/freesearch [topic]` — Exa API call, returns summary, synchronous, zero Claude tokens
- `/research [topic]` — Spawns background sub-agent using Gemini CLI, writes to
  findings.md, you keep working in main context

Both preserve the token conservation pattern you value.

## Implementation Order

### Step 1: Write all files
- [ ] 6 rules files in prototype/rules/
- [ ] 16 command files in prototype/commands/
- [ ] Slim CLAUDE.md in prototype/
- [ ] Migration script in scripts/

### Step 2: Archive v9
- [ ] Move current .claude/skills/ → archive/v9/skills/
- [ ] Move current .claude/hooks/ → archive/v9/hooks/
- [ ] Move current .claude/agents/ → archive/v9/agents/
- [ ] Move current AGENTS.md → archive/v9/AGENTS.md

### Step 3: Install v10
- [ ] Copy prototype/rules/ → ~/.claude/rules/
- [ ] Copy prototype/commands/ → ~/.claude/commands/
- [ ] Copy prototype/CLAUDE.md → ~/.claude/CLAUDE.md
- [ ] Test: start new Claude Code session, verify rules load
- [ ] Test: invoke each command, verify it works

### Step 4: Migrate projects
- [ ] Run migrate-v10.sh on each project that has AGENTS.md
- [ ] Verify .beads/ data still accessible via /beads
- [ ] Verify project-specific CLAUDE.md content preserved

## Auto-Handoff System (Context Protection)

Claude Code's statusline receives context window usage as JSON after every response.
We use this to auto-trigger handoffs before context is lost to auto-compact.

### How it works

```
statusline.sh (fires after every response)
  → reads context_window.used_percentage from JSON
  → writes percentage to /tmp/claude-oneshot/context-pct
  → displays "ctx: 73%" in status bar

auto-handoff.sh (Stop hook, fires after every response)
  → reads cached percentage from /tmp/claude-oneshot/context-pct
  → if >= 80%, outputs warning: "Run /handoff now"
  → sets marker so it only fires once per session

auto-handoff.md (rule, always loaded)
  → tells Claude: when you see the handoff warning, just do it
  → don't ask permission, save the handoff, tell user it's done

session-cleanup.sh (SessionStart hook)
  → clears stale markers from previous sessions
```

### Files

| File | Type | Purpose |
|------|------|---------|
| `hooks/statusline.sh` | Statusline | Monitor + cache context % |
| `hooks/auto-handoff.sh` | Stop hook | Trigger warning at 80% |
| `hooks/session-cleanup.sh` | SessionStart hook | Clear stale markers |
| `hooks/settings-snippet.json` | Config | Hook registrations for settings.json |
| `rules/auto-handoff.md` | Rule | Tells Claude to act on the warning |

### Threshold choice: 80%

- Auto-compact triggers at ~75-95% (hardcoded, varies)
- 80% gives enough room to write a handoff (~2-5% context) before compact fires
- The Stop hook fires once and sets a marker — no repeated nagging
- SessionStart clears the marker so each session gets one trigger

### Rules (updated total: 7)

| Rule | Size |
|------|------|
| `infra-routing.md` | ~250 bytes |
| `stack-defaults.md` | ~300 bytes |
| `anti-patterns.md` | ~300 bytes |
| `docs-first.md` | ~200 bytes |
| `secrets.md` | ~200 bytes |
| `lessons.md` | ~200 bytes |
| `auto-handoff.md` | ~200 bytes |
| **Total** | **~1.65KB (~410 tokens)** |

## Rollback Plan

If v10 doesn't work after a week:
1. `cp archive/v9/skills/ .claude/skills/`
2. `cp archive/v9/AGENTS.md ./AGENTS.md`
3. Restore hooks from archive
4. You're back to v9 in 30 seconds

## Roadmap (NOT v10, future versions)

| Feature | Version | Notes |
|---------|---------|-------|
| Dynamic skill discovery (auto-install) | v11+ | Requires skill registry + trust model |
| Skills marketplace integration | v11+ | skills.sh / openskills compatibility |
| Multi-agent swarm coordination | v12+ | Beyond fan-out, actual agent-to-agent |
| Cross-provider portability | v12+ | Same commands in Cursor/Windsurf |
| Lessons auto-extraction | v10.1 | Currently manual /oops, should be automatic |
