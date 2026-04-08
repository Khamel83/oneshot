---
description: Systematic debugging with 4 mandatory phases
agent: build
---

# /debug — Systematic Debugging Protocol

4-phase debugging. Phases 1-3 are read-only. No code changes until Phase 4.

## Usage

`/debug` or `/debug <description of the problem>`

## Behavior

### Phase 1: Investigate (READ-ONLY)

**Do not fix anything. Only observe.**

1. Reproduce the bug — get the exact error message, stack trace, or unexpected behavior. Show the output.
2. Identify the symptom — expected vs actual behavior.
3. Gather context — read relevant files, check `git log --oneline -10`, check tests.
4. Check for known causes: off-by-one, null handling, race conditions, config issues, dependency mismatches, state mutation.

Write a structured summary to `1shot/DEBUG.md`:
- Symptom: what's wrong
- Expected vs Actual
- Error Output (verbatim)
- Context: files read, recent changes, test status

### Phase 2: Analyze (READ-ONLY)

Still no code changes. Identify the root cause.

1. State the root cause hypothesis.
2. Classify: logic error, state bug, integration issue, environment issue, data issue.
3. Trace the data flow from input to failure point.
4. Confirm with evidence — point to specific lines.

Append to `1shot/DEBUG.md`:
- Root Cause: one sentence
- Bug Class: category
- Evidence: file:line with reasoning

### Phase 3: Hypothesize (READ-ONLY)

Design the minimal fix before writing it.

1. State the exact fix.
2. Predict impact — what else could break?
3. Design verification — how to confirm it works?
4. If uncertain: propose a diagnostic change (e.g., logging) first.

Append to `1shot/DEBUG.md`:
- Proposed Fix: exact change
- Risk Assessment
- Verification Plan

Ask the user: "Does this analysis look right? Should I proceed with the fix?"

### Phase 4: Fix

Now you may write code.

1. Implement the fix from Phase 3.
2. Verify: run the reproduction case from Phase 1. Show it passes.
3. Check for regressions: run existing tests. Show they pass.
4. Add regression test if applicable.
5. Commit: `fix: {what was wrong}`

Append to `1shot/DEBUG.md`:
- Fix Applied: what changed
- Verification: test output
- Regression test: added or N/A

### Done

```
Debug Complete
├─ Root cause: {one-liner}
├─ Bug class: {category}
├─ Files changed: {count}
├─ Verification: {pass/fail}
└─ Regression test: {added/skipped}
```
