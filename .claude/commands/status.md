Run `./bin/oneshot status` to list all dispatched tasks, or `./bin/oneshot status <task-id>` for details on a specific task.

Show the user the output. If there are active tasks, suggest next steps:
- `dispatched` → worker hasn't started yet, or worktree is ready
- `collected` → ready for review: `./bin/oneshot review <id>`
- `pending` → escalated task waiting for dispatch
