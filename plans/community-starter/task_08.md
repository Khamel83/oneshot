# task_08: Write scripts/test-community-starter.sh

## Goal
A single bash script that fully validates the community-starter template.
Run manually or from CI. Zero dependencies beyond Python 3 + standard tools.

## File to create
`/home/ubuntu/github/oneshot/scripts/test-community-starter.sh`

## What it must check (in order, fail fast)

1. **Required files present**
   Check these exist:
   - templates/community-starter/api/_supabase.py
   - templates/community-starter/api/auth.py
   - templates/community-starter/api/members.py
   - templates/community-starter/api/admin.py
   - templates/community-starter/api/email.py
   - templates/community-starter/api/system.py
   - templates/community-starter/vercel.json
   - templates/community-starter/requirements.txt
   - templates/community-starter/SETUP.md
   - templates/community-starter/.env.example
   - templates/community-starter/migrations/01_schema.sql
   - templates/community-starter/migrations/02_rls.sql
   - templates/community-starter/public/js/auth.js

2. **vercel.json is valid JSON**
   `python3 -c "import json; json.load(open('templates/community-starter/vercel.json'))"`

3. **Vercel function count ≤ 12**
   `grep -rl "class handler" templates/community-starter/api/*.py | wc -l`

4. **All env vars in .env.example are referenced in code**
   For each KEY= line in .env.example, grep for KEY in api/*.py and .github/workflows/*.yml

5. **Python syntax check**
   `python3 -m py_compile templates/community-starter/api/*.py`

6. **Tests pass**
   `cd templates/community-starter && PYTHONPATH=$(pwd) python3 -m pytest tests/ -q`

## Script must
- Print each check name before running it
- Print PASS/FAIL per check
- Exit 0 only if ALL checks pass
- Exit 1 with clear summary of what failed

## Make executable
`chmod +x scripts/test-community-starter.sh`
