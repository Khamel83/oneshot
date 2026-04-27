# Worker Lanes

## Current Phase: ZAI Dogfood

Active provider: **ZAI** (GLM models via OpenCode proxy).

| Lane | Model | Max Diff | Max Files | Arch Changes |
|------|-------|----------|-----------|-------------|
| `cheap_fast` | `glm-4.7-flash` | 150 lines | 5 | No |
| `cheap_summary` | `glm-4.5-air` | 100 lines | 5 | No |
| `routine_coder` | `glm-4.7` | 500 lines | 12 | No |
| `strong_reasoning` | `glm-5` | 800 lines | 20 | Yes |
| `premium_reasoning` | `glm-5.1` | 1000 lines | 25 | Yes |
| `review_only` | Claude Code (manual) | unlimited | unlimited | Yes |

**ZAI plan expires 2026-05-02.** Migrate before then (see `ZAI_TO_OPENCODE_GO_MIGRATION.md`).

## Future Phase: OpenCode Go

Provider: **OpenCode Go** (disabled, pending activation).

| Lane | Model | Max Diff | Max Files | Arch Changes |
|------|-------|----------|-----------|-------------|
| `cheap_fast` | `deepseek-v4-flash` | 150 | 5 | No |
| `cheap_summary` | `qwen3.5-plus` | 100 | 5 | No |
| `routine_coder` | `minimax-m2.7` | 500 | 12 | No |
| `strong_reasoning` | `kimi-k2.6` | 800 | 20 | Yes |
| `premium_reasoning` | `deepseek-v4-pro` | 1000 | 25 | Yes |
| `review_only` | Claude Code (manual) | unlimited | unlimited | Yes |

## Optional Providers

| Provider | Status | Use case |
|----------|--------|----------|
| Gemini | Disabled | Documentation, tests, summaries |
| Codex | Disabled | Alternate worker or reviewer |

## Model Selection Policy

1. **Don't use premium by default.** `routine_coder` is the default lane for implementation.
2. **Escalate on retry-twice.** If a task fails on `routine_coder` twice, escalate to `strong_reasoning`.
3. **Cross-file architecture → `strong_reasoning`.** Don't send refactors that touch >5 files to `routine_coder`.
4. **Premium is for recovery.** `premium_reasoning` means something went wrong. Investigate the spec before escalating.
5. **Review is always Claude.** The `review_only` lane means Claude reviews but doesn't implement.

## Budget Limits (OpenCode Go, when enabled)

- $12 per 5-hour window
- $30 per week
- $60 per month

Cheap/high-volume models (deepseek, qwen) for routine work. Premium models (kimi, deepseek-v4-pro) only on escalation.
