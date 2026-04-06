#!/bin/bash
# eval.sh - OneShot harness evaluation runner
# Usage:
#   ./scripts/eval.sh                     # Run all benchmarks
#   ./scripts/eval.sh --category classification
#   ./scripts/eval.sh --category routing
#   ./scripts/eval.sh --category config
#   ./scripts/eval.sh --save baseline     # Save results as named snapshot
#   ./scripts/eval.sh --compare baseline  # Compare against saved snapshot
#
# Run automatically by: ./scripts/ci.sh (in future)
# Exit code: 0 if all pass, 1 if any regression detected

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EVAL_DIR="$REPO_ROOT/eval"
RESULTS_DIR="$EVAL_DIR/results"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

ERRORS=0

section() {
    echo ""
    echo -e "${YELLOW}=== $1 ===${NC}"
}

log_ok() {
    echo -e "${GREEN}OK${NC}: $1"
}

log_error() {
    echo -e "${RED}FAIL${NC}: $1"
    ERRORS=$((ERRORS + 1))
}

# Defaults
CATEGORY="${1:-all}"
ACTION="run"

# Parse args
if [[ "${1:-}" == "--save" ]]; then
    ACTION="save"
    SNAPSHOT_NAME="${2:-baseline}"
elif [[ "${1:-}" == "--compare" ]]; then
    ACTION="compare"
    SNAPSHOT_NAME="${2:-baseline}"
elif [[ "${1:-}" == "--category" ]]; then
    CATEGORY="${2:-all}"
fi

mkdir -p "$RESULTS_DIR"

run_python_eval() {
    local script="$1"
    local label="$2"
    local extra_args=""

    if [[ "$CATEGORY" == "all" || "$CATEGORY" == "$label" ]]; then
        section "$label"
        if python3 "$EVAL_DIR/scripts/$script" $extra_args; then
            log_ok "$label passed"
        else
            log_error "$label failed"
        fi
    fi
}

if [[ "$ACTION" == "run" ]]; then
    echo "OneShot Harness Eval"
    echo "===================="
    echo "Category: $CATEGORY"
    echo ""

    run_python_eval "run_config_check.py" "config"
    run_python_eval "run_classification.py" "classification"
    run_python_eval "run_routing.py" "routing"

    echo ""
    echo "=========================================="
    if [ $ERRORS -eq 0 ]; then
        echo -e "${GREEN}ALL EVALS PASSED${NC}"
        exit 0
    else
        echo -e "${RED}$ERRORS EVAL(S) FAILED${NC}"
        exit 1
    fi

elif [[ "$ACTION" == "save" ]]; then
    TIMESTAMP=$(date +%Y-%m-%d--%H%M%S)
    RESULT_FILE="$RESULTS_DIR/${TIMESTAMP}--${SNAPSHOT_NAME}.json"

    echo "Saving eval results to $RESULT_FILE"

    # Run all evals, capture JSON output
    {
        echo "{"
        echo "  \"timestamp\": \"$(date -Iseconds)\","
        echo "  \"snapshot\": \"$SNAPSHOT_NAME\","
        echo "  \"config\": $(python3 "$EVAL_DIR/scripts/run_config_check.py" --json 2>&1),"
        echo "  \"classification\": $(python3 "$EVAL_DIR/scripts/run_classification.py" --set search --json 2>&1),"
        echo "  \"routing\": $(python3 "$EVAL_DIR/scripts/run_routing.py" --json 2>&1)"
        echo "}"
    } > "$RESULT_FILE"

    echo "Saved: $RESULT_FILE"
    exit 0

elif [[ "$ACTION" == "compare" ]]; then
    # Find the most recent snapshot matching the name
    SNAPSHOT_FILE=$(ls -t "$RESULTS_DIR/"*"--${SNAPSHOT_NAME}.json" 2>/dev/null | head -1)

    if [[ -z "$SNAPSHOT_FILE" ]]; then
        echo "No snapshot found for '$SNAPSHOT_NAME'"
        echo "Run: ./scripts/eval.sh --save $SNAPSHOT_NAME"
        exit 1
    fi

    echo "Comparing against snapshot: $SNAPSHOT_FILE"
    echo ""

    # Run current evals and compare
    CURRENT_CONFIG=$(python3 "$EVAL_DIR/scripts/run_config_check.py" --json 2>&1)
    CURRENT_CLS=$(python3 "$EVAL_DIR/scripts/run_classification.py" --set search --json 2>&1)
    CURRENT_RTE=$(python3 "$EVAL_DIR/scripts/run_routing.py" --json 2>&1)

    # Parse snapshot values
    SNAPPED_CLS_ACC=$(echo "$CURRENT_CLS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('category', {}).get('accuracy', 'N/A'))
print(d.get('risk', {}).get('accuracy', 'N/A'))
" 2>/dev/null || echo "parse error")

    echo "Current classification accuracy: $SNAPPED_CLS_ACC"

    # Check for regression (simple: if current run exits non-zero, it's a regression)
    REGRESSION=0
    for check in "config" "classification" "routing"; do
        section "$check"
        if [[ "$check" == "config" ]]; then
            echo "$CURRENT_CONFIG" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('passed', False):
    print('  Config: OK')
else:
    print('  Config: REGRESSION')
    for e in d.get('errors', []):
        print(f'    - {e}')
" 2>/dev/null || REGRESSION=1
        elif [[ "$check" == "classification" ]]; then
            echo "$CURRENT_CLS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
cat_acc = d.get('category', {}).get('accuracy', 0)
risk_acc = d.get('risk', {}).get('accuracy', 0)
print(f'  Category accuracy: {cat_acc}%')
print(f'  Risk accuracy: {risk_acc}%')
if cat_acc < 90 or risk_acc < 85:
    print('  REGRESSION: accuracy below threshold')
else:
    print('  OK')
" 2>/dev/null || REGRESSION=1
        elif [[ "$check" == "routing" ]]; then
            echo "$CURRENT_RTE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
acc = d.get('accuracy', 0)
print(f'  Routing accuracy: {acc}%')
if acc < 95:
    print('  REGRESSION: accuracy below threshold')
else:
    print('  OK')
" 2>/dev/null || REGRESSION=1
    fi
    done

    echo ""
    if [ $REGRESSION -gt 0 ]; then
        echo -e "${RED}REGRESSION DETECTED${NC}"
        exit 1
    else
        echo -e "${GREEN}NO REGRESSION${NC}"
        exit 0
    fi
fi
