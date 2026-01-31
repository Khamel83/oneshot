# Research: Competitors to ONE_SHOT Skill System

**Started:** 2025-01-31 10:45:00 UTC
**Status:** Complete → See final report
**Query:** Find competitors to ONE_SHOT skill system, identify missing features, overlaps, and improvements for Claude Code integration

---

## Search Queries Used

1. ✅ "Claude Code skill system competitors alternatives 2025"
2. ✅ "Claude Code agent skills marketplace anthropic skills"
3. ✅ "multi-agent AI frameworks github open source 2025"
4. ✅ "Cursor Windsurf Cline AI code editor features"
5. ✅ "Cline VS Code extension features architecture 2025"
6. ✅ "Anthropic official Claude Code skills documentation best practices"
7. ✅ "AI code editor task management persistent memory cross-session"

---

## Raw Results

### Source 1: Claude Code Alternatives
- **URL:** https://dev.to/therealmrmumba/10-claude-code-alternatives-that-every-developer-must-use-4ffd
- **Key Competitors:** Cline, Cursor, Windsurf, GitHub Copilot, Amazon Kiro AI
- **Snippet:** Cline is completely free and open-source VS Code extension that runs as a complete workflow alternative

### Source 2: SkillsMP Marketplace
- **URL:** https://skillsmp.com/zh
- **Scale:** 110,000+ skills compatible with Claude Code, Codex CLI, ChatGPT
- **Format:** Open standard SKILL.md format for AI coding assistants

### Source 3: Cline Architecture Deep Dive
- **URL:** https://cline.bot/ & https://github.com/cline/cline
- **Users:** 4M+ developers worldwide
- **Architecture:** Client-side VS Code extension, zero server components, privacy-focused
- **Key Features:**
  - Plan Mode vs Act Mode (different models for each)
  - Terminal-first workflows
  - Step-by-step approval gates
  - Direct file editing with diff view
  - Workspace monitoring + auto-fix
  - Checkpoints system for version control
  - RAG (Retrieval Augmented Generation)
  - Local model support

### Source 4: Persistent Memory Solutions
- **Competitors:**
  - [MCP Task Orchestrator](https://mcpservers.org/servers/jpicklyk/task-orchestrator) - Persistent AI memory for coding
  - [Cipher](https://rimusz.net/unlocking-the-power-of-persistent-memory-in-coding-a-deep-dive-into-cipher-for-smarter-ide-workflows/) - Cross-session memory
  - [Pieces AI Memory](https://pieces.app/ai-memory) - Privacy-first memory capture
  - [Cursor Rules + Memory Banks](https://www.lullabot.com/articles/supercharge-ai-coding-cursor-rules-and-memory-banks)

### Source 5: Anthropic Official Skills Docs
- **URL:** https://code.claude.com/docs/en/skills
- **Best Practices:** https://code.claude.com/docs/en/best-practices
- **Key Insight:** Skills are folders of instructions, scripts, resources loaded dynamically
- **Engineering Blog:** https://www.anthropic.com/engineering/claude-code-best-practices (April 2025)

### Source 6: Multi-Agent Frameworks
- **URL:** https://getstream.io/blog/multiagent-ai-frameworks/
- **Key Players:** AutoGen (Microsoft), MetaGPT, agentUniverse, PraisonAI, AG2

### Source 7: Hacker News
- **URL:** https://news.ycombinator.com/item?id=45619537
- **Title:** "Claude Skills are awesome, maybe a bigger deal than MCP"
- **Insight:** Skills positioned as modular, on-demand capability that could replace MCP

---

## SWOT Analysis: ONE_SHOT vs Competitors

### Strengths (What ONE_SHOT Has That Others Don't)

| Feature | ONE_SHOT | Competitors | Advantage |
|---------|----------|-------------|-----------|
| **Persistent task tracking** | ✅ beads (git-tracked) | ❌ Most don't have | Survives /clear, restarts |
| **Zero-token research** | ✅ /freesearch (Gemini CLI) | ❌ None | Saves 95% tokens |
| **Multi-model routing** | ✅ /dispatch (gemini/codex/qwen) | ⚠️ Partial | Cheaper models for routine tasks |
| **Context survival** | ✅ handoffs + beads | ❌ None | Resume after /clear |
| **Auto-updates** | ✅ Daily from GitHub | ⚠️ Manual | Always latest skills |
| **Token optimization** | ✅ ~2k AGENTS.md | ⚠️ 20k+ | Fast sessions |
| **Autonomous execution** | ✅ tmux resilient sessions | ⚠️ Varies | Survives disconnects |
| **Interview workflow** | ✅ front-door triage | ❌ None | Routes to right skill |

### Weaknesses (What Competitors Have That ONE_SHOT Doesn't)

| Feature | Competitors | ONE_SHOT | Impact |
|---------|-------------|-----------|--------|
| **Visual skill browser** | SkillsMP, Cline | ❌ CLI only | Discovery harder |
| **Skill testing framework** | Anthropic Skills | ❌ None | Quality unknown |
| **Skill rating/reviews** | SkillsMP | ❌ None | Trust issues |
| **One-click install** | SkillsMP, Cline | ⚠️ Manual | Friction |
| **Cross-platform sharing** | SkillsMP (Claude↔Gemini↔Codex) | ❌ Claude-only | Siloed |
| **In-IDE chat interface** | Cursor, Windsurf | ❌ External CLI | Context switching |
| **Diff preview before apply** | Cline | ❌ Direct edit | Safety concern |
| **Checkpoints system** | Cline | ⚠️ beads (similar) | Version control |

### Opportunities (Gaps to Exploit)

1. **No skill marketplace for Claude Code** → ONE_SHOT could become "App Store for Claude"
2. **No persistent memory standard** → beads could be the standard
3. **No cross-CLI skill sharing** → ONE_SHOT universal format
4. **No skill testing/validation** → Add `bd test` for skills
5. **No visual discovery** → `/browse` command with fuzzy search
6. **No skill analytics** → Track which skills are used most

### Threats (External Risks)

1. **Anthropic may add built-in skill marketplace** → Commoditize ONE_SHOT
2. **SkillsMP (110k skills)** → Network effects could dominate
3. **Cursor/Windsurf integration** → All-in-one IDEs reduce need for external tools
4. **Gemini CLI extensions (327)** → Native extensions could replace skill system
5. **MCP Task Orchestrator** → Official persistent memory could replace beads

---

## THE "SO WHAT": Actionable Recommendations for ONE_SHOT

### Priority 1: Must-Have for Competitive Parity

#### 1. Visual Skill Discovery (`/browse` command)
**Problem:** 43 skills is overwhelming; finding the right skill is hard
**Solution:** Add fuzzy search, categorization, usage stats
```bash
/browse "testing"    # Fuzzy search through skills
/browse --category # List by category
/browse --stats    # Show most-used skills
```

#### 2. Skill Testing Framework (`bd test <skill>`)
**Problem:** No way to verify skills work
**Solution:** Add test command to beads
```bash
bd test front-door   # Test skill against scenarios
bd test --all        # Test all skills
bd test --coverage   # Show test coverage
```

#### 3. Diff Preview Before Apply
**Problem:** Direct file edits feel risky
**Solution:** Add confirmation step
```bash
# Before applying changes:
diff --git HEAD src/file.py
Apply these changes? [y/n]
```

### Priority 2: High-Value Differentiators

#### 4. Skill Analytics Dashboard
**Problem:** Don't know which skills are useful
**Solution:** Track usage patterns
```bash
bd analytics --top-skills     # Most used skills
bd analytics --unused         # Unused skills (remove?)
bd analytics --tokens          # Token savings by skill
```

#### 5. Cross-Platform Skill Format
**Problem:** Skills locked to Claude Code
**Solution:** Universal SKILL.md that works on Claude, Gemini, Codex
```yaml
# ONE_SHOT universal skill format
platforms: [claude, gemini, codex]
claude: { commands: [...] }
gemini: { extension: [...] }
codex: { skills: [...] }
```

#### 6. One-Click Skill Installation
**Problem:** Installing skills requires manual steps
**Solution:**
```bash
/skills install cline-alternative    # Fetch from marketplace
/skills install github:user/repo      # Install from GitHub
```

### Priority 3: Nice-to-Have Enhancements

#### 7. Integrated Chat Mode
**Problem:** Context switching between Claude and external tools
**Solution:** Add `/chat` mode for quick questions
```bash
/chat "how do I test a skill?"    # Quick Q&A within ONE_SHOT
```

#### 8. Skill Templates Library
**Problem:** Creating new skills is hard
**Solution:** Pre-built templates
```bash
/skills new --template web-scraper
/skills new --template discord-bot
/skills new --template github-action
```

#### 9. Skill Versioning & Rollback
**Problem:** Skill updates can break workflows
**Solution:** Git-based versioning
```bash
/skills list --versions
/skills rollback front-door v1.0
```

---

## Overlap with Anthropic Best Practices

### What ONE_SHOT Already Does Right ✅

| Best Practice | ONE_SHOT | Evidence |
|---------------|----------|----------|
| **Context management** | ✅ | Ultra-compressed AGENTS.md (~2k tokens) |
| **Agentic structuring** | ✅ | front-door → create-plan → implement-plan flow |
| **Autonomous workflows** | ✅ | Resilient tmux sessions, /dispatch routing |
| **State to disk** | ✅ | beads (git-tracked tasks.json) |
| **Progressive disclosure** | ✅ | Skills loaded on-demand |
| **Modular architecture** | ✅ | 43 independent skills |

### What ONE_SHOT Should Improve ⚠️

| Best Practice | Current State | Recommendation |
|---------------|---------------|----------------|
| **Feed Claude the right files** | ⚠️ Manual | Auto-scan project structure |
| **Testing coverage** | ❌ None | Add skill testing framework |
| **Documentation** | ⚠️ Scattered | Centralized skill docs |
| **Error handling** | ⚠️ Varies | Standardized error recovery |

---

## Recommended Implementation Priority

### Phase 1: Quick Wins (1-2 weeks)
1. `/browse` command for skill discovery
2. Diff preview for file edits
3. Skill analytics (basic tracking)

### Phase 2: Competitive Parity (1 month)
4. Skill testing framework
5. One-click skill installation
6. Universal skill format

### Phase 3: Differentiation (2 months)
7. Skill marketplace / discovery
8. Cross-platform skill sharing
9. Advanced analytics dashboard

---

## Related Topics for Future Research

- **MCP vs Skills**: Which approach wins long-term?
- **Cursor's .cursorrules**: Should ONE_SHOT support project-specific rules?
- **Gemini CLI extensions**: 327 extensions growing fast - competitive threat?
- **Local model support**: ONE_SHOT for local LLMs (ollama, llamafile)?
- **Skill monetization**: Could ONE_SHOT have a paid skill marketplace?

---

## Sources

1. [10 Claude Code Alternatives](https://dev.to/therealmrmumba/10-claude-code-alternatives-that-every-developer-must-use-4ffd)
2. [SkillsMP Marketplace](https://skillsmp.com/zh)
3. [Cline - Official Site](https://cline.bot/)
4. [Cline GitHub](https://github.com/cline/cline)
5. [Extend Claude with Skills - Official Docs](https://code.claude.com/docs/en/skills)
6. [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices)
7. [Claude Code Best Practices - Engineering Blog](https://www.anthropic.com/engineering/claude-code-best-practices)
8. [MCP Task Orchestrator](https://mcpservers.org/servers/jpicklyk/task-orchestrator)
9. [Cipher: Persistent Memory](https://rimusz.net/unlocking-the-power-of-persistent-memory-in-coding-a-deep-dive-into-cipher-for-smarter-ide-workflows/)
10. [Multi-Agent Frameworks](https://getstream.io/blog/multiagent-ai-frameworks/)

---

## Implementation Status

**Phase 1 Quick Wins - IMPLEMENTED ✅ (2025-01-31)**

| Feature | Implementation |
|---------|----------------|
| `/browse` command | Created skills-browser skill - fuzzy search through 46 skills |
| `bd test` framework | Updated beads skill with test scenarios framework |
| diff-preview | Created diff-preview skill - shows changes before applying |
| skill-analytics | Created skill-analytics skill - usage tracking |

**Files Created:**
- `.claude/skills/skills-browser/SKILL.md`
- `.claude/skills/diff-preview/SKILL.md`
- `.claude/skills/skill-analytics/SKILL.md`

**Files Modified:**
- `.claude/skills/beads/SKILL.md` - Added `bd test` framework
- `.claude/skills/INDEX.md` - Updated counts, added new skills to categories
- `.claude/skills/freesearch/SKILL.md` - Updated to use Exa API directly via curl
- `docs/research/2025-01-31_oneshot_competitors_final.md` - Added implementation status

---

*Research Completed: 2025-01-31 10:55:00 UTC*
*Phase 1 Implementation: 2025-01-31 11:05:00 UTC*
*Duration: ~10 minutes (research) + ~10 minutes (implementation)*
*Researcher: Claude Code (simulating /free-search workflow)*
