# task_11: Delta analysis — proven repos vs community-starter

## Goal
Based on ALTERNATIVES.md (task_10), produce a clear delta analysis so the user can
decide what to pull in vs. keep custom.

## Format for DELTA_ANALYSIS.md

### Summary table

| Feature | Popular repos do it how | community-starter does it how | Verdict |
|---------|------------------------|-------------------------------|---------|
| Auth | Supabase Auth / Better Auth / Clerk | Supabase Auth (SDK) | ✅ On par |
| Email | Resend / Postmark / SES | Resend (pinned 2.7.0) | ✅ On par |
| Admin panel | Full CRUD dashboards | Basic member list + role toggle | ⚠️ Theirs is richer |
| File uploads | S3/Cloudflare R2 | Not included | ❌ Missing |
| Payments | Stripe integration | Not included | ❌ Missing (by design) |
| ... | | | |

### Things popular repos do better
(worth considering for future iterations)

### Things community-starter does better
(things we solved that popular repos still get wrong)

### Things only community-starter has
(unique to our use case — don't need to copy from anywhere)

### Recommended additions (if any)
What specifically, from which repo, and why it matters for the target use case.

## Output
Write to `/home/ubuntu/github/oneshot/plans/community-starter/DELTA_ANALYSIS.md`
