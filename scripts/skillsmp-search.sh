#!/bin/bash
# skillsmp-search.sh - Search SkillsMP and download skills to 1shot/skills/
#
# Usage:
#   ./scripts/skillsmp-search.sh "solidity smart contracts"
#   ./scripts/skillsmp-search.sh "kubernetes deploy" --install
#   ./scripts/skillsmp-search.sh "pdf parsing" --install --ai
#
# Options:
#   --install    Download the top result to 1shot/skills/
#   --ai         Use semantic AI search instead of keyword search
#   --limit N    Number of results (default: 5)
#
# Requires: SKILLSMP_API_KEY env var (or in secrets)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SKILLSMP_BASE="https://skillsmp.com/api/v1"
SKILLS_DIR="1shot/skills"
INSTALL=false
AI_SEARCH=false
LIMIT=5
QUERY=""

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --install) INSTALL=true; shift ;;
    --ai)      AI_SEARCH=true; shift ;;
    --limit)   LIMIT="$2"; shift 2 ;;
    -*)        echo "Unknown option: $1"; exit 1 ;;
    *)         QUERY="$1"; shift ;;
  esac
done

if [ -z "$QUERY" ]; then
  echo "Usage: $0 \"<search query>\" [--install] [--ai] [--limit N]"
  exit 1
fi

# Resolve API key — check env first, then secrets vault
API_KEY="${SKILLSMP_API_KEY:-}"
if [ -z "$API_KEY" ]; then
  # Secrets in this repo use dotenv format — must pass --input-type dotenv
  VAULT="${ONESHOT_VAULT:-$HOME/github/oneshot/secrets}"
  for candidate in "$VAULT/skillsmp.env.encrypted" "secrets/skillsmp.env.encrypted"; do
    if command -v sops &>/dev/null && [ -f "$candidate" ]; then
      API_KEY=$(SOPS_AGE_KEY_FILE=~/.age/key.txt sops -d --input-type dotenv --output-type dotenv "$candidate" 2>/dev/null | grep SKILLSMP_API_KEY | cut -d= -f2 || true)
      [ -n "$API_KEY" ] && break
    fi
  done
fi

if [ -z "$API_KEY" ]; then
  echo -e "${RED}✗${NC} SKILLSMP_API_KEY not set."
  echo "  Set it: export SKILLSMP_API_KEY=your_key"
  echo "  Or store in secrets: sops secrets/env.enc"
  exit 1
fi

# Choose endpoint
if [ "$AI_SEARCH" = true ]; then
  ENDPOINT="/skills/ai-search"
else
  ENDPOINT="/skills/search"
fi

echo -e "${BLUE}Searching SkillsMP:${NC} \"$QUERY\""
echo ""

# Call SkillsMP API
RESPONSE=$(curl -sf \
  --max-time 15 \
  -H "Authorization: Bearer $API_KEY" \
  -G \
  --data-urlencode "q=$QUERY" \
  --data-urlencode "limit=$LIMIT" \
  "$SKILLSMP_BASE$ENDPOINT" 2>/dev/null) || {
  echo -e "${RED}✗${NC} SkillsMP API request failed (check API key or network)"
  exit 1
}

# Parse response
SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success','false'))" 2>/dev/null || echo "false")

if [ "$SUCCESS" != "True" ] && [ "$SUCCESS" != "true" ]; then
  ERROR=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',{}).get('code','unknown'))" 2>/dev/null || echo "unknown")
  echo -e "${RED}✗${NC} SkillsMP error: $ERROR"
  exit 1
fi

# Extract skills
SKILLS_JSON=$(echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
skills = d.get('data', {}).get('skills', [])
for i, s in enumerate(skills):
    print(f\"{i+1}. {s.get('name','?')} — {s.get('description','')[:80]}\")
" 2>/dev/null)

if [ -z "$SKILLS_JSON" ]; then
  echo -e "${YELLOW}○${NC} No skills found for: \"$QUERY\""
  exit 0
fi

echo "$SKILLS_JSON"
echo ""

# Install top result if requested
if [ "$INSTALL" = true ]; then
  TOP_NAME=$(echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
skills = d.get('data', {}).get('skills', [])
if skills:
    print(skills[0].get('name',''))
" 2>/dev/null)

  TOP_CONTENT=$(echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
skills = d.get('data', {}).get('skills', [])
if skills:
    s = skills[0]
    print(s.get('content') or s.get('skill_content') or '')
" 2>/dev/null)

  if [ -z "$TOP_NAME" ]; then
    echo -e "${RED}✗${NC} Could not parse skill name from response"
    exit 1
  fi

  # Sanitize name for directory
  SKILL_DIR="${SKILLS_DIR}/$(echo "$TOP_NAME" | tr '[:upper:]' '[:lower:]' | tr ' /' '-' | tr -cd '[:alnum:]-')"
  mkdir -p "$SKILL_DIR"

  if [ -n "$TOP_CONTENT" ]; then
    echo "$TOP_CONTENT" > "$SKILL_DIR/SKILL.md"
  else
    # Fallback: write a stub with what we know
    echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
skills = d.get('data', {}).get('skills', [])
if skills:
    s = skills[0]
    print('---')
    print(f\"name: {s.get('name','')}\")
    print(f\"description: {s.get('description','')}\")
    print(f\"source: skillsmp\")
    print('---')
    print()
    print(f\"# {s.get('name','')}\")
    print()
    print(s.get('description',''))
    print()
    if s.get('tags'):
        print(f\"Tags: {', '.join(s.get('tags', []))}\")
" 2>/dev/null > "$SKILL_DIR/SKILL.md"
  fi

  echo -e "${GREEN}✓${NC} Installed: $SKILL_DIR/SKILL.md"
  echo ""
  echo "The operator will use this skill for tasks matching: \"$QUERY\""
fi
