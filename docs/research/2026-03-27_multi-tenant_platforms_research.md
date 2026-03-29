# Multi-Tenant Platform Research Report
**Date:** 2026-03-27
**Goal:** Find existing tools/kits for spinning up private micro-sites with auth and data, zero setup

---

## Summary

Found 3 relevant approaches, but **nothing that matches our exact vision** of "Supabase schema-per-tenant + Vercel Python functions + plain HTML/JS." Most existing tools are full-stack Next.js/React frameworks with per-row tenant isolation, not per-schema isolation.

---

## Key Findings

### 1. **multi-tenant-starter** (Tenlyr) - Postgres RLS Approach
**Stack:** TypeScript + Express + Postgres RLS + In-memory demo
**Stars:** Active (updated Mar 2026)
**URL:** https://github.com/Tenlyr/multi-tenant-starter

**What it does:**
- Enforces tenant isolation at the **data layer**, not via query filters
- Tenant context resolved once at request boundary (URL or header)
- Route handlers are tenant-agnostic - never write `WHERE tenant_id = X`
- Demo uses in-memory store; production uses Postgres + RLS with `SET app.tenant = $1`

**Key insight:**
> "Tenant context is resolved once, at the boundary — the rest of your code never has to think about it."

**Borrowable ideas:**
- ✅ Tenant resolution middleware (extract from subdomain/path)
- ✅ Request-bound tenant context (no passing tenant_id through every function)
- ✅ Isolation by construction (data layer enforces, not developer discipline)

**Different from us:**
- ❌ Row-level security (same schema, `WHERE tenant_id` in RLS policies)
- ❌ Full Express app (not micro-sites)
- ❌ Commercial product (Tenlyr) - not open source infrastructure

**RLS pattern they mention:**
```sql
-- Their suggested production upgrade
SET app.tenant = 'acme';
-- RLS policies use:
-- USING (tenant_id = current_setting('app.tenant', true)::uuid)
```

---

### 2. **multi-tenant-starterkit** (CoachBinAli) - React + Supabase
**Stack:** React 19 + Vite + Supabase + TanStack Query + shadcn/ui
**Stars:** Active (updated Mar 2026)
**URL:** https://github.com/CoachBinAli/multi-tenant-starterkit

**What it does:**
- Organization-based multi-tenancy with `organization_id` on every table
- Row-Level Security policies with `EXISTS` checks against `organization_members`
- Role-based access control (Owner/Admin/Member)
- Full-featured: file uploads, PDF generation, activity logs, notifications

**Schema pattern:**
```sql
-- Every table has organization_id
CREATE TABLE public.students (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES public.organizations(id),
  -- fields
);

-- RLS policy
CREATE POLICY "Users can view students in their orgs"
  ON public.students FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.organization_members
      WHERE organization_members.organization_id = students.organization_id
      AND organization_members.user_id = auth.uid()
    )
  );
```

**Borrowable ideas:**
- ✅ `organization_members` junction table with roles
- ✅ Invitation flow with tokens + expiration
- ✅ Activity logging table for audit trail
- ✅ Organization switcher UI pattern
- ✅ Storage bucket isolation: `(storage.foldername(name))[1]` extracts org_id from path

**Different from us:**
- ❌ Per-row isolation (shared schema with `organization_id` FKs)
- ❌ Heavy React frontend (not plain HTML/JS micro-sites)
- ❌ Single monolithic app (not tenant-spinnable micro-sites)

---

### 3. **supabase-tenant-rbac** (point-source) - PostgreSQL Extension
**Stack:** PostgreSQL extension for Supabase + SQL API
**Stars:** 460 (most popular)
**URL:** https://github.com/point-source/supabase-tenant-rbac

**What it does:**
- Multi-tenant RBAC as a PostgreSQL extension
- Groups (tenants/orgs) with members assigned roles
- Permissions vocabulary (registry) - prevents typos in permission strings
- Privilege escalation prevention via `grantable_roles[]`
- Claims caching for fast RLS policy checks
- Freshness guarantees - role changes take effect immediately, no JWT expiry wait

**Installation:**
```bash
curl -sL https://raw.githubusercontent.com/point-source/supabase-tenant-rbac/main/tools/install.sh | bash
supabase migration up
```

**RLS helpers:**
```sql
-- Check membership
CREATE POLICY "members can read" ON public.documents
  FOR SELECT TO authenticated
  USING (rbac.is_member(group_id));

-- Check permissions
CREATE POLICY "writers can insert" ON public.documents
  FOR INSERT TO authenticated
  WITH CHECK (rbac.has_permission(group_id, 'data.write'));

-- Check roles
CREATE POLICY "admins only" ON public.settings
  FOR UPDATE TO authenticated
  USING (rbac.has_role(group_id, 'admin'));
```

**Borrowable ideas:**
- ✅ **Claims caching pattern** - `user_claims` table with JSONB per group
- ✅ **Permission registry** - prevents typos, enables documentation
- ✅ **Escalation prevention** - `grantable_roles` array on each role
- ✅ **Group-based isolation** - distinct from organization-based (more flexible)
- ✅ **Immediate freshness** - triggers update claims on role change

**Different from us:**
- ❌ Still uses row-level security (groups/roles are tables, not schemas)
- ❌ Requires extension installation (not portable to other Postgres hosts)
- ❌ Heavy complexity for simple use cases

**Key architectural insight:**
> "Group Administrator is not a separate database role — it is any authenticated user who holds a role that grants sufficient `grantable_roles`"

This is **permission-based admin**, not role-based. Anyone with `grantable_roles: ['*']` becomes a group admin.

---

### 4. **Nextacular** - Next.js SaaS Starter
**Stack:** Next.js + Tailwind + Prisma + Stripe
**Stars:** 1359 (most popular overall)
**URL:** https://github.com/nextacular/nextacular

**What it does:**
- Full-stack multi-tenant SaaS boilerplate
- Focus on developer productivity for SaaS founders
- Stripe billing, shadcn/ui, Prisma ORM

**Different from us:**
- ❌ Traditional Next.js monolith (not micro-sites)
- ❌ Prisma ORM (we want raw SQL + RLS)
- ❌ Row-level tenant isolation

---

### 5. **Other GitHub Finds** (Less Relevant)

| Repo | Stack | Relevance |
|------|-------|-----------|
| `bvuz/Django-Multi-Tenant-SaaS-Starter-Template` | Django + PostgreSQL schema isolation | ⭐⭐ Schema-per-tenant pattern! But Django, not useful for us |
| `juliusjoska/nextjs-saas-starter` | Next.js 16 + Supabase + shadcn/ui | Standard Next.js SaaS starter |
| `nestjs-saas-starter` | NestJS + multi-tenancy | Backend-focused, not micro-sites |
| `Serverless-SaaS-Template` | AWS serverless (Cognito + Lambda + DynamoDB) | Wrong stack (AWS vs Supabase + Vercel) |
| `ahliweb/awcms` | React + Supabase multi-tenant CMS | CMS-focused, not generic micro-sites |
| `next-multitenant-2024` (tutorial) | Next.js 14 + Supabase + Cloudflare | ⭐ Cloudflare Workers + Supabase combo! Worth deep dive |

---

## Architectural Patterns Found

### Pattern 1: Per-Row Isolation (Most Common)
```sql
-- Every table has tenant/org_id
CREATE TABLE things (
  id uuid,
  organization_id uuid REFERENCES organizations(id)
);

-- RLS policy checks membership
CREATE POLICY "tenant isolation" ON things
  USING (
    EXISTS (
      SELECT 1 FROM organization_members
      WHERE organization_members.organization_id = things.organization_id
      AND organization_members.user_id = auth.uid()
    )
  );
```

**Pros:**
- Simple schema
- Easy to query across tenants (for admin analytics)
- Well-documented pattern

**Cons:**
- RLS policies on every table
- `organization_id` FK on every row
- Risk of missing policy on new table
- Can't easily backup/export single tenant

### Pattern 2: Schema-Per-Tenant (Django example, not Supabase)
```sql
-- Each tenant gets a schema
CREATE SCHEMA tenant_acme;
CREATE SCHEMA tenant_globex;

-- Each schema has identical tables
CREATE TABLE tenant_acme.things (...);
CREATE TABLE tenant_globex.things (...);

-- Switch via search_path
SET search_path = tenant_acme;
```

**Pros:**
- Complete data isolation
- Easy backup/restore per tenant
- Can `DROP SCHEMA tenant_x CASCADE` to offboard
- No RLS policies needed

**Cons:**
- Migrations must run N times (once per tenant)
- Can't query across tenants easily
- Schema management complexity

**This is OUR approach!** But no one does this with Supabase + Vercel yet.

### Pattern 3: PostgreSQL Extension (supabase-tenant-rbac)
```sql
-- Install extension
CREATE EXTENSION supabase_rbac;

-- Use RLS helpers
CREATE POLICY "members can read" ON docs
  USING (rbac.is_member(group_id));
```

**Pros:**
- Reusable patterns
- Escalation prevention built-in
- Claims caching for performance

**Cons:**
- Extension dependency (portability)
- Still uses row-level security under the hood
- Learning curve for custom SQL functions

---

## Key Ideas to Borrow

### From Tenlyr (multi-tenant-starter):
1. **Tenant resolution middleware** - Extract tenant from subdomain/path once at boundary
2. **Request-bound tenant context** - Store in `req.tenant`, not passed through every function
3. **Isolation by construction** - Data layer enforces, not developer discipline

### From CoachBinAli (multi-tenant-starterkit):
1. **Organization members junction table** - `organization_members(org_id, user_id, role)`
2. **Invitation flow** - Tokens with 7-day expiration, accept endpoint
3. **Activity logging** - Audit trail table with `organization_id`
4. **Storage isolation** - Extract org_id from folder path: `(storage.foldername(name))[1]`
5. **Organization switcher UI** - Dropdown for users with multiple orgs

### From point-source (supabase-tenant-rbac):
1. **Claims caching** - `user_claims` table with JSONB per group for fast RLS
2. **Permission registry** - Centralized vocabulary prevents typos
3. **Escalation prevention** - `grantable_roles` array on each role
4. **Immediate freshness** - Triggers update claims on role change (no JWT expiry wait)
5. **Group-based vs org-based** - Groups are more flexible than organizations

### From Django schema-per-tenant:
1. **Schema provisioning** - `CREATE SCHEMA tenant_x` on signup
2. **Schema switching** - `SET search_path = tenant_x` before queries
3. **Migration runner** - Apply migrations to all tenant schemas
4. **Tenant drop** - `DROP SCHEMA tenant_x CASCADE` for offboarding

---

## What Makes Our Approach Different

| Dimension | Existing Tools | Our Approach |
|-----------|---------------|--------------|
| **Isolation** | Per-row (RLS with `organization_id`) | Per-schema (`tenant_x.things`) |
| **Stack** | Next.js/React monoliths | Plain HTML/JS micro-sites |
| **Backend** | Server-side rendering (Next.js) | Vercel Python functions |
| **Provisioning** | Manual or paid services | Automated schema creation |
| **Data export** | CSV export per tenant | `pg_dump -n tenant_x` (full SQL) |
| **Cost** | Vercel Pro plan ($20/mo) | Vercel Hobby (free tier) |
| **Complexity** | Full-stack frameworks | Zero-build static sites |

**Unique value:** Spin up private micro-sites with zero config. Each tenant gets:
- Isolated Supabase schema
- Vercel-deployed static site
- Prebuilt auth, data, email
- Plain HTML/JS (no build step)

---

## Open Questions

1. **Migration management**: How to apply schema changes to N tenant schemas?
   - Django approach: `migrate_schemas` command
   - Our idea: Tenant migration table + background worker

2. **Subdomain vs path**: How do users access their micro-site?
   - `acme.yourplatform.com` (subdomain)
   - `yourplatform.com/acme` (path)
   - Custom domains (CNAME)

3. **Tenant limits**: How many schemas before Supabase complains?
   - Need to test: 100? 1000? 10000?
   - Alternative: Schema pooling with logical isolation

4. **Storage isolation**: How to handle Supabase Storage per tenant?
   - Separate buckets per tenant? (expensive)
   - Folder isolation with RLS? (like CoachBinali)
   - External storage (Cloudflare R2)?

---

## Next Steps

1. **Prototype schema-per-tenant provisioning**:
   - Sign-up flow that creates Supabase schema
   - Migration runner for all tenant schemas
   - Tenant drop/offboarding flow

2. **Research migration strategies**:
   - Django's `django-tenants` implementation
   - How Fly.io or Railway handle per-customer databases

3. **Define our RBAC layer**:
   - Use supabase-tenant-rbac patterns? Or simpler?
   - Need roles (Owner/Admin/Member) or just permissions?

4. **Validate stack choice**:
   - Test Vercel Python function limits (Hobby plan: 10s execution)
   - Test Supabase schema limits
   - Confirm subdomain routing works on Vercel

---

## Sources

- [Tenlyr multi-tenant-starter](https://github.com/Tenlyr/multi-tenant-starter)
- [CoachBinAli multi-tenant-starterkit](https://github.com/CoachBinAli/multi-tenant-starterkit)
- [point-source supabase-tenant-rbac](https://github.com/point-source/supabase-tenant-rbac)
- [Nextacular](https://github.com/nextacular/nextacular)
- [Django Multi-Tenant SaaS Starter](https://github.com/bvuz/Django-Multi-Tenant-SaaS-Starter-Template)
