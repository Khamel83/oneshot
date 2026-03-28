# task_12: Final commit to oneshot + delete standalone repo

## Goal
Commit everything, push, verify CI passes, then delete the now-redundant standalone community-starter repo.

## Pre-commit checklist
- [ ] templates/community-starter/ — all 25 files present, no .git or __pycache__
- [ ] .claude/rules/community.md — exists
- [ ] templates/LLM-OVERVIEW.md — updated
- [ ] CLAUDE.md — updated
- [ ] AGENTS.md — updated
- [ ] scripts/test-community-starter.sh — exists and executable
- [ ] .github/workflows/ci.yml — has validate-community-starter job
- [ ] plans/community-starter/ — PLAN.md + all task files + audit docs
- [ ] tests pass: bash scripts/test-community-starter.sh exits 0

## Commit command
```bash
cd /home/ubuntu/github/oneshot
git add templates/community-starter/ \
        .claude/rules/community.md \
        templates/LLM-OVERVIEW.md \
        CLAUDE.md AGENTS.md \
        scripts/test-community-starter.sh \
        .github/workflows/ci.yml \
        plans/community-starter/
git commit -m "feat: add community-starter template (Vercel+Supabase+Python)

Hardened membership community site template extracted from Net Worth Tennis.
Encodes security, reliability, and email lessons. 17 tests. Full CI validation.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push origin master
```

## After push
- Wait for CI to show green on GitHub
- If CI fails: diagnose, fix, new commit — do NOT push --force

## Delete standalone repo
```bash
rm -rf /home/ubuntu/github/community-starter
```
(Safe — everything is now in oneshot. networth was never affected.)

## Verify
```bash
ls /home/ubuntu/github/community-starter  # should: No such file or directory
ls /home/ubuntu/github/oneshot/templates/community-starter/api/  # should: list 6 .py files
```
