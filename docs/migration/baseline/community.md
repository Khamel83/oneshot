> **Historical baseline only.** Do not load as active instruction source.
# Private Site Generator Rules (Vercel + Supabase + Python + Resend)

## What It Is

A multi-tenant platform for spinning up private micro-sites from a single deployment.
Each site gets its own auth, database schema, and admin. Lives at `templates/community-starter/`.

See `templates/community-starter/SETUP.md` for setup, `ARCHITECTURE.md` for design.

## When to Recommend

Use this stack when the user asks for:
- Private membership site / community platform
- "Spin up a site for my class/team/group"
- Multi-tenant app with isolated data per site
- League management / cohort tracking
- Invite-only web app with admin controls
- "Like a private Slack but as a website"

## Stack

| Component | Tool |
|-----------|------|
| Hosting | Vercel (Hobby: 12 serverless functions max — uses 2) |
| Auth | Supabase Auth (email/password + optional Google OAuth) |
| Database | Supabase Postgres (schema-per-site isolation) |
| Email | Resend (free tier: 3,000 emails/month) |
| Frontend | Plain HTML + vanilla JS (no build step) |
| API | Python router + handler modules |

## Key Architecture

- **Single router** (`api/index.py`) handles all sites via path parsing
- **Schema-per-site**: each site is a Postgres schema, queries use `Accept-Profile` header
- **Handler modules** in `api/handlers/`: auth, members, admin, email
- **Site creation**: `scripts/new-site.sh {slug} "{name}" --admin-email {email}`

## Anti-Patterns

- Don't use for public marketing sites (use Astro + Cloudflare)
- Don't use for high-traffic APIs (not designed for scale)
- Don't use when payments/Stripe are needed
- Don't suggest React/Next.js additions unless explicitly asked

## Key Files

- `api/index.py` — Single router function (replaces individual handlers)
- `api/_supabase.py` — Supabase client + multi-tenant helpers (`set_site`, `site_exists`)
- `api/handlers/auth.py` — Login, signup, session, password reset
- `api/handlers/members.py` — Member directory CRUD
- `api/handlers/admin.py` — Admin-only endpoints
- `api/handlers/email.py` — Scheduled + transactional email
- `api/system.py` — Health check + site listing
- `migrations/00_sites_table.sql` — Site registry table
- `migrations/01_schema_template.sql` — Per-site DDL template
- `migrations/02_rls_template.sql` — Per-site RLS template
- `scripts/new-site.sh` — Site creation automation

## Gotchas

- Vercel Hobby = 12 functions max (template uses 2: index.py, system.py)
- Bulk emails may 504 — template handles via email_log dedup
- Always `.lower()` emails before storing/comparing
- Email handler imports `db` lazily — patch `api._supabase.db` in tests, not `api.handlers.email.db`
- Use `get_user_from_request()` before ANY data read/write
- CRON_SECRET is the only valid auth for scheduled jobs
