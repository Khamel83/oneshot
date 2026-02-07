# Starred Repos - Comprehensive Review

## Executive Summary

Analyzed 10 starred repos for ONE_SHOT v10 relevance. **3 are critical** to ONE_SHOT's future direction.

---

## Together Review: Key Themes

### Theme 1: Multi-Agent Orchestration

**CC-MIRROR** and **claude-sneakpeek** both show that:
- Anthropic has built native multi-agent features (TeammateTool, swarm mode)
- These features are feature-flagged, not publicly released
- Community is building around these hidden capabilities

**Implication for ONE_SHOT**: v10's simplification (removing orchestration) aligns with where Claude is going - native features will handle this.

### Theme 2: Isolated Variants

Both **CC-MIRROR** and **claude-sneakpeek** create isolated Claude instances:
- `~/.cc-mirror/mclaude/` vs `~/.claude/`
- Separate config, sessions, MCP servers
- Enables testing different providers/configurations

**Implication for ONE_SHOT**: Could use isolation for testing ONE_SHOT changes safely.

### Theme 3: Task Management Systems

**CC-MIRROR** has native task tools (TaskCreate, TaskGet, TaskUpdate, TaskList).
**awesome-claude-skills** has 100+ skills with progressive disclosure.
**ONE_SHOT v10** uses external beads + on-demand commands.

**Implication for ONE_SHOT**: Consider if native task tools (CC-MIRROR) or external (beads) is better long-term.

### Theme 4: Specialization vs General-Purpose

**awesome-claude-skills**: Domain-specific (AWS security, Move code quality, bioinformatics)
**ONE_SHOT v10**: General-purpose personal productivity
**Agent Lightning**: Agent training framework

**Implication for ONE_SHOT**: Stay general-purpose, but make it easy to add domain-specific rule packs.

---

## Individual Reviews

### 1. numman-ali/cc-mirror ⭐⭐⭐

**Purpose**: Pre-configured Claude Code variants with custom providers

**Key Features**:
- Isolated variants (`~/.cc-mirror/mclaude/`, `~/.cc-mirror/zai/`)
- Team mode (1.6.3): Multi-agent orchestration with task graph
- Native task tools (TaskCreate, TaskGet, TaskUpdate, TaskList)
- Provider switching (Z.ai, MiniMax, OpenRouter)

**ONE_SHOT Impact**:
- **HIGH**: Task tool pattern is cleaner than external beads
- **MEDIUM**: "Conductor" orchestration pattern for background workers
- **LOW**: Provider isolation (ONE_SHOT uses global config)

**Recommendation**: Study task tools for potential ONE_SHOT integration. Consider using cc-mirror for testing ONE_SHOT in isolation.

---

### 2. mikekelly/claude-sneakpeek ⭐⭐⭐

**Purpose**: Parallel Claude Code build with feature-flagged swarm mode

**Key Features**:
- Swarm mode: Native multi-agent with TeammateTool
- Delegate mode: Task tool spawns background agents
- Team coordination: Teammate messaging

**ONE_SHOT Impact**:
- **CRITICAL**: Shows Anthropic's roadmap - native multi-agent is coming
- **HIGH**: Validates v10's "back to basics" approach
- **MEDIUM**: TeammateTool may obsolete custom orchestration

**Recommendation**: Install and test swarm mode. Document for ONE_SHOT v11 planning. Re-evaluate v10 simplification based on Claude's native features.

---

### 3. BehiSecc/awesome-claude-skills ⭐⭐

**Purpose**: Curated list of 100+ Claude Skills

**Key Features**:
- Domain-specific skills (AWS, security, research, healthcare)
- Progressive disclosure (skills load contextually)
- Community contribution model

**ONE_SHOT Impact**:
- **MEDIUM**: Progressive disclosure pattern for rule loading
- **LOW**: ONE_SHOT is general-purpose, skills are specialized
- **LOW**: Community contribution model worth studying

**Recommendation**: Apply progressive disclosure to ONE_SHOT rules. Consider domain-specific rule packs.

---

### 4. microsoft/agent-lightning ⭐

**Purpose**: Train AI agents with reinforcement learning

**Key Features**:
- Zero code change agent optimization
- Framework-agnostic (LangChain, AutoGen, CrewAI)
- RL, prompt optimization, SFT

**ONE_SHOT Impact**:
- **LOW**: Different problem (training vs configuration)
- **LOW**: Orthogonal to ONE_SHOT's mission

**Recommendation**: Document clear boundary. ONE_SHOT = configuration, Agent Lightning = training.

---

### 5. steipete/summarize ⭐

**Purpose**: Summarize URLs/YouTube/Podcasts

**ONE_SHOT Impact**: LOW - Utility tool, not relevant to ONE_SHOT architecture.

---

### 6. dgtlmoon/changedetection.io ⭐

**Purpose**: Website change detection

**ONE_SHOT Impact**: LOW - SaaS tool, not relevant to ONE_SHOT architecture.

---

### 7. openclaw/openclaw ⭐⭐

**Purpose**: Personal AI assistant (any OS, any platform)

**ONE_SHOT Impact**:
- **MEDIUM**: Similar goal (personal AI assistant)
- **MEDIUM**: Different approach (OpenClaw = standalone app, ONE_SHOT = Claude Code config)

**Recommendation**: Compare architectural approaches. Could learn from OpenClaw's patterns.

---

### 8. github/copilot-sdk ⭐

**Purpose**: Integrate GitHub Copilot Agent into apps

**ONE_SHOT Impact**: LOW - SDK for app integration, not relevant to ONE_SHOT.

---

### 9. google/langextract ⭐

**Purpose**: Extract structured info from text using LLMs

**ONE_SHOT Impact**: LOW - NLP library, not relevant to ONE_SHOT architecture.

---

### 10. adithya-s-k/manim_skill ⭐

**Purpose**: Manim animations for math videos

**ONE_SHOT Impact**: LOW - Domain-specific skill, not relevant to ONE_SHOT.

---

## Priority Matrix

| Repo | Priority | Action | Timeline |
|------|----------|--------|----------|
| claude-sneakpeek | CRITICAL | Test swarm mode, document findings | Next session |
| cc-mirror | HIGH | Study task tools, evaluate integration | This week |
| awesome-claude-skills | MEDIUM | Apply progressive disclosure to rules | This week |
| openclaw | MEDIUM | Compare architectural approaches | When time |
| Agent Lightning | LOW | Document boundary | Later |
| Others | LOW | Monitor for changes | Later |

---

## Recommendations for ONE_SHOT v11

### 1. Embrace Native Claude Features ⭐⭐⭐
Claude Code is adding native multi-agent (swarm mode). ONE_SHOT should:
- Remove custom orchestration (already done in v10)
- Wait for native features to mature
- Document how to use native features with ONE_SHOT rules

### 2. Re-evaluate Task Management ⭐⭐
CC-MIRROR's native task tools vs external beads:
- Test both approaches
- Choose based on UX and reliability
- Consider hybrid: native tools + /beads command wrapper

### 3. Add Progressive Disclosure ⭐
Load rules contextually based on project type:
- `infra-routing.md` only for infra projects
- `stack-defaults.md` only for new projects
- Reduces always-on token cost

### 4. Support Domain-Specific Rule Packs ⭐
Enable community to share domain rules:
- `~/.claude/rules/aws/` for AWS projects
- `~/.claude/rules/security/` for security reviews
- Follow awesome-claude-skills contribution model

---

## Next Session Actions

1. **Install claude-sneakpeek** to test swarm mode
2. **Compare task tools** (CC-MIRROR vs beads)
3. **Design progressive disclosure** for ONE_SHOT rules
4. **Document ONE_SHOT v11 roadmap** based on Claude's native features
