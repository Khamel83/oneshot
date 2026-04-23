#!/bin/bash
# repo-pack.sh — Daily repo packing via repomix.
# Scans ~/github/ for repos with recent commits, runs repomix on each.
# Outputs docs/LLM-OVERVIEW.md (replaces hand-maintained version) + .janitor/repo-pack.json.
#
# Called by janitor-cron.sh. Can also run standalone: bash scripts/repo-pack.sh

set -euo pipefail

export PATH="${HOME}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"

REPO_BASE="${HOME}/github"
ACTIVE_DAYS=30
DEFAULT_CONFIG="${HOME}/github/oneshot/repomix.config.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PACKED=0
SKIPPED=0
FAILED=0

# Ensure repomix is available
if ! command -v repomix &>/dev/null; then
  echo "ERROR: repomix not found. Install with: npm install -g repomix"
  exit 1
fi

for dir in "$REPO_BASE"/*/; do
  repo=$(basename "$dir")
  cd "$dir" || continue

  # Must be a git repo
  git rev-parse --git-dir > /dev/null 2>&1 || continue

  # Check for recent activity (commits in last N days)
  recent=$(git log --since="${ACTIVE_DAYS} days ago" --oneline 2>/dev/null | head -1)
  if [ -z "$recent" ]; then
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Skip repos with no tracked files
  file_count=$(git ls-files | wc -l)
  if [ "$file_count" -eq 0 ]; then
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  echo "Packing: $repo ($file_count files)"

  # Use repo-local config if it exists, else the oneshot default
  cfg_flag=""
  if [ -f repomix.config.json ]; then
    cfg_flag="--config repomix.config.json"
  elif [ -f "$DEFAULT_CONFIG" ]; then
    cfg_flag="--config $DEFAULT_CONFIG"
  fi

  # Ensure output directory exists
  mkdir -p docs

  # Run repomix — quiet mode for cron, errors to stderr
  if repomix $cfg_flag --output "docs/LLM-OVERVIEW.md" --quiet 2>/tmp/repomix-err.log; then
    # Write metadata
    mkdir -p .janitor
    size=$(wc -c < "docs/LLM-OVERVIEW.md" 2>/dev/null || echo 0)
    cat > .janitor/repo-pack.json << EOF
{
  "timestamp": "$TIMESTAMP",
  "repo": "$repo",
  "files_tracked": $file_count,
  "output_size_bytes": $size,
  "active_threshold_days": $ACTIVE_DAYS
}
EOF
    PACKED=$((PACKED + 1))
  else
    echo "  FAILED: $repo — $(cat /tmp/repomix-err.log 2>/dev/null | tail -1)"
    FAILED=$((FAILED + 1))
  fi
done

echo "Repo-pack complete: $PACKED packed, $SKIPPED skipped (idle), $FAILED failed"
