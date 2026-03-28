# Community Starter — Setup Guide

A hardened template for private membership community sites.

**Stack**: Vercel (static HTML + Python functions) + Supabase + Resend

---

## What You Get

- Email/password login (backed by Supabase Auth)
- Member directory with public profiles
- Admin panel with role management
- Scheduled email jobs with 504 false-alarm protection
- Deny-all RLS so direct DB access is blocked
- Auto-populated member rows on signup (via DB trigger)

---

## Prerequisites

- Vercel account (Hobby plan fine — supports up to 12 Python functions)
- Supabase account (free tier fine — handles auth + DB)
- Resend account (free tier: 3,000 emails/month, shared across verified domains)
- Cloudflare account if you want a custom domain (recommended)

---

## Step 1 — Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **Settings → API** and copy:
   - `SUPABASE_URL` (e.g., `https://abcdef.supabase.co`)
   - `SUPABASE_ANON_KEY` (safe for frontend — still protected by RLS)
   - `SUPABASE_SERVICE_ROLE_KEY` (**SECRET** — server-side only, never expose)

3. Run migrations in **SQL Editor**:
   ```
   Run: migrations/01_schema.sql
   Run: migrations/02_rls.sql
   ```

4. Enable **Email/Password** auth:
   - Go to **Authentication → Providers → Email**
   - Enable it, configure confirm email if desired

5. (Optional) Enable **Google OAuth**:
   - Go to **Authentication → Providers → Google**
   - Add your Google OAuth client ID + secret
   - Set redirect URL to: `https://your-domain.com/dashboard`

---

## Step 2 — Resend Setup

1. Create account at [resend.com](https://resend.com)
2. Add and verify your sending domain
3. Create an API key → copy it as `RESEND_API_KEY`
4. Set `EMAIL_FROM` in env vars: `Your App <noreply@yourdomain.com>`

---

## Step 3 — Vercel Setup

1. Import this repo into Vercel
2. Add environment variables (Settings → Environment Variables):

   | Variable | Value | Environment |
   |----------|-------|-------------|
   | `SUPABASE_URL` | Your project URL | All |
   | `SUPABASE_ANON_KEY` | Public anon key | All |
   | `SUPABASE_SERVICE_ROLE_KEY` | Service role key | **Production only** |
   | `RESEND_API_KEY` | Your Resend key | Production |
   | `EMAIL_FROM` | `App <noreply@domain.com>` | Production |
   | `REPLY_TO` | `you@yourdomain.com` | Production |
   | `SITE_URL` | `https://www.yourdomain.com` | Production |
   | `ADMIN_EMAIL` | your admin email | Production |
   | `CRON_SECRET` | Random secret (see below) | Production |

3. Generate `CRON_SECRET`:
   ```bash
   openssl rand -hex 32
   ```

---

## Step 4 — GitHub Secrets

For scheduled jobs to work, add to **GitHub → Settings → Secrets**:
- `SITE_URL` = `https://www.yourdomain.com`
- `CRON_SECRET` = (same value as in Vercel)

---

## Step 5 — Cloudflare (Optional but Recommended)

1. Add your domain to Cloudflare
2. In Vercel → Settings → Domains, add your domain
3. Set Cloudflare DNS records as directed by Vercel
4. Keep **Proxy: enabled** in Cloudflare (orange cloud) for DDoS protection

---

## Step 6 — Deploy

Push to main. Vercel auto-deploys. Done.

---

## Customization Checklist

- [ ] **Branding**: Update `--color-primary` in all HTML files (it's the top CSS variable)
- [ ] **App name**: Search/replace `Your App` in HTML titles and nav
- [ ] **Email templates**: Update `send_welcome_email()` in `api/email.py`
- [ ] **Scheduled job**: Update cron schedule and action in `.github/workflows/scheduled-jobs.yml`
- [ ] **Member fields**: Add columns to `migrations/01_schema.sql` → update `PUBLIC_COLUMNS` / `OWN_COLUMNS` in `api/members.py`

---

## Architecture Decisions

### Why Supabase Auth instead of custom sessions?

Networth Tennis used a custom `session_tokens` table + `verify_session()` lookup. It worked but required:
- Manual token generation
- Manual expiry checking
- DB query on every request

Supabase Auth gives you JWT validation, Google OAuth, password reset emails, and token refresh for free. The API just calls `db().auth.get_user(token)` — one line.

### Why SERVICE_ROLE_KEY instead of anon key on the server?

The anon key is subject to RLS policies. Using the service role key server-side means:
- RLS enforced via your application code (not DB policies)
- No "insufficient permissions" surprises when you add a new table
- Simpler queries (no need to pass user context to every RLS policy)

The tradeoff: if a bug bypasses your auth check, it has full DB access. Mitigation: add RLS deny-all policies (done in `02_rls.sql`) so that even if someone gets the anon key from browser network traffic, they can't query the DB directly.

### Why plain HTML + vanilla JS instead of React/Next.js?

- No build step = no Vercel build minutes consumed
- No `node_modules` to maintain
- Instant deploys
- Easy for non-engineers to read and modify

If you need complex UI interactions, consider adding Alpine.js (CDN, no build).

### Why 60s maxDuration?

Bulk email sends can take 30+ seconds for 30+ members at Resend's 2 req/s rate limit. The 504 false-alarm pattern (function delivers all emails then times out returning the response) is real and happens without this. 60s is the Vercel Hobby plan maximum.

### Why check email_log on 504?

A 504 from Vercel means "your function took too long to respond" — not "your function crashed." By the time the 504 fires, the function may have already sent all emails. Without the email_log check, GitHub Actions would fire a false admin alert.

---

## Vercel Function Limit

Hobby plan: **12 serverless functions max** (files in `api/` with `class handler`).

Current count: 5 (`auth`, `members`, `admin`, `email`, `system`). You have 7 slots.

The CI check in `tests.yml` enforces this automatically.

---

## Common Gotchas (Learned the Hard Way)

1. **Email case sensitivity**: Always `.lower()` emails before storing/comparing.

2. **`date +%d` is zero-padded**: Use `date +%-d` in bash date comparisons — `"01" = "1"` is false.

3. **Greedy bulk loops**: Never `break` on email failure. Collect errors, continue sending.

4. **Column names**: Verify before `.order()` — a wrong column name returns a Supabase error dict, which your ORM may silently convert to `[]`.

5. **Auth on every endpoint**: Use `get_user_from_request()` before ANY data read/write. No exceptions.

6. **Strip sensitive fields**: Never return `password_hash`, internal tokens, or admin flags you didn't intend to expose. Use explicit column selects.

7. **504 ≠ failure**: See "Why check email_log on 504?" above.

8. **CRON_SECRET**: Never check `if '@' in auth` as a bypass. The only valid check is `auth == cron_secret`.
