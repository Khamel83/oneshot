#!/bin/bash
# ONE_SHOT v10 — Secrets Audit Script
#
# Audits a project for secret leakage and security issues:
#   - Unencrypted files in secrets/ directories
#   - Hardcoded secrets in code
#   - .env files not in .gitignore
#   - SOPS format validation
#
# Usage:
#   ./audit-secrets.sh [project-dir] [options]
#   ./audit-secrets.sh .
#   ./audit-secrets.sh ~/github/my-project --skip-sops
#   ./audit-secrets.sh --skip-sops  # check current dir

set -euo pipefail

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse arguments
SKIP_SOPS=false
PROJECT_DIR="."

for arg in "$@"; do
    case "$arg" in
        --skip-sops)
            SKIP_SOPS=true
            ;;
        --help|-h)
            echo "Usage: $0 [project-dir] [--skip-sops]"
            echo ""
            echo "Options:"
            echo "  project-dir    Directory to audit (default: .)"
            echo "  --skip-sops    Skip SOPS decryption validation"
            echo "  --help, -h     Show this help"
            exit 0
            ;;
        -*)
            echo "Unknown option: $arg" >&2
            echo "Use --help for usage" >&2
            exit 1
            ;;
        *)
            PROJECT_DIR="$arg"
            ;;
    esac
done

PROJECT_DIR=$(cd "$PROJECT_DIR" && pwd)

ISSUES=0
WARNINGS=0

echo "ONE_SHOT v10 — Secrets Audit"
echo "============================="
echo "Project: $PROJECT_DIR"
echo ""

# Patterns that indicate secrets
SECRET_PATTERNS=(
    "api[_-]?key"
    "apikey"
    "secret[_-]?key"
    "secret"
    "password"
    "token"
    "auth[_-]?token"
    "access[_-]?token"
    "refresh[_-]?token"
    "private[_-]?key"
    "aws[_-]?access[_-]?key"
    "aws[_-]?secret"
    "stripe[_-]?secret"
    "openai[_-]?api[_-]?key"
    "anthropic[_-]?api[_-]?key"
    "database[_-]?url"
    "connection[_-]?string"
)

# File extensions to scan
CODE_EXTS=(
    "py" "js" "ts" "jsx" "tsx" "go" "rs" "java" "php" "rb" "sh" "yaml" "yml" "toml" "json" "env"
)

# =============================================================================
# 1. Check for unencrypted files in secrets/ directories
# =============================================================================

echo -e "${BLUE}[1] Checking for unencrypted files in secrets/...${NC}"

if [ -d "$PROJECT_DIR/secrets" ]; then
    UNENCRYPTED=$(find "$PROJECT_DIR/secrets" -type f ! -name "*.encrypted" ! -name ".sops.yaml" ! -name ".gitignore" 2>/dev/null || true)

    if [ -n "$UNENCRYPTED" ]; then
        echo -e "${RED}[FAIL]${NC} Found unencrypted files in secrets/:"
        echo "$UNENCRYPTED" | while read -r file; do
            echo -e "  ${RED}✗${NC} $file"
        done
        ISSUES=$((ISSUES + 1))
    else
        echo -e "${GREEN}[PASS]${NC} All files in secrets/ are encrypted"
    fi
else
    echo -e "${YELLOW}[SKIP]${NC} No secrets/ directory"
fi

echo ""

# =============================================================================
# 2. Check .gitignore for .env files
# =============================================================================

echo -e "${BLUE}[2] Checking .gitignore for .env patterns...${NC}"

GITIGNORE="$PROJECT_DIR/.gitignore"
ENV_IGNORED=false

if [ -f "$GITIGNORE" ]; then
    if grep -q "^\.env$\|^\.env\.\*" "$GITIGNORE" 2>/dev/null; then
        echo -e "${GREEN}[PASS]${NC} .env files are in .gitignore"
        ENV_IGNORED=true
    else
        echo -e "${YELLOW}[WARN]${NC} .env files may not be in .gitignore"
        echo -e "       Add: .env or .env.* to .gitignore"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}[WARN]${NC} No .gitignore found"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# =============================================================================
# 3. Check for .env files that aren't encrypted
# =============================================================================

echo -e "${BLUE}[3] Checking for unencrypted .env files...${NC}"

PLAIN_ENV=$(find "$PROJECT_DIR" -maxdepth 3 -name ".env" -o -name ".env.*" ! -name "*.env.encrypted" ! -name "*.env.example" 2>/dev/null | grep -v node_modules | grep -v ".venv" || true)

if [ -n "$PLAIN_ENV" ]; then
    echo -e "${YELLOW}[WARN]${NC} Found unencrypted .env files:"
    echo "$PLAIN_ENV" | while read -r file; do
        # Check if it's gitignored
        if git -C "$PROJECT_DIR" check-ignore -q "$file" 2>/dev/null; then
            echo -e "  ${YELLOW}!${NC} $file (gitignored)"
        else
            echo -e "  ${RED}✗${NC} $file ${RED}NOT in .gitignore!${NC}"
            ISSUES=$((ISSUES + 1))
        fi
    done
else
    echo -e "${GREEN}[PASS]${NC} No unencrypted .env files found"
fi

echo ""

# =============================================================================
# 4. Scan code for hardcoded secrets
# =============================================================================

echo -e "${BLUE}[4] Scanning code for potential hardcoded secrets...${NC}"

FOUND_SECRET=false

# Build find pattern for code files
FIND_ARGS=()
for ext in "${CODE_EXTS[@]}"; do
    FIND_ARGS+=(-name "*.$ext" -o)
done
# Remove last -o
FIND_ARGS=("${FIND_ARGS[@]:0:${#FIND_ARGS[@]}-1}")

# Find code files (excluding common dirs)
CODE_FILES=$(find "$PROJECT_DIR" -type f \( "${FIND_ARGS[@]}" \) \
    ! -path "*/node_modules/*" \
    ! -path "*/.venv/*" \
    ! -path "*/venv/*" \
    ! -path "*/target/*" \
    ! -path "*/.git/*" \
    ! -path "*/dist/*" \
    ! -path "*/build/*" \
    ! -path "*/.*.encrypted" \
    ! -name "*.example" \
    2>/dev/null || true)

for pattern in "${SECRET_PATTERNS[@]}"; do
    if [ -n "$CODE_FILES" ]; then
        # Case-insensitive search for the pattern
        MATCHES=$(echo "$CODE_FILES" | xargs grep -i -l "$pattern" 2>/dev/null || true)

        if [ -n "$MATCHES" ]; then
            while read -r file; do
                # Check for actual values (not just variable names or comments)
                SUSPICIOUS=$(grep -i "$pattern" "$file" | grep -v "^\s*//" | grep -v "^\s*#" | grep -v "os\.getenv\|process\.env\|getenv\|import.*os" | grep -E '=.*["\x27]|:[^:]*["\x27]' || true)

                if [ -n "$SUSPICIOUS" ]; then
                    if [ "$FOUND_SECRET" = false ]; then
                        echo -e "${YELLOW}[WARN]${NC} Found potential hardcoded secrets:"
                        FOUND_SECRET=true
                    fi
                    echo -e "  ${YELLOW}!${NC} $file contains \"$pattern\""
                    # Show first suspicious line (sanitized)
                    FIRST_LINE=$(echo "$SUSPICIOUS" | head -1)
                    # Sanitize - hide long values
                    SANITIZED=$(echo "$FIRST_LINE" | sed -E 's/=["\x27][^"\x27]{10,}["\x27]/=***REDACTED***/')
                    echo -e "     $SANITIZED"
                fi
            done <<< "$MATCHES"
        fi
    fi
done

if [ "$FOUND_SECRET" = false ]; then
    echo -e "${GREEN}[PASS]${NC} No obvious hardcoded secrets found"
else
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# =============================================================================
# 5. Validate SOPS files (if sops is available)
# =============================================================================

echo -e "${BLUE}[5] Validating SOPS encrypted files...${NC}"

if [ "$SKIP_SOPS" = true ]; then
    echo -e "${YELLOW}[SKIP]${NC} SOPS validation disabled (--skip-sops)"
elif command -v sops &> /dev/null; then
    ENCRYPTED_FILES=$(find "$PROJECT_DIR" -name "*.encrypted" -o -name "*.enc.*" 2>/dev/null || true)

    if [ -n "$ENCRYPTED_FILES" ]; then
        INVALID=0
        while read -r file; do
            if ! sops -d "$file" &> /dev/null; then
                echo -e "${RED}[FAIL]${NC} $file - cannot decrypt (invalid SOPS format?)"
                INVALID=$((INVALID + 1))
            fi
        done <<< "$ENCRYPTED_FILES"

        if [ "$INVALID" -eq 0 ]; then
            echo -e "${GREEN}[PASS]${NC} All SOPS files are valid"
        else
            ISSUES=$((ISSUES + INVALID))
        fi
    else
        echo -e "${YELLOW}[SKIP]${NC} No SOPS encrypted files found"
    fi
else
    echo -e "${YELLOW}[SKIP]${NC} sops not installed"
fi

echo ""

# =============================================================================
# 6. Check for age/sops config
# =============================================================================

echo -e "${BLUE}[6] Checking SOPS configuration...${NC}"

SOPS_CONFIG="$PROJECT_DIR/.sops.yaml"
GLOBAL_SOPS="$HOME/github/oneshot/.sops.yaml"

if [ -f "$SOPS_CONFIG" ]; then
    echo -e "${GREEN}[PASS]${NC} .sops.yaml found"
elif [ -f "$GLOBAL_SOPS" ]; then
    echo -e "${GREEN}[PASS]${NC} Using global SOPS config (~/github/oneshot/.sops.yaml)"
else
    echo -e "${YELLOW}[WARN]${NC} No .sops.yaml found"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# =============================================================================
# Summary
# =============================================================================

echo "============================="
echo -e "${BLUE}Summary:${NC}"
echo ""

if [ "$ISSUES" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}✓ No issues found!${NC}"
    exit 0
elif [ "$ISSUES" -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo ""
    echo "Review the warnings above. They may not be critical but should be understood."
    exit 0
else
    echo -e "${RED}✗ $ISSUES issue(s) found, $WARNINGS warning(s)${NC}"
    echo ""
    echo "Fix the issues before committing or pushing."
    exit 1
fi
