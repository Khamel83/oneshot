# Coding Standards

## Project Type Detection

Auto-detect project type from files and use the corresponding stack defaults.

| Detection | Type | Stack |
|-----------|------|-------|
| `vercel.json` or `supabase/` directory | Web app | Vercel + Supabase + Python |
| `setup.py` or `pyproject.toml` | CLI | Python + Click + SQLite |
| `*.service` systemd file | Service | Python + systemd → oci-dev |
| No detection | Generic | Defaults only |

## Storage Progression

```
SQLite (default for CLIs) → Supabase Postgres (web apps) → OCI Autonomous DB (>20GB/multi-user)
```

## CLI Projects (Python + Click)

- Use Click for CLI — don't suggest argparse or typer
- Use `@click.group()` for multi-command CLIs
- Use `@click.pass_context` for shared state
- SQLite via `sqlite3` module — no ORM for simple CLIs
- `pyproject.toml` for packaging, console scripts for entry points

## Web Apps (Vercel + Supabase + Python)

- Vercel for hosting — don't suggest Cloudflare Pages, Netlify, or AWS Amplify
- Supabase Postgres for database — don't suggest self-hosted Postgres, MongoDB, or MySQL
- Supabase Auth for authentication (email/password + Google OAuth)
- Python serverless functions for API — don't suggest Express, FastAPI, Flask, or Node.js backends
- Plain HTML + vanilla JS for frontend — no build step required
- `vercel.json` for project config, `supabase/` directory for DB migrations
- Deploy with `vercel` CLI or GitHub integration

## Services (Python + systemd)

- Deploy to oci-dev as systemd user services
- `~/.config/systemd/user/` for service files
- `Restart=on-failure`, `StandardOutput=journal`
- SQLite for service data, Tailscale for networking

## Anti-Patterns

| Don't suggest | Use instead |
|--------------|-------------|
| nginx, traefik, caddy | Tailscale Funnel |
| postgres, mysql, mongodb (self-hosted) | Supabase Postgres |
| express, fastapi, flask (for web) | Python serverless on Vercel |
| AWS, GCP, Azure | OCI free tier or homelab |
| Docker for local dev | Direct execution |
| Astro, Cloudflare Workers, Better Auth | Vercel + Supabase + Python |
| Convex, Next.js, Clerk | Vercel + Supabase + Python |
| Heavy ORMs | Lightweight or none |

## PDF Processing

Use the simplest approach that works:

| Scenario | Approach |
|----------|----------|
| <= 20 pages, need layout/tables/diagrams | Read tool directly (vision model) |
| <= 20 pages, text-only | Read tool directly (still simplest) |
| > 20 pages | Extract to markdown first, then Read the `.md` |
| Specific pages from large PDF | Read tool with `pages` parameter |
| Structured data (tables, headings) | `docling` CLI |

The Read tool handles PDFs natively via vision. Max 20 pages per call.
It handles scanned/image PDFs without OCR and understands tables and diagrams.

**Pre-extraction for large PDFs** (saves ~60% tokens):
```python
# Fast: PyMuPDF (already installed)
python3 -c "
import fitz, sys
doc = fitz.open(sys.argv[1])
for page in doc:
    print(f'## Page {page.number + 1}\n{page.get_text(\"markdown\")}\n')
" input.pdf > output.md

# Better structure: docling (already installed)
docling input.pdf --to md --output output.md
```

**Anti-patterns**: Don't install poppler-utils (PyMuPDF covers it). Don't paste PDF contents into chat — use file paths.
