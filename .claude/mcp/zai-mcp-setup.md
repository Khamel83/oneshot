# ZAI MCP Server Setup Guide

**Last Updated**: 2026-02-02

This guide explains how to install and configure ZAI MCP servers for enhanced planning and development capabilities in ONE_SHOT.

---

## Overview

ZAI provides three MCP (Model Context Protocol) servers that extend Claude Code capabilities:

| MCP Server | Purpose | Tools |
|------------|---------|-------|
| **Vision MCP** | Image and video analysis | ui_to_artifact, diagnose_error_screenshot, understand_technical_diagram, analyze_data_visualization, ui_diff_check, image_analysis, video_analysis |
| **Web Search MCP** | Real-time web research | webSearchPrime |
| **Zread MCP** | GitHub repository intelligence | search_doc, get_repo_structure, read_file |

---

## Prerequisites

1. **ZAI API Key**: Get your API key from [ZAI DevPack](https://docs.z.ai/devpack/overview)
2. **Claude Code CLI**: Must be installed (`claude --version`)
3. **API Key Storage**: Store in SOPS secrets vault (recommended)

---

## Installation

### Step 1: Get Your ZAI API Key

1. Visit [ZAI DevPack](https://docs.z.ai/devpack/overview)
2. Sign up/login
3. Generate an API key
4. Store securely:

```bash
# Add to SOPS secrets vault
cd ~/github/oneshot/secrets
sops edit secrets.yaml
```

Add to `secrets.yaml`:
```yaml
zai:
  api_key: "your-zai-api-key-here"
```

### Step 2: Install Vision MCP Server

```bash
# One-click install for Claude Code
claude mcp add -s user zai-mcp-server --env Z_AI_API_KEY=your_api_key Z_AI_MODE=ZAI -- npx -y "@z_ai/mcp-server"
```

**What this does:**
- Adds MCP server to user-level Claude config
- Sets ZAI API key as environment variable
- Installs the npx package globally

**Verify installation:**
```bash
claude mcp list | grep zai-mcp-server
```

### Step 3: Install Web Search MCP Server

```bash
# One-click install (HTTP MCP server)
claude mcp add -s user -t http web-search-prime https://api.z.ai/api/mcp/web_search_prime/mcp --header "Authorization: Bearer your_api_key"
```

**What this does:**
- Adds HTTP-based MCP server to user config
- Sets Authorization header with your API key

**Verify installation:**
```bash
claude mcp list | grep web-search-prime
```

### Step 4: Install Zread MCP Server

```bash
# One-click install (HTTP MCP server)
claude mcp add -s user -t http zread https://api.z.ai/api/mcp/zread/mcp --header "Authorization: Bearer your_api_key"
```

**What this does:**
- Adds HTTP-based MCP server for GitHub repo access

**Verify installation:**
```bash
claude mcp list | grep zread
```

### Step 5: Verify All MCP Servers

```bash
# List all configured MCP servers
claude mcp list

# Expected output:
# - zai-mcp-server (stdio)
# - web-search-prime (http)
# - zread (http)
```

---

## Configuration

### MCP Config Location

MCP servers are configured in:
```
~/.claude/config.json
```

### Manual Config (if needed)

If auto-install fails, edit `~/.claude/config.json`:

```json
{
  "mcpServers": {
    "zai-mcp-server": {
      "command": "npx",
      "args": ["-y", "@z_ai/mcp-server"],
      "env": {
        "Z_AI_API_KEY": "your_api_key",
        "Z_AI_MODE": "ZAI"
      }
    },
    "web-search-prime": {
      "url": "https://api.z.ai/api/mcp/web_search_prime/mcp",
      "headers": {
        "Authorization": "Bearer your_api_key"
      }
    },
    "zread": {
      "url": "https://api.z.ai/api/mcp/zread/mcp",
      "headers": {
        "Authorization": "Bearer your_api_key"
      }
    }
  }
}
```

---

## Usage

### Vision MCP Tools

```bash
# In Claude Code, use vision tools:
claude "Analyze this screenshot: error.png"
claude "Turn this UI mockup into code: design.png"
claude "Understand this architecture diagram: arch.png"
```

### Web Search MCP Tools

```bash
# In Claude Code:
claude "Search for latest Python async best practices using Web Search MCP"
claude "Research WebSocket patterns for real-time apps"
```

### Zread MCP Tools

```bash
# In Claude Code:
claude "Explore the FastAPI repository structure using Zread MCP"
claude "Search FastAPI docs for middleware examples"
```

---

## Quota Awareness

ZAI MCP servers have quota limits based on your plan:

| Plan Tier | Web Search + Zread | Vision Pool |
|-----------|-------------------|-------------|
| Lite | 100 total/month | 5 hours |
| Pro | 1,000 total/month | 5 hours |
| Max | 4,000 total/month | 5 hours |

### Check Your Quota

```bash
# Via ZAI CLI (if installed)
zai quota

# Or via ZAI dashboard
# Visit: https://dashboard.z.ai/
```

### Best Practices

- **Prefer Web Search MCP** over built-in WebSearch (saves Claude tokens)
- **Use Zread MCP** instead of cloning repos (faster, no disk usage)
- **Check quota** before heavy MCP usage
- **Fallback to built-in tools** when quota is low

---

## Integration with ONE_SHOT Skills

The MCP servers integrate with multiple ONE_SHOT skills:

| Skill | Vision MCP | Web Search MCP | Zread MCP |
|-------|------------|----------------|-----------|
| `debugger` | ✅ diagnose_error_screenshot | ✅ search solutions | ✅ explore error sources |
| `deep-research` | | ✅ primary research | ✅ codebase exploration |
| `front-door` | ✅ analyze reference UIs | ✅ tech research | ✅ dependency research |
| `code-reviewer` | | ✅ search patterns | ✅ explore similar code |
| `create-plan` | ✅ diagram analysis | ✅ research | ✅ dependency exploration |
| `continuous-planner` | ✅ all vision tools | ✅ all research | ✅ all codebase |
| `refactorer` | | | ✅ understand patterns |

---

## Troubleshooting

### MCP Server Not Showing

```bash
# Check Claude config
cat ~/.claude/config.json

# Restart Claude Code
# Exit and restart the terminal
```

### API Key Issues

```bash
# Verify API key is set
echo $Z_AI_API_KEY

# Test API key
curl -H "Authorization: Bearer your_api_key" https://api.z.ai/api/mcp/web_search_prime/mcp
```

### Quota Exceeded

```bash
# Check quota status
zai quota

# Upgrade plan if needed
# Visit: https://dashboard.z.ai/billing
```

---

## Removal

To remove MCP servers:

```bash
# Remove Vision MCP
claude mcp remove zai-mcp-server

# Remove Web Search MCP
claude mcp remove web-search-prime

# Remove Zread MCP
claude mcp remove zread
```

---

## References

- [ZAI DevPack Documentation](https://docs.z.ai/devpack/overview)
- [Claude MCP Documentation](https://docs.anthropic.com/claude-code/mcp)
- [ONE_SHOT continuous-planner Skill](../skills/continuous-planner/SKILL.md)
