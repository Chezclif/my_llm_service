#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
PYTHON="${PYTHON:-python3}"
COVERAGE=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./run_tests.sh [OPTIONS]"
            echo "Options:"
            echo "  --coverage, -c   Include coverage report"
            echo "  --verbose, -v    Verbose output"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${YELLOW}Starting test suite...${NC}\n"

# Create reports directory
mkdir -p reports

# Build pytest command
PYTEST_CMD="$PYTHON -m pytest tests/ \
    --html=reports/test_report.html \
    --self-contained-html \
    -v"

# Add coverage if requested
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD \
        --cov=. \
        --cov-report=html:reports/coverage \
        --cov-report=term"
fi

# Run tests
if $PYTEST_CMD; then
    echo -e "\n${GREEN}✅ Tests passed!${NC}"
    echo -e "${GREEN}📊 Test report: reports/test_report.html${NC}"

    if [ "$COVERAGE" = true ]; then
        echo -e "${GREEN}📈 Coverage report: reports/coverage/index.html${NC}"
    fi

    exit 0
else
    echo -e "\n${RED}❌ Tests failed!${NC}"
    exit 1
fi
