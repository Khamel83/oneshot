# Claude Code + Non-Anthropic Models: April 2026 Research

**Research date**: 2026-04-04
**Question**: Can Claude Code (Anthropic CLI) use non-Anthropic models natively in April 2026?

---

## Executive Summary

- **Yes, it works** — and it is the dominant community pattern as of April 2026. Setting `ANTHROPIC_BASE_URL` to a provider that exposes an Anthropic-compatible API is the primary supported mechanism.
- **OpenRouter works natively and directly** — set `ANTHROPIC_BASE_URL=https://openrouter.ai/api`, no local proxy required. OpenRouter maintains an "Anthropic skin" that passes through tool use, streaming, and thinking blocks.
- **LiteLLM proxy is the officially documented path** for providers that only speak OpenAI format (Azure, Bedrock, Ollama, etc.) — LiteLLM translates between Anthropic and OpenAI wire formats and is documented by Anthropic.
- **Z.AI (GLM)** works identically to the ZAI pattern already in use: `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic`.
- **Critical gotcha**: Claude Code uses **three internal model tiers** (Haiku/Sonnet/Opus). If only one is configured, intermittent 404 errors occur. Must set all three: `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`.
- **Active bug (Apr 4 2026)**: Claude Code 2.1.92 on Windows silently exits with `claude -p` when using non-`sk-ant-` prefixed API keys. Interactive mode also affected. Suspected pre-flight key format validation. Duplicates exist for v2.1.64+. Linux/macOS unaffected by this specific bug but related auth issues exist.

---

## Providers with Anthropic-Compatible APIs

### Tier 1: Native Anthropic Skin (no proxy needed)

| Provider | ANTHROPIC_BASE_URL | Notes |
|---|---|---|
| **OpenRouter** | `https://openrouter.ai/api` | 200+ models; Anthropic skin built-in; tool use pass-through; needs `ANTHROPIC_API_KEY=""` explicitly empty |
| **Z.AI (GLM)** | `https://api.z.ai/api/anthropic` | GLM-4.7 etc.; already in use in oneshot |
| **Ollama** (local) | `http://localhost:11434` | Added official Claude Code support; requires proxy for non-native models |

### Tier 2: Native Anthropic-Format Endpoint

| Provider | Endpoint pattern | Notes |
|---|---|---|
| **302.AI** | `https://api.302.ai` | "Claude Compatible" — Anthropic wire format, routes to many backends |
| **Bifrost** (self-hosted) | `http://localhost:8080/anthropic` | Open-source Go gateway; 11µs overhead; handles OpenAI/Bedrock/Vertex/Gemini behind Anthropic endpoint |
| **CCProxy** (self-hosted) | `http://localhost:3456` | Node.js proxy; wraps OpenRouter/Anthropic/other providers |

### Tier 3: Via LiteLLM Proxy (translation layer required)

| Provider | Via LiteLLM? | Notes |
|---|---|---|
| Azure OpenAI | Yes | Uses OpenAI format; LiteLLM translates |
| AWS Bedrock | Yes | IAM auth; LiteLLM translates |
| Vertex AI (Gemini) | Yes | Google auth; LiteLLM translates |
| DeepSeek | Yes | Also available directly via OpenRouter |
| Groq | Yes | Fast inference; also via OpenRouter |
| Local Ollama | Yes | Alternative to direct Ollama support |
| Any OpenAI-compat | Yes | LiteLLM supports 100+ providers |

---

## LiteLLM / Proxy Solutions

### LiteLLM (officially documented by Anthropic)

LiteLLM is the **officially supported** proxy path for non-Anthropic models. Anthropic's own docs at `docs.litellm.ai/docs/tutorials/claude_non_anthropic_models` document this pattern.

**How it works**:
1. LiteLLM runs locally as `litellm --config config.yaml` on port 4000
2. It exposes an Anthropic Messages API endpoint at `http://0.0.0.0:4000`
3. Claude Code uses `ANTHROPIC_BASE_URL=http://0.0.0.0:4000` and `ANTHROPIC_AUTH_TOKEN=$LITELLM_MASTER_KEY`
4. LiteLLM translates Anthropic format → target provider format on the fly

**Sample config.yaml** for OpenRouter via LiteLLM:
```yaml
model_list:
  - model_name: claude-sonnet-4-20250514
    litellm_params:
      model: openrouter/anthropic/claude-sonnet-4-20250514
      api_key: os.environ/OPENROUTER_API_KEY
  - model_name: deepseek-chat
    litellm_params:
      model: openrouter/deepseek/deepseek-chat
      api_key: os.environ/OPENROUTER_API_KEY
  - model_name: qwen3-coder
    litellm_params:
      model: openrouter/qwen/qwen3-coder:free
      api_key: os.environ/OPENROUTER_API_KEY
```

**Caveats**:
- Python process overhead vs. Go-based Bifrost (LiteLLM: ~10-100ms; Bifrost: 11µs)
- Must manage the proxy process lifecycle
- Tool calling translation works for major providers (OpenAI, Gemini, Anthropic)
- Some niche providers may have incomplete tool use translation

### Bifrost (Go, open-source, April 2026)

Published April 1, 2026. Go-based gateway (`npx -y @maximhq/bifrost`) with:
- Anthropic-compatible endpoint at `/anthropic`
- 11µs overhead, 5000 RPS single instance
- Multi-provider failover (OpenAI → Gemini → Anthropic)
- Budget enforcement, semantic caching, MCP server mode
- Self-hosted only (no managed option)

### OpenRouter Direct (no proxy)

**Simplest path** for non-Anthropic models through Claude Code:
```bash
export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
export ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY"
export ANTHROPIC_API_KEY=""   # must be explicitly empty, not just unset
export ANTHROPIC_DEFAULT_HAIKU_MODEL="qwen/qwen3-4b:free"
export ANTHROPIC_DEFAULT_SONNET_MODEL="qwen/qwen3-coder:free"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek/deepseek-r1-0528:free"
```

OpenRouter docs explicitly state: "Claude Code with OpenRouter is **only guaranteed to work** with the Anthropic first-party provider." — meaning OpenRouter will route to Anthropic Claude by default and this is the safe path. Non-Claude models via OpenRouter are community-supported, not Anthropic-guaranteed.

---

## April 2026 Developments

### Major: Claude Code Source Code Leak (March 31, 2026)

Anthropic accidentally published 512,000+ lines of TypeScript source code to npm. This exposed:
- Internal model routing logic (confirmed the 3-tier Haiku/Sonnet/Opus split)
- Pre-flight validation that checks `firstParty` provider status — explains silent exits with non-`sk-ant-` keys
- Upcoming features competitors could now clone

### Bifrost Gateway Launch (April 2026)

New Go-based Anthropic-compatible gateway, open-source, optimized specifically for Claude Code. Benchmarked at 11µs overhead. Supports weighted routing, automatic failover, budget controls, MCP server mode.

### Active Bug: v2.1.92 Silent Exit (April 4, 2026)

GitHub issue #43607 (filed today): Claude Code 2.1.92 on Windows silently exits when:
- `ANTHROPIC_API_KEY` has non-`sk-ant-` prefix (e.g., `tp-` for third-party)
- `ANTHROPIC_BASE_URL` points to a third-party endpoint

GitHub auto-detected duplicates: #22760, #31132 (broken since v2.1.64+), #36998 (interactive mode ignores ANTHROPIC_BASE_URL). This is a regression — it worked in earlier versions.

### Ollama Official Claude Code Support

Ollama added native Claude Code support. Direct connection at `http://localhost:11434` now works without a translation proxy, as long as you set all three model tier env vars.

### Claude Code Changelog: Provider Fixes

From `code.claude.com/docs/en/changelog`:
- "Fixed API 400 errors when using ANTHROPIC_BASE_URL with third-party providers"
- "Fixed /remote-control appearing for gateway and third-party provider deployments"

These appear in recent releases, suggesting Anthropic is treating third-party BASE_URL as a supported (if unofficial) use case.

### Community Ecosystem Growth

Multiple purpose-built projects emerged:
- `claude-code-router` (musistudio/GitHub) — lightweight router between Claude Code and multiple backends
- `CCORP` (terhechte/GitHub) — Rust-based Claude Code→OpenRouter proxy
- `CCProxy` (ccproxy.orchestre.dev) — Node.js multi-provider proxy
- `anyclaude` (coder/anyclaude) — drop-in wrapper, no config files needed

---

## Community Consensus

**Status: Functional for most use cases, with known rough edges**

| Aspect | Assessment |
|---|---|
| Overall viability | Production-ready with caveats |
| OpenRouter + Claude models | Fully functional, officially documented by OpenRouter |
| OpenRouter + non-Claude models | Community-supported, works but degrades |
| LiteLLM proxy | Officially documented by Anthropic, widely used |
| Bifrost/CCProxy | Production-viable, newer but active |
| Local Ollama | Functional but tool calling is unreliable on smaller models |
| Edit success rate | ~70-80% for non-Claude models vs ~98% for Claude |
| Anthropic's stance | Officially "unsupported" but unofficially tolerated; fixes being shipped |

**The edit accuracy problem is real**: Claude Code's diff/edit format was optimized for Claude's output style. Other models produce structurally valid but slightly off diffs — wrong whitespace, context lines, line numbers. This causes `claude apply-edit` failures that require manual retries. This is the primary quality gap vs. running actual Claude.

**Tool calling is the other gate**: Claude Code relies heavily on structured tool calls for file read/write/execute. Models without robust function calling (smaller local models, some open-source) fall back to describing actions instead of executing them. Models that work well: GPT-4o+, Gemini Pro, Claude, Qwen3-Coder, DeepSeek-V3. Models that struggle: sub-14B local models, older open-source.

---

## Recommendation for Orchestration Architecture

**Context**: oneshot has three free options running — gemini_cli (free until EOY), codex (free monthly quota), ZAI GLM (free until May 2026). The existing `claw-code-agent` wraps Claude Code with ZAI GLM via `ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic`.

### Option A: Keep claw-code-agent as-is, no change

**Pros**: Already working. ZAI GLM-4.7 has strong tool use. Simple.
**Cons**: GLM free tier expires May 2026. Need plan B.

### Option B: Replace claw-code-agent with LiteLLM → OpenRouter

**Architecture**:
```
Claude Code CLI
  → ANTHROPIC_BASE_URL=http://localhost:4000
  → LiteLLM proxy
    → OpenRouter API
      → qwen/qwen3-coder:free (SONNET tier)
      → deepseek/deepseek-r1-0528:free (OPUS tier)
      → qwen/qwen3-4b:free (HAIKU tier)
```

**Pros**:
- Free models on OpenRouter (39 free models as of April 2026)
- Can swap models without changing Claude Code config
- LiteLLM officially documented by Anthropic
- Single proxy handles fallback logic

**Cons**:
- Requires running a local LiteLLM process
- Free models have rate limits and availability fluctuates
- Edit accuracy worse than ZAI GLM (which is Claude-class)

### Option C: OpenRouter Direct (no proxy)

```bash
export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
export ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY"
export ANTHROPIC_API_KEY=""
export ANTHROPIC_DEFAULT_SONNET_MODEL="anthropic/claude-sonnet-4-20250514"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="anthropic/claude-haiku-4-20250514"
export ANTHROPIC_DEFAULT_OPUS_MODEL="anthropic/claude-opus-4-20250514"
```

**Pros**: Simplest possible setup. OpenRouter + Anthropic 1P is the "only guaranteed" path per OpenRouter docs. Adds reliability/failover over direct Anthropic API. Cost tracking.
**Cons**: Still costs money per token (just routed through OpenRouter).

### Option D: OpenRouter Direct with free non-Claude models

Same as C but pointing model vars at free models (qwen3-coder:free, etc.)

**Pros**: Potentially free. 39+ free models on OpenRouter.
**Cons**: Free models are rate-limited, availability changes. Edit quality degrades. Not appropriate for tasks requiring precise file edits.

### Recommendation

**For the oneshot orchestration use case (cheap-lane worker)**:

1. **Immediately**: Configure `claw-code-agent` to also accept OpenRouter as a fallback for when ZAI GLM expires in May. This is a one-env-var change.

2. **After May 2026**: Switch to **Option C (OpenRouter → Anthropic 1P)** for tasks where quality matters. For bulk/cheap tasks, use **Option D (OpenRouter → qwen3-coder:free)** as the cheap-lane worker.

3. **Skip the LiteLLM proxy** unless you specifically need Bedrock, Azure, or Vertex — OpenRouter's native Anthropic skin handles everything you need without running a separate process.

4. **The bigger question about claw-code-agent**: The agent exists to provide a "Claude Code agentic loop with a free model." Given that:
   - gemini_cli is free until EOY and is already a strong coder
   - codex is free with monthly quota
   - ZAI expires in May
   - OpenRouter free models have quality/reliability issues

   **The most practical path**: deprecate `claw-code-agent` as a free-model hack after May, and reserve Claude Code (via OpenRouter or direct Anthropic) for tasks that actually need the agentic loop quality. Use gemini_cli or codex as the cheap-lane workers instead — they're better supported and free longer.

---

## Sources

1. **LiteLLM Official Docs** — `docs.litellm.ai/docs/tutorials/claude_non_anthropic_models` — Official Anthropic-endorsed tutorial for Claude Code with non-Anthropic models
2. **OpenRouter Official Docs** — `openrouter.ai/docs/guides/coding-agents/claude-code-integration` — Complete OpenRouter setup guide for Claude Code, including model vars
3. **ali.ac article** — `ali.ac/articles/how-to-use-claude-code-with-custom-providers/` — Practical Z.ai + OpenRouter config with shell aliases; includes non-Claude model overrides
4. **Morph LLM guide** — `morphllm.com/use-different-llm-claude-code` — Comprehensive comparison of all proxy methods; model compatibility matrix; edit accuracy data
5. **dan1t0.com** — `dan1t0.com/2026/01/19/claude-code-with-free-models-ollama-openrouter-setup/` — Critical: documents the 3-model-tier requirement; recommended free model combinations
6. **Bifrost dev.to** — `dev.to/pranay_batta/how-to-connect-non-anthropic-models-to-claude-code-with-bifrost-ai-gateway-5dnj` — April 1 2026; Go gateway benchmarks, multi-provider failover
7. **GitHub Issue #43607** — `github.com/anthropics/claude-code/issues/43607` — Active April 4 2026 bug: silent exit with third-party keys on v2.1.92; links to related issues #22760, #31132, #36998
8. **CCProxy docs** — `ccproxy.orchestre.dev/providers/openrouter` — Tool calling requirement; model selection guide; free model recommendations
9. **Claude Code changelog** — `code.claude.com/docs/en/changelog` — Recent fixes for ANTHROPIC_BASE_URL with third-party providers
10. **Serper search results** — Multiple queries across "ANTHROPIC_BASE_URL non-anthropic models", "claude code openrouter", "LiteLLM anthropic proxy", "third-party provider april 2026"
