# Architecture — Web App Scaffold

## Overview

One Vercel deployment serves unlimited sites at `domain/{slug}`. Each site gets isolated data (Postgres schema), auth, and management — created with one command.

## Routing

```
domain.com/                  → root (site list)
domain.com/{slug}/           → site homepage
domain.com/{slug}/login      → login page
domain.com/{slug}/dashboard  → member view
domain.com/{slug}/admin      → admin panel
domain.com/{slug}/api/*      → API (single router function)
```

Vercel rewrites handle path-based routing:

```json
{ "source": "/:site/api/(.*)", "destination": "/api/index" },
{ "source": "/:site/login", "destination": "/login.html" },
{ "source": "/:site/dashboard", "destination": "/dashboard.html" },
{ "source": "/:site/admin", "destination": "/admin.html" },
{ "source": "/:site", "destination": "/index.html" }
```

## API

### Router (`api/index.py`)

Single Vercel function replaces 5 individual handlers. Parses `/{site}/api/{handler}` from the path:

1. Extract `{site}` slug from path
2. Check `public.sites` table — 404 if not found
3. Call `set_site(slug)` to set `Accept-Profile` header on Supabase client
4. Dispatch to handler module in `api/handlers/`

### Handler Modules (`api/handlers/`)

| Module | Endpoints | Auth |
|--------|-----------|------|
| `auth.py` | login, signup, session, reset_password | Public (login/signup) + token (session) |
| `members.py` | me, view, list, update_profile | Token required |
| `admin.py` | set_admin, delete_member | Admin only |
| `email.py` | send_digest, send_welcome, check_recent_send | CRON_SECRET (server-to-server) |

### System (`api/system.py`)

Separate Vercel function (not routed through `index.py`). Health check + bug report + site listing. No site context needed.

## Database

### Schema-per-Tenant

Each site is a Postgres schema. The `Accept-Profile` header switches schemas per request.

```
public.sites              → site registry
{slug}.members            → user profiles
{slug}.email_log          → sent email audit log
(no trigger — signup handler inserts directly)
```

### Site Creation (`scripts/new-site.sh`)

1. Validate slug (lowercase, alphanumeric + hyphens, 3-30 chars)
2. Check site doesn't exist in `public.sites`
3. `CREATE SCHEMA IF NOT EXISTS {slug}`
4. Create `members` + `email_log` tables
5. Create RLS policies (deny-all anon, read auth, update own)
6. Member creation handled by signup handler (no trigger needed)
7. Register in `public.sites`
8. Create admin user via Supabase Auth Admin API

### Isolation

- Each schema has its own RLS policies
- The signup handler inserts into `{site}.members` directly using the Accept-Profile header set by the router
- `Accept-Profile` header limits all queries to one schema
- Service role key bypasses RLS server-side (application handles auth checks)

## Frontend

Plain HTML + vanilla JS. No build step.

- `public/js/auth.js` — Multi-tenant helpers: `getSite()`, `api(path)`, `page(path)`
- Storage keys are site-scoped: `app_token_{site}`, `app_member_{site}`
- All HTML files extract site slug from `window.location.pathname`

## Migrations

| File | Purpose |
|------|---------|
| `00_sites_table.sql` | `public.sites` table (site registry) |
| `01_schema_template.sql` | Template DDL with `{{SLUG}}` placeholder |
| `02_rls_template.sql` | Template RLS policies with `{{SLUG}}` placeholder |

`01_schema_template.sql` and `02_rls_template.sql` are not run directly — `new-site.sh` replaces `{{SLUG}}` and executes via Supabase API or CLI.

## Function Count

Vercel Hobby plan: 12 max. This template uses **2**:
1. `api/index.py` — router (handles all site API requests)
2. `api/system.py` — health check, bug report, site listing
