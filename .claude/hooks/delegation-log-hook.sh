#!/bin/bash
# SubagentStop hook: logs delegation events to .claude/delegation-log.jsonl
# Deterministic — fires every time a subagent completes, no prompt needed.
#
# INSTALL: cp this to ~/.claude/delegation-log-hook.sh && chmod +x ~/.claude/delegation-log-hook.sh
# Then add SubagentStop hook entry to ~/.claude/settings.json (see settings-patch.json)

input=$(cat)

# Extract fields from the SubagentStop event JSON
agent_type=$(echo "$input" | jq -r '.agent_type // "unknown"')
model=$(echo "$input" | jq -r '.model // "unknown"')
tool_calls=$(echo "$input" | jq -r '.tool_calls_count // 0')
duration_ms=$(echo "$input" | jq -r '.duration_ms // 0')
# SubagentStop provides the subagent's final output
output=$(echo "$input" | jq -r '.output // ""' | head -c 200)

# Determine log location: project .claude/ if it exists, else ~/.claude/
if [ -d ".claude" ]; then
  log_file=".claude/delegation-log.jsonl"
else
  log_file="$HOME/.claude/delegation-log.jsonl"
fi

# Determine result heuristic: if output contains error/fail keywords, mark partial
result="success"
if echo "$output" | grep -qiE '(error|failed|exception|timeout|could not|unable to)'; then
  result="partial"
fi

# Build and append log entry
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
jq -cn \
  --arg ts "$timestamp" \
  --arg agent "$agent_type" \
  --arg model "$model" \
  --arg result "$result" \
  --argjson calls "${tool_calls:-0}" \
  --argjson dur "${duration_ms:-0}" \
  --arg summary "$(echo "$output" | head -c 80)" \
  '{timestamp: $ts, agent_type: $agent, model: $model, result: $result, tool_calls_count: $calls, duration_ms: $dur, summary: $summary}' \
  >> "$log_file" 2>/dev/null

# Always exit 0 — logging should never block the agent
exit 0
