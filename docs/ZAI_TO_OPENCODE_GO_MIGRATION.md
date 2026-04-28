# ZAI to OpenCode Go Migration

## Current State: ZAI Dogfood Phase

The harness currently routes all lanes through **ZAI** (GLM models) via Claude CLI with custom `ANTHROPIC_BASE_URL`. This is a dogfood phase to validate the dispatch/collect/review lifecycle before committing to a paid provider.

**ZAI plan expires: 2026-05-02.** All lanes must migrate to OpenCode Go before this date.

## Why OpenCode Go

- **Cost:** $5 first month, $10/month subscription — predictable and cheap
- **Model diversity:** DeepSeek, Qwen, MiniMax, Kimi, MiMo — different strengths for different lanes
- **Multiple invocation paths:** Not limited to OpenCode CLI — Claude CLI and direct API also work
- **Rate limits:** Managed by OpenCode platform, not per-provider

## Architecture: Harness vs Provider

OpenCode Go is a **model gateway**, not an OpenCode-CLI-only tool. Three invocation paths:

| Path | How | Models | Best For |
|------|-----|--------|----------|
| **OpenCode CLI** | `opencode run --model opencode-go/<id>` | All models | Universal fallback |
| **Claude CLI** | `claude -p` + `ANTHROPIC_BASE_URL` | MiniMax M2.5, M2.7 only | Full toolchain (bash, edit, grep, git) |
| **Direct API** | HTTP POST to OpenAI-compatible endpoint | All models | Summaries, extraction, classification |

Path 2 gives the full Claude Code toolchain with OpenCode Go pricing. Path 3 is lightweight — no shell access for the model.

## Endpoint Routing (Per-Model, Not Universal)

Endpoints are **per-protocol, not universal**:

| Protocol | Endpoint | Models | Usable By |
|----------|----------|--------|-----------|
| OpenAI-compatible | `https://opencode.ai/zen/go/v1/chat/completions` | GLM, Kimi, DeepSeek, MiMo, Qwen | OpenCode CLI, Direct API |
| Anthropic-compatible | `https://opencode.ai/zen/go/v1/messages` | MiniMax M2.5, M2.7 | Claude CLI, OpenCode CLI |

Models metadata: `https://opencode.ai/zen/go/v1/models` (dynamic model list).

**Key constraint:** The Claude CLI runner path (`ANTHROPIC_BASE_URL`) only works with MiniMax models. Other models need the OpenCode CLI or direct API (OpenAI-compatible endpoint).

## Pricing

| Plan | Cost |
|------|------|
| First month | $5 |
| Ongoing | $10/month |

Usage limits (dollar-based, vary by model cost):

| Window | Limit |
|--------|-------|
| 5 hours | $12 |
| 1 week | $30 |
| 1 month | $60 |

These limits apply to the OpenCode Go platform total, not per-lane. The routing policy conserves budget by defaulting to cheap models and escalating only on failure.

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

### 3. Choose invocation path per lane

The `routine_coder` lane defaults to MiniMax (Anthropic-compatible) for full Claude CLI toolchain. Other lanes use the direct API or OpenCode CLI.

```yaml
lanes:
  cheap_fast:
    current_provider: opencode_go    # was zai
    current_model: deepseek_v4_flash # was glm_4_5_air
    # Uses direct API (OpenAI-compatible)
  cheap_summary:
    current_provider: opencode_go    # was zai
    current_model: qwen_3_5_plus     # was glm_4_5_air
    # Uses direct API (OpenAI-compatible)
  routine_coder:
    current_provider: opencode_go    # was zai
    current_model: minimax_m2_7      # was glm_5_1
    future_runner: opencode_go_claude # Claude CLI path (full toolchain)
    # Uses Claude CLI (Anthropic-compatible)
  strong_reasoning:
    current_provider: opencode_go    # was zai
    current_model: kimi_k2_6         # was glm_5_turbo
    # Uses OpenCode CLI or direct API
  premium_reasoning:
    current_provider: opencode_go    # was zai
    current_model: deepseek_v4_pro   # was glm_5_turbo
    # Uses OpenCode CLI or direct API
```

### 4. Test each lane

```bash
./bin/oneshot lanes  # verify the table shows opencode_go models
./bin/oneshot dispatch --lane routine_coder --task "test task" --allow-dirty
# Claude CLI path: claude -p --model minimax-m2.7 --dangerously-skip-permissions ...
# Direct API path: python3 -c "from core.dispatch.direct_api import call; ..."
```

### 5. Disable ZAI

After all lanes are migrated and tested:

```yaml
providers:
  zai:
    enabled: false  # was true
```

## Model Mapping

| ZAI (current) | OpenCode Go (future) | Protocol | Notes |
|---------------|---------------------|----------|-------|
| `glm-4.5-air` | `deepseek-v4-flash` | OpenAI | Faster, cheaper |
| `glm-4.5-air` | `qwen3.5-plus` | OpenAI | Good at summarization |
| `glm-5.1` | `minimax-m2.7` | **Anthropic** | Claude CLI path (full toolchain) |
| `glm-5-turbo` | `kimi-k2.6` | OpenAI | Strong reasoning |
| `glm-5-turbo` | `deepseek-v4-pro` | OpenAI | Premium fallback |
| — | `glm-5` | OpenAI | GLM available on OCG too |
| — | `glm-5.1` | OpenAI | Premium reasoning tier |
| — | `mimo-v2-pro` | OpenAI | Routine coder |
| — | `mimo-v2-omni` | OpenAI | Routine coder |
| — | `mimo-v2.5-pro` | OpenAI | Strong reasoning |
| — | `mimo-v2.5` | OpenAI | Routine coder |

## Runner Templates

Three runner templates in `.oneshot/config/models.yaml`:

| Template | Harness | Protocol | Models | Toolchain |
|----------|---------|----------|--------|-----------|
| `opencode_go` | OpenCode CLI | Both | All | OpenCode tools |
| `opencode_go_claude` | Claude CLI | Anthropic | MiniMax only | Full (bash, edit, grep, git) |
| `opencode_go_api` | Direct API | OpenAI | All | None (request/response only) |

## Rollback

If OpenCode Go doesn't work out, revert the `current_*` fields back to ZAI values. The `future_*` fields stay as documentation of the intended migration target. The ZAI provider config remains in the file as a fallback.
