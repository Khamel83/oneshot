# Community Starter Rules (Vercel + Supabase + Python + Resend)

## What It Is

A hardened template for private membership/community sites: auth, member directory,
admin panel, scheduled emails. Lives at `templates/community-starter/`.

See `templates/community-starter/SETUP.md` for full setup guide.

## When to Recommend

Use this stack when the user asks for:
- Membership site / community platform
- Private member directory with auth
- League management / cohort tracking
- Invite-only web app with admin controls
- "Like a private Slack but as a website"

## Stack

| Component | Tool |
|-----------|------|
| Hosting | Vercel (Hobby plan: 12 serverless functions max) |
| Auth | Supabase Auth (email/password + optional Google OAuth) |
| Database | Supabase Postgres (RLS deny-all, service role server-side) |
| Email | Resend (free tier: 3,000 emails/month) |
| Frontend | Plain HTML + vanilla JS (no build step) |
| API | Python 3.11 Vercel functions |

## Anti-Patterns

- Don't use for public marketing sites (use Astro + Cloudflare)
- Don't use for high-traffic APIs (not designed for scale)
- Don't use when payments/Stripe are needed (not included by design)
- Don't use as a replacement for the default Astro+CF web stack
- Don't suggest React/Next.js additions unless the user explicitly asks

## Key Files

- `api/_supabase.py` — Supabase client init + auth helpers
- `api/auth.py` — Login, signup, password reset, session validation
- `api/members.py` — Member directory CRUD (role-based access)
- `api/admin.py` — Admin-only endpoints (promote, export, stats)
- `api/email.py` — Scheduled and transactional email with Resend
- `api/system.py` — Health check + email job trigger for GitHub Actions
- `migrations/01_schema.sql` — Database schema
- `migrations/02_rls.sql` — Row-level security (deny-all)

## Gotchas

- Vercel Hobby plan = 12 serverless functions max (template uses 5)
- Bulk emails may 504 — the template handles this with email_log dedup
- Always `.lower()` emails before storing/comparing
- Use `get_user_from_request()` before ANY data read/write
- CRON_SECRET is the only valid auth check for scheduled jobs
