# Multi-Tenant Platform Research — 2026-03-27

## Question

Are there better approaches, existing tools, or borrowable ideas for a multi-tenant private site generator (Supabase schema-per-tenant + Vercel Python functions)?

## Answer

**No one is doing what we're doing.** Every multi-tenant starter on GitHub uses per-row isolation (`tenant_id` column on every table) + React/Next.js monolith. Our combination of schema-per-tenant isolation + plain HTML/JS + 2 Vercel functions + zero-config site creation is novel.

---

## What Exists

| Project | Isolation | Stack | Stars |
|---------|-----------|-------|-------|
| multi-tenant-starter (Tenlyr) | Per-row RLS | TS + Postgres | Low |
| multi-tenant-starterkit (CoachBinAli) | Per-row RLS | React 19 + Supabase | 460 |
| supabase-tenant-rbac (point-source) | Per-row RLS + PG extension | Supabase | Low |
| Nextacular | Per-row | Next.js SaaS starter | 1359 |

None do schema-per-tenant. None use plain HTML/JS. None automate site provisioning.

## What Makes Ours Different

| Dimension | Existing Tools | Ours |
|-----------|---------------|------|
| Isolation | Per-row (RLS with tenant_id) | Per-schema (Accept-Profile) |
| Frontend | React/Next.js monolith | Plain HTML + vanilla JS |
| Backend | Server-side rendering | Vercel Python functions |
| Provisioning | Manual or paid | One-command automation |
| Cost | Vercel Pro ($20/mo) | Vercel Hobby (free) |
| Functions | 5-12+ | 2 |

---

## Borrowable Ideas (evaluated)

### Adopted: Direct handler member creation (replaces trigger)
- Our original design used a DB trigger on `auth.users` that checked `raw_user_meta_data->>'site'`
- Problem: `raw_user_meta_data` is user-modifiable — a signup could claim any site
- Fix: The router already knows the site slug from the URL path. The signup handler inserts into `{site}.members` directly after creating the auth user. No trigger, no metadata dependency.

### Considered but skipped

| Idea | Why Skipped |
|------|-------------|
| Edge Middleware routing | Would replace api/index.py router, but requires adding TypeScript. Current rewrite approach is simpler and works. |
| Vercel Platforms Starter patterns | Subdomain-based routing. Overkill — path-based routing is simpler. |
| Auto-RLS event trigger | Automatically enables RLS on new tables. Our templates already include RLS, no need. |
| Invitation tokens with expiry | Adds complexity. Our model is "owner shares the login URL" — zero friction. |
| Claims caching for RLS | For high-traffic apps. We have tiny private sites. |
| Storage bucket isolation | We don't use Supabase Storage. Not relevant. |

### Supabase RLS performance tip

Wrap `auth.uid()` in SELECT: `(select auth.uid()) = user_id` — 94-99% perf improvement.
Not needed at our scale but worth knowing.

---

## Conclusion

The architecture is sound. No existing tool does what we're building. The one change worth making is removing the DB trigger in favor of direct handler insertion (security + simplicity).
