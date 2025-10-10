#!/bin/bash
# Purpose: Complete workflow script for test suite optimization
# Scope: Automates the entire process of identifying and removing redundant tests
# Usage: ./scripts/optimize_tests.sh [--dry-run] [--target-pct N] [--max-drop N]

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DRY_RUN=""
TARGET_PCT="40"
MAX_DROP="2.0"

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --target-pct)
            TARGET_PCT="$2"
            shift 2
            ;;
        --max-drop)
            MAX_DROP="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --dry-run         Simulate removal without actually deleting tests"
            echo "  --target-pct N    Target percentage of tests to remove (default: 40)"
            echo "  --max-drop N      Maximum coverage drop allowed (default: 2.0)"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}================================================================================${NC}"
echo -e "${BLUE}                    TEST SUITE OPTIMIZATION WORKFLOW${NC}"
echo -e "${BLUE}================================================================================${NC}"
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Target removal: ${TARGET_PCT}%"
echo "  Max coverage drop: ${MAX_DROP}%"
if [ -n "$DRY_RUN" ]; then
    echo -e "  ${YELLOW}Mode: DRY RUN (simulation only)${NC}"
else
    echo -e "  ${RED}Mode: ACTUAL REMOVAL${NC}"
fi
echo ""

# Phase 1: Run tests with coverage context tracking
echo -e "${GREEN}Phase 1: Running tests with coverage context tracking...${NC}"
echo "This may take several minutes..."
echo ""

# Ensure .artifacts directory exists
mkdir -p .artifacts

if poetry run pytest --cov=src --cov-report=html --cov-report=term -q; then
    echo -e "${GREEN}✓ Tests completed successfully${NC}"
else
    echo -e "${RED}✗ Tests failed. Fix failing tests before optimization.${NC}"
    exit 1
fi

# Check if coverage database exists
if [ ! -f ".coverage" ]; then
    echo -e "${RED}✗ Coverage database not found${NC}"
    echo "  Expected: .coverage"
    exit 1
fi

echo -e "${GREEN}✓ Coverage database generated${NC}"
echo ""

# Phase 2: Analyze coverage and identify duplicates
echo -e "${GREEN}Phase 2: Analyzing test coverage for duplicates...${NC}"
echo ""

if poetry run python scripts/analyze_test_coverage.py; then
    echo -e "${GREEN}✓ Analysis complete${NC}"
else
    echo -e "${RED}✗ Analysis failed${NC}"
    exit 1
fi

# Check if candidates file was generated
if [ ! -f ".artifacts/removal_candidates.json" ]; then
    echo -e "${YELLOW}⚠ No removal candidates found${NC}"
    echo "  This could mean:"
    echo "    - Tests have very little overlap"
    echo "    - Duplicate threshold is too high"
    echo "    - Context tracking didn't work properly"
    exit 0
fi

echo -e "${GREEN}✓ Removal candidates identified${NC}"
echo ""

# Show summary from JSON
echo -e "${BLUE}Candidate Summary:${NC}"
TOTAL_TESTS=$(jq '.total_tests' .artifacts/removal_candidates.json)
NUM_CANDIDATES=$(jq '.candidates | length' .artifacts/removal_candidates.json)
echo "  Total tests: ${TOTAL_TESTS}"
echo "  Candidates for removal: ${NUM_CANDIDATES}"
echo ""

# Phase 3: Remove redundant tests
if [ -n "$DRY_RUN" ]; then
    echo -e "${YELLOW}Phase 3: Simulating test removal (dry run)...${NC}"
else
    echo -e "${RED}Phase 3: Removing redundant tests...${NC}"
    echo -e "${YELLOW}⚠  This will modify your test files!${NC}"
    echo ""
    read -p "Continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi
fi
echo ""

if poetry run python scripts/remove_redundant_tests.py \
    $DRY_RUN \
    --target-pct "$TARGET_PCT" \
    --max-drop "$MAX_DROP" \
    --candidates-file .artifacts/removal_candidates.json; then
    echo -e "${GREEN}✓ Removal process completed${NC}"
else
    echo -e "${RED}✗ Removal process failed${NC}"
    exit 1
fi

# Show results
if [ -f ".artifacts/removed_tests.json" ]; then
    echo ""
    echo -e "${BLUE}Results Summary:${NC}"

    REMOVED_COUNT=$(jq '.removed_tests | length' .artifacts/removed_tests.json)
    BASELINE_COV=$(jq '.baseline_coverage' .artifacts/removed_tests.json)
    FINAL_COV=$(jq '.final_coverage' .artifacts/removed_tests.json)
    COV_DROP=$(jq '.coverage_drop' .artifacts/removed_tests.json)

    echo "  Tests removed: ${REMOVED_COUNT}"
    echo "  Baseline coverage: ${BASELINE_COV}%"
    echo "  Final coverage: ${FINAL_COV}%"
    echo "  Coverage drop: ${COV_DROP}%"

    if (( $(echo "$COV_DROP <= $MAX_DROP" | bc -l) )); then
        echo -e "  ${GREEN}✓ Coverage drop within acceptable limits${NC}"
    else
        echo -e "  ${RED}✗ Coverage drop exceeds threshold${NC}"
    fi
fi

echo ""
echo -e "${BLUE}================================================================================${NC}"

if [ -n "$DRY_RUN" ]; then
    echo -e "${YELLOW}DRY RUN COMPLETE${NC}"
    echo "  No files were modified"
    echo "  To perform actual removal, run without --dry-run"
else
    echo -e "${GREEN}OPTIMIZATION COMPLETE${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git diff tests/"
    echo "  2. Run tests: poetry run pytest"
    echo "  3. Run quality checks: just lint-full"
    echo "  4. If satisfied, commit changes"
    echo ""
    echo "Backup preserved at: .test_backup/"
fi

echo -e "${BLUE}================================================================================${NC}"
