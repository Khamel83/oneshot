# Gemini CLI Documentation

> Google's open-source AI coding agent for the terminal.
> npm package: `@google/gemini-cli` | GitHub: google-gemini/gemini-cli
> License: Apache 2.0
> Cached: 2026-04-01 | Source: https://github.com/google-gemini/gemini-cli

---

## Overview

Gemini CLI is an open-source AI agent that brings the power of Gemini directly into your terminal. It provides lightweight access to Gemini, giving you the most direct path from your prompt to the model.

### Key Selling Points

- **Free tier**: 60 requests/min and 1,000 requests/day with personal Google account
- **Powerful Gemini 3 models**: Access to improved reasoning and 1M token context window
- **Built-in tools**: Google Search grounding, file operations, shell commands, web fetching
- **Extensible**: MCP (Model Context Protocol) support for custom integrations
- **Terminal-first**: Designed for developers who live in the command line
- **Open source**: Apache 2.0 licensed

---

## Installation

```bash
# Using npx (no installation required)
npx @google/gemini-cli

# Install globally with npm
npm install -g @google/gemini-cli

# Install globally with Homebrew (macOS/Linux)
brew install gemini-cli

# Install globally with MacPorts (macOS)
sudo port install gemini-cli
```

### Release Channels

| Channel | Install Command | Cadence |
|---------|----------------|---------|
| **Stable** (recommended) | `npm install -g @google/gemini-cli@latest` | Weekly, Tuesdays UTC 20:00 |
| **Preview** | `npm install -g @google/gemini-cli@preview` | Weekly, Tuesdays UTC 23:59 |
| **Nightly** | `npm install -g @google/gemini-cli@nightly` | Daily, UTC 00:00 |

---

## Authentication

### Option 1: Sign in with Google (Recommended)

Best for individual developers. Free tier: 60 req/min, 1000 req/day.

```bash
gemini
# Choose "Sign in with Google" at the prompt
```

For Code Assist License users:
```bash
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
gemini
```

### Option 2: Gemini API Key

Best for specific model control. Free tier: 1000 req/day (Flash only).

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
gemini
```

Get key from: https://aistudio.google.com/apikey

### Option 3: Vertex AI

Best for enterprise/production workloads.

```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
export GOOGLE_GENAI_USE_VERTEXAI=true
gemini
```

### Vertex AI with ADC (gcloud)

```bash
unset GOOGLE_API_KEY GEMINI_API_KEY  # Must unset first
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="us-central1"
gemini
```

### Vertex AI with Service Account (CI/CD)

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/keyfile.json"
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
gemini
```

### Persisting Environment Variables

Use `.gemini/.env` files (auto-loaded by Gemini CLI):
```bash
mkdir -p ~/.gemini
cat >> ~/.gemini/.env <<'EOF'
GOOGLE_CLOUD_PROJECT="your-project-id"
GEMINI_API_KEY="your-key"
EOF
```

Variables are loaded from the first `.env` file found (not merged). Search order:
1. Current directory `.gemini/.env`
2. Parent directories up to root
3. `~/.gemini/.env`
4. `~/.env`

---

## Quotas and Pricing

| Auth Method | Free Tier | Rate Limit |
|-------------|-----------|------------|
| Google Sign-in (Code Assist for individuals) | 1000 req/day | 60 req/min |
| Gemini API Key (unpaid) | 250 req/day | 10 req/min |
| Vertex AI (Express Mode) | 90 days no billing | Variable |
| Google AI Pro/Ultra subscription | Higher limits | 60+ req/min |
| Code Assist Standard (org) | 1500 req/day | 120 req/min |
| Code Assist Enterprise (org) | 2000 req/day | 120 req/min |
| Vertex AI (pay-as-you-go) | N/A | Dynamic shared quota |
| Gemini API Key (pay-as-you-go) | N/A | Per pricing tier |

Check usage: `/stats model` command in the CLI.

---

## Basic Usage

### Interactive Mode

```bash
# Start in current directory
gemini

# Include multiple directories
gemini --include-directories ../lib,../docs

# Use specific model
gemini -m gemini-2.5-flash
```

### Non-Interactive / Headless Mode

```bash
# Simple text response
gemini -p "Explain the architecture of this codebase"

# Structured JSON output
gemini -p "Explain the architecture" --output-format json

# Streaming JSON events (newline-delimited JSONL)
gemini -p "Run tests and deploy" --output-format stream-json

# Auto-approve all actions (YOLO mode)
gemini -p "Refactor everything" --yolo

# Pipe input
cat README.md | gemini -p "Summarize this documentation"

# Git diff for commit messages
git diff --cached | gemini -p "Write a concise commit message" --output-format json

# JSON response with stats
gemini -p "query" --output-format json | jq '.response'
```

### Headless Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| Text (default) | (none) | Human-readable output |
| JSON | `--output-format json` | Programmatic processing, includes stats + metadata |
| Stream JSON | `--output-format stream-json` | Real-time event streaming, live UI updates |

### JSON Response Schema

```json
{
  "response": "string",
  "stats": {
    "models": {
      "[model-name]": {
        "api": { "totalRequests": 2, "totalErrors": 0, "totalLatencyMs": 5053 },
        "tokens": { "prompt": 24939, "candidates": 20, "total": 25113, "cached": 21263 }
      }
    },
    "tools": {
      "totalCalls": 1,
      "totalSuccess": 1,
      "totalFail": 0,
      "totalDurationMs": 1881,
      "byName": { "google_web_search": { "count": 1, "success": 1 } }
    },
    "files": { "totalLinesAdded": 0, "totalLinesRemoved": 0 }
  },
  "error": { "type": "string", "message": "string", "code": "number" }
}
```

### Stream JSON Event Types

1. `init` - Session starts (session_id, model)
2. `message` - User prompts and assistant responses
3. `tool_use` - Tool call requests with parameters
4. `tool_result` - Tool execution results (success/error)
5. `error` - Non-fatal errors and warnings
6. `result` - Final session outcome with aggregated stats

### Key Headless Flags

| Flag | Description |
|------|-------------|
| `--prompt`, `-p` | Run in headless mode |
| `--output-format` | Output format: `text`, `json`, `stream-json` |
| `--model`, `-m` | Specify the Gemini model |
| `--debug`, `-d` | Enable debug mode |
| `--include-directories` | Include additional directories |
| `--yolo`, `-y` | Auto-approve all actions |
| `--approval-mode` | Set approval mode: `default`, `auto_edit`, `yolo`, `plan` |
| `--sandbox`, `-s` | Enable sandboxing |

---

## Configuration

### Settings File Locations

Precedence (lower overridden by higher):

1. **System defaults**: `/etc/gemini-cli/system-defaults.json` (Linux)
2. **User settings**: `~/.gemini/settings.json`
3. **Project settings**: `.gemini/settings.json`
4. **System settings** (override all): `/etc/gemini-cli/settings.json`
5. **Environment variables** (from `.env` files or shell)
6. **Command-line arguments** (highest precedence)

### Key Settings

```json
{
  "general": {
    "defaultApprovalMode": "default",
    "checkpointing": { "enabled": false },
    "maxAttempts": 10,
    "plan": { "modelRouting": true },
    "sessionRetention": { "enabled": true, "maxAge": "30d" }
  },
  "model": {
    "name": "gemini-2.5-flash",
    "maxSessionTurns": -1,
    "compressionThreshold": 0.5
  },
  "context": {
    "fileName": ["AGENTS.md", "CONTEXT.md", "GEMINI.md"]
  },
  "tools": {
    "sandbox": "docker"
  },
  "security": {
    "folderTrust": { "enabled": false }
  }
}
```

### Approval Modes

| Mode | Description |
|------|-------------|
| `default` | Prompts for approval on every tool execution |
| `auto_edit` | Auto-approves edit tools, prompts for shell commands |
| `plan` | Read-only mode, no tool execution |
| `yolo` | Auto-approve all actions (CLI flag only: `--yolo`) |

### Model Configurations (Built-in Aliases)

| Alias | Model | Thinking |
|-------|-------|----------|
| `gemini-3-pro-preview` | gemini-3-pro-preview | HIGH |
| `gemini-3-flash-preview` | gemini-3-flash-preview | HIGH |
| `gemini-2.5-pro` | gemini-2.5-pro | budget 8192 |
| `gemini-2.5-flash` | gemini-2.5-flash | budget 8192 |
| `gemini-2.5-flash-lite` | gemini-2.5-flash-lite | budget 8192 |

Custom aliases can be defined in `settings.json` under `modelConfigs.aliases`.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Gemini API key authentication |
| `GOOGLE_API_KEY` | Vertex AI API key |
| `GOOGLE_GENAI_USE_VERTEXAI` | Set to `true` for Vertex AI |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | GCP location (e.g., `us-central1`) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON key |
| `GEMINI_SANDBOX` | Sandbox mode: `true`, `docker`, `podman`, `sandbox-exec`, `runsc`, `lxc` |
| `SANDBOX_FLAGS` | Custom flags for docker/podman |
| `SEATBELT_PROFILE` | macOS seatbelt profile |
| `SANDBOX_SET_UID_GID` | Force host UID/GID mapping in sandbox |

---

## Context Files (GEMINI.md)

GEMINI.md files provide persistent instructional context to the model.

### Context Hierarchy (loaded in order)

1. **Global**: `~/.gemini/GEMINI.md` - applies to all projects
2. **Workspace**: `GEMINI.md` files in workspace directories and parents
3. **Just-in-time**: Auto-scanned when tools access a directory/file

### Example GEMINI.md

```markdown
# Project: My TypeScript Library
## General Instructions
- When you generate new TypeScript code, follow the existing coding style.
- Ensure all new functions and classes have JSDoc comments.
- Prefer functional programming paradigms where appropriate.

## Coding Style
- Use 2 spaces for indentation.
- Prefix interface names with `I` (e.g., `IUserService`).
- Always use strict equality (`===` and `!==`).
```

### Memory Commands

- `/memory show` - Display full concatenated context
- `/memory refresh` - Force re-scan of all GEMINI.md files
- `/memory add` - Append text to global `~/.gemini/GEMINI.md`

### Modular Context with Imports

```markdown
# Main GEMINI.md file
This is the main content.
@./components/instructions.md
More content here.
@../shared/style-guide.md
```

### Custom Context File Names

```json
{
  "context": {
    "fileName": ["AGENTS.md", "CONTEXT.md", "GEMINI.md"]
  }
}
```

---

## Checkpointing

Automatically saves snapshots before file modifications.

### Enable in settings.json

```json
{
  "general": {
    "checkpointing": { "enabled": true }
  }
}
```

### How it works

1. Before any file-modifying tool runs, a checkpoint is created
2. Includes: Git snapshot (in `~/.gemini/history/`), conversation history, tool call
3. Does NOT interfere with your project's own Git repository

### Using checkpoints

```
/restore                          # List available checkpoints
/restore 2025-06-22T10-00-00_000Z-my-file.txt-write_file  # Restore specific
```

Restoring: reverts files, restores conversation, re-proposes the original tool call.

---

## Custom Commands

TOML-based reusable command shortcuts.

### File Locations

1. **Global**: `~/.gemini/commands/*.toml` - available in any project
2. **Project**: `.gemini/commands/*.toml` - project-specific, can override global

### Naming

- `~/.gemini/commands/test.toml` -> `/test`
- `.gemini/commands/git/commit.toml` -> `/git:commit`

### TOML Format

```toml
description = "Generates a Git commit message based on staged changes."
prompt = """
Please generate a Conventional Commit message based on the following git diff:
```diff
!{git diff --staged}
```
"""
```

### Features

- `{{args}}` - Context-aware argument injection
- `!{command}` - Shell command execution (with confirmation)
- `@{path/to/file}` - File content injection
- `@{path/to/dir}` - Directory listing injection (respects .gitignore)

---

## Sandboxing

Isolates potentially dangerous operations from your host system.

### Sandbox Methods

| Method | Platform | Description |
|--------|----------|-------------|
| macOS Seatbelt | macOS only | Lightweight, built-in `sandbox-exec` |
| Docker/Podman | Cross-platform | Container-based, complete process isolation |
| gVisor/runsc | Linux only | User-space kernel via gVisor (strongest isolation) |
| LXC/LXD | Linux only | Full-system containers (experimental) |
| Windows Native | Windows only | Uses `icacls` for integrity levels |

### Enable Sandbox

```bash
# Command flag
gemini -s -p "analyze the code structure"

# Environment variable
export GEMINI_SANDBOX=true
gemini -p "run the test suite"

# Settings file
# { "tools": { "sandbox": "docker" } }
```

### macOS Seatbelt Profiles

| Profile | Description |
|---------|-------------|
| `permissive-open` (default) | Write restrictions, network allowed |
| `permissive-proxied` | Write restrictions, network via proxy |
| `restrictive-open` | Strict restrictions, network allowed |
| `strict-open` | Read and write restrictions, network allowed |

### Custom Sandbox Flags

```bash
export SANDBOX_FLAGS="--security-opt label=disable"
export GEMINI_SANDBOX=docker
gemini -p "build the project"
```

### gVisor Setup

```bash
# Install runsc, configure Docker daemon
docker run --runtime=runsc ...
export GEMINI_SANDBOX=runsc
gemini -p "build the project"
```

### LXC Setup

```bash
lxd init --auto
lxc launch ubuntu:24.04 gemini-sandbox
export GEMINI_SANDBOX=lxc
gemini -p "build the project"
```

---

## Trusted Folders

Security feature that requires approval before loading project-specific configs.

### Enable

```json
{
  "security": {
    "folderTrust": { "enabled": true }
  }
}
```

### Untrusted Folder Restrictions

When a folder is untrusted ("safe mode"):
1. Workspace settings are ignored (`.gemini/settings.json`)
2. Environment variables from `.env` files are ignored
3. Extensions cannot be installed/updated/uninstalled
4. Tool auto-acceptance is disabled
5. Automatic memory loading is disabled
6. MCP servers do not connect
7. Custom commands are not loaded

### Management

- `/permissions` - Change trust for current folder
- `~/.gemini/trustedFolders.json` - Central trust rules file

---

## MCP Server Integration

Configure MCP servers in `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "$GITHUB_TOKEN" }
    }
  }
}
```

Usage in CLI:
```
> @github List my open pull requests
> @slack Send a summary of today's commits to #dev channel
```

---

## GitHub Integration

Gemini CLI GitHub Action for CI/CD:
- **Pull Request Reviews**: Automated code review with contextual feedback
- **Issue Triage**: Automated labeling and prioritization
- **On-demand Assistance**: Mention `@gemini-cli` in issues/PRs
- **Custom Workflows**: Automated, scheduled, and on-demand workflows

Package: `google-github-actions/run-gemini-cli`

---

## Quick Reference: CLI Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--prompt` | `-p` | Run in headless/non-interactive mode |
| `--model` | `-m` | Specify model |
| `--sandbox` | `-s` | Enable sandboxing |
| `--yolo` | `-y` | Auto-approve all actions |
| `--approval-mode` | | `default`, `auto_edit`, `yolo`, `plan` |
| `--output-format` | | `text`, `json`, `stream-json` |
| `--include-directories` | | Include additional directories |
| `--debug` | `-d` | Enable debug mode |
| `--version` | | Show version |

---

## Related Documentation (Official)

- Official docs site: https://geminicli.com/docs/
- GitHub: https://github.com/google-gemini/gemini-cli
- NPM: https://www.npmjs.com/package/@google/gemini-cli
- Google Search Grounding: https://ai.google.dev/gemini-api/docs/grounding
- Quotas: https://developers.google.com/gemini-code-assist/resources/quotas
- Gemini API Pricing: https://ai.google.dev/gemini-api/docs/pricing
- Vertex AI Pricing: https://cloud.google.com/vertex-ai/pricing
