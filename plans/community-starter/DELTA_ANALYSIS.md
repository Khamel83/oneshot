# Delta Analysis: Popular Repos vs community-starter

Feature-by-feature comparison based on ALTERNATIVES.md research (8 repos analyzed).

---

## Summary Table

| Feature | Popular repos do it how | community-starter does it how | Verdict |
|---------|------------------------|-------------------------------|---------|
| Auth | Supabase Auth, Clerk, NextAuth, Auth.js | Supabase Auth (sync SDK, dict params) | ✅ On par |
| Email | Resend + React Email (mickasmt), Nodemailer (makerkit), or none | Resend (Python SDK, retry on 429) | ✅ On par (missing rich templates) |
| Admin panel | Full CRUD dashboards (mickasmt, ixartz) | Basic member list + role toggle | ⚠️ Theirs is richer |
| Member directory | None have public-facing directory | Yes — PUBLIC_COLUMNS + OWN_COLUMNS separation | ✅ Unique to us |
| Bulk email | None have scheduled bulk sends | Yes — cron via GitHub Actions + 504 handling | ✅ Unique to us |
| File uploads | S3/Cloudflare R2 (ixartz) | Not included | ❌ Missing |
| Payments | Stripe (nextjs/saas, mickasmt, shadcn) | Not included | ❌ Missing (by design) |
| Testing | ixartz: Vitest+Playwright+Storybook; most: none | 17 pytest tests + CI validation | ✅ Better than most |
| Build step | All require Next.js/React build pipeline | None — plain HTML + vanilla JS + Python | ✅ Simpler |
| i18n | makerkit (i18next), ixartz (next-intl) | Not included | ❌ Missing |
| Activity logging | nextjs/saas-starter (user events) | Not included | ❌ Missing |
| Dark mode | ixartz, vercel with-supabase (CSS only) | Not included | ❌ Missing |
| RLS defense | vercel with-supabase (standard RLS) | Deny-all RLS (blocks anon key even if leaked) | ✅ Better |
| Seed data | nextjs/saas-starter (pnpm db:seed) | Not included | ❌ Missing |
| Function limit | Not tracked (no concern with Node.js) | CI-enforced ≤12 functions | ✅ Unique awareness |
| Vercel runtime | @vercel/node (most) | @vercel/python 6.28.0 | — Different, not worse |
| Deployment | One-click Vercel deploy (most) | Git push (Vercel auto-deploy) | ✅ Same experience |

---

## Things Popular Repos Do Better

1. **Rich email templates** — mickasmt uses React Email for beautiful transactional emails. Our plain HTML strings work but aren't as polished.

2. **Activity/audit logging** — nextjs/saas-starter tracks every user action. We have no audit trail.

3. **Seed data + setup script** — nextjs/saas-starter has `pnpm db:seed` with a test user. We rely on manual signup.

4. **Admin dashboard richness** — mickasmt has an orders page, ixartz has user impersonation. Our admin panel is minimal (member list + role toggle).

5. **Dark mode** — Trivial CSS addition that most alternatives include. We don't.

---

## Things community-starter Does Better

1. **No build step** — Every alternative requires npm install + build. We deploy on git push with zero build minutes.

2. **504 false-alarm handling** — Real production lesson. None of the alternatives handle the case where a bulk email send completes but Vercel returns 504. We dedup via email_log.

3. **Deny-all RLS** — Defense-in-depth. Even if the anon key leaks from browser traffic, direct DB queries are blocked. Most alternatives rely solely on application-layer checks.

4. **DB trigger for member rows** — Auto-creates member profile on signup. Reduces API surface area and eliminates race conditions.

5. **Function count awareness** — CI enforces the 12-function Vercel limit. Most alternatives have no awareness of their serverless function count.

6. **Testing coverage** — 17 tests vs. most alternatives having zero. Only ixartz has more comprehensive testing.

7. **Python simplicity** — The auth handler is 150 lines. The equivalent Next.js auth setup spans multiple files, middleware, and server actions.

---

## Things Only community-starter Has

1. **Public member directory** with column-level access control (PUBLIC_COLUMNS vs OWN_COLUMNS)
2. **Scheduled bulk email** via GitHub Actions (no separate scheduler service)
3. **email_log dedup** to prevent duplicate sends on 504 retries
4. **CRON_SECRET auth pattern** for automation endpoints
5. **Vercel function count CI check**

---

## Recommended Additions

| Addition | Source | Effort | Why |
|----------|--------|--------|-----|
| Seed data script | nextjs/saas-starter | Low | Easier onboarding — auto-create admin user on first deploy |
| Rich email templates | mickasmt | Medium | Better welcome/notification emails; use Jinja2 (Python-native, no React needed) |
| Activity logging | nextjs/saas-starter | Low | Track who changed what; single `activity_log` table + trigger |
| Magic link auth | mickasmt | Low | Passwordless option for less technical users |
| Member search/filter | None (build ourselves) | Medium | Essential for communities > 20 members |

---

*Generated: 2026-03-27*
