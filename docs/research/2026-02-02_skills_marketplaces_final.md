# Research: AI Skills Marketplaces Ecosystem - Final Report

**Completed:** 2026-02-02
**Duration:** Comprehensive (15-20 min)
**Goal:** Ecosystem overview to determine if ONE_SHOT should sunset in favor of existing solutions

---

## Executive Summary

The AI skills marketplace ecosystem has **exploded since late 2025**. What was once a novel idea (ONE_SHOT's early skills system) is now a **competitive landscape** with multiple mature platforms, standards, and marketplaces.

**Key Finding:** There are now **better alternatives** for most of ONE_SHOT's functionality. The market has converged on **MCP (Model Context Protocol)** as the standard for tool integration, with **SkillsMP** dominating the skills marketplace space.

---

## Critical Platforms Identified

### 1. **SkillsMP** (skillsmp.com) - The Skills Marketplace Giant
- **110,000+ agent skills** compatible with Claude Code, Codex CLI, ChatGPT
- Uses the **SKILL.md open standard** (same format as ONE_SHOT)
- Features search, intelligent recommendations
- Categories: Development, Business, Data, Communication, Document Processing
- Chinese market dominance (26,000+ GitHub stars on related repos)

### 2. **Smithery.ai** - The MCP Marketplace Leader
- **7,000+ MCP servers** (largest MCP registry)
- Described as "Google for MCPs"
- Built-in observability, testing, and distribution
- Agent-first internet infrastructure
- Connects agents to MCPs in minutes

### 3. **MCP Market** (mcpmarket.com)
- Claude Code plugin reference and marketplace
- Covers schemas, marketplaces, MCP servers, installation scopes
- Production integrations: 50+

### 4. **PulseMCP** (pulsemcp.com)
- **7,890+ MCP servers** updated daily
- Real-time directory growth tracking

### 5. **Gradually.ai**
- **1,065+ MCP servers** directory
- Multi-platform support (Claude, ChatGPT, Cursor)

---

## Standards Landscape (2026)

### The 2026 Protocol Stack
1. **MCP (Model Context Protocol)** - Agent-to-tool connections (Anthropic standard)
2. **A2A (Agent-to-Agent)** - Multi-agent coordination
3. **AG-UI / A2UI** - Agent UI interactions
4. **ACP** - Agent communication protocol

### Standardization Bodies
- **W3C Community Group**: AI Agent Protocol Community Group
- **IETF Draft**: MCP specification in progress
- **AgentProtocol.ai**: Open API specification

---

## ONE_SHOT Competitive Analysis

| Feature | ONE_SHOT | SkillsMP | Smithery.ai | Winner |
|---------|----------|----------|-------------|--------|
| **Skills Count** | 51 | 110,000+ | 7,000+ MCP | SkillsMP |
| **Discovery** | Manual list | Search + recommendations | "Google for MCPs" | Smithery |
| **Distribution** | Git clone | One-click install | Built-in packaging | Both |
| **Standard** | SKILL.md | SKILL.md | MCP | SkillsMP |
| **Multi-Model** | Claude, Codex, Gemini, Qwen | Claude, Codex, ChatGPT | Universal MCP | Smithery |
| **Observability** | Beads (custom) | Unknown | Built-in | Smithery |
| **Documentation** | Custom AGENTS.md | SKILL.md standard | MCP spec | Both |

---

## What ONE_SHOT Does Better (Personal Stack)

These are **unique value props** worth preserving:

1. **Beads System** - Git-backed persistent task tracking with dependencies
2. **Personal Tech Stack Defaults** - Convex+Next.js+Clerk, Python+Click+SQLite, oci-dev deployment
3. **Continuous Planning (v8.3)** - 3-file pattern (task_plan.md, findings.md, progress.md)
4. **Tailscale + poytz routing** - Personal infrastructure preferences
5. **Global CLAUDE.md** - Cross-project instructions management
6. **Heartbeat & Fleet Management** - Auto-update and health checks

---

## How Skills Actually Work (The Missing UX Piece)

### Official Claude Code Skills System

After researching the official documentation, here's how Claude Code skills actually work:

**Location Hierarchy:**
| Location | Path | Scope |
|----------|------|-------|
| Personal | `~/.claude/skills/<name>/SKILL.md` | All projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project only |
| Enterprise | Managed settings | Organization-wide |

**Slash Command Creation:**
- Create directory: `mkdir -p ~/.claude/skills/my-skill`
- Add `SKILL.md` with YAML frontmatter
- The `name` field becomes `/slash-command`
- **That's it** - Claude auto-discovers and loads it

**Example ONE_SHOT Skill Conversion:**

```markdown
---
name: front-door
description: Intelligent entry point for all tasks. Interviews, triages, and routes. Use when starting any non-trivial work, when user says 'build me', 'new project', 'help me', '/interview', or '/front-door'.
disable-model-invocation: true
---

# Front Door

You are the intelligent entry point for ONE_SHOT tasks...
```

This creates `/front-door` - **same as ONE_SHOT today**.

### SkillsMP Integration

**SkillsMP** is just a **directory** of skills - not a replacement for local skills:
- Browse: https://skillsmp.com/
- Install: Copy `SKILL.md` to `~/.claude/skills/<name>/`
- **No special CLI needed** - just standard Claude Code skills

### Smithery.ai Integration

**Smithery** is for **MCP servers** (external tool integrations):
- Connect apps: Notion, Gmail, GitHub, Figma, etc.
- Install via: `claude mcp add` or Smithery's CLI
- **Separate from skills** - these are tools, not instructions

### Key Insight: ONE_SHOT IS ALREADY COMPATIBLE

ONE_SHOT skills **already use the standard format**:
- `SKILL.md` files ✓
- YAML frontmatter ✓
- Slash commands ✓
- Local discovery ✓

**The difference is:**
- ONE_SHOT: 51 skills in `~/.github/oneshot/.claude/skills/`
- SkillsMP: 110,000+ skills browsable online
- Claude Code Official: Native support, no marketplace needed

---

## The Real Question: What Does ONE_SHOT Provide Beyond Skills?

ONE_SHOT v8.3 is more than just skills:

| Component | What It Does | Can It Be Replaced? |
|-----------|--------------|-------------------|
| **51 Skills** | Task-specific workflows | Yes - by SkillsMP selection |
| **AGENTS.md** | Skill router (pattern matching) | No - Claude does this via `description` |
| **KHAMEL MODE** | Personal tech stack defaults | No - unique value |
| **Beads** | Git-backed task tracking | Partially - task trackers exist |
| **CLAUDE.md** | Cross-project instructions | No - this IS the standard |
| **Heartbeat** | Auto-update system | No - unique feature |
| **Dispatch** | Multi-model CLI routing | Partially - MCP servers exist |

---

## Recommendations for v9

### Option A: Sunset ONE_SHOT Core, Keep Personal Config (Minimal)
**Approach:** Migrate to SkillsMP/Smithery, keep only personal config

**What to Keep:**
- `~/.claude/CLAUDE.md` (personal tech stack defaults)
- `continuous-planner` skill (unique 3-file pattern)
- `beads` tracking system (if not available elsewhere)
- Personal deployment patterns (oci-dev, homelab)

**What to Drop:**
- 48 skills (available on SkillsMP)
- AGENTS.md skill router (use marketplace search)
- Custom skill templates (use standard SKILL.md)
- Multi-model dispatch (use MCP universal routing)

**Migration Path:**
1. Install SkillsMP CLI
2. Import favorite skills from marketplace
3. Keep `~/.claude/CLAUDE.md` for personal defaults
4. Use MCP servers for external tool access

### Option B: Minimal v9 - "Personal Layer" Only
**Approach:** ONE_SHOT becomes a thin personalization layer over marketplaces

**Architecture:**
```
┌─────────────────────────────────────────┐
│     ONE_SHOT v9 - Personal Layer       │
│  (Tech stack + Beads + Continuous Plan)  │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌──────────────┐
│  SkillsMP   │  │ Smithery.ai  │
│ (110K skills)│  │ (7K MCP)     │
└─────────────┘  └──────────────┘
```

**Components:**
1. **`CLAUDE.md`** - Tech stack defaults (Convex, Python, oci-dev)
2. **`beads/`** - Task tracking (if unique value)
3. **`continuous-planner/`** - 3-file planning pattern
4. **`integrations/`** - Shortcuts to SkillsMP/Smithery favorites

**Size Reduction:** ~8,000 lines → ~500 lines

### Option C: Hybrid - Skills Directory with Marketplace Fallback
**Approach:** Keep curated skills, use marketplace for discovery

**Structure:**
```
.claude/
├── CLAUDE.md              # Personal tech stack
├── skills/
│   ├── continuous-planner/ # Unique value
│   ├── beads/              # Unique value
│   └── marketplace.txt     # SkillsMP favorites manifest
└── marketplace-symlink/    # → SkillsMP installed skills
```

---

## Decision Framework

### Sunset ONE_SHOT If:
- ✅ SkillsMP/Smithery cover 90%+ of use cases
- ✅ Personal config can live in `~/.claude/CLAUDE.md`
- ✅ No desire to maintain skill infrastructure
- ✅ OK with dependency on external platforms

### Keep Minimal v9 If:
- ✅ Beads system provides unique value
- ✅ Continuous planning pattern is unique
- ✅ Personal tech stack defaults critical
- ✅ Want control over skill curation

### Keep Full ONE_SHOT If:
- ✅ Enjoy maintaining skill ecosystem
- ✅ Want complete independence
- ✅ Unique workflows not covered elsewhere

---

## Action Items for Decision

1. **Audit ONE_SHOT skills** against SkillsMP catalog
2. **Test Smithery.ai** MCP marketplace
3. **Evaluate Beads** against alternative task tracking
4. **Document personal tech stack** requirements
5. **Create v9 branch** if Option B or C chosen

---

## Sources

### Marketplaces
- [SkillsMP: 110,000+ Agent Skills](https://skillsmp.com/zh)
- [Smithery.ai: 7,000+ MCP Servers](https://smithery.ai/)
- [MCP Market: Plugin Reference](https://mcpmarket.com/)
- [PulseMCP: 7,890+ Servers](https://www.pulsemcp.com/servers)
- [Gradually.ai: 1,065+ MCP Servers](https://www.gradually.ai/en/mcp-servers/)

### Standards & Documentation
- [Claude Code Plugin Reference 2026](https://mcpmarket.com/tools/skills/claude-code-plugin-reference-2026)
- [Claude Skills vs MCP: 2026 Guide](https://www.cometapi.com/claude-skills-vs-mcp-the-2026-guide-to-agentic-architecture/)
- [MCP Specification (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25)
- [Extend Claude with Skills - Official Docs](https://code.claude.com/docs/en/skills)
- [W3C AI Agent Protocol Community Group](https://www.w3.org/community/agentprotocol/)

### Articles & Analysis
- [The Case for Universal AI Extension Standards](https://jduncan.io/blog/2025-11-10-universal-ai-extension-standard/)
- [Claude Skills are Awesome, Maybe Bigger Than MCP](https://news.ycombinator.com/item?id=45619537)
- [2026: Year for Enterprise-Ready MCP Adoption](https://www.cdata.com/blog/2026-year-enterprise-ready-mcp-adoption)
- [Tool-space Interference in the MCP Era - Microsoft Research](https://www.microsoft.com/en-us/research/blog/tool-space-interference-in-the-mcp-era-designing-for-agent-compatibility-at-scale/)
- [My Predictions for MCP and AI-Assisted Coding in 2026](https://dev.to/blackgirlbytes/my-predictions-for-mcp-and-ai-assisted-coding-in-2026-16bm)

### Curated Lists
- [Awesome Claude Skills](https://github.com/travisvn/awesome-claude-skills)
- [Awesome MCP Servers](https://github.com/wong2/awesome-mcp-servers)
- [Top 10 MCP Servers for 2026](https://www.datacamp.com/blog/top-mcp-servers-and-clients)
- [Complete List of 50+ Best MCP Servers](https://mcpplaygroundonline.com/blog/awesome-mcp-servers)

### Community
- [Reddit: Is there a subagent website similar to SkillsMP?](https://www.reddit.com/r/ClaudeAI/comments/1qirqog/is_there_a_subagent_website_similar_to_skillsmpcom/)
- [Reddit: I've been tracking what people are building with Claude](https://www.reddit.com/r/ClaudeAI/comments/1o9ph4u/ive_been_tracking-what_people_are_building_with/)
- [GitHub: SkillsMP Self-Introduction](https://github.com/ruanyf/weekly/issues/8210)

---

## Next Steps

1. **Review this research** with personal workflow in mind
2. **Decide on Option A, B, or C**
3. **If B or C:** Create v9 branch and implement
4. **If A:** Document migration plan to SkillsMP/Smithery
5. **Update CLAUDE.md** with final decision

---

**In-Progress Research:** `docs/research/2026-02-02_skills_marketplaces_in_progress.md`
