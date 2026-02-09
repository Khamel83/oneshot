#!/bin/bash
# docs-check.sh - SessionStart hook
# Auto-checks project dependencies against docs cache and reports available docs
#
# Usage: Add to .claude/settings.json:
# "SessionStart": [
#   {
#     "matcher": "",
#     "hooks": [{ "type": "command", "command": "~/.claude/hooks/docs-check.sh", "timeout": 5 }]
#   }
# ]

set -euo pipefail

CACHE_BASE="${DOCS_CACHE:-$HOME/github/docs-cache/docs/cache}"
CACHE_INDEX="$CACHE_BASE/.index.md"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
EXTERNAL_DIR="$PROJECT_ROOT/docs/external"

# Color output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Exit silently if no cache
if [[ ! -f "$CACHE_INDEX" ]]; then
    exit 0
fi

# Get cached doc names (lowercase for matching)
get_cached_names() {
    grep -E '^\|' "$CACHE_INDEX" | tail -n +3 | grep -v '^|--' | \
        while IFS='|' read -r _ name _; do
            echo "$name" | xargs | tr '[:upper:]' '[:lower:]'
        done
}

CACHED_NAMES=$(get_cached_names)

# Detect dependencies from common files
detect_deps() {
    local deps=""

    # Node.js - dependencies + devDependencies
    if [[ -f package.json ]]; then
        deps="$deps "$(jq -r '.dependencies + .devDependencies | keys[]?' package.json 2>/dev/null | tr '[:upper:]' '[:lower:]' || true)
        # Extract from @types/ packages too
        deps="$deps "$(jq -r '.devDependencies | keys[]? | select(startswith("@types/")) | sub("^@types/"; "")' package.json 2>/dev/null | tr '[:upper:]' '[:lower:]' || true)
    fi

    # Python - requirements.txt
    if [[ -f requirements.txt ]]; then
        while IFS= read -r line; do
            # Skip comments and empty lines
            [[ "$line" =~ ^#.*$ ]] && continue
            [[ -z "$line" ]] && continue
            # Extract package name (before any version specifier)
            pkg=$(echo "$line" | sed 's/[>=<!].*//' | sed 's/\[.*//' | xargs | tr '[:upper:]' '[:lower:]')
            [[ -n "$pkg" ]] && deps="$deps $pkg"
        done < requirements.txt
    fi

    # Python - pyproject.toml
    if [[ -f pyproject.toml ]]; then
        # Parse dependencies array
        deps="$deps "$(grep -E '^dependencies = \[' -A 1000 pyproject.toml | grep '"' | sed 's/.*"\([^"]*\)".*/\1/' | sed 's/[>=<!].*//' | sed 's/\[.*//' | xargs | tr '[:upper:]' '[:lower:]' || true)
        # Parse optional-dependencies
        deps="$deps "$(grep -E '^\[project.optional-dependencies\]' -A 1000 pyproject.toml | grep '^\[' -B 1000 | grep '"' | sed 's/.*"\([^"]*\)".*/\1/' | sed 's/[>=<!].*//' | xargs | tr '[:upper:]' '[:lower:]' || true)
    fi

    # Python - setup.py or setup.cfg
    if [[ -f setup.py ]]; then
        deps="$deps "$(grep -E "(install_requires|requirements)" setup.py | grep '"' | sed 's/.*"\([^"]*\)".*/\1/' | sed 's/[>=<!].*//' | xargs | tr '[:upper:]' '[:lower:]' || true)
    fi

    # Go - go.mod
    if [[ -f go.mod ]]; then
        while IFS= read -r line; do
            # Skip require and indirect lines
            [[ "$line" =~ ^require ]] && continue
            [[ "$line" =~ ^\s*// ]] && continue
            [[ -z "$line" ]] && continue
            # Extract package path, then get last component
            pkg=$(echo "$line" | awk '{print $1}' | sed 's|.*/||' | xargs | tr '[:upper:]' '[:lower:]')
            [[ -n "$pkg" ]] && deps="$deps $pkg"
        done < <(sed -n '/^require (/, /^)/p' go.mod)
    fi

    # Rust - Cargo.toml
    if [[ -f Cargo.toml ]]; then
        deps="$deps "$(grep -E '^\[dependencies\]' -A 1000 Cargo.toml | grep '=' | sed 's/\s*\([^=]*\).*/\1/' | xargs | tr '[:upper:]' '[:lower:]' || true)
    fi

    # Docker - check for services
    if [[ -f docker-compose.yml ]] || [[ -f docker-compose.yaml ]]; then
        deps="$deps docker"
    fi

    # Kubernetes
    if compgen -G "*.yaml" >/dev/null 2>&1 && grep -q "apiVersion:.*k8s.io" *.yaml 2>/dev/null; then
        deps="$deps kubernetes"
    fi

    echo "$deps" | xargs -n1 | sort -u
}

PROJECT_DEPS=$(detect_deps)

# Find relevant cached docs
RELEVANT=""
for cached in $CACHED_NAMES; do
    # Check exact match
    if echo "$PROJECT_DEPS" | grep -qx "$cached"; then
        RELEVANT="$RELEVANT $cached"
        continue
    fi
    # Check partial match (e.g., "react" matches "@types/react")
    for dep in $PROJECT_DEPS; do
        if [[ "$dep" == *"$cached"* || "$cached" == *"$dep"* ]]; then
            RELEVANT="$RELEVANT $cached"
            break
        fi
    done
done

# Report findings
if [[ -n "$RELEVANT" ]]; then
    echo -e "${GREEN}## Cached Docs Available${NC}"
    echo ""
    echo -e "The following docs are cached and relevant to this project:"
    echo ""
    for name in $(echo "$RELEVANT" | xargs -n1 | sort -u); do
        echo -e "  ${BLUE}- ${name}${NC}"
    done
    echo ""
    echo -e "Reference with: ${YELLOW}@docs/external/<name>/README.md${NC}"

    # Check if docs are linked
    if [[ -d "$EXTERNAL_DIR" ]]; then
        LINKED=$(ls "$EXTERNAL_DIR" 2>/dev/null | wc -l)
        if [[ "$LINKED" -gt 0 ]]; then
            echo ""
            echo -e "Linked docs (${LINKED}): ${YELLOW}ls docs/external/${NC}"
        else
            echo ""
            echo -e "Link docs with: ${YELLOW}docs-link add$(echo "$RELEVANT" | sed 's/ / /g')${NC}"
        fi
    fi
    echo ""
fi
