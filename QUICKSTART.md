# ONE_SHOT Quick Commands

## Install (First Time)

```bash
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
```

Or if you have the repo cloned:
```bash
bash install.sh
```

## Update

```bash
oneshot-update        # Check and auto-update if newer version found
oneshot-update force  # Force update now
oneshot-update status # Show version and last check
```

## Skills (10 total)

| Skill | What it does |
|-------|--------------|
| `/short` | Quick iteration on existing work |
| `/full` | New project or major refactor |
| `/conduct` | Multi-model orchestration until done |
| `/handoff` | Save context before `/clear` |
| `/restore` | Resume from handoff |
| `/research` | Background research via Gemini or search |
| `/freesearch` | Zero-token web search (Exa API) |
| `/doc` | Cache external docs locally |
| `/vision` | Analyze images or websites |
| `/secrets` | Manage SOPS/Age encrypted secrets |

## Typical Session

```
claude .          # Open Claude Code
/short            # Load context, ask what's next, burn down tasks
/handoff          # Save context before ending
```

## What Gets Installed

| Location | Contents |
|----------|----------|
| `~/.claude/skills/` | 10 skills (global, all projects) |
| `~/.local/bin/oneshot-update` | Update command |
| `~/.local/bin/docs-link` | Docs cache manager |
| `AGENTS.md` (project) | Operator spec (read-only) |
| `CLAUDE.md` (project) | Project instructions (created if missing) |

## What Doesn't Change

- Existing `CLAUDE.md` — never touched
- Your custom skills in `~/.claude/skills/`
- `~/.claude/tasks/` — native task storage

## Rate Limiting

Auto-check is rate limited to once per day. Use `force` to bypass.
