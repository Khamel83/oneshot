# Task Classes & Routing Contract

Task classes are the bridge between intent and execution. Every task in OneShot
gets classified into one of these classes, which determines its lane, worker
pool, and review path.

## Task Classes

> **Note**: The lane names below (`cheap`, `balanced`, `premium`, `research`) describe the legacy `/conduct` routing system (`config/lanes.yaml`). The active dispatch harness uses different lane names (`cheap_fast`, `cheap_summary`, `routine_coder`, `strong_reasoning`, `premium_reasoning`) — see `.oneshot/config/models.yaml`.

| Class | Lane | Category | Preferred Workers |
|-------|------|----------|-------------------|
| `plan` | premium | general | claude_code |
| `research` | research | research | gemini_cli, codex |
| `search_sweep` | research | research | gemini_cli, codex |
| `implement_small` | cheap | coding | codex, gemini_cli |
| `implement_medium` | balanced | coding | codex, gemini_cli |
| `test_write` | cheap | coding | codex, gemini_cli |
| `review_diff` | premium | review | codex, claude_code |
| `doc_draft` | cheap | writing | gemini_cli, codex |
| `summarize_findings` | cheap | writing | gemini_cli, codex |

### `plan` — Planning & Decomposition
- **Lane**: premium | **Category**: general
- **Planner**: claude_code (required)
- **Worker**: None (planner handles directly)
- **Review**: claude_code
- **Use when**: Starting any non-trivial work, creating a roadmap, breaking down goals

### `research` — Deep Research
- **Lane**: research | **Category**: research
- **Planner**: claude_code
- **Worker**: gemini_cli + argus (search backend)
- **Review**: claude_code (optional, for synthesis)
- **Use when**: Need to understand a domain, gather information, investigate options

### `search_sweep` — Quick Search Scan
- **Lane**: research | **Category**: research
- **Planner**: None
- **Worker**: argus + cheap summarizer
- **Review**: claude_code (optional)
- **Use when**: Quick fact-checking, finding specific docs, looking up syntax

### `implement_small` — Bounded Implementation
- **Lane**: cheap | **Category**: coding
- **Planner**: claude_code (for task decomposition)
- **Worker**: cheap pool (codex, gemini_cli, glm_claude)
- **Review**: claude_code (required)
- **Use when**: Small code change, single file, clear requirements, isolated scope
- **Max scope**: Single module, well-defined inputs/outputs

### `implement_medium` — Medium Implementation
- **Lane**: balanced | **Category**: coding
- **Planner**: claude_code (required)
- **Worker**: balanced pool (codex, gemini_cli)
- **Review**: claude_code (required)
- **Use when**: Multi-file change, cross-cutting concern, moderate complexity

### `test_write` — Test Generation
- **Lane**: cheap | **Category**: coding
- **Planner**: claude_code (for test strategy)
- **Worker**: cheap pool
- **Review**: claude_code
- **Use when**: Writing tests for existing code, test scaffolding

### `review_diff` — Code Review
- **Lane**: premium | **Category**: review
- **Planner**: None
- **Worker**: claude_code or strong reviewer
- **Review**: claude_code (final say)
- **Use when**: Adversarial review, quality gate, challenge pass

### `doc_draft` — Documentation Draft
- **Lane**: cheap | **Category**: writing
- **Planner**: None
- **Worker**: cheap pool
- **Review**: claude_code (optional polish)
- **Use when**: Writing README sections, API docs, inline comments

### `summarize_findings` — Result Summarization
- **Lane**: cheap | **Category**: writing
- **Planner**: None
- **Worker**: cheap pool
- **Review**: None
- **Use when**: Condensing research, summarizing logs, creating executive summaries

## Classification Guide

To classify a task, ask:

1. **Does it require understanding the full repo context?** → `plan` or `review_diff`
2. **Does it need web search?** → `research` or `search_sweep`
3. **Is it a code change?**
   - Single file, clear scope → `implement_small`
   - Multi-file, moderate complexity → `implement_medium`
4. **Is it a test?** → `test_write`
5. **Is it documentation?** → `doc_draft`
6. **Is it summarizing something?** → `summarize_findings`

## Lane Escalation

Each lane has a `fallback_lane` in `config/lanes.yaml`. If a worker fails:
- `cheap` → `balanced` → `premium` → inline (Claude handles directly)
- `research` → `balanced` → inline

Three consecutive failures → circuit breaker → log blocker → skip.

## Available Workers

| Worker | Lane(s) | Backend | Notes |
|--------|---------|---------|-------|
| `opencode_go/deepseek-v4-flash` | cheap_fast, routine_coder | OpenCode Go API | Fast, default for routine tasks |
| `opencode_go/kimi-k2.6` | strong_reasoning | OpenCode Go API | Strong reasoning, cross-file changes |
| `opencode_go/deepseek-v4-pro` | premium_reasoning | OpenCode Go API | Escalation only |
| `opencode_go/minimax-m2.7` | routine_coder (legacy) | OpenCode Go / Claude CLI path | Anthropic-compatible endpoint |
| `codex` | (legacy) | ChatGPT Plus OAuth | Requires `unset OPENAI_API_KEY` |
| `gemini_cli` | (legacy) | Google API | Direct CLI |
| `glm_claude` | (retired) | ZAI/GLM | ⚠️ Plan expired 2026-05-02 — unavailable |
| `claude_code` | premium, planner | Anthropic API | Main orchestrator, never dispatched externally |

## Risk Classification

Every task has a **risk level** (`low`, `medium`, `high`) that controls what workers
can do autonomously. Risk and complexity (task class) are **independent axes** -- a
3-line auth change is small complexity but high risk; a large refactoring of utility
functions is high complexity but low risk.

### Risk Levels

| Level | Auto-edit | Auto-verify | Auto-commit | Needs approval | Sync-only |
|-------|-----------|-------------|-------------|----------------|-----------|
| `low` | Yes | Yes | No | No | No |
| `medium` | No | Yes | No | Yes | No |
| `high` | No | Yes | No | Yes | Yes |

### Inference Rules

Risk is inferred from keywords in the task description and affected file paths:

**High risk** (any match): auth, billing, migration, security, password, token,
secret, credential, production, deploy

**Low risk** (any match): refactor, rename, test, lint, doc, format, comment

**Medium risk**: everything else (default)

High-risk keywords take priority over low-risk keywords -- if a description contains
both "refactor" and "auth", it's classified as high risk.

### Examples

- "Fix typo in README" -- `implement_small`, risk `low`
- "Rename `utils.py` to `helpers.py`" -- `implement_small`, risk `low`
- "Add login endpoint" -- `implement_medium`, risk `high`
- "Deploy v2 to production" -- `plan`, risk `high`
- "Format all Python files with black" -- `implement_small`, risk `low`
- "Add caching to API handler" -- `implement_medium`, risk `medium`

## CLI Reference

```bash
# List active dispatch lanes
./bin/oneshot lanes

# Check dispatched task status
./bin/oneshot status

# Check if Argus is available
python -c "from core.search.argus_client import is_available; print(is_available())"
```
