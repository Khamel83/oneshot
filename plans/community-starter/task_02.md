# task_02: Add .claude/rules/community.md

## Goal
Add a new rule file to oneshot that tells Claude when to recommend the community-starter template.

## File to create
`/home/ubuntu/github/oneshot/.claude/rules/community.md`

## Acceptance criteria
- File exists at `.claude/rules/community.md`
- Describes when to use this stack (membership sites, communities, leagues, cohorts)
- States it is an ALTERNATIVE to Astro+CF, not a replacement
- Links to `templates/community-starter/SETUP.md`
- Lists the stack: Vercel + Supabase + Python + Resend
- Lists anti-patterns (don't use for public marketing sites, high-traffic APIs, etc.)

## Do not
- Change web.md or khamel-mode.md
- Add community-starter as the *default* for anything
