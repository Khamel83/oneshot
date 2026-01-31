#!/usr/bin/env bash
# Check if MCP servers are running and responsive

set -euo pipefail

ISSUES=0

# Check for running MCP processes
check_mcp_processes() {
  local mcp_count=0

  # Look for common MCP server processes
  if pgrep -f "mcp-server" >/dev/null 2>&1; then
    mcp_count=$((mcp_count + $(pgrep -f "mcp-server" | wc -l)))
  fi

  if pgrep -f "npx.*@modelcontextprotocol" >/dev/null 2>&1; then
    mcp_count=$((mcp_count + $(pgrep -f "npx.*@modelcontextprotocol" | wc -l)))
  fi

  if [[ $mcp_count -gt 0 ]]; then
    echo "✓ MCP Servers: $mcp_count running"
    return 0
  else
    echo "⊘ MCP Servers: none running (optional)"
    return 0
  fi
}

# Check Claude MCP config
check_mcp_config() {
  local config_file="$HOME/.claude/mcp_config.json"

  if [[ ! -f "$config_file" ]]; then
    return 0  # No MCP config is fine
  fi

  local server_count
  server_count=$(python3 -c "import json; print(len(json.load(open('$config_file')).get('mcpServers', {})))" 2>/dev/null || echo "0")

  if [[ $server_count -gt 0 ]]; then
    echo "✓ MCP Config: $server_count servers configured"
  fi

  return 0
}

check_mcp_processes || ISSUES=1
check_mcp_config || ISSUES=1

exit $ISSUES
