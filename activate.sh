#!/bin/bash
###############################################################################
# Space Hulk Game - Virtual Environment Activation Helper
#
# This script provides a convenient way to activate the virtual environment.
# It checks if the virtual environment exists and activates it.
#
# Usage: source ./activate.sh
#        (Note: Must use 'source' or '.' to activate in current shell)
###############################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment not found at .venv/${NC}"
    echo -e "${YELLOW}Please run ./setup.sh first to create the virtual environment.${NC}"
    return 1 2>/dev/null || exit 1
fi

# Check if we're already in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Note: Already in a virtual environment: $VIRTUAL_ENV${NC}"
    echo -e "${YELLOW}Deactivating current environment first...${NC}"
    deactivate
fi

# Activate the virtual environment
source .venv/bin/activate

# Verify activation
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${GREEN}✓ Virtual environment activated successfully!${NC}"
    echo -e "${GREEN}  Location: $VIRTUAL_ENV${NC}"
    echo -e "${GREEN}  Python: $(which python)${NC}"
    echo ""
    echo -e "You can now run:"
    echo -e "  ${YELLOW}crewai run${NC}              - Run the game"
    echo -e "  ${YELLOW}python -m unittest discover${NC} - Run tests"
    echo -e "  ${YELLOW}deactivate${NC}             - Exit the virtual environment"
    echo ""
else
    echo -e "${RED}Error: Failed to activate virtual environment${NC}"
    return 1 2>/dev/null || exit 1
fi
