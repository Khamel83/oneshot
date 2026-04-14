#!/bin/bash
# SubagentStop hook: logs delegation spans to .claude/delegation-log.jsonl
# Deterministic — fires every time a subagent completes, no prompt needed.
#
# v12.2: Enriched with Agent Lightning-inspired span format
#   - span_id for chaining into trajectories
#   - session_id for grouping spans per session
#   - task_input/task_output (truncated) for trace visibility
#   - tool_sequence for action pattern analysis
#   - reward heuristic (1.0=success, 0.5=partial, 0.0=failure)
#
# INSTALL: cp this to ~/.claude/delegation-log-hook.sh && chmod +x ~/.claude/delegation-log-hook.sh
# Then add SubagentStop hook entry to ~/.claude/settings.json (see settings-patch.json)

input=$(cat)

# Extract fields from the SubagentStop event JSON
agent_type=$(echo "$input" | jq -r '.agent_type // "unknown"')
model=$(echo "$input" | jq -r '.model // "unknown"')
tool_calls=$(echo "$input" | jq -r '.tool_calls_count // 0')
duration_ms=$(echo "$input" | jq -r '.duration_ms // 0')

# Truncated input/output for trace visibility (Agent Lightning: span data)
task_input=$(echo "$input" | jq -r '.task_prompt // .input // ""' | head -c 200)
task_output=$(echo "$input" | jq -r '.output // ""' | head -c 200)

# Tool sequence — ordered list of tools used (Agent Lightning: action sequence)
tool_sequence=$(echo "$input" | jq -c '.tool_names // []')

# Generate span_id (unique per delegation event)
span_id=$(cat /proc/sys/kernel/random/uuid 2>/dev/null || date +%s%N | sha256sum | head -c 36)

# Session ID from environment (groups spans into trajectories)
session_id="${CLAUDE_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-unknown}}"

# Determine log location: project .claude/ if it exists, else ~/.claude/
if [ -d ".claude" ]; then
  log_file=".claude/delegation-log.jsonl"
else
  log_file="$HOME/.claude/delegation-log.jsonl"
fi

# Determine result + reward heuristic (Agent Lightning: reward signal)
result="success"
reward=1.0
if echo "$task_output" | grep -qiE '(error|failed|exception|timeout|could not|unable to)'; then
  # Check if it's a complete failure vs partial
  if echo "$task_output" | grep -qiE '(fatal|crash|aborted|panic|no results)'; then
    result="failure"
    reward=0.0
  else
    result="partial"
    reward=0.5
  fi
fi

# Build and append enriched log entry
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
jq -cn \
  --arg ts "$timestamp" \
  --arg span "$span_id" \
  --arg session "$session_id" \
  --arg agent "$agent_type" \
  --arg model "$model" \
  --arg result "$result" \
  --argjson reward "$reward" \
  --argjson calls "${tool_calls:-0}" \
  --argjson dur "${duration_ms:-0}" \
  --argjson tools "${tool_sequence:-[]}" \
  --arg input "$(echo "$task_input" | head -c 200)" \
  --arg output "$(echo "$task_output" | head -c 80)" \
  '{
    timestamp: $ts,
    span_id: $span,
    session_id: $session,
    agent_type: $agent,
    model: $model,
    result: $result,
    reward: $reward,
    tool_calls_count: $calls,
    duration_ms: $dur,
    tool_sequence: $tools,
    task_input: $input,
    summary: $output
  }' \
  >> "$log_file" 2>/dev/null

# Always exit 0 — logging should never block the agent
exit 0
