#!/bin/bash
# Quick activation script for QGIS Hub Plugin development environment
#
# Usage:
#   source activate.sh
#   OR
#   . activate.sh

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}QGIS Hub Plugin - Development Environment${NC}"
echo "=========================================="
echo ""

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not found at .venv${NC}"
    echo "Please run the setup first:"
    echo "  python3 -m venv .venv --system-site-packages"
    echo "  source .venv/bin/activate"
    echo "  pip install -U -r requirements/development.txt"
    return 1
fi

# Activate virtual environment
source .venv/bin/activate

# Verify activation
if [ "$VIRTUAL_ENV" != "" ]; then
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
    echo ""
    echo "Python: $(python --version)"
    echo "Location: $VIRTUAL_ENV"
    echo ""
    echo "Available commands:"
    echo "  pytest tests/unit/ -v       # Run unit tests"
    echo "  black qgis_hub_plugin/       # Format code"
    echo "  flake8 qgis_hub_plugin/      # Lint code"
    echo "  pre-commit run --all-files   # Run all checks"
    echo ""
    echo "For full documentation, see DEVELOPMENT_SETUP.md"
else
    echo -e "${YELLOW}Failed to activate virtual environment${NC}"
    return 1
fi
