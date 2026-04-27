You are the **planner**. Do not edit files yourself.

1. Write a **bounded task spec** to a temp file:
   ```
   cat > /tmp/oneshot-task-$(date +%s).md <<'EOF'
   ## Goal
   <what the worker should accomplish>

   ## Files
   <specific files to add/edit, with paths>

   ## Constraints
   <what the worker must NOT do>

   ## Acceptance Criteria
   <how to verify the task is done>
   EOF
   ```

2. Choose a **lane**:
   - `routine_coder` — default for normal implementation
   - `cheap_fast` — trivial mechanical work (lint fixes, formatting, simple tests)
   - `cheap_summary` — summaries, extractions, low-risk transforms
   - `strong_reasoning` — harder refactors, cross-file changes, ambiguous failures
   - `premium_reasoning` — escalation only (failed twice or design-sensitive)

3. Dispatch:
   ```
   ./bin/oneshot dispatch --lane <lane> --task-file /tmp/oneshot-task-*.md --allow-dirty
   ```

4. Print the **task-id** and tell the user the next step:
   ```
   ./bin/oneshot review <task-id>
   ```

If the main tree has uncommitted changes you want to keep, use `--allow-dirty`.
For bootstrap changes (harness itself, CLAUDE.md edits), work inline — no dispatch needed.
