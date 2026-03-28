# Private Site Generator — Setup Guide

A multi-tenant platform that lets you spin up unlimited private micro-sites from a single deployment. Each site gets its own auth, database schema, and admin — created with one command.

**Stack**: Vercel (static HTML + Python functions) + Supabase + Resend

---

## What You Get

- One deployment, unlimited private sites at `yourdomain.com/{slug}`
- Email/password login per site (Supabase Auth)
- Member directory with profiles
- Admin panel with role management
- Scheduled email jobs with dedup
- Deny-all RLS so direct DB access is blocked
- Auto-member creation on signup (via DB trigger)
- Schema-per-site data isolation

---

## Prerequisites

- Vercel account (Hobby plan fine)
- Supabase account (free tier fine)
- Resend account (free tier: 3,000 emails/month)
- Cloudflare account if you want a custom domain

---

## Step 1 — Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Copy from **Settings → API**:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`

3. Run in **SQL Editor**:
   ```
   Run: migrations/00_sites_table.sql
   ```

4. Enable **Email/Password** auth:
   - **Authentication → Providers → Email** → Enable

5. (Optional) Enable **Google OAuth**:
   - **Authentication → Providers → Google** → Add credentials

---

## Step 2 — Resend Setup

1. Create account at [resend.com](https://resend.com)
2. Add and verify your sending domain
3. Create an API key → `RESEND_API_KEY`
4. Set `EMAIL_FROM`: `Your App <noreply@yourdomain.com>`

---

## Step 3 — Vercel Setup

1. Import repo into Vercel
2. Add environment variables:

   | Variable | Where |
   |----------|-------|
   | `SUPABASE_URL` | All |
   | `SUPABASE_ANON_KEY` | All |
   | `SUPABASE_SERVICE_ROLE_KEY` | Production only |
   | `RESEND_API_KEY` | Production |
   | `EMAIL_FROM` | Production |
   | `REPLY_TO` | Production |
   | `SITE_URL` | Production |
   | `ADMIN_EMAIL` | Production |
   | `CRON_SECRET` | Production (generate with `openssl rand -hex 32`) |

---

## Step 4 — Create Your First Site

```bash
./scripts/new-site.sh my-class "Mrs. Smith's 2nd Grade" --admin-email me@example.com
```

This creates:
- A Supabase schema (`my-class`)
- Tables: `members`, `email_log`
- RLS policies (deny-all anon, read auth, update own)
- Auto-member trigger (signup → member row)
- Site registration in `public.sites`
- Admin user via Supabase Auth Admin API

Output:
```
=== Site Created ===
  URL:      https://yourdomain.com/my-class
  Admin:    me@example.com
  Password: <generated>
  Login:    https://yourdomain.com/my-class/login
```

---

## Step 5 — GitHub Secrets (for scheduled emails)

Add to **GitHub → Settings → Secrets**:
- `SITE_URL` = your production URL
- `CRON_SECRET` = same value as Vercel

---

## Step 6 — Cloudflare (Optional)

1. Add domain to Cloudflare
2. Vercel → Settings → Domains → Add domain
3. Set DNS records per Vercel instructions
4. Keep Proxy enabled (orange cloud)

---

## How It Works

### Routing

```
yourdomain.com/                  → root page (site list)
yourdomain.com/{slug}/           → site homepage
yourdomain.com/{slug}/login      → login
yourdomain.com/{slug}/dashboard  → member view
yourdomain.com/{slug}/admin      → owner panel
yourdomain.com/{slug}/api/*      → API (routed to single function)
```

### Multi-Tenant Database

Each site is a Postgres schema. Queries use the `Accept-Profile` header to target the right schema — no table name changes needed.

```
public.sites          → site registry (slug, name, config)
my-class.members      → that site's members
my-class.email_log    → that site's emails
other-site.members    → completely isolated
```

### API Router

One Vercel function (`api/index.py`) handles all sites. It parses the path, looks up the site, sets the schema header, and dispatches to handler modules in `api/handlers/`.

---

## Customization

- **Branding**: Update `--color-primary` in HTML files
- **App name**: Search/replace in HTML titles and nav
- **Email templates**: Update `send_welcome_email()` in `api/handlers/email.py`
- **Scheduled job**: Update cron schedule in `.github/workflows/scheduled-jobs.yml`
- **Member fields**: Add columns to `migrations/01_schema_template.sql`, update column lists in `api/handlers/members.py`

---

## Common Gotchas

1. **Email case sensitivity**: Always `.lower()` emails before storing/comparing.
2. **504 != failure**: Bulk emails may timeout, but emails are still sent. The template deduplicates via `email_log`.
3. **Auth on every endpoint**: Use `get_user_from_request()` before ANY data read/write.
4. **CRON_SECRET**: Never check `if '@' in auth` as a bypass.
5. **Vercel Hobby plan**: 12 serverless functions max. This template uses 2 (`index.py`, `system.py`).
