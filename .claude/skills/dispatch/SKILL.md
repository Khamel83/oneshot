---
name: dispatch
description: Multi-model CLI orchestrator. Routes tasks to locally-installed AI CLIs (claude, codex, gemini, qwen). Zero Claude tokens for executed work.
homepage: https://github.com/Khamel83/oneshot
metadata: {"oneshot":{"emoji":"\ud83d\udce5","requires":{"bins":["claude","codex","gemini"]}}}
---

# /dispatch - Multi-Model CLI Orchestrator

**Route tasks to the best CLI tool.** Minimize Claude Code tokens by leveraging pre-authenticated local CLIs.

## When To Use

User says:
- `/dispatch [task]` - Auto-select best CLI
- `/dispatch gemini [task]` - Explicit CLI selection
- `/dispatch codex "Write a function"` - Code generation
- "Use gemini for research"
- "Route to codex for this"

---

## Available CLIs

| CLI | Version | Auth | Best For | Cost |
|-----|---------|------|----------|------|
| `claude` | 2.1.25 | Max plan | Complex reasoning, planning | $$$ |
| `codex` | 0.92.0 | OpenAI | Code generation, refactoring | $$ |
| `gemini` | 0.26.0 | Google | Research, Q&A, free tier | FREE |
| `qwen` | TBD | Qwen | General tasks (2K free/day) | FREE |

---

## How It Works

**Three modes:**

### Mode 1: Explicit Dispatch

User specifies target CLI:

```bash
# Dispatch to codex
codex "Write a Python function that validates email addresses"

# Dispatch to gemini (0 tokens)
gemini --yolo "Research: best practices for API rate limiting"

# Dispatch to claude
claude -p "Design a microservices architecture for..." --output-format json
```

### Mode 2: Auto-Select (Smart Routing)

Based on task keywords:

| Task Pattern | Routes To | Reason |
|--------------|-----------|--------|
| "research", "find out", "what is", "explain" | `gemini` | Free tier, web search |
| "write code", "implement", "refactor", "fix bug" | `codex` | Optimized for code |
| "plan", "design", "architect", "complex" | `claude` | Best reasoning |
| Ambiguous (no match) | Ask user OR default to `gemini` | Cheapest option |

### Mode 3: Multi-Step Plan Execution

Execute a plan with different tools per step:

```bash
/dispatch plan TODO.md  # Execute each step with appropriate CLI
```

---

## CLI Invocation Patterns

### Claude Code CLI
```bash
# Simple prompt
claude -p "prompt" --output-format json

# With working directory context
claude -p "prompt" --cwd /path/to/project

# Non-interactive (for automation)
claude -p "prompt" --dangerously-skip-permissions --output-format json
```

### OpenAI Codex CLI
```bash
# Simple code generation (non-interactive)
codex exec "Write a Python function that..."

# With file context
codex exec --file src/main.py "Refactor this to use async"

# Interactive (for terminal use)
codex "Write a Python function that..."
```

### Gemini CLI
```bash
# Simple query (interactive)
gemini "What are best practices for..."

# Non-interactive with auto-approve
gemini --yolo "Comprehensive research on..."

# With model override
gemini --model gemini-2.5-pro "Complex analysis..."
```

### Qwen Code CLI (after installation)
```bash
# Non-interactive (one-shot)
qwen "Implement this feature"

# Interactive (for terminal use)
qwen -i "Implement this feature"

# With file context
qwen --file main.ts "Add error handling"
```

---

## Output Location

All CLI outputs saved to:
```
~/github/oneshot/dispatch/<timestamp>-<cli>/
├── prompt.txt     # Original prompt sent
├── output.txt     # Raw CLI output
└── summary.md     # Key findings (if applicable)
```

---

## Model Selection Logic

```yaml
# Keyword-based routing
cli_router:
  codex:
    keywords: ["generate code", "write function", "implement", "refactor", "fix bug", "code review"]

  gemini:
    keywords: ["research", "explain", "summarize", "what is", "find out", "search for"]

  claude:
    keywords: ["plan", "design", "architect", "complex", "analyze trade-offs", "multi-step"]

  qwen:
    keywords: ["general task", "quick question", "simple"]
    fallback: true  # Use when others fail
```

---

## Fallback Chain

If primary CLI fails:
1. Try fallback CLI from matrix
2. If all fail, return error with diagnostics
3. Never silently swallow errors

---

## Integration with Beads

```bash
# Track multi-step dispatch as beads tasks
bd create "Dispatch: Research auth patterns" -l dispatch -d "gemini"
bd update <id> --status in_progress
# ... execute ...
bd close <id> --reason "Output: research.md"
```

---

## Setup (One-Time)

### Claude (already installed)
```bash
# Verify
claude --version
```

### Codex (already installed)
```bash
# Verify
codex --version

# Authenticate if needed
codex auth login
```

### Gemini (already installed)
```bash
# Verify
gemini --version

# Authenticate if needed
gemini auth login
```

### Qwen Code (to be installed)
```bash
# Install via npm
npm install -g @qwen-code/qwen-code

# Verify (binary is named 'qwen')
qwen --version
# Output: 0.8.2

# Test
qwen "test"
```

---

## Example Usage

**User says:** `/dispatch "Research WebSocket best practices"`

**You do:**
1. Detect "research" keyword → route to gemini
2. Run:
   ```bash
   mkdir -p ~/github/oneshot/dispatch/$(date +%s)-gemini
   gemini --yolo "Research WebSocket best practices for real-time applications.
   Focus on: connection handling, reconnection strategies, scalability, and security.
   Output format: Markdown with code examples." > output.txt
   ```
3. Read output.txt and summarize key findings

---

## Why This Exists

- ✅ Minimize Claude Code token usage
- ✅ Leverage specialized CLIs (codex for code, gemini for research)
- ✅ Zero API keys needed (all pre-authenticated)
- ✅ Fallback options if one CLI fails

**Trade-off:** Less context awareness than Claude Code sub-agents, but significantly cheaper.

---

## Anti-Patterns

- Dispatching trivial tasks (just answer directly)
- Using `claude` for simple research (use `gemini`, it's free)
- Using `gemini` for complex code (use `codex`)
- Not capturing output (always save to file)
- Ignoring CLI errors (always check exit codes)

---

## Keywords

dispatch, route, delegate, multi-model, codex, gemini, qwen, cli, orchestrate
