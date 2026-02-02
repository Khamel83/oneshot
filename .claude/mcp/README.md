# MCP Tool Catalog - ONE_SHOT

**Last Updated**: 2026-02-02

Model Context Protocol (MCP) servers extend Claude Code with external tools. This catalog documents available MCP servers and their integration with ONE_SHOT skills.

---

## Available MCP Servers

### ZAI MCP Servers

| Server | Type | Tools | Use Cases |
|--------|------|-------|-----------|
| **Vision MCP** | stdio | ui_to_artifact, diagnose_error_screenshot, understand_technical_diagram, analyze_data_visualization, ui_diff_check, image_analysis, video_analysis | UI mockups → code, error screenshots, architecture diagrams, charts |
| **Web Search MCP** | http | webSearchPrime | Real-time research, latest docs, news |
| **Zread MCP** | http | search_doc, get_repo_structure, read_file | GitHub repo exploration, code research |

**Setup Guide**: See [zai-mcp-setup.md](./zai-mcp-setup.md)

---

## Tool Reference

### Vision MCP Tools

| Tool | Description | Best For |
|------|-------------|----------|
| `ui_to_artifact` | Convert UI screenshots to code/specs | front-door, create-plan |
| `extract_text_from_screenshot` | OCR for code, terminals, docs | debugger, research |
| `diagnose_error_screenshot` | Analyze error screenshots for root cause | debugger |
| `understand_technical_diagram` | Parse architecture, flow, UML, ER diagrams | create-plan, deep-research |
| `analyze_data_visualization` | Extract insights from charts and dashboards | deep-research, observability |
| `ui_diff_check` | Compare two UI screenshots | code-reviewer, visual-iteration |
| `image_analysis` | General-purpose image understanding | Any skill |
| `video_analysis` | Analyze videos ≤8MB | Any skill |

**Usage Pattern**:
```markdown
## Visual Analysis (via Vision MCP)
### [Date] - Screenshot Analysis
- **Image**: filename.png
- **Tool Used**: diagnose_error_screenshot
- **Findings**: [analysis results]
```

### Web Search MCP Tools

| Tool | Description | Best For |
|------|-------------|----------|
| `webSearchPrime` | Search the web for current information | All research tasks |

**Usage Pattern**:
```markdown
### MCP-Enabled Research
#### Web Search (via webSearchPrime)
- **Query**: "[search query]"
- **Results**: [key findings with URLs]
- **Relevance**: [how this applies]
```

### Zread MCP Tools

| Tool | Description | Best For |
|------|-------------|----------|
| `search_doc` | Search repository documentation | Dependency research |
| `get_repo_structure` | Get GitHub repo file structure | Understanding projects |
| `read_file` | Read complete file from GitHub | Code review, patterns |

**Usage Pattern**:
```markdown
#### Zread Repository Analysis
- **Repo**: owner/repo
- **Documentation**: [key docs found]
- **Code Structure**: [relevant files and purposes]
```

---

## Skill Integration Matrix

| Skill | Vision MCP | Web Search MCP | Zread MCP | Primary Use |
|-------|------------|----------------|-----------|-------------|
| `debugger` | ✅ diagnose_error_screenshot | ✅ search solutions | ✅ explore error sources | Error diagnosis |
| `deep-research` | | ✅ primary research | ✅ codebase exploration | Comprehensive research |
| `front-door` | ✅ analyze reference UIs | ✅ tech research | ✅ dependency research | Project planning |
| `code-reviewer` | | ✅ search patterns | ✅ explore similar code | Quality checks |
| `create-plan` | ✅ diagram analysis | ✅ research | ✅ dependency exploration | Plan creation |
| `continuous-planner` | ✅ all vision tools | ✅ all research | ✅ all codebase | Living plans |
| `refactorer` | | | ✅ understand patterns | Safe refactoring |
| `observability-setup` | ✅ analyze dashboards | ✅ best practices | | Monitoring setup |
| `visual-iteration` | ✅ ui_diff_check | ✅ design trends | | UI polish |

---

## Quota Management

### ZAI Quota Tiers

| Plan Tier | Web Search + Zread | Vision Pool | Best For |
|-----------|-------------------|-------------|----------|
| Lite | 100 total/month | 5 hours | Personal projects |
| Pro | 1,000 total/month | 5 hours | Active development |
| Max | 4,000 total/month | 5 hours | Teams, heavy usage |

### Quota Tracking

```bash
# Check quota via ZAI CLI (if installed)
zai quota

# Or check dashboard
# Visit: https://dashboard.z.ai/
```

### Quota-Smart Strategies

1. **Prefer MCP over built-in tools** when available (saves Claude tokens)
2. **Check quota before heavy usage** (batch research, multiple screenshots)
3. **Fallback to free alternatives** when quota is low:
   - Web Search MCP → Built-in WebSearch
   - Zread MCP → git clone + Glob/Grep
4. **Batch requests** when possible (fewer API calls)

---

## MCP-First Patterns

### Research Pattern

**OLD WAY** (token-intensive):
```bash
# Use built-in WebSearch
WebSearch("best practices for X")
```

**NEW WAY** (MCP-first):
```bash
# Use Web Search MCP
webSearchPrime("best practices for X")
# Saves Claude tokens, better results
```

### GitHub Exploration Pattern

**OLD WAY** (slow, disk usage):
```bash
# Clone repo and explore
git clone https://github.com/owner/repo
cd repo
find . -name "*.py"
```

**NEW WAY** (MCP-first):
```bash
# Use Zread MCP
get_repo_structure("owner/repo")
# Faster, no disk usage
```

### Error Diagnosis Pattern

**OLD WAY** (manual analysis):
```bash
# User pastes error text
# Claude reads and analyzes
```

**NEW WAY** (MCP-first):
```bash
# User shares screenshot
diagnose_error_screenshot("error.png")
# Automatic visual analysis
```

---

## MCP Command Reference

### List MCP Servers

```bash
claude mcp list
```

### Add MCP Server

```bash
# stdio server
claude mcp add -s user server-name --env KEY=value -- command

# http server
claude mcp add -s user -t http server-name https://url --header "Key: Value"
```

### Remove MCP Server

```bash
claude mcp remove server-name
```

### Test MCP Server

```bash
# In Claude Code, invoke MCP tool
claude "Use webSearchPrime to search for 'X'"
```

---

## Troubleshooting

### MCP Server Not Showing

```bash
# Check config
cat ~/.claude/config.json

# Restart Claude Code
# Exit and restart terminal
```

### API Key Issues

```bash
# Verify API key
echo $Z_AI_API_KEY

# Test API
curl -H "Authorization: Bearer $Z_AI_API_KEY" https://api.z.ai/api/mcp/web_search_prime/mcp
```

### Quota Exceeded

```bash
# Check quota
zai quota

# Use fallback tools
# Web Search MCP → WebSearch
# Zread MCP → git clone
```

---

## References

- [ZAI MCP Setup Guide](./zai-mcp-setup.md)
- [ZAI DevPack Documentation](https://docs.z.ai/devpack/overview)
- [Claude MCP Documentation](https://docs.anthropic.com/claude-code/mcp)
- [continuous-planner Skill](../skills/continuous-planner/SKILL.md)
