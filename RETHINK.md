# ONE_SHOT Rethink: From Framework to Kit

## The Problem

ONE_SHOT v9 has 52 skills, 12,260 lines of skill code, a 10.6KB AGENTS.md, and a 9.3KB
CLAUDE.md. In practice, it doesn't reliably do what it's supposed to because:

1. **Skill routing fights Claude's native system.** Claude Code already has a skill loader,
   sub-agents, hooks, and MCP. ONE_SHOT builds a second routing layer on top, and the two
   interfere with each other rather than composing cleanly.

2. **Context budget is blown on meta-instructions.** ~20KB of CLAUDE.md + AGENTS.md loads
   before any project context. That's ~5,000 tokens of overhead telling Claude how to think
   instead of what this project needs.

3. **Most skills restate native capabilities.** Claude already knows how to debug, refactor,
   write tests, review code, and plan. Skills like `debugger`, `refactorer`, `test-runner`,
   and `code-reviewer` are mostly restating what Claude does by default, wrapped in a routing
   framework.

4. **The ecosystem moved.** Claude Code now supports `.claude/rules/` for modular instructions,
   native hooks for automation, and the Task tool for sub-agent delegation. These didn't exist
   when ONE_SHOT was designed.

## What the ecosystem confirms

Looking at repos with 5K-41K stars in this space:

- **Popular ≠ sophisticated.** Stars come from friction reduction and distribution, not prompt
  engineering depth.
- **Nobody solves persistent memory.** Every popular repo assumes stateless fresh starts.
- **Nobody solves personal infra routing.** They're generic; ONE_SHOT's strength is being personal.
- **The skill-as-file format won.** OpenSkills (8K stars) standardized on it. Claude Code adopted it natively.

## The Rethink: Framework → Kit

Instead of an orchestration framework that routes everything, ONE_SHOT becomes a **personal
productivity kit** — a small set of files that make Claude Code work better for *you specifically*.

### Architecture

```
~/.claude/
├── CLAUDE.md              # Identity + defaults (< 800 bytes)
├── rules/                 # Modular rules (loaded contextually)
│   ├── infra-routing.md   # Your 3 machines + Tailscale
│   ├── stack-defaults.md  # SQLite→Convex→OCI progression
│   ├── deploy-patterns.md # Tailscale Funnel, not nginx
│   ├── anti-patterns.md   # Things to flag/avoid
│   └── lessons.md         # Symlink to persistent lessons DB
└── commands/              # Custom slash commands (only for novel workflows)
    ├── deploy.md          # /deploy → push to oci-dev
    ├── sync-secrets.md    # /sync-secrets → SOPS/Age workflow
    └── audit.md           # /audit → strategic communication filter

~/github/oneshot/
├── CLAUDE.md              # Project-specific (for oneshot repo itself)
├── .claude/rules/         # Oneshot-specific rules
├── secrets/               # SOPS/Age encrypted (keep this)
├── scripts/               # Shell scripts (keep useful ones)
└── archive/               # Old skills (reference only)
```

### What stays (genuinely adds capability Claude doesn't have)

| Keep | Why |
|------|-----|
| **KHAMEL MODE identity** | Claude doesn't know your machines/IPs/preferences |
| **Infrastructure routing** | 3 machines, Tailscale, specific IPs — real config |
| **Stack defaults** | SQLite→Convex→OCI progression is a real opinion |
| **Anti-pattern detection** | Flagging nginx/postgres/aws when you use Tailscale/SQLite/OCI |
| **Secrets management** | SOPS/Age workflow is genuinely complex |
| **The Audit** | Strategic communication filter is a real novel capability |
| **Lessons system** | Persistent learning is the gap nobody else fills |
| **Deploy workflow** | `push-to-cloud` with your specific infra is real automation |

### What goes (restates native capabilities)

| Kill | Why |
|------|-----|
| **Skill router / AGENTS.md** | Claude Code has native skill loading |
| **debugger, refactorer, test-runner, code-reviewer** | Claude does these natively |
| **front-door / interview system** | Just ask questions; Claude already triages |
| **create-plan, implement-plan, continuous-planner** | Claude plans natively with TodoWrite |
| **dispatch / multi-model routing** | Interesting but adds complexity for marginal gain |
| **beads** | Replace with GitHub Issues or simple TODO.md |
| **resume-handoff / create-handoff** | Claude Code has native context compression |
| **failure-recovery** | Claude recovers on its own; prompting doesn't help much |
| **thinking-modes** | Claude has native extended thinking |
| **batch-processor, parallel-validator** | Task tool with sub-agents does this natively |
| **freesearch, search-fallback, deep-research** | WebSearch + Task tool covers this |
| **skills-browser, skill-analytics, skillsmp-browser** | Meta-tools for managing tools |
| **auto-updater** | Nothing to update if skills are gone |
| **hooks system** | Use Claude Code's native hooks instead |

### What transforms (keep the knowledge, change the delivery)

| Skill | Becomes |
|-------|---------|
| `push-to-cloud` | `~/.claude/commands/deploy.md` (custom slash command) |
| `secrets-vault-manager` | `~/.claude/commands/sync-secrets.md` |
| `the-audit` | `~/.claude/commands/audit.md` |
| `remote-exec` | `~/.claude/rules/infra-routing.md` (just the machine list + SSH patterns) |
| `docker-composer` | `~/.claude/rules/deploy-patterns.md` (your specific Docker opinions) |
| `convex-resources` | `~/.claude/rules/stack-defaults.md` |
| `oci-resources` | `~/.claude/rules/stack-defaults.md` |

## The Numbers

| Metric | Before (v9) | After (kit) |
|--------|-------------|-------------|
| Skill files | 52 directories, 69 files | 0 skills |
| Rule files | 0 | ~8 focused rules |
| Custom commands | 23 slash commands | 3 commands |
| CLAUDE.md size | 9,297 bytes | < 800 bytes |
| AGENTS.md size | 10,641 bytes | Deleted |
| Total prompt overhead | ~20KB (~5,000 tokens) | ~3KB (~750 tokens) |
| Lines of instruction | 12,260 | ~400 |

## Migration Path

### Phase 1: Slim global config (do now)
- Write new `~/.claude/CLAUDE.md` (< 800 bytes)
- Create `~/.claude/rules/` with 5-8 focused files
- Test for a week alongside existing system

### Phase 2: Extract commands (week 2)
- Convert `push-to-cloud` → `/deploy` command
- Convert `secrets-vault-manager` → `/sync-secrets` command
- Convert `the-audit` → `/audit` command

### Phase 3: Archive skills (week 3)
- Move all skills to `archive/skills-v9/`
- Remove AGENTS.md from projects
- Remove hooks that inject AGENTS.md

### Phase 4: Evaluate (week 4)
- Is Claude actually more effective with less overhead?
- Are there workflows you miss? Add them back as rules/commands.
- Does persistent learning (lessons) work better with less noise?

## The Real Bet

The hypothesis: **Claude Code with 750 tokens of focused personal context will outperform
Claude Code with 5,000 tokens of orchestration overhead.** Because:

1. More context budget for actual project code
2. No routing conflicts between your system and Claude's native system
3. Rules load contextually (only when relevant files are touched)
4. Custom commands only for workflows Claude genuinely can't do natively

If this is wrong, skills can be restored from archive. The migration is fully reversible.

## What ONE_SHOT Becomes

ONE_SHOT stops being a "framework" and becomes a **personal Claude Code configuration** that
you maintain in the oneshot repo. Other people can fork it as a starting template for their
own personal configs. The value isn't the orchestration — it's the *opinions* (stack defaults,
infra routing, anti-patterns, lessons).

This is actually more shareable than the current system, because people can adopt individual
rules without buying into the whole framework.
