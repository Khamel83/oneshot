# task_05: /doc audit — library versions vs actual code

## Goal
Verify that the library versions pinned in requirements.txt match what we actually use in code.
Fetch current changelogs/release notes to check for breaking changes since our pinned versions.

## Libraries to check
1. `supabase==2.15.0` — check if 2.15.0 is current or if there's a newer version with breaking changes
2. `resend==2.7.0` — same check
3. `@vercel/python@4.3.1` — check if runtime version in vercel.json is current

## Method
Use the `mcp__plugin_context7_context7__resolve-library-id` and `mcp__plugin_context7_context7__query-docs` tools,
OR use web search / WebFetch to check PyPI for latest versions and changelogs.

## Checks to perform
- Is `supabase==2.15.0` still the latest stable? If not, are there breaking API changes?
- Is `create_client(url, key)` still the correct constructor signature?
- Is `resend==2.7.0` still current? Is `resend.Emails.send(params)` still correct?
- Is `resend.exceptions.RateLimitError` still the correct exception class?
- Is `@vercel/python@4.3.1` the current recommended runtime?

## Output
Write results to `/home/ubuntu/github/oneshot/plans/community-starter/DOC_AUDIT.md`

Format:
```
## supabase-py
- Pinned: 2.15.0
- Current: X.X.X
- Breaking changes since pinned: [none / list them]
- Code usage matches docs: [yes/no + details]

## resend
...

## vercel python runtime
...
```

## If drift found
Update `templates/community-starter/requirements.txt` and/or `vercel.json` with the corrected versions.
Update `SETUP.md` if any setup instructions changed.
