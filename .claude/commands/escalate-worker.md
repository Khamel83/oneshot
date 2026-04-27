Escalate a failed or insufficient task to a stronger lane.

1. Read the current task's result to understand what went wrong:
   ```
   ./bin/oneshot review <task-id>
   ```

2. Pick the **next stronger lane**:
   ```
   cheap_fast → routine_coder → strong_reasoning → premium_reasoning
   cheap_summary → routine_coder → strong_reasoning → premium_reasoning
   ```

3. Create the escalation:
   ```
   ./bin/oneshot escalate <task-id> --lane <new-lane>
   ```

4. Dispatch the new task:
   ```
   ./bin/oneshot dispatch --lane <new-lane> --task-file <path-from-escalate-output> --allow-dirty
   ```

5. Clean up the old worktree:
   ```
   ./bin/oneshot worktree remove <old-task-id>
   ```

Never escalate twice to the same lane. If premium_reasoning fails, report back to the user.
