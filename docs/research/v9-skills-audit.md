# ONE_SHOT v9 Skills Audit

**Created:** 2026-02-02
**Purpose:** Identify unique vs replaceable skills for the "play calling" system

---

## The Vision: "Offensive Coordinator" Model

```
User: "Build X"
  ↓
front-door interviews/triages
  ↓
create-plan / continuous-planner creates the playbook
  ↓
User approves the plan
  ↓
implement-plan executes the plays (skills) deterministically
  ↓
beads tracks progress
  ↓
Done
```

---

## Category 1: ORCHESTRATION LAYER (The Coordinator) - UNIQUE

These skills implement your "play calling" system. **Cannot be replaced by marketplaces.**

| Skill | Purpose | Unique? | Why |
|-------|---------|---------|-----|
| **front-door** | Interview, triage, route tasks | ✅ YES | Your entry point pattern |
| **create-plan** | Structured implementation plans | ✅ YES | Creates the playbook |
| **continuous-planner** | Living 3-file plans | ✅ YES | Survives /clear, multi-model |
| **implement-plan** | Execute plans with beads tracking | ✅ YES | Runs the plays deterministically |
| **autonomous-builder** | Headless implementation | ✅ YES | Background execution |

**Keep these.** They're the core of your vision.

---

## Category 2: TASK TRACKING (The Backbone) - UNIQUE

| Skill | Purpose | Unique? | Why |
|-------|---------|---------|-----|
| **beads** | Git-backed task tracking with dependencies | ✅ YES | Links plans to execution |
| **create-handoff** | Preserve context before /clear | ✅ YES | Session continuity |
| **resume-handoff** | Resume from handoff | ✅ YES | Session recovery |
| **failure-recovery** | Recovery protocols | ✅ YES | Handle stuck agents |

**Keep these.** They enable the deterministic execution.

---

## Category 3: PERSONAL STACK (Your Defaults) - UNIQUE

These encode YOUR infrastructure preferences:

| Skill | Purpose | Unique? | Why |
|-------|---------|---------|-----|
| **push-to-cloud** | Deploy to oci-dev | ✅ YES | Your deployment pattern |
| **remote-exec** | SSH to homelab/macmini/oci-dev | ✅ YES | Your infrastructure |
| **secrets-sync** | SOPS secrets sync | ✅ YES | Your secrets management |
| **secrets-vault-manager** | SOPS + Age vault | ✅ YES | Your encryption setup |
| **dispatch** | Multi-model CLI (claude/codex/gemini/zai) | ⚠️ PARTIAL | MCP exists but routing is unique |
| **convex-resources** | Convex backend preference | ✅ YES | Your tech stack |
| **oci-resources** | OCI free-tier preference | ✅ YES | Your infrastructure |
| **KHAMEL MODE** (in CLAUDE.md) | Tech stack defaults | ✅ YES | Your conventions |

**Keep these.** They're your personal "offensive playbook."

---

## Category 4: EXECUTION SKILLS (The Players) - CHECK AGAINST SKILLSMP

These are the "players" that execute specific plays. **May have equivalents on SkillsMP.**

| Skill | Purpose | Replaceable? | Action |
|-------|---------|--------------|--------|
| debugger | Systematic debugging | ❓ Check SkillsMP | Audit |
| refactorer | Refactoring patterns | ❓ Check SkillsMP | Audit |
| test-runner | Run tests (pytest/jest/go) | ❓ Check SkillsMP | Audit |
| code-reviewer | Code reviews with security | ❓ Check SkillsMP | Audit |
| api-designer | API design (REST/GraphQL) | ❓ Check SkillsMP | Audit |
| git-workflow | Branches/commits/PRs | ❓ Check SkillsMP | Audit |
| ci-cd-setup | GitHub Actions | ❓ Check SkillsMP | Audit |
| docker-composer | Docker/Docker Compose | ❓ Check SkillsMP | Audit |
| database-migrator | Schema migrations | ❓ Check SkillsMP | Audit |
| documentation-generator | README/LLM-OVERVIEW | ❓ Check SkillsMP | Audit |
| performance-optimizer | Profile and optimize | ❓ Check SkillsMP | Audit |
| observability-setup | Logging/metrics/alerts | ❓ Check SkillsMP | Audit |

---

## Category 5: RESEARCH & UTILITIES - CHECK AGAINST SKILLSMP

| Skill | Purpose | Replaceable? | Action |
|-------|---------|--------------|--------|
| deep-research | Gemini CLI research | ❓ Check SkillsMP | Audit |
| freesearch | Exa API research (0 tokens) | ⚠️ PARTIAL | Exa is unique |
| delegate-to-agent | Subagent delegation | ❓ Check SkillsMP | Audit |
| diff-preview | Preview changes | ❓ Check SkillsMP | Audit |

---

## Category 6: META-SKILLS (About Skills) - MOSTLY REPLACEABLE

| Skill | Purpose | Replaceable? | Action |
|-------|---------|--------------|--------|
| auto-updater | Update skills from GitHub | ✅ YES | Built-in Claude Code |
| skill-analytics | Track skill usage | ✅ YES | Nice to have, not core |
| skills-browser | Browse local skills | ✅ YES | SkillsMP is better |
| skillsmp-browser | Browse SkillsMP | ✅ YES | Use SkillsMP directly |
| hooks-manager | Manage hooks | ❓ Check SkillsMP | Audit |
| thinking-modes | Extended thinking | ❓ Check SkillsMP | Audit |

---

## Category 7: INTERVIEW MODES - UNIQUE BUT SIMPLE

| Skill | Purpose | Unique? | Action |
|-------|---------|---------|--------|
| full-interview | Force full depth | ✅ YES | Keep (simple) |
| quick-interview | Force quick mode | ✅ YES | Keep (simple) |
| smart-interview | Reset to auto | ✅ YES | Keep (simple) |

---

## Summary Statistics

| Category | Count | Unique | Replaceable |
|----------|-------|--------|-------------|
| Orchestration | 5 | 5 | 0 |
| Task Tracking | 4 | 4 | 0 |
| Personal Stack | 8 | 8 | 0 |
| Execution | 13 | ? | ? |
| Research/Utils | 5 | 1 | ? |
| Meta-skills | 5 | 0 | 5 |
| Interview modes | 3 | 3 | 0 |

**Core unique skills:** 20 (cannot be replaced)
**Execution skills to audit:** 18
**Meta-skills to drop:** 5

---

## Next Steps

1. ✅ **Audit execution skills against SkillsMP** (in progress)
2. **Identify which execution skills to keep** (personal patterns)
3. **Design v9 architecture** focused on orchestration
4. **Document the "play calling" system explicitly**
5. **Create branch with minimal unique skills + best execution skills**

---

## Key Insight

**The value of ONE_SHOT is NOT the individual skills.**

The value is the **ORCHESTRATION SYSTEM** that:
1. Interviews to understand requirements (front-door)
2. Creates a plan linking skills (create-plan/continuous-planner)
3. Gets user approval
4. Executes deterministically (implement-plan + beads)
5. Recovers from failures (failure-recovery)

**SkillsMP provides players. ONE_SHOT provides the playbook.**

---

## The v9 Question

> **Can we make the orchestration more explicit and powerful?**

Instead of reducing skills, what if we:
1. Make the "play calling" first-class
2. Make skill discovery from SkillsMP seamless
3. Make plan→execution deterministic and trackable

**This is v9's opportunity.**
