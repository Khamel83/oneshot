# Community Starter Alternatives Analysis

Research of open-source repos solving similar problems to our community starter template
(private membership site with auth, member directory, email, admin panel).

**Our stack**: Vercel (static HTML + Python serverless) + Supabase + Resend + vanilla JS

---

## Summary Table

| Repo | Stars | Updated | Stack | Auth | Admin | Email | Testing |
|------|-------|---------|-------|------|-------|-------|---------|
| nextjs/saas-starter | 15.5k | 2026-03 | Next.js + Drizzle + Postgres + Stripe | JWT cookies | Basic RBAC | None | None |
| shadcn-ui/taxonomy | 19.2k | 2026-03 | Next.js + Prisma + PlanetScale + Stripe | NextAuth.js | None | None | None |
| ixartz/SaaS-Boilerplate | 6.9k | 2026-03 | Next.js + Drizzle + Clerk + PGlite | Clerk (MFA, passkeys, social, impersonation) | RBAC + user impersonation | None (Max version adds React Email) | Vitest + Playwright + Storybook + Percy visual |
| steven-tey/precedent | 5.1k | 2026-03 | Next.js + Clerk + Vercel | Clerk (full suite) | None | None | None |
| vercel/nextjs-subscription-payments | 7.7k | 2026-03 (sunset) | Next.js + Supabase + Stripe | Supabase Auth (GitHub OAuth) | None | None | None |
| mickasmt/next-saas-stripe-starter | 3.0k | 2026-03 | Next.js + Prisma + Neon + Auth.js v5 | Auth.js v5 (social providers) | Admin panel (orders, user roles) | Resend + React Email + magic links | None |
| makerkit/nextjs-saas-starter-kit-lite | 408 | 2026-03 | Next.js + Supabase + Tailwind + Turborepo | Supabase Auth | Lite: none (Full: super admin panel) | Lite: none (Full: Nodemailer/Resend/React Email) | Playwright (basic) |
| vercel/next.js examples/with-supabase | ~140k (monorepo) | 2026-03 | Next.js + Supabase + shadcn/ui | Supabase Auth (email/password) | None | None | None |

---

## Detailed Analysis

### nextjs/saas-starter
- **Stars**: 15,546 | **Last commit**: 2026-03-27 | **License**: MIT
- **URL**: https://github.com/nextjs/saas-starter
- **Stack**: Next.js (App Router) + Drizzle ORM + Postgres + Stripe + shadcn/ui + Zod
- **Auth**: Email/password with JWT cookies. Custom auth implementation (not a third-party provider). Global middleware for route protection, local middleware for Server Actions.
- **Email**: None (no email integration)
- **Admin**: Basic RBAC with Owner and Member roles. Activity logging system for user events. Dashboard with CRUD on users/teams. No dedicated admin panel UI.
- **Testing**: None
- **Key features we don't have**:
  - Stripe Checkout + Customer Portal (subscription management)
  - Marketing landing page with animated terminal
  - Pricing page connected to Stripe
  - Activity logging/audit trail
  - Zod schema validation on all inputs
  - `pnpm db:setup` one-command setup script
  - Seed data with default test user
- **Notable**: This is the **official replacement** for `vercel/nextjs-subscription-payments`. It is intentionally minimal and positioned as a learning resource, not production-ready. No email at all. No i18n. No team management beyond Owner/Member. Strong separation of concerns with middleware layers. The Drizzle ORM integration is clean and well-structured.

---

### shadcn-ui/taxonomy
- **Stars**: 19,176 | **Last commit**: 2026-03-27 | **License**: MIT
- **URL**: https://github.com/shadcn-ui/taxonomy
- **Stack**: Next.js 13 (App Router) + Prisma ORM + PlanetScale (MySQL) + Stripe + Radix UI + Tailwind CSS + MDX + Contentlayer + Zod
- **Auth**: NextAuth.js (GitHub OAuth primary, email noted as alternative)
- **Email**: None
- **Admin**: None (no admin panel, no RBAC)
- **Testing**: None
- **Key features we don't have**:
  - Documentation site with MDX + Contentlayer
  - Blog system
  - Stripe subscription management
  - Marketing pages (pricing, features, etc.)
  - Dark mode
  - Open Graph image generation (`@vercel/og`)
- **Notable**: **Explicitly not a starter template** -- it is an experiment by shadcn. Uses PlanetScale (MySQL), not Postgres, which is increasingly niche. Last meaningful feature work was around Next.js 13 betas. Known issues with OG images in catch-all routes. Good reference for how to structure a Next.js app with MDX content, but not suitable to fork as a production base. The README literally says "This is not a starter template."

---

### ixartz/SaaS-Boilerplate
- **Stars**: 6,943 | **Last commit**: 2026-03-27 | **License**: MIT
- **URL**: https://github.com/ixartz/SaaS-Boilerplate
- **Stack**: Next.js + Drizzle ORM + Clerk Auth + Tailwind CSS + shadcn/ui + T3 Env + React Hook Form + Pino.js logging
- **Auth**: Clerk (full suite): email/password, magic links, MFA, social auth (Google, Facebook, Twitter, GitHub, Apple), passkeys, user impersonation. Organization/team support built in.
- **Email**: Free version: None. Pro/Max versions add React Email with transactional emails.
- **Admin**: RBAC with roles and permissions. User impersonation (admin can act as any user). Team/organization management with member invites. No dedicated admin dashboard UI in free version.
- **Testing**: Vitest + React Testing Library (unit), Playwright (E2E/integration), Storybook (UI), Percy (visual regression), GitHub Actions CI. Codecov for coverage. Checkly for monitoring-as-code.
- **Key features we don't have**:
  - Multi-tenancy with team/org support and member invites
  - i18n via next-intl + Crowdin integration
  - Sentry error monitoring with Spotlight for dev
  - Pino.js logging + Better Stack log management
  - Storybook for component development
  - User impersonation for admin debugging
  - Semantic release + automatic changelog
  - Bundle analyzer
  - Dark mode (Pro version)
  - Stripe payments (Pro version)
  - Drizzle Studio for DB exploration
- **Notable**: Most feature-rich free boilerplate by far. Has a three-tier pricing model (Free/Pro/Max) where the free version is genuinely usable but the best features are paywalled. The Clerk dependency is a significant consideration -- Clerk is a third-party service with its own pricing at scale (free up to 10k MAU). Heavy dependency tree. The monorepo structure adds complexity. Dependencies updated monthly. Has a `FIXME:` convention for customization points. PGlite for offline/local dev DB is a nice touch. This is a SaaS template, not a community/membership template -- no member directory concept.

---

### steven-tey/precedent
- **Stars**: 5,096 | **Last commit**: 2026-03-27 | **License**: MIT
- **URL**: https://github.com/steven-tey/precedent
- **Stack**: Next.js + Clerk + Vercel + Tailwind CSS + Radix UI + Framer Motion + Lucide icons
- **Auth**: Clerk (full managed auth with drop-in React components)
- **Email**: None
- **Admin**: None
- **Testing**: None
- **Key features we don't have**:
  - Framer Motion animations
  - Custom hooks (useIntersectionObserver, useLocalStorage, useScroll)
  - Open Graph image generation at edge
  - Vercel Analytics integration
- **Notable**: This is NOT a SaaS starter or community template. It is an opinionated collection of components, hooks, and utilities. No database, no API routes, no admin panel, no email. It is a UI/component starting point only. The Clerk dependency means you are locked into their auth service. Useful as a reference for clean component architecture and hooks patterns, but fundamentally different from our template's purpose.

---

### vercel/nextjs-subscription-payments (SUNSET)
- **Stars**: 7,712 | **Last commit**: 2026-03-23 | **License**: MIT
- **URL**: https://github.com/vercel/nextjs-subscription-payments
- **Stack**: Next.js (Pages Router) + Supabase (Auth + Postgres) + Stripe
- **Auth**: Supabase Auth with GitHub OAuth. JWT-based sessions via Supabase middleware.
- **Email**: None (password reset emails handled by Supabase Auth built-in)
- **Admin**: None. No role management, no admin panel.
- **Testing**: None
- **Key features we don't have**:
  - Stripe Checkout integration with automatic price syncing
  - Stripe Customer Portal for subscription management
  - Stripe webhook handling for subscription lifecycle
  - Vercel + Supabase one-click deploy integration
  - Stripe fixtures file for bootstrapping test products/prices
- **Notable**: **This repo is officially sunset**. The README warns it has been replaced by `nextjs/saas-starter`. Uses the older Pages Router, not App Router. The architecture diagram shows a clean webhook pattern that is worth studying. The Stripe + Supabase integration pattern (products/prices stored in Postgres, synced via webhooks) is well-designed and could be adapted. However, do not use this as a starting point -- it will not receive updates.

---

### mickasmt/next-saas-stripe-starter
- **Stars**: 2,969 | **Last commit**: 2026-03-27 | **License**: MIT
- **URL**: https://github.com/mickasmt/next-saas-stripe-starter
- **Stack**: Next.js 14 + Prisma ORM + Neon (serverless Postgres) + Auth.js v5 + Resend + React Email + shadcn/ui + Stripe + Framer Motion + Contentlayer + Server Actions
- **Auth**: Auth.js v5 with multiple social providers (Google, Twitter, GitHub, etc.)
- **Email**: **Resend + React Email** with magic link authentication emails. Email templates in `emails/` directory. Contentlayer for documentation pages.
- **Admin**: **Full admin panel** with admin layout, orders management page, and role-based access. Protected routes for admin. User role system.
- **Testing**: None (no test files found)
- **Key features we don't have**:
  - Admin panel with orders page
  - React Email for transactional emails (rich HTML email templates)
  - Magic link authentication via email
  - Contentlayer for documentation site
  - Framer Motion animations
  - Neon serverless Postgres (auto-scaling)
  - Server Actions (Next.js 14 pattern)
  - `npm-check-updates` for dependency management
  - One-click Vercel deploy
- **Notable**: **Closest functional match to our template.** Has the same trifecta we target: auth + admin panel + email (Resend). However, it is significantly more complex: Next.js build step, Prisma ORM, Contentlayer for docs, Stripe for payments. No test coverage at all. The Neon database dependency adds another service to manage. Uses Server Actions which couples frontend and backend. The admin panel is basic (orders view, user roles) but functional. Good reference for how to structure a Resend + React Email integration. Our Python approach is simpler and has no build step.

---

### makerkit/nextjs-saas-starter-kit-lite
- **Stars**: 408 | **Last commit**: 2026-03-27 | **License**: MIT
- **URL**: https://github.com/makerkit/nextjs-saas-starter-kit-lite
- **Stack**: Next.js 15 + Supabase + TailwindCSS v4 + Shadcn UI + Turborepo (monorepo) + i18next + React Query + Zod
- **Auth**: Supabase Auth (email/password + social providers)
- **Email**: Lite version: None. Full version: Nodemailer, Resend, or other providers with React Email templates.
- **Admin**: Lite version: None. Full version: Super Admin panel.
- **Testing**: Playwright (basic setup only in lite version). Full version has comprehensive test suite.
- **Key features we don't have**:
  - Turborepo monorepo structure (apps/web + packages/ui + packages/features)
  - i18n with both client and server-side translations
  - React Query for data fetching/caching
  - Marketing pages with responsive design
  - Protected routes
  - User profile and settings pages
- **Notable**: This is the "lite" (free) version of a commercial SaaS starter kit. The lite version is intentionally stripped down -- it is primarily a evaluation tool for the paid version ($299+). The monorepo structure (Turborepo) adds significant complexity that is unnecessary for a community site. Supabase local dev requires Docker. No admin panel, no email, no billing in the lite version. The paid full version includes all features but is not open source. Good reference for clean monorepo architecture and i18n patterns, but the lite version is too bare-bones to be useful as a starting point.

---

### vercel/next.js examples/with-supabase
- **Stars**: N/A (example within next.js monorepo, 138k+ stars) | **Last commit**: 2026-03-28 | **License**: MIT
- **URL**: https://github.com/vercel/next.js/tree/canary/examples/with-supabase
- **Stack**: Next.js (App Router) + Supabase (Auth + Postgres) + shadcn/ui + Tailwind CSS + next-themes
- **Auth**: Supabase Auth via `@supabase/ssr` package (cookie-based sessions). Password-based auth UI from Supabase UI Library. Works across all Next.js rendering contexts (client, server, route handlers, middleware, server actions).
- **Email**: None (Supabase Auth handles password reset emails natively)
- **Admin**: None
- **Testing**: None
- **Key features we don't have**:
  - `@supabase/ssr` package for seamless cookie-based auth across all rendering contexts
  - next-themes for dark mode
  - shadcn/ui pre-configured with multiple style options
  - One-click deploy via Vercel + Supabase integration (env vars auto-assigned)
  - Demo site: https://demo-nextjs-with-supabase.vercel.app
- **Notable**: This is the **official Vercel + Supabase starter**. It is minimal by design -- auth + Supabase + shadcn, nothing else. The `@supabase/ssr` integration pattern is the reference implementation for how to do cookie-based Supabase auth in Next.js. Good as a starting point if you want to add features incrementally, but you would need to build admin panel, member directory, and email integration from scratch. No admin features, no email, no member management. The simplest of all repos reviewed, but also the most authoritative for the Supabase + Next.js integration pattern.

---

## Key Takeaways

### What makes our template different

Our template fills a niche that none of these repos address well:

1. **No build step**: Plain HTML + vanilla JS + Python serverless. Every other repo requires a Next.js/React build pipeline.
2. **Python backend**: All alternatives use TypeScript/Node.js. Our Python functions are simpler and don't need npm/node.
3. **12 function limit awareness**: We explicitly track and CI-enforce the Vercel Hobby plan limit.
4. **504 false-alarm handling**: We've solved the real-world problem of Vercel serverless functions timing out during bulk email sends.
5. **Deny-all RLS**: Defense-in-depth approach where RLS blocks direct DB access even if anon key leaks.
6. **DB trigger for member rows**: Auto-populated member profiles on signup, reducing API surface area.
7. **Scheduled jobs via GitHub Actions**: Cron email jobs without needing a separate scheduler service.

### Features worth considering from alternatives

| Feature | Source | Effort | Value |
|---------|--------|--------|-------|
| React Email templates (vs plain text) | mickasmt | Medium | High -- richer welcome/notification emails |
| Activity/audit logging | nextjs/saas-starter | Low | Medium -- track who changed what |
| Stripe subscriptions | nextjs/saas-starter, mickasmt | High | High if charging for membership |
| i18n | makerkit, ixartz | Medium | Low unless multi-language needed |
| User impersonation (admin) | ixartz | Medium | Low -- debugging tool only |
| Magic link auth | mickasmt | Low | Medium -- passwordless login |
| Dark mode | ixartz, vercel with-supabase | Low | Low -- CSS only |
| Seed data / setup script | nextjs/saas-starter | Low | High -- easier onboarding |
| Member search/filter | None found | Medium | High -- useful for growing communities |

### Gaps across ALL alternatives

None of the repos reviewed have a proper **member directory** with search/filter -- they have user management but not a public-facing directory. None have **scheduled/bulk email jobs** as a first-class feature. None target the "private community" use case (most are SaaS billing templates). Our template is uniquely positioned for the community/membership niche.

---

*Generated: 2026-03-27*
