# /batch — Parallel Multi-File Operations

Apply the same operation across many files using parallel background agents.

## Usage

`/batch "rename foo to bar" src/**/*.ts`
`/batch --dry-run "add error handling" src/services/**/*.ts`

## Process

### 1. Identify Targets

```
Task:
  subagent_type: Explore
  description: "Find batch targets"
  prompt: "Find all files matching: [pattern]. Return file paths only, max 100."
```

### 2. Create Batches

Group files into batches of 5:
```
Files found: 30 → 6 batches of 5
```

### 3. Checkpoint

```bash
git stash push -m "batch-processor checkpoint"
```

### 4. Spawn Parallel Agents

In a SINGLE message, spawn agents for all batches:

```
Task:
  subagent_type: general-purpose
  description: "Batch 1: files 1-5"
  run_in_background: true
  prompt: |
    Apply operation: [description]
    Files: [list]
    For each: read → apply change → write → test (if applicable)
    Return: JSON {success: [], failed: []}
```

### 5. Aggregate Results

```
Total: 30 files
Success: 28
Failed: 2
  - path/file7.ts: Syntax error
  - path/file23.ts: Test failed
```

### 6. Handle Failures

If >20% failures: `git stash pop` (rollback)
Otherwise: report failures for manual review.

## Common Operations

**Rename:** Replace `/\boldName\b/g` with "newName" in all matching files
**Add import:** Add import statement to files that don't have it
**Update pattern:** Replace `console.log` with `logger.info`, add import

## Performance

| Files | Agents | Time |
|-------|--------|------|
| 30 | 6 parallel | ~30 sec |
| 50 | 10 parallel | ~30 sec |
| 100 | 20 parallel | ~45 sec |

vs sequential: 30 files × 10 sec = 5 min → **10x faster**

Context savings: ~700 tokens total vs 15,000 tokens sequential → **95% savings**
