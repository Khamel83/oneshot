# Delegation & Review Rules

**Authoritative source**: `docs/instructions/review.md`

See @docs/instructions/review.md

## Claude-Specific Additions

- SubagentStop hook logs to `.claude/delegation-log.jsonl` automatically
- Use `model: "haiku"` for low-complexity delegations
- `git add -A && git commit` checkpoint before high-criticality delegation
