---
description: Restore context from a handoff file
agent: build
---

# /restore — Resume from Handoff

Loads context from a previous `/handoff` session.

## Steps

1. Find the latest handoff file:
   ```bash
   ls -t 1shot/HANDOFF-*.md 2>/dev/null | head -1
   ```

2. If `$ARGUMENTS` is provided, use that as the file path instead.

3. Read the handoff file and summarize:
   - What was being worked on
   - What's completed vs pending
   - Any blockers
   - Next steps

4. Ask the user (via `question` tool): "Ready to continue from where you left off? Anything changed?"

5. Resume work based on the handoff's next steps.
