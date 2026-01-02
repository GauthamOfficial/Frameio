#!/bin/bash
#
# Dependency Audit Script for Frameio
# Checks for outdated and vulnerable dependencies
#

set -e

echo "=========================================="
echo "Frameio Dependency Audit"
echo "Date: $(date)"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

REPORT_FILE="/tmp/dependency-audit-$(date +%Y%m%d).txt"

echo "Audit report will be saved to: $REPORT_FILE"
echo ""

# Frontend audit
echo "=== Frontend Dependencies (npm) ==="
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend
    
    echo "Checking for outdated packages..."
    npm outdated >> "$REPORT_FILE" 2>&1 || true
    
    echo "Running security audit..."
    npm audit >> "$REPORT_FILE" 2>&1 || true
    
    echo "Checking for known vulnerabilities..."
    npm audit --audit-level=moderate >> "$REPORT_FILE" 2>&1 || true
    
    cd ..
    echo -e "${GREEN}✓${NC} Frontend audit complete"
else
    echo -e "${YELLOW}⚠${NC} Frontend directory not found"
fi

echo ""

# Backend audit
echo "=== Backend Dependencies (pip) ==="
if [ -d "backend" ] && [ -f "backend/requirements.txt" ]; then
    cd backend
    
    # Activate virtual environment if it exists
    if [ -f "../venv/bin/activate" ]; then
        source ../venv/bin/activate
    fi
    
    echo "Checking for outdated packages..."
    pip list --outdated >> "$REPORT_FILE" 2>&1 || true
    
    echo "Checking for known vulnerabilities..."
    if command -v pip-audit &> /dev/null; then
        pip-audit >> "$REPORT_FILE" 2>&1 || true
    else
        echo "pip-audit not installed. Install with: pip install pip-audit" >> "$REPORT_FILE"
        echo -e "${YELLOW}⚠${NC} pip-audit not installed. Install with: pip install pip-audit"
    fi
    
    cd ..
    echo -e "${GREEN}✓${NC} Backend audit complete"
else
    echo -e "${YELLOW}⚠${NC} Backend directory not found"
fi

echo ""
echo "=========================================="
echo "Audit complete! Review report: $REPORT_FILE"
echo "=========================================="

# Summary
echo ""
echo "Summary:"
echo "--------"
if grep -q "vulnerabilities found" "$REPORT_FILE"; then
    echo -e "${RED}✗${NC} Vulnerabilities detected - review report"
else
    echo -e "${GREEN}✓${NC} No critical vulnerabilities found"
fi

if grep -q "outdated" "$REPORT_FILE"; then
    echo -e "${YELLOW}⚠${NC} Outdated packages found - consider updating"
fi

