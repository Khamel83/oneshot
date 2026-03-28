# task_10: Research open source community/membership starters on GitHub

## Goal
Find well-maintained repos with real GitHub traction that solve a similar problem:
private membership/community site with auth, member directory, email, admin panel.

## Search queries to run (use WebSearch or gh CLI)
- "supabase membership starter site:github.com stars:>500"
- "nextjs supabase saas boilerplate stars:>1000"
- "vercel supabase auth template"
- "open source membership site boilerplate"
- Known candidates to look up directly:
  - `vercel/next.js` examples/with-supabase
  - `supabase/supabase` starter templates
  - `shadcn-ui/taxonomy`
  - `leerob/next-saas-rbac`
  - `mickasmt/next-saas-stripe-starter`
  - `ixartz/SaaS-Boilerplate`

## For each repo found, document:
- Repo name + stars + last commit date
- Stack (frontend, backend, auth, database, email)
- Auth approach (OAuth, magic link, password, etc.)
- Email integration (which provider, how they handle bulk)
- Admin panel (exists? what can it do?)
- Testing coverage (exists? what framework?)
- License
- Key "wow" features we don't have
- Notable gotchas or complexity

## Output
Write to `/home/ubuntu/github/oneshot/plans/community-starter/ALTERNATIVES.md`
Aim for 5–8 repos. Quality over quantity.
