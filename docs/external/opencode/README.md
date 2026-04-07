# OpenCode CLI Documentation

> Cached from https://opencode.ai/docs on 2026-04-07 (v1.3.13)
> Open-source AI coding agent with TUI, desktop app, and IDE extensions.
> Provider-agnostic: supports 75+ LLM providers natively.

---

## Quick Start

```bash
curl -fsSL https://opencode.ai/install | bash
# or: npm install -g opencode-ai
# or: brew install anomalyco/tap/opencode
```

Run `/init` in a project to generate `AGENTS.md`. Run `/connect` to add API keys.

---

## Config File: `opencode.json`

### Full Schema

```jsonc
{
  "$schema": "https://opencode.ai/config.json",

  // Default model (provider/model-id format)
  "model": "openrouter/google/gemini-2.5-flash",
  "small_model": "provider/model",     // for title generation etc
  "default_agent": "build",            // primary agent name
  "username": "ubuntu",

  // Instructions (loaded as system context)
  "instructions": ["AGENTS.md"],       // file paths, string array

  // Provider config (see Providers section below)
  "provider": { },

  // Commands (see Commands section below)
  "command": { },

  // Agents (see Agents section below)
  "agent": { },

  // Permissions (see Tools section below)
  "permission": { },

  // MCP servers (see MCP section below)
  "mcp": { },

  // Tools — enable/disable specific tools
  "tools": { "tool_name": true/false },

  // Misc
  "logLevel": "INFO",                  // DEBUG | INFO | WARN | ERROR
  "share": "manual",                   // manual | auto | disabled
  "autoupdate": true,
  "snapshot": true,                    // filesystem snapshots for undo
  "disabled_providers": ["copilot"],
  "enabled_providers": ["openrouter", "anthropic"],
  "plugin": ["npm-module-name"],
  "compaction": { "auto": true, "prune": true, "reserved": 1000 },
  "skills": { "paths": ["/path/to/skills/"], "urls": ["https://..."] },
  "watcher": { "ignore": ["node_modules", ".git"] },
  "formatter": { },
  "lsp": { },
  "server": { "port": 4096, "hostname": "127.0.0.1" }
}
```

### File Locations

| Path | Purpose |
|------|---------|
| `.opencode/opencode.json` | Project-level config (this is the one that matters) |
| `~/.config/opencode/` | Global config dir |
| `~/.local/share/opencode/` | Runtime data: `opencode.db`, `log/`, `snapshot/` |
| `~/.cache/opencode/` | Cache dir |
| `~/.local/state/opencode/` | State dir |

### Env Var Interpolation

Use `{env:VAR_NAME}` in any string value:
```json
{ "provider": { "anthropic": { "options": { "apiKey": "{env:ANTHROPIC_API_KEY}" } } } }
```

---

## Providers

OpenCode supports 75+ LLM providers. Key ones:

| Provider | Config ID | Notes |
|----------|-----------|-------|
| Anthropic | `anthropic` | Supports Claude Pro/Max subscription via `/connect` |
| OpenAI | `openai` | Supports ChatGPT Plus/Pro subscription |
| OpenRouter | `openrouter` | Multi-model routing, many models preloaded |
| Google Vertex AI | `google-vertex-ai` | Requires `GOOGLE_APPLICATION_CREDENTIALS` |
| Z.AI | `z-ai` | GLM models, supports GLM Coding Plan |
| DeepSeek | `deepseek` | DeepSeek Reasoner etc |
| Local (Ollama) | `ollama` | Requires `@ai-sdk/openai-compatible` |
| Local (LM Studio) | `lmstudio` | Requires `@ai-sdk/openai-compatible` |
| OpenCode Zen | `opencode` | Curated models tested by OpenCode team |

### Adding a Provider

1. Run `/connect` → select provider → enter API key
2. Credentials stored in `~/.local/share/opencode/auth.json`
3. Run `/models` to select a model

### Custom Provider (OpenAI-compatible)

```json
{
  "provider": {
    "myprovider": {
      "npm": "@ai-sdk/openai-compatible",    // for /v1/chat/completions
      "name": "My Provider Display Name",
      "options": {
        "baseURL": "https://api.myprovider.com/v1",
        "apiKey": "{env:MY_API_KEY}"
      },
      "models": {
        "my-model": {
          "name": "My Model Display Name",
          "limit": { "context": 200000, "output": 65536 }
        }
      }
    }
  }
}
```

**npm package choice**: Use `@ai-sdk/openai-compatible` for `/v1/chat/completions` endpoints, `@ai-sdk/openai` for `/v1/responses`.

---

## Agents

Two types: **primary** (direct interaction) and **subagent** (specialized, called via `@` mention or Task tool).

### Built-in Agents

| Agent | Mode | Purpose |
|-------|------|---------|
| `build` | primary | Default, all tools enabled |
| `plan` | primary | Analysis/planning only, no edits |
| `general` | subagent | General-purpose, full tools (except todo) |
| `explore` | subagent | Fast read-only codebase exploration |
| `compaction` | internal (hidden) | Context compression |
| `title` | internal (hidden) | Session title generation |
| `summary` | internal (hidden) | Session summary |

### Defining Agents

**In opencode.json:**
```json
{
  "agent": {
    "reviewer": {
      "description": "Reviews code for best practices",
      "mode": "subagent",
      "model": "openrouter/google/gemini-2.5-flash",
      "temperature": 0.1,
      "steps": 10,                        // max iterations (optional)
      "prompt": "You are a code reviewer...", // or "{file:./prompts/review.txt}"
      "tools": {
        "write": false,
        "edit": false,
        "bash": false
      },
      "permission": {
        "bash": {
          "git diff": "allow",
          "git log*": "allow",
          "*": "deny"
        }
      },
      "hidden": false,                    // hide from @ autocomplete
      "color": "#FF5733"                   // hex or theme color name
    }
  }
}
```

**As Markdown file** (`.opencode/agents/reviewer.md`):
```markdown
---
description: Reviews code for quality
mode: subagent
model: openrouter/google/gemini-2.5-flash
temperature: 0.1
tools:
  write: false
  edit: false
  bash: false
---

You are a code reviewer. Focus on security, performance, and maintainability.
```

Markdown file name = agent name. Locations:
- Global: `~/.config/opencode/agents/`
- Project: `.opencode/agents/`

### Key Agent Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `mode` | string | `"all"` | `"primary"`, `"subagent"`, or `"all"` |
| `model` | string | (default) | Override model for this agent |
| `temperature` | float | (model default) | 0.0-1.0, controls randomness |
| `steps` | int | (unlimited) | Max agent iterations before forced summary |
| `prompt` | string | (built-in) | Custom system prompt; use `{file:./path}` for file reference |
| `description` | string | **required** | What this agent does |
| `hidden` | bool | false | Hide from @ autocomplete (subagent only) |
| `disable` | bool | false | Disable this agent |
| `color` | string | (default) | Hex color or theme name |
| `tools` | object | (all enabled) | Per-tool boolean enable/disable |
| `permission` | object | (inherited) | Per-tool permission overrides |

### Task Permissions (controlling which subagents an agent can call)

```json
{
  "agent": {
    "orchestrator": {
      "permission": {
        "task": {
          "*": "deny",
          "code-reviewer": "ask"
        }
      }
    }
  }
}
```

---

## Commands

Custom commands are prompts triggered by `/name`. Defined in `opencode.json` or as markdown files.

### In opencode.json

```json
{
  "command": {
    "test": {
      "template": "Run tests and show failures",
      "description": "Run tests with coverage",
      "agent": "build",              // optional: run with specific agent
      "model": "provider/model",    // optional: override model
      "subtask": false              // optional: force subtask mode
    }
  }
}
```

### As Markdown File (`.opencode/commands/test.md`)

```markdown
---
description: Run tests with coverage
agent: build
model: anthropic/claude-sonnet-4-20250514
---

Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.
```

File name = command name. Locations:
- Global: `~/.config/opencode/commands/`
- Project: `.opencode/commands/`

### Prompt Placeholders

| Syntax | Description |
|--------|-------------|
| `$ARGUMENTS` | User-provided arguments |
| `$1`, `$2`, `$3` | Positional arguments |
| `` !`command` `` | Shell output injection (runs in project root) |
| `@filename` | File content inclusion |

Example:
```markdown
---
description: Review recent changes
---

Recent git commits:
!`git log --oneline -10`

Review these changes and suggest improvements.
```

---

## Tools

### Built-in Tools

| Tool | Permission Key | Description |
|------|---------------|-------------|
| `bash` | `bash` | Execute shell commands |
| `read` | `read` | Read file contents (supports offset/limit) |
| `write` | `write` | Create or overwrite files |
| `edit` | `edit` | Find-replace in existing files |
| `grep` | `grep` | Regex content search (ripgrep) |
| `glob` | `glob` | File pattern matching (ripgrep) |
| `list` | `list` | List directory contents |
| `patch` | `patch` | Apply patch files |
| `lsp` | `lsp` | LSP operations (experimental) |
| `skill` | `skill` | Load a SKILL.md file |
| `todowrite` | `todowrite` | Session-scoped task tracking |
| `webfetch` | `webfetch` | Fetch URL content |
| `websearch` | `websearch` | Web search (Exa AI, no API key needed) |
| `question` | `question` | Ask user questions interactively |
| `task` | `task` | Spawn subagent tasks |
| `batch` | `batch` | Execute up to 25 tool calls in parallel |
| `plan_exit` | `plan_exit` | Exit plan mode, switch to build |

### Permission System

```json
{
  "permission": {
    // Simple: string action
    "bash": "ask",           // "ask" | "allow" | "deny"
    "todowrite": "allow",
    "question": "deny",

    // Pattern-based: glob → action
    "read": {
      "*": "allow",
      "*.env": "ask"
    },
    "bash": {
      "*": "ask",
      "git push *": "ask",
      "git status *": "allow",
      "grep *": "allow",
      "python -m core.*": "allow"
    },
    "external_directory": {
      "*": "ask",
      "/home/ubuntu/.claude/skills/*": "allow"
    }
  }
}
```

**Rules**: Last match wins. Put `*` wildcard first, specific rules after.

Pattern-based permissions available for: `read`, `edit`, `glob`, `grep`, `list`, `bash`, `task`, `external_directory`, `lsp`, `skill`.

Wildcard for MCP tools: `mymcp_*` matches all tools from `mymcp` server.

### `.ignore` file

To include `.gitignore`d files in search/list:
```
!node_modules/
!dist/
```

---

## MCP Servers

### Local (stdio) MCP Server

```json
{
  "mcp": {
    "myserver": {
      "type": "local",
      "command": ["npx", "-y", "@some-org/mcp-server", "--arg"],
      "environment": { "API_KEY": "{env:MY_API_KEY}" },
      "enabled": true,
      "timeout": 5000
    }
  }
}
```

### Remote (SSE) MCP Server

```json
{
  "mcp": {
    "myserver": {
      "type": "remote",
      "url": "https://mcp.example.com/sse",
      "headers": { "Authorization": "Bearer ..." }
    }
  }
}
```

### CLI

```bash
opencode mcp add     # Interactive MCP server addition
opencode mcp list    # List servers and status
opencode mcp auth <name>   # OAuth authentication
opencode mcp logout <name> # Remove OAuth credentials
opencode mcp debug <name>  # Debug OAuth connection
```

---

## Session Management

| Command | Description |
|---------|-------------|
| `opencode --continue` / `-c` | Resume last session |
| `opencode --session <id>` | Resume specific session |
| `opencode --fork` | Fork a session |
| `opencode session list` | List sessions |
| `opencode session delete` | Delete a session |
| `opencode export` | Export session as JSON |
| `opencode import` | Import session from JSON |
| `opencode serve` | Headless server |
| `opencode web` | Server + web UI |
| `opencode run --format json` | JSON event stream |

---

## Other Features

| Feature | Description |
|---------|-------------|
| `opencode stats` | Token usage, cost, tool breakdowns |
| `opencode agent create` | Interactive agent creation |
| `opencode pr <number>` | Fetch + checkout PR, then run |
| `opencode db` | Interactive SQLite shell |
| `/undo` | Undo last change |
| `/redo` | Redo undone change |
| `/share` | Generate shareable link |
| LSP | goToDefinition, findReferences, hover, etc. |

---

## Annotations

> Recent agent notes from working with OpenCode

- [Configuration](annotations/2026-04-07-config.md) - Full config schema, providers, agents, commands
- [Provider Setup](annotations/2026-04-07-providers.md) - OpenRouter, Anthropic, Z.AI, custom providers
