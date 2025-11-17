#!/bin/bash

###############################################################################
# Node.js Version Verification Script
#
# This script verifies that Node.js 20+ is installed and ready for
# frontend development.
###############################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================="
echo -e "Node.js Environment Verification"
echo -e "==================================================${NC}"
echo ""

# Check Node.js version
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js installed: ${NODE_VERSION}"

    # Extract major version
    NODE_MAJOR=$(node --version | cut -d'.' -f1 | sed 's/v//')

    if [ "$NODE_MAJOR" -ge 20 ]; then
        echo -e "${GREEN}✓${NC} Node.js version is compatible (>=20)"
    else
        echo -e "${RED}✗${NC} Node.js version is too old (need >=20, have v${NODE_MAJOR})"
        echo -e "${YELLOW}  Please see NODE_UPGRADE.md for upgrade instructions${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Node.js is not installed"
    echo -e "${YELLOW}  Please see NODE_UPGRADE.md for installation instructions${NC}"
    exit 1
fi

# Check npm version
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm installed: v${NPM_VERSION}"
else
    echo -e "${RED}✗${NC} npm is not installed"
    exit 1
fi

# Check if frontend dependencies are installed
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Frontend dependencies not installed"
    echo -e "${YELLOW}  Run: cd frontend && npm install${NC}"
fi

# Check .nvmrc
if [ -f ".nvmrc" ]; then
    NVMRC_VERSION=$(cat .nvmrc)
    echo -e "${GREEN}✓${NC} .nvmrc specifies Node ${NVMRC_VERSION}"
fi

# Check frontend package.json engines
if [ -f "frontend/package.json" ]; then
    if grep -q '"engines"' frontend/package.json; then
        echo -e "${GREEN}✓${NC} frontend/package.json has engines specification"
    fi
fi

echo ""
echo -e "${BLUE}==================================================${NC}"
echo -e "${GREEN}✓ Node.js environment verification complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. cd frontend"
echo "  2. npm install (if not already done)"
echo "  3. npm test"
echo ""
