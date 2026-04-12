#!/usr/bin/env bash
# Install (or update) the janitor cron job on the current machine.
#
# Runs the janitor once per hour, logs to ~/.janitor-cron.log.
# Safe to run multiple times — overwrites the existing entry.
#
# Usage:
#   bash scripts/install-janitor-cron.sh [--uninstall] [--interval MINUTES]
#
# Options:
#   --uninstall     Remove the janitor cron entry
#   --interval N    Run every N minutes (default: 60)
#   --dry-run       Print the crontab entry without installing it

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$HOME/.janitor-cron.log"
INTERVAL=60
DRY_RUN=false
UNINSTALL=false

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --uninstall) UNINSTALL=true; shift ;;
        --interval)  INTERVAL="$2"; shift 2 ;;
        --dry-run)   DRY_RUN=true; shift ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# Detect Python
PYTHON=$(command -v python3 || command -v python || echo "")
if [[ -z "$PYTHON" ]]; then
    echo "Error: python3 not found in PATH" >&2
    exit 1
fi

# Detect virtualenv (if exists alongside project)
VENV_ACTIVATE=""
for venv_path in "$PROJECT_DIR/.venv/bin/activate" "$PROJECT_DIR/venv/bin/activate" "$HOME/.venvs/oneshot/bin/activate"; do
    if [[ -f "$venv_path" ]]; then
        VENV_ACTIVATE="source $venv_path && "
        break
    fi
done

# Build the cron command
CRON_CMD="${VENV_ACTIVATE}cd \"$PROJECT_DIR\" && $PYTHON -m core.janitor.cron >> \"$LOG_FILE\" 2>&1"

# Build the cron schedule
# INTERVAL=60 → run at minute 0 of every hour: "0 * * * *"
# INTERVAL=30 → run every 30 minutes: "*/30 * * * *"
# INTERVAL=15 → run every 15 minutes: "*/15 * * * *"
if [[ "$INTERVAL" -eq 60 ]]; then
    CRON_SCHEDULE="0 * * * *"
elif [[ "$INTERVAL" -ge 60 ]]; then
    HOURS=$(( INTERVAL / 60 ))
    CRON_SCHEDULE="0 */$HOURS * * *"
else
    CRON_SCHEDULE="*/$INTERVAL * * * *"
fi

CRON_ENTRY="$CRON_SCHEDULE $CRON_CMD  # janitor-oneshot"

if [[ "$DRY_RUN" == "true" ]]; then
    echo "Would add crontab entry:"
    echo "  $CRON_ENTRY"
    exit 0
fi

# Remove existing janitor-oneshot entries
CURRENT_CRONTAB=$(crontab -l 2>/dev/null | grep -v "# janitor-oneshot" || true)

if [[ "$UNINSTALL" == "true" ]]; then
    echo "$CURRENT_CRONTAB" | crontab - 2>/dev/null || crontab - <<< ""
    echo "Janitor cron entry removed."
    exit 0
fi

# Add new entry
NEW_CRONTAB="${CURRENT_CRONTAB}
${CRON_ENTRY}"

echo "$NEW_CRONTAB" | crontab -

echo "Janitor cron installed:"
echo "  Schedule : $CRON_SCHEDULE (every $INTERVAL minutes)"
echo "  Project  : $PROJECT_DIR"
echo "  Log      : $LOG_FILE"
echo "  Python   : $PYTHON"
if [[ -n "$VENV_ACTIVATE" ]]; then
    echo "  Venv     : detected (will activate before running)"
fi
echo ""
echo "Test with: $PYTHON -m core.janitor.cron --once --verbose"
echo "View logs: tail -f $LOG_FILE"
echo "Remove:    bash scripts/install-janitor-cron.sh --uninstall"
