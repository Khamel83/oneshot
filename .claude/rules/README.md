# ONE_SHOT Progressive Disclosure Rules

## How It Works

Rules are split into:
- **core.md** - Always loaded (~150 lines)
- **khamel-mode.md** - User-specific defaults (~50 lines)
- **web.md** - Web app rules (Astro + Cloudflare + Better Auth + Postgres)
- **cli.md** - CLI rules (Python + Click)
- **service.md** - Service/API rules (Python + systemd)

## Token Savings

| Approach | Tokens |
|----------|--------|
| Old: Full CLAUDE.md | ~2000 |
| New: Core + Project type | ~300 |

**Savings: ~85%**

## Detection

Claude should auto-detect project type from files:

| Detection | Project Type | Rules Loaded |
|-----------|--------------|--------------|
| `astro.config.*` or `wrangler.toml` | Web app | core + khamel-mode + web |
| `setup.py` or `pyproject.toml` | CLI | core + khamel-mode + cli |
| `*.service` systemd file | Service | core + khamel-mode + service |
| No detection | Generic | core + khamel-mode |

## Usage in Projects

In your project's `CLAUDE.md`:

```markdown
# Project Configuration

(Your project-specific stuff here)

---

## ONE_SHOT Rules

Auto-detect project type and load appropriate rules.

If this is a **web app** (Astro + Cloudflare): Use web defaults
If this is a **CLI** (Python + Click): Use CLI defaults
If this is a **service** (Python + systemd): Use service defaults

See ~/.claude/rules/ for full rule definitions.
```
