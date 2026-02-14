---
name: delegation-trajectory
description: View delegation trajectories — chains of spans grouped by session
---

# Delegation Trajectory Viewer

Assemble delegation spans into session-level execution trajectories (inspired by Agent Lightning's trajectory concept).

## Instructions

1. Read `.claude/delegation-log.jsonl` (or `~/.claude/delegation-log.jsonl` if project-level doesn't exist)
2. Parse the JSONL and group entries by `session_id`
3. For each session (trajectory), display:
   - Session ID
   - Number of spans (delegations)
   - Timeline: ordered sequence of agent_type → result
   - Total tool calls across all spans
   - Total duration
   - Average reward score
   - Tool sequence pattern (most common tool chains)

4. If the user provided arguments, filter:
   - `session:<id>` → show detailed view of one trajectory
   - `last:<N>` → show only last N sessions
   - `failures` → show only sessions with at least one failed span
   - `patterns` → show recurring tool sequence patterns across all trajectories

5. If no log file exists, say "No delegation log found. Spans are logged automatically via the SubagentStop hook."

## Example Output

```
Delegation Trajectories (last 5 sessions)
───────────────────────────────────────────────────────────────────
Session abc123 (2026-02-13, 4 spans)
  1. Explore [haiku]  → success (reward: 1.0, 8 calls, 12.3s)
  2. Bash [haiku]     → success (reward: 1.0, 1 call, 2.1s)
  3. general [sonnet] → partial (reward: 0.5, 15 calls, 45.2s)
  4. Explore [haiku]  → success (reward: 1.0, 5 calls, 8.7s)
  Trajectory: avg reward 0.88, 29 total calls, 68.3s total
  Tool pattern: [Glob, Read, Grep] → [Bash] → [Read, Grep, WebSearch, Read...] → [Glob, Read]

Session def456 (2026-02-13, 1 span)
  1. Bash [haiku] → success (reward: 1.0, 2 calls, 3.4s)
  Trajectory: avg reward 1.0, 2 total calls, 3.4s total
...

Summary: 5 sessions, 12 total spans, avg reward 0.91
```

## Detailed Session View (`session:<id>`)

```
Trajectory: abc123
───────────────────────────────────────────────────────────────────
Span 1: uuid-1234
  Agent: Explore | Model: haiku | Result: success | Reward: 1.0
  Input: "Find all error handling patterns in src/"
  Output: "Found 12 error handling patterns across 5 files..."
  Tools: [Glob, Read, Read, Grep, Read, Grep, Read, Read]
  Duration: 12.3s

Span 2: uuid-5678
  Agent: Bash | Model: haiku | Result: success | Reward: 1.0
  Input: "Run the test suite"
  Output: "All 47 tests passed"
  Tools: [Bash]
  Duration: 2.1s
...

Credit flow: Span 1 (search) → Span 3 (implementation) had lowest reward — bottleneck
```
