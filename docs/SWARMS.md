# ONE_SHOT Swarm Guide

Agent team orchestration using Claude's experimental Agent Teams feature.

## Prerequisites

Enable experimental feature:
```bash
# Add to ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Or export in shell:
```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

## When to Use Swarms

| Good for Swarms | NOT for Swarms |
|-----------------|----------------|
| Research & review | Sequential tasks |
| Competing hypotheses | Same-file edits |
| Cross-layer coordination | Work with many dependencies |
| New modules/features | Routine tasks |

**Token cost**: Swarms use significantly more tokens (each teammate = separate Claude instance).

## Swarm Patterns

### 1. Research & Review
Multiple teammates investigate different aspects simultaneously.

```
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
```

### 2. Competing Hypotheses (Debugging)
Teammates test different theories in parallel and debate.

```
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk to
each other to try to disprove each other's theories, like a scientific debate.
```

### 3. Cross-Layer Coordination
Different teammates own different layers (frontend, backend, tests).

```
Create an agent team to implement [feature]:
- One teammate on frontend (Astro components)
- One teammate on backend (Cloudflare Workers)
- One teammate on tests
```

### 4. New Modules
Each teammate owns a separate piece.

```
Create a team with 4 teammates to refactor these modules in parallel.
```

## Controls

| Mode | Key | Action |
|------|-----|--------|
| In-process | `Shift+Up/Down` | Select teammate |
| In-process | `Enter` | View teammate's session |
| In-process | `Escape` | Interrupt teammate |
| In-process | `Ctrl+T` | Toggle task list |
| Any | `Shift+Tab` | Delegate mode (lead only coordinates) |

## Display Modes

| Mode | Description | Requirements |
|------|-------------|--------------|
| `in-process` | All in main terminal | None |
| `split-panes` | Each teammate in own pane | tmux or iTerm2 |

Force mode via CLI:
```bash
claude --teammate-mode in-process
```

## Plan Approval Mode

For complex/risky tasks:
```
Spawn an architect teammate to refactor [module].
Require plan approval before they make any changes.
```

Teammate plans → Lead approves → Implementation begins.

## Task Management

- Tasks: pending → in_progress → completed
- Dependencies: Blocked tasks wait for dependencies
- Assignment: Lead assigns OR teammates self-claim

## Cleanup

1. Shut down teammates: "Ask [teammate] to shut down"
2. Clean up team: "Clean up the team"

## Limitations

- No session resumption with in-process teammates
- Task status can lag
- One team per session
- No nested teams
- Lead is fixed
- Split panes require tmux or iTerm2
- **External models NOT supported** (Claude models only)

## Quality Gates (Hooks)

| Hook | When | Exit Code 2 |
|------|------|-------------|
| `TeammateIdle` | Teammate about to go idle | Send feedback, keep working |
| `TaskCompleted` | Task marked complete | Prevent completion, send feedback |

## Best Practices

1. **Give context** - Include task-specific details in spawn prompt
2. **Size tasks right** - Self-contained with clear deliverables
3. **Wait for teammates** - "Wait for teammates before proceeding"
4. **Start with research** - Before parallel implementation
5. **Avoid file conflicts** - Each teammate owns different files
6. **Monitor and steer** - Check in, redirect, synthesize

## Sources

- [Claude Code Agent Teams Docs](https://code.claude.com/docs/en/agent-teams)
- [Reddit Walkthrough](https://www.reddit.com/r/ClaudeCode/comments/1qz8tyy/how_to_set_up_claude_code_agent_teams_full/)
- [Claude Swarm Mode Guide](https://help.apiyi.com/en/claude-code-swarm-mode-multi-agent-guide-en.html)
