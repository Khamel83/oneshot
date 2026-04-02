# OpenCode CLI Documentation

> Cached from https://opencode.ai/docs on 2026-04-01
> Open-source AI coding agent with TUI, desktop app, and IDE extensions.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Agents](#agents)
- [Providers](#providers)

---

## Getting Started

OpenCode is an open-source AI coding agent. It provides terminal, desktop app, and IDE extension interfaces.

### Prerequisites

To use OpenCode in the terminal, you need:

1. A modern terminal emulator (WezTerm, Alacritty, Ghostty, Kitty)
2. API keys for the LLM providers you want to use

### Quick Start

1. Run `/connect` to configure API keys
2. Navigate to your project directory
3. Run OpenCode -- it will analyze your project and create an `AGENTS.md` file
4. Start asking questions or requesting changes

### Usage Patterns

**Ask questions**: `How is authentication handled in @packages/functions/src/api/index.ts`

**Plan mode** (Tab key to toggle): Describe what you want, OpenCode suggests how without making changes

**Build mode** (Tab key to toggle): OpenCode implements the plan

**Undo/Redo**: `/undo` and `/redo` commands to revert or re-apply changes

**Share**: Conversations can be shared via generated links

---

## Installation

### Install Script (recommended)

```bash
curl -fsSL https://opencode.ai/install | bash
```

### Node.js

```bash
npm install -g opencode-ai
```

### Homebrew (macOS/Linux)

```bash
brew install anomalyco/tap/opencode
```

> Use the OpenCode tap for latest version. Official `brew install opencode` formula updates less frequently.

### Arch Linux

```bash
sudo pacman -S opencode           # Stable
paru -S opencode-bin              # Latest from AUR
```

### Other Methods

- **Mise**: `mise use -g github:anomalyco/opencode`
- **Docker**: `docker run -it --rm ghcr.io/anomalyco/opencode`
- **NPM**: `npm install -g opencode-ai` (Windows compatible)
- Direct binary downloads from Releases page

---

## Configuration

### Connecting Providers

1. Run `/connect` in the TUI, select a provider, follow auth flow
2. Recommended for beginners: **OpenCode Zen** (curated models tested by the OpenCode team)
3. Credentials stored in `~/.local/share/opencode/auth.json`

### Config File

Configuration lives in `opencode.json` at project root:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "anthropic": {
      "options": {
        "baseURL": "https://api.anthropic.com/v1"
      }
    }
  },
  "agent": {
    "build": {
      "model": "anthropic/claude-sonnet-4-20250514"
    }
  }
}
```

**Note**: The `/docs/configuration` page returned 403 (blocked) when caching. Provider config and agent config sections are documented above and below from the providers and agents pages.

---

## Agents

OpenCode has two types of agents: **primary** (you interact directly) and **subagents** (called by primary agents or via `@` mention).

### Built-in Primary Agents

| Agent | Description | Tools |
|-------|-------------|-------|
| **Build** | Default agent with all tools enabled | All |
| **Plan** | Restricted agent for planning/analysis only | Read-only (file edits and bash set to `ask`) |

### Built-in Subagents

| Agent | Description | Tools |
|-------|-------------|-------|
| **General** | General-purpose research and multi-step tasks | All (except todo) |
| **Explore** | Fast read-only codebase exploration | Read-only |

### System Agents (hidden, auto-run)

- **Compaction**: Compresses long context into smaller summaries
- **Title**: Generates session titles
- **Summary**: Creates session summaries

### Agent Configuration (JSON)

In `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "{file:./prompts/build.txt}",
      "tools": {
        "write": true,
        "edit": true,
        "bash": true
      }
    },
    "plan": {
      "mode": "primary",
      "model": "anthropic/claude-haiku-4-20250514",
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      }
    },
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "tools": {
        "write": false,
        "edit": false
      }
    }
  }
}
```

### Agent Configuration (Markdown)

Place `.md` files in:
- Global: `~/.config/opencode/agents/`
- Project-level: `.opencode/agents/`

Filename becomes the agent name. Example `.opencode/agents/review.md`:

```markdown
---
description: Reviews code for quality and best practices
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
tools:
  write: false
  edit: false
  bash: false
---

You are in code review mode. Focus on:
- Code quality and best practices
- Potential bugs and edge cases
- Performance implications
- Security considerations
Provide constructive feedback without making direct changes.
```

### Agent Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `description` | Brief description (required for subagents) | - |
| `mode` | `primary`, `subagent`, or `all` | `all` |
| `model` | Override model with `provider/model-id` format | Default model |
| `prompt` | System prompt file path: `{file:./prompts/foo.txt}` | Built-in |
| `tools` | Object of tool names to `true`/`false` | All enabled |
| `temperature` | 0.0-1.0 (0=deterministic, 1=creative) | Model default |
| `top_p` | Alternative to temperature for diversity | Model default |
| `steps` | Max agent iterations before text-only response | Unlimited |
| `disable` | Set `true` to disable agent | `false` |
| `hidden` | Hide subagent from `@` autocomplete menu | `false` |
| `color` | UI color (hex or theme name) | Default |
| `permission` | Per-agent permission overrides | Inherited |
| `permission.task` | Control which subagents can be called via Task tool | - |

### Permissions

Configure what agents can do:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "deny"
  },
  "agent": {
    "build": {
      "permission": {
        "edit": "ask"
      }
    }
  }
}
```

Permission values: `"ask"` (prompt), `"allow"` (auto-approve), `"deny"` (block)

Per-agent bash command permissions with glob patterns:

```json
{
  "agent": {
    "build": {
      "permission": {
        "bash": {
          "*": "ask",
          "git diff": "allow",
          "git log*": "allow"
        }
      }
    }
  }
}
```

Last matching rule wins. Place `*` first, specific rules after.

### Usage

- **Switch primary agents**: `Tab` key or configured `switch_agent` shortcut
- **Call subagents**: `@general help me search for this function`
- **Navigate sessions**: `<Leader>+Right` / `<Leader>+Left` to cycle parent/child sessions

### Example Agents

**Documentation Agent**:
```markdown
---
description: Writes and maintains project documentation
mode: subagent
tools:
  bash: false
---
You are a technical writer. Create clear, comprehensive documentation.
```

**Security Audit Agent**:
```markdown
---
description: Performs security audits and identifies vulnerabilities
mode: subagent
tools:
  write: false
  edit: false
---
You are a security expert. Focus on identifying potential security issues.
```

---

## Providers

OpenCode supports **75+ LLM providers** via AI SDK and Models.dev, including local models.

### Quick Setup

1. `/connect` to add API key
2. Configure provider in `opencode.json` if needed
3. `/models` to select a model

### Notable Providers

| Provider | Notes |
|----------|-------|
| **Anthropic** | Claude Pro/Max subscription or API key |
| **OpenAI** | ChatGPT Plus/Pro subscription or API key |
| **OpenCode Zen** | Curated models tested by OpenCode team |
| **GitHub Copilot** | Device flow auth at github.com/login/device |
| **GitLab Duo** | OAuth or PAT, with plugin for MR/issue tools |
| **Amazon Bedrock** | AWS credentials, profile, or bearer token |
| **Google Vertex AI** | Service account JSON or gcloud CLI auth |
| **Azure OpenAI** | Resource name + API key |
| **Ollama** | Local models via OpenAI-compatible API |
| **LM Studio** | Local models via OpenAI-compatible API |
| **llama.cpp** | Local models via llama-server |

### Custom Provider (OpenAI-compatible)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "myprovider": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "My AI Provider Display Name",
      "options": {
        "baseURL": "https://api.myprovider.com/v1",
        "apiKey": "{env:MY_API_KEY}",
        "headers": {
          "Authorization": "Bearer custom-token"
        }
      },
      "models": {
        "my-model-name": {
          "name": "My Model Display Name",
          "limit": {
            "context": 200000,
            "output": 65536
          }
        }
      }
    }
  }
}
```

Key fields:
- `npm`: `@ai-sdk/openai-compatible` for `/v1/chat/completions`, `@ai-sdk/openai` for `/v1/responses`
- `options.baseURL`: API endpoint
- `options.apiKey`: Can use `{env:VAR_NAME}` syntax
- `options.headers`: Custom headers per request
- `limit.context` / `limit.output`: Token limits for context display

### Local Models

**Ollama**:
```json
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": { "baseURL": "http://localhost:11434/v1" },
      "models": { "llama2": { "name": "Llama 2" } }
    }
  }
}
```

**LM Studio**:
```json
{
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LM Studio (local)",
      "options": { "baseURL": "http://127.0.0.1:1234/v1" },
      "models": { "google/gemma-3n-e4b": { "name": "Gemma 3n-e4b (local)" } }
    }
  }
}
```

### Troubleshooting

1. `opencode auth list` to check stored credentials
2. Verify provider ID matches between `/connect` and `opencode.json`
3. Use correct npm package (`@ai-sdk/cerebras` for Cerebras, `@ai-sdk/openai-compatible` for others)
4. Check `options.baseURL` is correct

---

## Cached Pages

| Page | URL | Status |
|------|-----|--------|
| Main docs | https://opencode.ai/docs | OK |
| Configuration | https://opencode.ai/docs/configuration | 403 (blocked) |
| Agents | https://opencode.ai/docs/agents | OK |
| Providers | https://opencode.ai/docs/providers | OK (bonus) |
