# OneShot v2 Redesign — Research Report

> **Date**: 2026-04-04
> **Source**: Research synthesis from Claude Code docs, Anthropic internal usage report, academic literature on AI coding assistants, and Claude Code source leak commentary.
> **Status**: Suggested changes — not all need to be applied. Use as reference.

## Core Premise

The harness should optimize less for raw prompt cleverness and more for **workflow control**. Anthropic's docs highlight `CLAUDE.md`, hooks, custom commands, agent teams, and MCP as the main customization surfaces, while their internal report repeatedly emphasizes detailed repo instructions, self-verifying loops, task-type routing, and periodic resets/checkpoints.

## What the Evidence Says

| Theme | Evidence | Design Implication |
|---|---|---|
| Context quality matters more than raw autonomy | Anthropic says `CLAUDE.md` is read at session start and is meant to encode coding standards, architecture decisions, preferred libraries, and review checklists. Their internal teams say "the better you document your workflows, tools, and expectations in Claude.md files, the better Claude Code performs." Research identifies lack of project-size context as a major barrier to use and trust. | Build `oneshot` as a context-packaging system first. |
| Verification is central | Anthropic's own teams recommend self-sufficient loops that run builds, tests, and lints automatically, and say this works especially well when Claude generates tests before code. The official overview also frames Claude Code as something that can write tests, fix lint failures, and verify work across files. | Make verification a mandatory state, not an optional add-on. |
| Different tasks need different autonomy | Anthropic's internal product team explicitly distinguishes asynchronous work for peripheral/prototyping tasks from synchronous supervision for core business logic and critical fixes. Research shows developers are notably less comfortable letting assistants apply fixes unsupervised, citing trust and control concerns. | Add a task classifier that changes permissions and workflow depth by task type. |

## Recommended Architecture

Redesign `oneshot` as a workflow engine with six first-class stages:

### State Machine

1. **Intake**
2. **Explore**
3. **Plan**
4. **Implement**
5. **Verify**
6. **Commit or reset**

This matches the "explore → plan → implement → commit" pattern in Claude Code guidance.

### Suggested Repo Structure

```text
oneshot/
  harness/
    intake/
      task_classifier.ts
      risk_router.ts
    context/
      build_context.ts
      file_selector.ts
      prompt_budget.ts
      session_compactor.ts
    planning/
      planner.ts
      plan_schema.ts
    execution/
      implementer.ts
      command_runner.ts
      patch_applier.ts
    verification/
      test_runner.ts
      lint_runner.ts
      acceptance_checker.ts
    memory/
      scratchpad.ts
      task_journal.ts
      repo_facts.ts
    adapters/
      claude_code.ts
      opencode.ts
      generic_agent.ts
  templates/
    CLAUDE.md
    TASK_SPEC.md
    REVIEW_CHECKLIST.md
    SESSION_SUMMARY.md
  policies/
    low-risk.json
    medium-risk.json
    high-risk.json
```

## Stage Details

### Intake

Classify each task before touching the model. Infer from file paths, keywords, and repo-defined risk rules.

| Task Class | Examples | Default Mode |
|---|---|---|
| Low risk | Test generation, lint cleanup, docs, renames, small refactors | Async allowed |
| Medium risk | Non-core feature work, UI changes, isolated bug fixes | Planned + verified |
| High risk | Auth, billing, migrations, security-sensitive changes, infra changes | Synchronous only |

### Explore

Force an exploration pass that answers:
- What files are likely relevant?
- What commands validate this area?
- What prior conventions exist?
- What hidden constraints apply?

Generate a structured exploration artifact:

```json
{
  "goal": "...",
  "candidate_files": ["..."],
  "commands_to_run": ["npm test -- foo", "pnpm lint"],
  "constraints": ["must preserve API shape", "follow existing React Query pattern"],
  "unknowns": ["where auth token refresh happens"]
}
```

### Plan

Produce a machine-readable plan:

```json
{
  "objective": "...",
  "assumptions": ["..."],
  "steps": [
    {"id":"1","action":"add failing tests","files":["..."]},
    {"id":"2","action":"implement minimal fix","files":["..."]},
    {"id":"3","action":"refactor naming","files":["..."]}
  ],
  "verification": [
    {"type":"test","command":"pnpm test path/to/spec"},
    {"type":"lint","command":"pnpm eslint path/to/file"}
  ],
  "rollback": "git restore ...",
  "risk_level": "medium"
}
```

### Implement

- Require a clean working tree or create an isolated branch/worktree before major tasks.
- Apply one plan step at a time.
- Record every model action into a task journal.
- Auto-stop when edits exceed the planned scope.
- Trigger a "simplify pass" if the patch size or dependency count grows too fast.

### Verify

"No verification, no completion" as a hard rule.

Verifier order:
1. Targeted tests
2. Lint/static analysis
3. Type check/build
4. Acceptance assertions from the task spec
5. Diff review against allowed files

### Commit or Reset

Two explicit endings:
- `commit-success`: summarize, document, commit, optional PR.
- `reset-with-summary`: discard changes, preserve plan + lessons + failure notes.

## Context Subsystem

Four layers:

| Layer | Purpose | Source |
|---|---|---|
| Stable repo guidance | Coding standards, architecture, commands, review checklist | `CLAUDE.md` |
| Task spec | Current objective, constraints, acceptance criteria | `TASK_SPEC.md` |
| Short-lived working context | Relevant file excerpts, diffs, diagnostics | Generated per run |
| Durable learned context | Commands discovered, pitfalls, subsystem notes | `repo_facts.ts` / `SESSION_SUMMARY.md` |

## Files to Add

### CLAUDE.md (structured template)

```md
# Project identity
What this repo does in 5-10 lines

# Architecture
Key modules and invariants

# Commands
Install, test, lint, typecheck, build

# Safe-change rules
Files/subsystems that require extra care

# Preferred patterns
State management, API style, naming conventions

# Review checklist
Tests, types, docs, migration safety, perf, security
```

### TASK_SPEC.md

```md
# Goal
# Non-goals
# Constraints
# Acceptance tests
# Files likely involved
# Human decisions still required
```

### SESSION_SUMMARY.md

```md
# What changed
# Why it changed
# Commands that worked
# Surprises/pitfalls
# Follow-ups
# Recommended CLAUDE.md updates
```

## Harness Policies

### Low-risk policy
- Automatic edits
- Auto-run tests/lint
- Auto-commit optional

### Medium-risk policy
- Implementation only from approved plan
- Tests/lint mandatory
- Human approval before commit

### High-risk policy
- Exploration + plan
- Suggested patches only
- No autonomous apply

## Adapter Design

```ts
interface AgentHarness {
  explore(input: ExploreRequest): Promise<ExploreResult>
  plan(input: PlanRequest): Promise<PlanResult>
  implement(input: ImplementRequest): Promise<ImplementResult>
  verify(input: VerifyRequest): Promise<VerifyResult>
  summarize(input: SummaryRequest): Promise<SummaryResult>
}
```

## Leak-Era Takeaways

- Orchestration logic matters more than model weights
- Planning/review flows, memory systems, context injection, multi-agent/tool orchestration are the differentiators
- Aggressive use of parallel tool execution as a design pattern
- Fork-join planning: subtasks produce scoped mini-plans, merge into verified plan

## Evaluation Framework

| Task Type | Why Include It | Expected Outcome |
|---|---|---|
| Test generation | High-value, research-backed use case | Generate passing tests with edge cases |
| Small bug fix | Common official workflow | Fix + targeted verification |
| Refactor | Frequent internal usage pattern | Mechanical safety + no behavior drift |
| New feature in peripheral area | Good async candidate | Strong autonomy possible |
| Core logic change | Poor async candidate | More supervision required |
| Docs/runbook synthesis | Strong Claude use case internally | High usefulness, low risk |

Metrics: task success rate, human interventions, resets needed, patch size vs plan size, tests added, escaped errors after verification, time to trustworthy result.

## Assumption Shifts

- From "best prompt wins" to "best workflow wins"
- From "one session should carry the whole task" to "sessions should compact, summarize, and reset deliberately"
- From "autonomy is the product" to "appropriate autonomy by task class is the product"
- From "repo context is static" to "repo context should be continuously improved by session summaries"
- From "verification is downstream" to "verification is the central loop"

## Minimum Viable Redesign (Priority Order)

1. Structured `CLAUDE.md` template support
2. `TASK_SPEC.md` generator
3. Task classifier with low/medium/high-risk routing
4. Mandatory verification pipeline
5. End-of-session summary back into repo memory

## Strongest Recommendation

Make `oneshot` a **context-and-verification OS** for coding agents. Claude Code works best when the repo tells it how to behave, the task is concretized into a spec, the scope is staged, and every change is checked by objective validators before trust is granted.

## Sources

1. Claude Code overview - Claude Code Docs https://code.claude.com/docs/en/overview
2. 50 Claude Code Tips and Best Practices For Daily Use - Builder.io https://www.builder.io/blog/claude-code-tips-best-practices
3. Claude Code Best Practices: Lessons From Real Projects https://ranthebuilder.cloud/blog/claude-code-best-practices-lessons-from-real-projects/
4. 10 Essential Claude Code Best Practices You Need to Know https://discuss.huggingface.co/t/10-essential-claude-code-best-practices-you-need-to-know/174731
5. Using AI-Based Coding Assistants in Practice - arXiv https://arxiv.org/html/2406.07765v2
6. Claude Code Best Practices - GitHub Pages https://rosmur.github.io/claudecode-best-practices/
7. Claude Code Source Code Leak: 8 Hidden Features You Can Use - MindStudio https://www.mindstudio.ai/blog/claude-code-source-code-leak-8-hidden-features/
8. [AINews] The Claude Code Source Leak - Latent.Space https://www.latent.space/p/ainews-the-claude-code-source-leak
9. Anthropic's Guide to Claude Code: Best Practices for Agentic Coding https://www.reddit.com/r/ClaudeAI/comments/1k5slll/
10. [PDF] How Anthropic teams use Claude Code https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf
11. Claude Code Best Practices: Planning, Context Transfer, TDD - DataCamp https://www.datacamp.com/tutorial/claude-code-best-practices
12. [2406.07765] Using AI-Based Coding Assistants in Practice - arXiv https://arxiv.org/abs/2406.07765
13. Deep dive into the Claude Code source leak - Reddit https://www.reddit.com/r/ClaudeCode/comments/1sawq4l/
14. awattar/claude-code-best-practices - GitHub https://github.com/awattar/claude-code-best-practices
15. What context would make AI coding assistants actually useful - Reddit https://www.reddit.com/r/webdev/comments/1nq63fj/
16. Skill authoring best practices - Claude API Docs https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
17. Using AI-Based Coding Assistants in Practice (v1) - arXiv https://arxiv.org/html/2406.07765v1
