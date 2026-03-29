#!/usr/bin/env bash
# ONE-SHOT Heartbeat — Daily health check for all machines
# Usage: ./heartbeat.sh [--force] [--quiet]
#
# Checks:
#   1. ONE-SHOT repo up to date
#   2. GLM model version (auto-updates)
#   3. Secrets decryptable
#   4. CLI tools (Claude Code, Codex, Gemini)
#   5. API keys (ZAI, Tavily, Exa, etc.)
#   6. MCP servers configured
#   7. Tailscale + internet connectivity
#   8. Cross-machine reachability (oci, homelab, macmini)
#
# Deploy to all machines via oneshot sync + git pull.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/state.sh"

# Parse arguments
QUIET=false
FORCE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quiet|-q) QUIET=true ;;
    --force|-f) FORCE=true ;;
  esac
  shift
done

# Once-per-day gate
TODAY=$(date +%Y-%m-%d)
LAST_CHECK=$(state_get_last_check)

if [[ "$FORCE" != "true" ]] && [[ "$LAST_CHECK" == "$TODAY" ]]; then
  [[ "$QUIET" != "true" ]] && echo "heartbeat: already ran today ($TODAY)"
  exit 0
fi

if [[ "$QUIET" != "true" ]]; then
  echo ""
  echo "╔══════════════════════════════════════════╗"
  echo "║  ONE-SHOT Heartbeat  $(date '+%Y-%m-%d %H:%M')  ║"
  echo "║  $(hostname)                              ║"
  echo "╚══════════════════════════════════════════╝"
fi

RESULTS=()
ISSUES=0

run_check() {
  local name="$1"
  local script="$2"
  local fix_flag=""

  if [[ ! -f "$script" ]]; then
    RESULTS+=("○ $name (script missing)")
    return
  fi

  [[ "$FORCE" == "true" && "$script" == *"check-clis.sh" ]] && fix_flag="--fix"

  if output=$("$script" $fix_flag 2>&1); then
    # Extract just the pass/fail lines for summary
    local passed failed
    passed=$(echo "$output" | grep -c "^✓" || true)
    failed=$(echo "$output" | grep -c "^⚠️" || true)

    if [[ "$QUIET" != "true" ]]; then
      echo "$output" | sed 's/^/  /'
    fi

    if [[ "$failed" -eq 0 ]]; then
      RESULTS+=("✓ $name")
    else
      RESULTS+=("⚠️  $name ($failed issue(s))")
      ISSUES=$((ISSUES + failed))
    fi
  else
    RESULTS+=("⚠️  $name (exit $?)")
    ISSUES=$((ISSUES + 1))
  fi
}

# ── Run all checks ─────────────────────────────────────────────────────────

run_check "ONE-SHOT Repo"  "$SCRIPT_DIR/check-oneshot.sh"
run_check "GLM Model"      "$SCRIPT_DIR/check-glm.sh"
run_check "Secrets"        "$SCRIPT_DIR/sync-secrets.sh"
run_check "CLI Tools"      "$SCRIPT_DIR/check-clis.sh"
run_check "API Keys"       "$SCRIPT_DIR/check-apis.sh"
run_check "MCP Servers"    "$SCRIPT_DIR/check-mcps.sh"
run_check "Connectivity"   "$SCRIPT_DIR/check-connections.sh"

# ── Cross-machine check ────────────────────────────────────────────────────

if [[ "$QUIET" != "true" ]]; then
  echo "  Cross-Machine Reachability:"
fi

MACHINE_OK=0
MACHINE_TOTAL=0
THIS_IP=$(tailscale ip -4 2>/dev/null || echo "")

check_machine() {
  local name="$1"
  local host="$2"
  local ip="${3:-}"

  # Skip self (compare by IP)
  if [[ -n "$ip" && "$ip" == "$THIS_IP" ]]; then
    if [[ "$QUIET" != "true" ]]; then echo "  ○ $name — self"; fi
    return
  fi

  MACHINE_TOTAL=$((MACHINE_TOTAL + 1))

  if ssh -o ConnectTimeout=3 -o BatchMode=yes "$host" true 2>/dev/null; then
    if [[ "$QUIET" != "true" ]]; then echo "  ✓ $name"; fi
    MACHINE_OK=$((MACHINE_OK + 1))
  else
    if [[ "$QUIET" != "true" ]]; then echo "  ⚠️  $name — unreachable"; fi
    ISSUES=$((ISSUES + 1))
  fi
}

check_machine "oci-dev"  "oci-dev"    "100.126.13.70"
check_machine "homelab" "homelab"   "100.112.130.100"
check_machine "macmini"  "macmini"   "100.113.216.27"

RESULTS+=("✓ Machines: $MACHINE_OK/$MACHINE_TOTAL reachable")

# ── Save state + summary ───────────────────────────────────────────────────

state_set_last_check "$TODAY"

if [[ "$QUIET" != "true" ]]; then
  echo ""
  echo "Results:"
  for r in "${RESULTS[@]}"; do
    echo "  $r"
  done

  if [[ $ISSUES -gt 0 ]]; then
    echo ""
    echo "  $ISSUES issue(s) found — run with --force to auto-fix CLIs"
  fi
  echo ""
fi

exit $ISSUES
