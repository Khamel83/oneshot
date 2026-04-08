---
description: Test-driven development with RED-GREEN-REFACTOR cycle
agent: build
---

# /tdd — Test-Driven Development

RED-GREEN-REFACTOR cycle. No production code without a failing test shown first.

## Usage

`/tdd` or `/tdd <feature or behavior to implement>`

## Behavior

### The Cycle

Repeat until the feature is complete:

#### RED: Write a Failing Test

1. Read relevant files, check existing tests.
2. Write one test for the desired behavior. It must:
   - Be specific to one behavior
   - Fail for the right reason (not syntax/import error)
   - Have a clear, descriptive name
3. Run the test. Show the output. It must fail.
4. Do not write any production code yet.

#### GREEN: Make It Pass

1. Write the minimal code to make the test pass.
2. Run the test. Show the output. It must pass.
3. Don't over-engineer. Only what's needed for this one test.
4. If you need to change the test to make it pass, go back to RED.

#### REFACTOR: Clean Up

1. Run all tests — they must pass before refactoring.
2. Clean up: rename, extract, simplify. One change at a time.
3. Run all tests after each refactoring step. If anything breaks, revert.
4. Stop when clean enough.

### Rules

1. **No production code without a failing test shown first.** Non-negotiable.
2. One test, one fix. Don't batch.
3. Tests are the spec. If it's not tested, it doesn't exist.
4. Show output for every RED and GREEN step.

### Exceptions

- Bug fixes without test infrastructure: write test as part of fix (RED+GREEN in one step).
- Exploratory coding: prototype first, throw away, then TDD for real.

### Done

```
TDD Complete
├─ Tests written: N
├─ Tests passing: N
├─ Cycles: N
└─ Coverage: {files covered}
```
