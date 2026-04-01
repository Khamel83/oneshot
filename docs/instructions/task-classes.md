# Task Classes & Routing Contract

Task classes are the bridge between intent and execution. Every task in OneShot
gets classified into one of these classes, which determines its lane, worker
pool, and review path.

## Task Classes

### `plan` — Planning & Decomposition
- **Lane**: premium
- **Planner**: claude_code (required)
- **Worker**: None (planner handles directly)
- **Review**: claude_code
- **Use when**: Starting any non-trivial work, creating a roadmap, breaking down goals

### `research` — Deep Research
- **Lane**: research
- **Planner**: claude_code
- **Worker**: gemini_cli + argus (search backend)
- **Review**: claude_code (optional, for synthesis)
- **Use when**: Need to understand a domain, gather information, investigate options

### `search_sweep` — Quick Search Scan
- **Lane**: research
- **Planner**: None
- **Worker**: argus + cheap summarizer
- **Review**: claude_code (optional)
- **Use when**: Quick fact-checking, finding specific docs, looking up syntax

### `implement_small` — Bounded Implementation
- **Lane**: cheap
- **Planner**: claude_code (for task decomposition)
- **Worker**: cheap pool (MiniMax, MiMo, StepFun, etc.)
- **Review**: claude_code (required)
- **Use when**: Small code change, single file, clear requirements, isolated scope
- **Max scope**: Single module, well-defined inputs/outputs

### `implement_medium` — Medium Implementation
- **Lane**: balanced
- **Planner**: claude_code (required)
- **Worker**: balanced pool (Gemini Flash, Codex, MiniMax)
- **Review**: claude_code (required)
- **Use when**: Multi-file change, cross-cutting concern, moderate complexity

### `test_write` — Test Generation
- **Lane**: cheap
- **Planner**: claude_code (for test strategy)
- **Worker**: cheap pool
- **Review**: claude_code
- **Use when**: Writing tests for existing code, test scaffolding

### `review_diff` — Code Review
- **Lane**: premium
- **Planner**: None
- **Worker**: claude_code or strong reviewer
- **Review**: claude_code (final say)
- **Use when**: Adversarial review, quality gate, challenge pass

### `doc_draft` — Documentation Draft
- **Lane**: cheap
- **Planner**: None
- **Worker**: cheap pool
- **Review**: claude_code (optional polish)
- **Use when**: Writing README sections, API docs, inline comments

### `summarize_findings` — Result Summarization
- **Lane**: cheap
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

## CLI Reference

```bash
# Resolve routing for a task class
python -m core.router.resolve --class implement_small

# Check available models for a lane
python -c "from core.router.model_registry import models_for_lane; print(models_for_lane('cheap'))"

# Check if Argus is available
python -c "from core.search.argus_client import is_available; print(is_available())"
```
