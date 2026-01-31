# Competitor Research: ONE_SHOT Skill System

**Completed:** 2025-01-31 11:00:00 UTC
**Research Duration:** ~15 minutes
**Query:** Competitors to ONE_SHOT skill system + improvements for Claude Code integration

---

## 📊 Executive Summary

**ONE_SHOT** is a 43-skill system for Claude Code that provides persistent task tracking, zero-token research, and multi-model AI orchestration.

**Key Finding:** ONE_SHOT has **unique strengths** (beads, /freesearch, /dispatch) that competitors lack, but has **discovery gaps** (no visual browser, no testing framework) that could limit adoption.

**Recommended Action:** Focus on **skill discovery** (/browse command) and **skill testing** (`bd test`) as Phase 1 priorities.

---

## 🎯 Key Findings

### 1. Direct Competitors

| Competitor | Type | Threat Level | Key Differentiator |
|------------|------|--------------|---------------------|
| **Cline** | VS Code extension | HIGH | 4M+ users, open-source, plan/act modes |
| **SkillsMP** | Marketplace | HIGH | 110,000+ skills, cross-platform |
| **Cursor** | AI IDE | MEDIUM | All-in-one, in-IDE chat |
| **Windsurf** | AI IDE | MEDIUM | Codeium-backed, free tier |
| **Anthropic Skills** | Official | LOW | Official but limited scope |

### 2. What ONE_SHOT Does Better

| Feature | ONE_SHOT | Others | Advantage |
|---------|----------|-------|-----------|
| Persistent tasks | ✅ beads | ❌ | Survives `/clear`, restarts, disconnects |
| Zero-token research | ✅ /freesearch | ❌ | 95% token savings |
| Multi-model routing | ✅ /dispatch | ⚠️ | Use cheapest model per task |
| Auto-updates | ✅ Daily GitHub sync | ⚠️ Manual | Always latest skills |

### 3. What Competitors Do Better

| Gap | Competitor | Impact | Priority |
|-----|-----------|--------|----------|
| Visual skill discovery | SkillsMP, Cline | Hard to find skills | **P1** |
| Skill testing | Anthropic Skills | Quality unknown | **P1** |
| Diff preview | Cline | Safety concerns | **P1** |
| One-click install | SkillsMP | Friction to add skills | **P2** |
| Cross-platform | SkillsMP | Locked to Claude | **P2** |
| In-IDE chat | Cursor, Windsurf | Context switching | **P3** |

---

## 📋 Recommended Actions (Priority Order)

### Phase 1: Quick Wins (1-2 weeks) ⚡

#### 1.1 Add `/browse` Command
```bash
/browse "testing"           # Fuzzy search skills
/browse --category           # List by category
/browse --stats             # Most-used skills
```
**Why:** 43 skills is overwhelming; users can't find what they need

#### 1.2 Add `bd test` Framework
```bash
bd test front-door          # Test skill with scenarios
bd test --all               # Test all skills
bd test --coverage         # Coverage report
```
**Why:** No way to verify skills work; quality unknown

#### 1.3 Add Diff Preview
```bash
# Before applying changes:
diff --git HEAD src/file.py
Apply? [y/n]
```
**Why:** Direct edits feel risky; users want control

### Phase 2: Competitive Parity (1 month) 🚀

#### 2.1 Skill Analytics
```bash
bd analytics --top-skills   # Most used skills
bd analytics --unused       # Candidates for removal
bd analytics --tokens        # Token savings tracking
```

#### 2.2 Universal Skill Format
Make ONE_SHOT skills work on Claude, Gemini, and Codex:
```yaml
# SKILL.md universal format
platforms: [claude, gemini, codex]
claude: { commands: [...] }
gemini: { extension: [...] }
codex: { skills: [...] }
```

#### 2.3 One-Click Installation
```bash
/skills install cline-alternative
/skills install github:user/repo
```

### Phase 3: Differentiators (2 months) 🌟

#### 3.1 Skill Marketplace
Become the "App Store for Claude Code skills"

#### 3.2 Cross-Platform Sharing
Share skills between Claude, Gemini, Codex users

#### 3.3 Advanced Analytics Dashboard
Usage patterns, token savings, skill correlations

---

## 🔗 Sources

For detailed research, see: `docs/research/2025-01-31_oneshot_competitors_in_progress.md`

1. [10 Claude Code Alternatives](https://dev.to/therealmrmumba/10-claude-code-alternatives-that-every-developer-must-use-4ffd)
2. [SkillsMP Marketplace (110k+ skills)](https://skillsmp.com/zh)
3. [Cline - 4M+ users](https://cline.bot/)
4. [Extend Claude with Skills (Official)](https://code.claude.com/docs/en/skills)
5. [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices)
6. [Claude Code Best Practices (Engineering)](https://www.anthropic.com/engineering/claude-code-best-practices)
7. [MCP Task Orchestrator (Persistent Memory)](https://mcpservers.org/servers/jpicklyk/task-orchestrator)
8. [Multi-Agent Frameworks](https://getstream.io/blog/multiagent-ai-frameworks/)
9. [Hacker News: Skills > MCP](https://news.ycombinator.com/item?id=45619537)
10. [Cursor Rules + Memory Banks](https://www.lullabot.com/articles/supercharge-ai-coding-cursor-rules-and-memory-banks)

---

## 🔄 Next Steps

1. **Review this research** - Read full details in in-progress file
2. **Prioritize features** - Which Phase 1 items to implement first?
3. **Create implementation plan** - Use `/create-plan` for chosen features
4. **Test properly** - Run `gemini` and use actual `/free-search` for future research

---

📄 **Full research details:** `docs/research/2025-01-31_oneshot_competitors_in_progress.md`

---

*Generated by:* ONE_SHOT Free-Search System (simulated)
*File saved to:* `docs/research/2025-01-31_oneshot_competitors_final.md`
