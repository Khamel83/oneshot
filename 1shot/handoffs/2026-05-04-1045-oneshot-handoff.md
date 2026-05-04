# Handoff: SKILL.md YAML Fixes

**Created**: 2026-05-04 10:45
**Context Used**: ~5%

## Quick Summary
Fixed 3 broken SKILL.md files (debug, tdd, conduct) whose `description` fields contained colons that broke YAML parsing. Added double-quotes around each description value. Also noted a 4th issue: ARGUS_API_KEY missing on oci-dev (but that lives in SOPS, not in this repo's code).

## What's Done
- [x] Fix debug/SKILL.md — quoted description field (commit: pending)
- [x] Fix tdd/SKILL.md — quoted description field (commit: pending)
- [x] Fix conduct/SKILL.md — quoted description field (commit: pending)

## In Progress
- [ ] Commit these 3 fixes
- [ ] Push to remote

## Not Started
- [ ] Any other SKILL.md files with the same colon-in-description pattern — should scan all skills

## Active Files
- `.claude/skills/debug/SKILL.md` — fixed
- `.claude/skills/tdd/SKILL.md` — fixed
- `.claude/skills/conduct/SKILL.md` — fixed

## Key Decisions Made
1. Decision: Wrap description in double-quotes rather than escaping individual colons | Rationale: Cleaner, future-proof against additional special chars in descriptions

## Important Discoveries
- SKILL.md files with unquoted descriptions containing colons (e.g. "Trigger keywords:") cause YAML parse failures and silently skip the entire skill

## Blockers / Open Questions
| # | Question | Status |
|---|---------|--------|
| 1 | Should other SKILL.md files be audited for the same pattern? | Open |

## Learnings & Suggested Updates

### Pitfalls Encountered
- Any YAML value containing a colon (`:`) must be quoted or the colon must be escaped (`\:`) — this is a common YAML footgun for description fields

### Suggested Instruction Updates
- Add to `docs/instructions/skills.md` or the SKILL.md template: "DESCRIPTION VALUES MUST BE QUOTED if they contain colons (e.g. 'Trigger keywords:')"

## Next Steps (Prioritized)
1. **Immediate**: `git add .claude/skills/debug/SKILL.md .claude/skills/tdd/SKILL.md .claude/skills/conduct/SKILL.md && git commit && git push`
2. **Then**: Audit all other `.claude/skills/*/SKILL.md` files for unquoted colons in description fields

## Resume
/restore @~/github/oneshot/1shot/handoffs/2026-05-04-1045-oneshot-handoff.md
