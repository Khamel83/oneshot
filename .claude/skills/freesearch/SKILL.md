---
name: freesearch
description: TRULY FREE research via Gemini CLI - zero Claude tokens burned. Uses Bash directly, no sub-agent.
homepage: https://github.com/Khamel83/oneshot
metadata: {"oneshot":{"emoji":"🆓","requires":{"bins":["gemini"]}}}
---

# /freesearch - TRULY FREE Research

**Uses 0 Claude Code tokens.** Calls Gemini CLI directly via Bash.

## When To Use

User says:
- `/freesearch [topic]` - Slash command
- "Free research on [topic]"
- "Research without burning tokens"

---

## How It Works

**Direct execution, no sub-agent:**

1. Ask 2-3 clarifying questions (goal, depth, audience)
2. Run Gemini CLI directly via Bash tool:
   ```bash
   gemini --yolo "COMPREHENSIVE RESEARCH PROMPT"
   ```
3. Save output to `~/github/oneshot/research/[slug]/research.md`

**Key difference from deep-research:**
| Skill | Claude Tokens Used |
|-------|-------------------|
| `/deep-research` | ❌ Yes (sub-agent wrapper) |
| `/freesearch` | ✅ No (direct Bash) |

---

## Research Prompt Template

```bash
gemini --yolo "Conduct comprehensive research on: [TOPIC]

CONTEXT:
- Goal: [user's goal - learning/decision/writing/curiosity]
- Depth: [overview/technical/deep-dive]
- Audience: [technical/general/expert]

COVER THESE SECTIONS:

1. Overview & Core Concepts
   - What is this? Why does it matter?
   - Key terminology and definitions
   - Historical context

2. Current State
   - Latest developments (2024-2025)
   - Major players and projects
   - Market adoption/status

3. Technical Deep Dive
   - How it works (mechanisms, architecture)
   - Key techniques and algorithms
   - Technical challenges

4. Practical Applications
   - Real-world use cases
   - Tools and libraries available
   - Implementation examples

5. Challenges & Open Problems
   - Technical barriers
   - Ethical considerations
   - Limitations

6. Future Outlook
   - Trends and predictions
   - Emerging areas
   - What to watch

7. Resources
   - Key papers and research
   - Notable researchers/teams
   - Communities and forums
   - Courses and learning materials

OUTPUT FORMAT: Markdown with proper headings. Aim for 500+ lines with specific examples and citations."
```

---

## Output Location

```
~/github/oneshot/research/<slug>/research.md
```

Example: `~/github/oneshot/research/polymarket-api/research.md`

---

## Setup (One-Time)

```bash
# Install Gemini CLI
npm install -g @google/gemini-cli

# Authenticate
gemini auth login

# Verify
gemini "test"
```

---

## Example Usage

**User says:** `/freesearch Polymarket API`

**You do:**
1. Ask: "What's your goal? Building something, learning, or making a decision?"
2. User: "Building a betting bot"
3. Run:
   ```bash
   mkdir -p ~/github/oneshot/research/polymarket-api
   gemini --yolo "Conduct comprehensive research on Polymarket API...
   [full prompt with context about building a betting bot]
   " > ~/github/oneshot/research/polymarket-api/research.md
   ```
4. Read the file and summarize key findings

---

## Why This Exists

The `deep-research` skill wraps Gemini CLI in a Claude sub-agent, which still burns tokens. This skill calls Gemini CLI **directly** via the Bash tool, so:

- ✅ 0 Claude Code tokens for research
- ✅ Only main conversation tokens (clarifying questions, summary)
- ✅ Same quality research (Gemini 2.5 Pro)

**Trade-off:** Less sophisticated than the sub-agent approach (no multi-step iteration), but saves significant tokens.

---

## Tips

- Research takes 30-90 seconds (Gemini is fast)
- Use `--yolo` flag to auto-approve file operations
- Check `~/github/oneshot/research/` for past research
- Always include user's goal in the prompt for better results
