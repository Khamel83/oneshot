# ZAI to OpenCode Go Migration

## Current State: ZAI Dogfood Phase

The harness currently routes all lanes through **ZAI** (GLM models) via OpenCode proxy. This is a dogfood phase to validate the dispatch/collect/review lifecycle before committing to a paid provider.

**ZAI plan expires: 2026-05-02.** All lanes must migrate to OpenCode Go before this date.

## Why OpenCode Go

- **Cost:** $12/5h, $30/week, $60/month — predictable and cheap
- **Model diversity:** DeepSeek, Qwen, MiniMax, Kimi — different strengths for different lanes
- **Same runner shape:** `opencode run --model <resolved-model-id>` — identical invocation style across OpenCode-backed providers
- **Rate limits:** Managed by OpenCode platform, not per-provider

## Migration Steps

### 1. Get an API key

```bash
# Register at opencode.ai and get your API key
# Set it in the vault
secrets set oneshot "OPENCODE_GO_API_KEY=<your-key>" --commit
```

### 2. Enable the provider

In `.oneshot/config/models.yaml`:

```yaml
providers:
  opencode_go:
    enabled: true  # was false
```

### 3. Migrate lanes one at a time

For each lane, change `current_provider` and `current_model` to the `future_*` values:

```yaml
lanes:
  cheap_fast:
    current_provider: opencode_go    # was zai
    current_model: deepseek_v4_flash # was glm_4_7_flash
  cheap_summary:
    current_provider: opencode_go    # was zai
    current_model: qwen_3_5_plus     # was glm_4_5_air
  routine_coder:
    current_provider: opencode_go    # was zai
    current_model: minimax_m2_7      # was glm_4_7
  strong_reasoning:
    current_provider: opencode_go    # was zai
    current_model: kimi_k2_6         # was glm_5
  premium_reasoning:
    current_provider: opencode_go    # was zai
    current_model: deepseek_v4_pro   # was glm_5_1
```

### 4. Test each lane

```bash
./bin/oneshot lanes  # verify the table shows opencode_go models
./bin/oneshot dispatch --lane routine_coder --task "test task" --allow-dirty
# Check worker.log shows: opencode run --model opencode-go/minimax-m2.7 ...
```

### 5. Disable ZAI

After all lanes are migrated and tested:

```yaml
providers:
  zai:
    enabled: false  # was true
```

## Model Mapping

| ZAI (current) | OpenCode Go (future) | Notes |
|---------------|---------------------|-------|
| `glm-4.7-flash` | `deepseek-v4-flash` | Faster, cheaper |
| `glm-4.5-air` | `qwen3.5-plus` | Good at summarization |
| `glm-4.7` | `minimax-m2.7` | Solid coder |
| `glm-5` | `kimi-k2.6` | Strong reasoning |
| `glm-5.1` | `deepseek-v4-pro` | Premium fallback |
| `glm-5-turbo` | — | No direct equivalent; use `glm-5` via ZAI fallback if needed |

## Budget Limits

| Window | Limit |
|--------|-------|
| 5 hours | $12 |
| 1 week | $30 |
| 1 month | $60 |

These limits apply to the OpenCode Go platform total, not per-lane. The routing policy conserves budget by defaulting to cheap models and escalating only on failure.

## Rollback

If OpenCode Go doesn't work out, revert the `current_*` fields back to ZAI values. The `future_*` fields stay as documentation of the intended migration target. The ZAI provider config remains in the file as a fallback.
