# Multi-Provider Claude Code Research

**Research Date:** 2026-02-14
**Status:** Complete

---

## Executive Summary

**Is multi-provider Claude Code viable?** Yes, highly viable.

**Recommended approach:** Use `cc-mirror` for the easiest multi-instance setup, or `claude-code-router` for more granular control. Both tools solve the problem of running isolated Claude Code instances with different model providers.

### Key Findings

1. **Tool calling works via OpenRouter** - The previous issues with Gemini Flash and other models have been largely resolved. OpenRouter standardizes the tool calling interface across models.

2. **cc-mirror is the most polished solution** - It provides isolated instances, provider presets, and one-command setup for Z.ai (GLM), MiniMax, Kimi, OpenRouter, and more.

3. **The `--jinja` flag is critical** - When using local/cloud models through routers, the `--jinja` flag is essential for tool calling to work properly.

4. **GLM-4.7/5 and MiniMax M2.1 are production-ready** - Both have strong tool calling support and are cost-effective alternatives to Claude.

---

## cc-mirror Overview

**Repository:** https://github.com/numman-ali/cc-mirror

cc-mirror is an opinionated Claude Code distribution that:

1. **Clones** Claude Code into isolated instances
2. **Configures** provider endpoints, model mapping, and env defaults
3. **Applies** prompt packs and tweakcc themes
4. **Packages** everything into a single command

### Directory Structure

```
~/.cc-mirror/
  ├── mclaude/                    # Mirror Claude (vanilla)
  │   ├── native/                 # Claude Code installation
  │   ├── config/                 # API keys, sessions, MCP servers
  │   ├── tweakcc/                # Theme customization
  │   └── variant.json            # Metadata
  ├── zai/                        # Z.ai variant (GLM models)
  ├── minimax/                    # MiniMax variant (M2.1)
  └── kimi/                       # Kimi Code variant
```

### Supported Providers

| Provider | Models | Auth | Best For |
|----------|--------|------|----------|
| **Mirror Claude** | Native Claude | OAuth/API Key | Clean isolation, vanilla experience |
| **Z.ai** | GLM-4.7, GLM-4.5-Air, GLM-5 | API Key | Heavy coding with GLM reasoning |
| **MiniMax** | MiniMax-M2.1 | API Key | Unified model experience, coding |
| **Kimi** | kimi-for-coding, Kimi K2.5 | API Key | Long-context coding, agent swarms |
| **OpenRouter** | 100+ models | Auth Token | Model flexibility, pay-per-use |
| **CCRouter** | Ollama, DeepSeek, etc. | Optional | Local-first development |
| **Ollama** | Local + cloud models | Auth Token | Local-first + hybrid setups |
| **GatewayZ** | Multi-provider gateway | Auth Token | Centralized routing |
| **Vercel** | Multi-provider gateway | Auth Token | Vercel AI Gateway |
| **NanoGPT** | Claude Code endpoint | Auth Token | Simple endpoint setup |

### Quick Start Commands

```bash
# Vanilla isolated Claude Code
npx cc-mirror quick --provider mirror --name mclaude

# Z.ai (GLM models)
npx cc-mirror quick --provider zai --api-key "$Z_AI_API_KEY"

# MiniMax (M2.1)
npx cc-mirror quick --provider minimax --api-key "$MINIMAX_API_KEY"

# Kimi Code (kimi-for-coding)
npx cc-mirror quick --provider kimi --api-key "$KIMI_API_KEY"

# OpenRouter (100+ models)
npx cc-mirror quick --provider openrouter --api-key "$OPENROUTER_API_KEY" \
  --model-sonnet "anthropic/claude-sonnet-4-20250514"

# Ollama (local models)
npx cc-mirror quick --provider ollama --api-key "ollama" \
  --model-sonnet "qwen3-coder" --model-opus "qwen3-coder" --model-haiku "qwen3-coder"

# DeepSeek via CCRouter
npx cc-mirror quick --provider ccrouter
```

### Key Features

- **Isolated configs** - Each variant has its own config, sessions, MCP servers, credentials
- **Brand themes** - Custom color themes per provider via tweakcc
- **Version pinning** - Can track stable/latest or pin specific versions
- **Prompt packs** - Provider-optimized prompts for better model performance

---

## OpenRouter Tool Calling Status

### Current State (February 2026)

**Tool calling via OpenRouter is now functional** for most models. OpenRouter standardizes the tool calling interface across models and providers.

### Top Tool-Calling Models on OpenRouter

Based on weekly usage data (February 2026):

| Model | Context | Input Price | Output Price | Notes |
|-------|---------|-------------|--------------|-------|
| **Gemini 3 Flash Preview** | 1.05M | $0.50/M | $3/M | #1 tool calling model, agentic workflows |
| **Claude Sonnet 4.5** | 1M | $3/M | $15/M | #1 for technology tasks |
| **DeepSeek V3.2** | 164K | $0.25/M | $0.38/M | Great value, GPT-5 class reasoning |
| **Kimi K2.5** | 262K | $0.45/M | $2.50/M | #1 for programming, agent swarms |
| **Gemini 2.5 Flash** | 1.05M | $0.30/M | $2.50/M | Strong reasoning, configurable |
| **Claude Opus 4.5** | 200K | $5/M | $25/M | Frontier reasoning |
| **Grok Code Fast 1** | 256K | $0.20/M | $1.50/M | Economical coding model |
| **MiniMax M2.1** | 197K | $0.27/M | $1.10/M | Lightweight, coding-optimized |
| **Grok 4.1 Fast** | 2M | $0.20/M | $0.50/M | 2M context, best for research |
| **GLM 4.7** | 203K | $0.40/M | $1.50/M | Enhanced programming capabilities |

### Known Issues

1. **Gemini 3 via OpenRouter** - There are reported HTTP 400 errors with function calling (GitHub issue #1081 on claude-code-router). Reasoning details must be preserved for multi-turn tool calling.

2. **The `--jinja` flag** - When using Claude Code with local/cloud models via routers, the `--jinja` flag is **essential** for tool calling to work:
   > "The --jinja flag is important -- without it, tool calling doesn't work. I learned this the hard way."

3. **Reasoning preservation** - Some models (MiniMax M2.1, Gemini 3 Pro) require preserving reasoning between turns to avoid performance degradation.

---

## Model Provider Options

### 1. Z.ai (GLM Models)

**Official docs:** https://docs.z.ai/devpack/tool/claude

| Model | Release | Key Features |
|-------|---------|--------------|
| GLM-4.5 | July 2025 | Reasoning, coding, agentic abilities |
| GLM-4.6 | Late 2025 | Agentic performance, competitive pricing |
| GLM-4.7 | Dec 2025 | Advanced coding, stable multi-step reasoning |
| GLM-5 | Early 2026 | Open-sourced, vibe coding to agentic engineering |

**Integration notes:**
- "When Claude Code thinks it's calling Sonnet or Opus, it's actually using GLM-4.7 through Z.ai's API"
- GLM Coding Plan offers ~3x usage at fraction of Claude cost
- Reported ~80% as good as native Claude Code
- Works with Claude Code, Kilo Code, Roo Code, Cline, Droid, OpenCode

### 2. MiniMax (M2.1)

**Official docs:** https://platform.minimaxi.com/docs/guides/text-ai-coding-tools

**Key features:**
- Only 10 billion activated parameters (lightweight)
- 49.4% on Multi-SWE-Bench, 72.5% on SWE-Bench Multilingual
- Native tool calling capabilities
- Compatible with Anthropic's Claude API interface
- Preserves reasoning between turns (important for multi-turn)

**Pricing:** $0.27/M input, $1.10/M output

### 3. Kimi (K2.5)

**Official docs:** https://platform.moonshot.ai/docs/guide/agent-support

**Key features:**
- 256K context window
- Visual coding capability
- Agent swarm paradigm (up to 100 sub-agents, 1,500 parallel tool calls)
- Strong for general reasoning and agentic tool-calling

**Pricing:** $0.45/M input, $2.50/M output

### 4. DeepSeek (V3.2)

**Official docs:** https://api-docs.deepseek.com/guides/anthropic_api

**Key features:**
- Official Anthropic API compatibility guide
- DeepSeek Sparse Attention (DSA) for efficiency
- GPT-5 class reasoning at much lower cost
- Gold-medal results on 2025 IMO and IOI

**Known issues:**
- vLLM deployments may not fully support tool calling
- API Error 422 reported with deepseek-chat

**Pricing:** $0.25/M input, $0.38/M output (extremely cost-effective)

### 5. OpenRouter (Multi-Model Gateway)

**Tool calling collection:** https://openrouter.ai/collections/tool-calling-models

**Advantages:**
- Single API key for 100+ models
- Standardized tool calling interface
- Pay-per-use across all providers
- Easy model switching

**Configuration example:**
```bash
npx cc-mirror quick --provider openrouter --api-key "$OPENROUTER_API_KEY" \
  --model-sonnet "anthropic/claude-sonnet-4-20250514"
```

---

## Implementation Recommendations

### Recommended Setup for Multi-Provider Usage

#### Option A: cc-mirror (Easiest)

```bash
# Install cc-mirror
npm install -g cc-mirror

# Create variants for different providers
npx cc-mirror quick --provider mirror --name mclaude      # Vanilla Claude
npx cc-mirror quick --provider zai --name glm             # Z.ai GLM models
npx cc-mirror quick --provider openrouter --name orouter  # OpenRouter

# Run them
mclaude    # Vanilla Claude
glm        # GLM-4.7
orouter    # OpenRouter (access to all models)
```

#### Option B: claude-code-router (More Control)

**Repository:** https://github.com/musistudio/claude-code-router

```bash
# Install
npm install -g @anthropic-ai/claude-code
npm install -g claude-code-router

# Create config at ~/.claude-code-router/config.json
{
  "providers": {
    "openrouter": {
      "baseURL": "https://openrouter.ai/api",
      "apiKey": "${OPENROUTER_API_KEY}"
    },
    "deepseek": {
      "baseURL": "https://api.deepseek.com",
      "apiKey": "${DEEPSEEK_API_KEY}"
    }
  },
  "models": {
    "sonnet": "anthropic/claude-sonnet-4-20250514",
    "opus": "anthropic/claude-opus-4-20250514"
  }
}

# Run with --jinja flag for tool calling
claude-code-router --jinja
```

#### Option C: Manual Environment Variables

```bash
# Switch between providers via environment variables

# Native Claude
export ANTHROPIC_API_KEY="sk-..."
claude

# Via OpenRouter
export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
export ANTHROPIC_API_KEY="sk-or-..."
claude

# Via Z.ai (GLM)
export ANTHROPIC_BASE_URL="https://api.z.ai/v1"
export ANTHROPIC_API_KEY="zai-..."
claude
```

### Recommended Model Selection

| Use Case | Recommended Model | Via |
|----------|-------------------|-----|
| **Heavy coding (cost-effective)** | GLM-4.7 | Z.ai direct |
| **Budget coding** | DeepSeek V3.2 | OpenRouter or direct |
| **Long context / agent swarms** | Kimi K2.5 | OpenRouter or direct |
| **Fast agentic workflows** | Gemini 3 Flash Preview | OpenRouter |
| **Maximum quality** | Claude Opus 4.5 | Native or OpenRouter |
| **Local/offline** | Qwen3-Coder | Ollama via cc-mirror |

### Environment Variable Strategy

Create shell aliases or scripts:

```bash
# ~/.bashrc or ~/.zshrc

# Native Claude
alias claude-native='unset ANTHROPIC_BASE_URL && ANTHROPIC_API_KEY="$ANTHROPIC_NATIVE_KEY" claude'

# OpenRouter
alias claude-or='ANTHROPIC_BASE_URL="https://openrouter.ai/api" ANTHROPIC_API_KEY="$OPENROUTER_API_KEY" claude'

# Z.ai GLM
alias claude-glm='ANTHROPIC_BASE_URL="https://api.z.ai/v1" ANTHROPIC_API_KEY="$ZAI_API_KEY" claude'

# DeepSeek
alias claude-ds='ANTHROPIC_BASE_URL="https://api.deepseek.com" ANTHROPIC_API_KEY="$DEEPSEEK_API_KEY" claude'
```

---

## Cost Comparison

| Provider | Model | Input | Output | Relative to Claude Sonnet |
|----------|-------|-------|--------|--------------------------|
| Anthropic | Claude Sonnet 4.5 | $3/M | $15/M | 1x (baseline) |
| Anthropic | Claude Opus 4.5 | $5/M | $25/M | 1.7x |
| DeepSeek | V3.2 | $0.25/M | $0.38/M | **12x cheaper** |
| Z.ai | GLM-4.7 | $0.40/M | $1.50/M | **10x cheaper** |
| MiniMax | M2.1 | $0.27/M | $1.10/M | **13x cheaper** |
| Kimi | K2.5 | $0.45/M | $2.50/M | **6x cheaper** |
| OpenRouter | Gemini 3 Flash | $0.50/M | $3/M | **5x cheaper** |

---

## Resources / Links

### Tools

- [cc-mirror](https://github.com/numman-ali/cc-mirror) - Multi-instance Claude Code manager
- [claude-code-router](https://github.com/musistudio/claude-code-router) - Route Claude Code to any LLM
- [tweakcc](https://github.com/numman-ali/tweakcc) - Theme and customize Claude Code

### Provider Documentation

- [OpenRouter Tool Calling Models](https://openrouter.ai/collections/tool-calling-models)
- [Z.ai Claude Code Integration](https://docs.z.ai/devpack/tool/claude)
- [MiniMax AI Coding Tools Guide](https://platform.minimaxi.com/docs/guides/text-ai-coding-tools)
- [Kimi Agent Support Guide](https://platform.moonshot.ai/docs/guide/agent-support)
- [DeepSeek Anthropic API Compatibility](https://api-docs.deepseek.com/guides/anthropic_api)

### Tutorials

- [Run Claude Code with Local & Cloud Models](https://medium.com/@luongnv89/run-claude-code-on-local-cloud-models-in-5-minutes-ollama-openrouter-llama-cpp-6dfeaee03cda) - Covers `--jinja` flag importance
- [Beyond Anthropic: Using Claude Code with Any Model](https://lgallardo.com/2025/08/20/claude-code-router-openrouter-beyond-anthropic/) - Claude Code Router guide
- [GLM-4.7 vs Claude Code Comparison](https://zoer.ai/posts/zoer/z-ai-glm-4-6-vs-claude-code-comparison)

### Community

- [r/ClaudeCode subreddit](https://www.reddit.com/r/ClaudeCode/)
- [Claude Code Router Issues](https://github.com/musistudio/claude-code-router/issues) - Active community troubleshooting

---

## Your Specific Setup (Khamel)

### Current State
- `zai` → wrapper script with ZAI_API_KEY + YOLO mode
- `cc` → native Claude Pro plan auth + YOLO mode

### Target State (cc-mirror based)

| Command | Provider | Model | Visual Theme |
|---------|----------|-------|--------------|
| `cc` | Native Anthropic | Claude Pro (your auth) | Default |
| `zai` | Z.ai | GLM-5 | Dark carbon + gold |
| `ds` | CCRouter | DeepSeek V3.2 | Sky blue |
| `kimi` | OpenRouter | Kimi K2.5 | Teal/cyan gradient |
| `mini` | OpenRouter | MiniMax M2.1 | Coral/red/orange |
| `gemini` | Gemini CLI | Gemini 3 | (separate tool) |

### Setup Commands

```bash
# Install cc-mirror
npm install -g cc-mirror

# 1. Vanilla Claude (isolated from your main install)
npx cc-mirror quick --provider mirror --name cc

# 2. Z.ai GLM-5 (replaces your current zai wrapper)
npx cc-mirror quick --provider zai --name zai --api-key "$ZAI_API_KEY"

# 3. DeepSeek via CCRouter
npx cc-mirror quick --provider ccrouter --name ds

# 4. Kimi K2.5 via OpenRouter
npx cc-mirror quick --provider openrouter --name kimi \
  --api-key "$OPENROUTER_API_KEY" \
  --model-sonnet "moonshotai/kimi-k2.5"

# 5. MiniMax M2.5 via OpenRouter (NEW - Feb 2026)
npx cc-mirror quick --provider openrouter --name mini \
  --api-key "$OPENROUTER_API_KEY" \
  --model-sonnet "minimax/minimax-m2.5"
```

### Key Benefits Over Current Approach

1. **Isolated instances** - Each has its own `~/.cc-mirror/<name>/config/` directory
2. **Visual differentiation** - Each provider has a unique theme (gold for Z.ai, coral for MiniMax, etc.)
3. **Auto-updating** - `cc-mirror update zai` or track `--claude-version latest`
4. **Separate sessions/MCP** - No config conflicts between instances
5. **Your main Claude untouched** - Native `claude` command still works as-is

### Update Commands

```bash
# Update all variants to latest Claude Code
npx cc-mirror update

# Update specific variant
npx cc-mirror update zai

# Track stable channel (less bleeding edge)
npx cc-mirror update zai --claude-version stable
```

---

## Conclusion

Multi-provider Claude Code is **highly viable** with mature tooling available:

1. **For ease of use:** Use `cc-mirror` to create isolated instances per provider
2. **For flexibility:** Use `claude-code-router` with OpenRouter for access to 100+ models
3. **For cost savings:** GLM-4.7, DeepSeek V3.2, and MiniMax M2.1 offer 10-12x cost reduction
4. **For maximum quality:** Stick with native Claude Opus 4.5 / Sonnet 4.5

The critical gotcha is the `--jinja` flag when using routers - without it, tool calling may fail silently.

---

## Final Working Solution (Feb 2026)

After testing cc-mirror, we went back to a simpler approach using shell functions.

### What Didn't Work
- **cc-mirror**: Installed old Claude Code version (2.1.1), had bugs with mode switching, npm deprecation warnings
- **Aliases**: Couldn't properly unset environment variables
- **ANTHROPIC_API_KEY**: Many providers need `ANTHROPIC_AUTH_TOKEN` instead

### What Worked
Shell functions in `~/.bashrc` with:
1. **Separate config directories** (`~/.claude-zai`, `~/.claude-ds`, etc.) to avoid auth conflicts
2. **ANTHROPIC_AUTH_TOKEN** (not API_KEY) for most providers
3. **--jinja flag** for OpenRouter providers (critical for tool calling)
4. **--model flag** to specify the model

### Working Functions

```bash
# zai - GLM-5 via Z.ai (direct API)
zai() {
    CLAUDE_CONFIG_DIR="$HOME/.claude-zai" \
    ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    ANTHROPIC_AUTH_TOKEN="$ZAI_API_KEY" \
    claude --dangerously-skip-permissions --model glm-5 "$@"
}

# ds - DeepSeek (direct API)
ds() {
    CLAUDE_CONFIG_DIR="$HOME/.claude-ds" \
    ANTHROPIC_BASE_URL="https://api.deepseek.com" \
    ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY" \
    claude --dangerously-skip-permissions --model deepseek-chat "$@"
}

# kimi - Kimi K2.5 via OpenRouter (needs --jinja)
kimi() {
    CLAUDE_CONFIG_DIR="$HOME/.claude-kimi" \
    ANTHROPIC_BASE_URL="https://openrouter.ai/api" \
    ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY" \
    claude --dangerously-skip-permissions --jinja --model moonshotai/kimi-k2.5 "$@"
}

# mini - MiniMax M2.5 via OpenRouter (needs --jinja)
mini() {
    CLAUDE_CONFIG_DIR="$HOME/.claude-mini" \
    ANTHROPIC_BASE_URL="https://openrouter.ai/api" \
    ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY" \
    claude --dangerously-skip-permissions --jinja --model minimax/minimax-m2.5 "$@"
}
```

### Key Learnings
1. **Auth conflicts**: Use separate `CLAUDE_CONFIG_DIR` for each provider
2. **Token vs Key**: Use `ANTHROPIC_AUTH_TOKEN` for Z.ai, OpenRouter, DeepSeek
3. **Tool calling via routers**: The `--jinja` flag is ESSENTIAL for OpenRouter
4. **Keep it simple**: cc-mirror added complexity without clear benefits for this use case
