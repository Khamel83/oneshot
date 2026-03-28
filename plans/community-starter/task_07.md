# task_07: Cross-check SETUP.md accuracy

## Goal
Every claim in SETUP.md must be verifiable against actual code. No doc rot.

## File to audit
`/home/ubuntu/github/oneshot/templates/community-starter/SETUP.md`

## Checks

### 1. Env vars
Every var in `.env.example` must be referenced somewhere in `api/*.py` or `.github/workflows/*.yml`.
Run: `grep -r "SUPABASE_URL\|SUPABASE_ANON_KEY\|..." api/ .github/` and verify each is present.

### 2. Vercel function count
SETUP.md says "5 handlers, 7 slots remaining". Count actual handlers:
`grep -rl "class handler" templates/community-starter/api/*.py | wc -l`
Update the number if wrong.

### 3. Resend free tier note
SETUP.md says "3,000 emails/month". Verify this is still the current free tier limit.
Also add: "Works with any verified domain — multiple domains on one account, shared 3k limit."

### 4. maxDuration note
SETUP.md explains why maxDuration=60. Verify vercel.json actually has 60, not 30.

### 5. Gotchas section
Every gotcha must reference a real file/line. Spot-check 3–4 gotchas.

## Output
Write corrections directly to SETUP.md. Note any changes made at bottom of this task file.
