# Task Plan: ONE_SHOT v10.4

**Created**: 2026-02-12
**Status**: Ready
**Last Updated**: 2026-02-12

## Summary
Fix oneshot.sh update logic and integrate heartbeat properly. Eliminate blind overwrites and cascade failures.

## Problem Statement

### Current Issues
1. **Blind overwrite**: oneshot.sh always overwrites AGENTS.md from GitHub, even if local is newer
2. **Cascade effect**: check-oneshot.sh auto-pulls → triggers cascade → SOPS errors
3. **No smart update**: Doesn't check if files actually need updating
4. **Heartbeat not integrated**: heartbeat.sh exists but not properly wired

### The Cascade
```
heartbeat (daily)
  → check-oneshot.sh (git pull) ← ROOT CAUSE: auto-pulls without --fix
    → oneshot.sh runs (blind AGENTS.md overwrite)
      → check-apis.sh runs
        → sync-secrets.sh runs
          → SOPS errors if path wrong
```

### Root Causes
| File | Lines | Issue |
|------|-------|-------|
| `check-oneshot.sh` | 29-30 | `git pull --quiet` always runs, no --fix flag |
| `oneshot.sh` | 104-105 | `curl ... > AGENTS.md` always overwrites |
| `check-apis.sh` | 8-13 | PROJECT_DIR always resolves to oneshot, not caller's project |
| `heartbeat.sh` | 72 | Calls check-oneshot without safeguards |

## Goals
- [ ] Fix check-oneshot.sh to NOT auto-pull (root cause of cascade)
- [ ] Smart version checking before any file overwrites
- [ ] AGENTS.md merge strategy (don't clobber local changes)
- [ ] Fix SOPS path logic for actual project context
- [ ] Make all check scripts idempotent (--fix flag)
- [ ] Properly integrate heartbeat.sh with rate limiting

## Decisions
| # | Question | Options | Decision | Rationale |
|---|----------|---------|----------|-----------|
| 1 | check-oneshot.sh behavior? | Always pull, ask user, check-only | Check-only unless --fix | Stops cascade, user controls updates |
| 2 | AGENTS.md update strategy? | Always overwrite, ask user, skip if modified, force flag | Skip if modified, --force to override | Don't clobber, allow explicit override |
| 3 | SOPS config path? | Hardcode, env var, auto-detect from caller | Detect from caller's PWD | Scripts run from various dirs |
| 4 | Heartbeat trigger? | Manual only, auto on cd, cron, git hook | Auto on cd + manual + rate limit | Best UX without spamming |
| 5 | Heartbeat logging? | Silent, stdout, log file | Log to /tmp/heartbeat.log | Debug when things fail |

## Technical Approach

### 0. Fix check-oneshot.sh (ROOT CAUSE)

**Current problem**: Always runs `git pull`, which triggers cascade.

**Solution**: Check-only by default, only pull when --fix flag:

```bash
#!/usr/bin/env bash
# Auto-update ONE-SHOT repo from origin (only with --fix)

set -euo pipefail

ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"
FIX_MODE=false

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --fix) FIX_MODE=true ;;
    --check) FIX_MODE=false ;;
  esac
done

if [[ ! -d "$ONESHOT_DIR" ]]; then
  echo "⚠️  ONE-SHOT: repo not found at $ONESHOT_DIR"
  exit 1
fi

cd "$ONESHOT_DIR"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "⚠️  ONE-SHOT: not a git repository"
  exit 1
fi

# Check for updates (always)
git fetch origin >/dev/null 2>&1

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/master 2>/dev/null || git rev-parse origin/main)

if [[ "$LOCAL" == "$REMOTE" ]]; then
  echo "✓ ONE-SHOT: up to date"
  exit 0
fi

# Updates available
echo "⚠️  ONE-SHOT: update available ($LOCAL != $REMOTE)"

if [[ "$FIX_MODE" == true ]]; then
  echo "   Updating..."
  if git pull --quiet >/dev/null 2>&1; then
    echo "✓ ONE-SHOT: updated to latest"
    exit 0
  else
    echo "⚠️  ONE-SHOT: update failed (merge conflict or network)"
    exit 1
  fi
else
  echo "   Run with --fix to update"
  exit 0
fi
```

### 1. Smart Update Logic for oneshot.sh

**Requirements**:
- Handle non-git directories (fresh install)
- Handle staged AND unstaged changes
- Handle network failures gracefully
- Support --force flag to override local changes

```bash
# Smart AGENTS.md update function
update_agents_md() {
  local AGENTS_FILE="AGENTS.md"
  local FORCE_UPDATE="${1:-false}"

  # Fresh install - no file exists
  if [[ ! -f "$AGENTS_FILE" ]]; then
    curl -sL "$ONESHOT_BASE/AGENTS.md" > "$AGENTS_FILE" 2>/dev/null || \
      curl -sL "$ONESHOT_BASE/README.md" > "$AGENTS_FILE"
    echo "  ${GREEN}✓${NC} AGENTS.md (created)"
    return 0
  fi

  # Check if we're in a git repo
  if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "  ${YELLOW}○${NC} AGENTS.md (not in git repo, skipping update)"
    return 0
  fi

  # Check for ANY local changes (staged or unstaged)
  if git status --porcelain "$AGENTS_FILE" 2>/dev/null | grep -qE "^[AM]"; then
    if [[ "$FORCE_UPDATE" == "true" ]]; then
      echo "  ${YELLOW}⚠${NC} AGENTS.md (force overwrite with --force)"
    else
      echo "  ${YELLOW}○${NC} AGENTS.md (locally modified, use --force to update)"
      return 0
    fi
  fi

  # Try to compare with remote (handle network failure)
  if ! git fetch origin >/dev/null 2>&1; then
    echo "  ${YELLOW}○${NC} AGENTS.md (network error, cannot check for updates)"
    return 0
  fi

  LOCAL_HASH=$(git rev-parse HEAD:"$AGENTS_FILE" 2>/dev/null || echo "none")
  REMOTE_HASH=$(git rev-parse origin/master:"$AGENTS_FILE" 2>/dev/null || git rev-parse origin/main:"$AGENTS_FILE" 2>/dev/null || echo "none")

  if [[ "$LOCAL_HASH" == "$REMOTE_HASH" ]]; then
    echo "  ${GREEN}✓${NC} AGENTS.md (up to date)"
    return 0
  fi

  # Remote is newer - update
  curl -sL "$ONESHOT_BASE/AGENTS.md" > "$AGENTS_FILE" 2>/dev/null || \
    curl -sL "$ONESHOT_BASE/README.md" > "$AGENTS_FILE"
  echo "  ${GREEN}✓${NC} AGENTS.md (updated from remote)"
  return 0
}

# Call the function
update_agents_md "$FORCE_MODE"
```

### 2. Fix SOPS Path (Context-Aware)

**Problem**: check-apis.sh sets `PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"` which is ALWAYS oneshot dir, not caller's project.

**Solution**: Detect SOPS config from caller's working directory (PWD):

```bash
# Auto-detect SOPS config from current working directory
detect_sops_config() {
  local start_dir="$PWD"
  local checked_dirs=()

  # Check current dir and walk up 3 levels
  for i in {0..3}; do
    if [[ -f "$start_dir/.sops.yaml" ]]; then
      echo "$start_dir/.sops.yaml"
      return 0
    fi
    checked_dirs+=("$start_dir")
    start_dir="$(dirname "$start_dir")"

    # Stop at home directory
    [[ "$start_dir" == "$HOME" ]] && break
  done

  # Fallback to global oneshot config
  if [[ -f "$HOME/github/oneshot/.sops.yaml" ]]; then
    echo "$HOME/github/oneshot/.sops.yaml"
    echo "  ⚠️  Using global oneshot .sops.yaml (checked: ${checked_dirs[*]})" >&2
    return 0
  fi

  return 1
}

# Use detected config
SOPS_CONFIG=$(detect_sops_config) || {
  echo "⊘ SOPS: No .sops.yaml found in current or parent directories"
  exit 0  # Not an error, just skip
}

export SOPS_CONFIG
```

**Note**: Remove hardcoded `PROJECT_DIR` from check-apis.sh - use PWD-based detection instead.

### 3. Make Check Scripts Idempotent

Pattern for all check scripts:

```bash
#!/usr/bin/env bash
# Check script template - idempotent by default

set -euo pipefail

FIX_MODE=false

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --fix|-f) FIX_MODE=true ;;
    --check|-c) FIX_MODE=false ;;
    --quiet|-q) QUIET=true ;;
  esac
done

# 1. Check condition (always runs)
check_condition() {
  # Return 0 if OK, 1 if needs fixing
  [[ -f "required_file" ]] && return 0 || return 1
}

# 2. Fix condition (only runs with --fix)
fix_condition() {
  # Only modify state here
  touch "required_file"
}

# Main
if check_condition; then
  echo "✓ Check passed"
  exit 0
else
  echo "⚠️  Check failed"
  if [[ "$FIX_MODE" == true ]]; then
    fix_condition
    echo "✓ Fixed"
    exit 0
  else
    echo "   Run with --fix to repair"
    exit 1
  fi
fi
```

### 4. Heartbeat Integration (Rate-Limited)

**Problem**: Spawns background process with no logging, runs on every cd.

**Solution**: Rate limit + proper logging:

```bash
# heartbeat-install.sh - Install shell hooks for auto-heartbeat

HEARTBEAT_LOG="${HEARTBEAT_LOG:-/tmp/heartbeat.log}"
ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"
HEARTBEAT_SCRIPT="$ONESHOT_DIR/scripts/heartbeat.sh"

# Rate limiting: only run if last run was > 23 hours ago
oneshot_heartbeat_guarded() {
  # Only run in directories with CLAUDE.md
  [[ -f "CLAUDE.md" ]] || return 0

  # Check last run time
  local last_run_file="$HOME/.cache/oneshot-heartbeat-last"
  local now=$(date +%s)
  local last_run=0

  if [[ -f "$last_run_file" ]]; then
    last_run=$(cat "$last_run_file" 2>/dev/null || echo 0)
  fi

  # 23 hours = 82800 seconds
  local elapsed=$((now - last_run))
  if [[ $elapsed -lt 82800 ]]; then
    return 0  # Skip, ran recently
  fi

  # Update last run time
  mkdir -p "$HOME/.cache"
  echo "$now" > "$last_run_file"

  # Run heartbeat in background with logging
  if [[ -x "$HEARTBEAT_SCRIPT" ]]; then
    "$HEARTBEAT_SCRIPT" --safe >>"$HEARTBEAT_LOG" 2>&1 &
  fi
}

# Bash integration
install_bash_hook() {
  local hook_code='# ONE_SHOT Heartbeat
oneshot_heartbeat_guarded() {
  if [[ -f "CLAUDE.md" ]]; then
    local last_run_file="$HOME/.cache/oneshot-heartbeat-last"
    local now=$(date +%s)
    local last_run=$(cat "$last_run_file" 2>/dev/null || echo 0)
    if [[ $((now - last_run)) -gt 82800 ]]; then
      echo "$now" > "$last_run_file"
    fi
  fi
}
PROMPT_COMMAND+="oneshot_heartbeat_guarded;"'

  if ! grep -q "ONE_SHOT Heartbeat" "$HOME/.bashrc" 2>/dev/null; then
    echo "" >> "$HOME/.bashrc"
    echo "# ONE_SHOT Heartbeat" >> "$HOME/.bashrc"
    echo "oneshot_heartbeat() { if [[ -f \"CLAUDE.md\" ]]; then $HOME/github/oneshot/scripts/heartbeat.sh --safe >>/tmp/heartbeat.log 2>&1 &; fi; }" >> "$HOME/.bashrc"
    echo "PROMPT_COMMAND=\"oneshot_heartbeat;\$PROMPT_COMMAND\"" >> "$HOME/.bashrc"
    echo "✓ Installed bash hook"
  else
    echo "✓ Bash hook already installed"
  fi
}

# Zsh integration
install_zsh_hook() {
  # Similar for zsh using chpwd hook
  echo "Zsh hook installation: TODO"
}
```

**heartbeat.sh --safe mode**: Skip check-oneshot.sh (no git pull):

```bash
# Add --safe flag to heartbeat.sh
SAFE_MODE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --safe|-s) SAFE_MODE="--safe"; shift ;;
    # ... other flags
  esac
done

# In the check() function:
if [[ "$SAFE_MODE" != "--safe" ]]; then
  check "ONE-SHOT" "$SCRIPT_DIR/check-oneshot.sh"
else
  echo "○ ONE-SHOT (safe mode, skipping check)"
fi
```

## Implementation Phases

### Phase 0: Fix Root Cause (check-oneshot.sh)
- [ ] 0.1: Add --fix flag to check-oneshot.sh
- [ ] 0.2: Make git pull conditional on --fix
- [ ] 0.3: Default to check-only (no pull)
- [ ] 0.4: Test heartbeat runs check without pulling

### Phase 1: Fix oneshot.sh Smart Updates
- [ ] 1.1: Create update_agents_md() function
- [ ] 1.2: Handle non-git dirs (fresh install)
- [ ] 1.3: Check for staged AND unstaged changes (`git status --porcelain | grep -E "^[AM]"`)
- [ ] 1.4: Add --force flag to override local changes
- [ ] 1.5: Handle network failures gracefully
- [ ] 1.6: Test scenarios: fresh, modified, staged, network-down

### Phase 2: Fix SOPS Path Detection
- [ ] 2.1: Create detect_sops_config() that walks up from PWD
- [ ] 2.2: Remove hardcoded PROJECT_DIR from check-apis.sh
- [ ] 2.3: Update sync-secrets.sh to use same detection
- [ ] 2.4: Test in: oneshot dir, sub-project (weather-cli), random dir

### Phase 3: Make Scripts Idempotent
- [ ] 3.1: Add --fix flag to check-clis.sh
- [ ] 3.2: Add --fix flag to check-mcps.sh
- [ ] 3.3: Add --fix flag to check-connections.sh
- [ ] 3.4: Ensure check only, no modifications without --fix
- [ ] 3.5: Test idempotency (run twice, second should be no-op)

### Phase 4: Integrate Heartbeat
- [ ] 4.1: Create heartbeat-install.sh script
- [ ] 4.2: Add --safe mode to heartbeat.sh (skip check-oneshot)
- [ ] 4.3: Implement rate limiting (23-hour cache file)
- [ ] 4.4: Add logging to /tmp/heartbeat.log
- [ ] 4.5: Install via oneshot.sh or manual
- [ ] 4.6: Test: cd multiple times, verify only one heartbeat runs

## Files to Modify

| File | Changes |
|------|---------|
| `scripts/check-oneshot.sh` | Add --fix flag, conditional git pull |
| `oneshot.sh` | Smart update_agents_md() function, --force flag |
| `scripts/check-apis.sh` | Fix SOPS path detection (PWD-based) |
| `scripts/sync-secrets.sh` | Use PWD-based SOPS detection |
| `scripts/check-clis.sh` | Add --fix flag |
| `scripts/check-mcps.sh` | Add --fix flag |
| `scripts/check-connections.sh` | Add --fix flag |
| `scripts/heartbeat.sh` | Add --safe mode (skip check-oneshot) |
| `scripts/heartbeat-install.sh` | NEW - shell integration with rate limit |
| `.claude/rules/core.md` | Update heartbeat reference |

## Success Metrics
- [ ] check-oneshot.sh does NOT pull without --fix flag
- [ ] AGENTS.md never overwrites local changes (without --force)
- [ ] check-apis.sh works from any directory (PWD-based detection)
- [ ] All check scripts are idempotent (no --fix = no changes)
- [ ] Heartbeat runs max once per 23 hours
- [ ] No cascade failures when heartbeat runs

## Dependencies
- None

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Users surprised by no auto-update | High | Low | Clear message: "Run with --fix to update" |
| git status grep patterns fail edge cases | Med | Med | Test: staged, unstaged, both, untracked |
| PWD-based SOPS detection finds wrong file | Low | Med | Walk up from PWD, stop at .sops.yaml found |
| Heartbeat rate file corrupted | Low | Low | Touch file on error, fallback to re-run |
| check-oneshot.sh network fails | Med | Low | Graceful message, exit 0 (not an error) |

## Test Plan

### Phase 0 Tests
```bash
# Test 1: Check-only (default)
./scripts/check-oneshot.sh
# Expected: "Run with --fix to update", no git pull

# Test 2: Fix mode
./scripts/check-oneshot.sh --fix
# Expected: git pull executes

# Test 3: Up to date
./scripts/check-oneshot.sh --fix
# Expected: "up to date", no pull
```

### Phase 1 Tests
```bash
# Test 1: Fresh install (no AGENTS.md)
rm AGENTS.md && bash oneshot.sh
# Expected: AGENTS.md created

# Test 2: Locally modified
echo "# Modified" >> AGENTS.md && git add AGENTS.md
bash oneshot.sh
# Expected: "locally modified, use --force"

# Test 3: Force overwrite
bash oneshot.sh --force
# Expected: AGENTS.md overwritten

# Test 4: Staged changes
git add AGENTS.md && bash oneshot.sh
# Expected: Detect staged changes, skip update
```

### Phase 2 Tests
```bash
# Test 1: From oneshot dir
cd ~/github/oneshot && ./scripts/check-apis.sh
# Expected: Uses local .sops.yaml

# Test 2: From sub-project
cd ~/github/oneshot/examples/weather-cli && ./scripts/check-apis.sh
# Expected: Uses parent .sops.yaml or oneshot .sops.yaml

# Test 3: From random dir
cd /tmp && ./scripts/check-apis.sh
# Expected: Uses oneshot .sops.yaml with warning
```

### Phase 4 Tests
```bash
# Test 1: Rate limiting
cd ~/github/oneshot
./scripts/heartbeat-install.sh
cd . && cd oneshot  # Multiple times
# Expected: Only one heartbeat runs (check log)

# Test 2: Safe mode
./scripts/heartbeat.sh --safe
# Expected: Skips check-oneshot, no git pull
```

---
## Revision History
| Date | Changed By | Summary |
|------|------------|---------|
| 2026-02-12 | claude | Initial plan for v10.4 - fix oneshot.sh update logic |
| 2026-02-12 | claude | Added Phase 0 (root cause), improved git checks, fixed SOPS PWD detection, added heartbeat rate limiting |
