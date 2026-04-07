---
description: Save context for session handoff
agent: build
---

# /handoff — Save Context

Preserves current session context so you can resume later with `/restore`.

## Steps

1. Collect current state:
   ```bash
   git status --short
   git log --oneline -5
   git diff --stat HEAD~3..HEAD 2>/dev/null
   ```

2. Ask the user (via `question` tool): "What's the current focus? Any blockers or decisions to note?"

3. Write handoff file to `1shot/HANDOFF-{timestamp}.md`:

   ```markdown
   # Handoff — {date}

   ## Context
   What we were working on.

   ## Progress
   - [x] Completed items
   - [ ] In-progress items
   - [ ] Next items

   ## Decisions
   Key decisions made and why.

   ## Blockers
   Anything blocking progress.

   ## Files Changed
   git diff --stat output

   ## Next Steps
   What to do when resuming.
   ```

4. Tell the user: "Handoff saved to `1shot/HANDOFF-{timestamp}.md`. Resume with `/restore`."
