#!/bin/bash
#
# Security Audit Script for Frameio
# Run this script regularly to check for security issues
#

set -e

echo "=========================================="
echo "Frameio Security Audit"
echo "Date: $(date)"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "1. Checking for malicious processes..."
if pgrep -f "6e1c" > /dev/null; then
    check_fail "Malicious process '6e1c' detected!"
    ps aux | grep 6e1c
else
    check_pass "No malicious processes detected"
fi

echo ""
echo "2. Checking for suspicious network connections..."
if netstat -tulpn 2>/dev/null | grep -E "34.236.146.239|:90" > /dev/null; then
    check_fail "Suspicious network connections detected!"
    netstat -tulpn | grep -E "34.236.146.239|:90"
else
    check_pass "No suspicious network connections"
fi

echo ""
echo "3. Checking for malicious files..."
MALICIOUS_FILES=$(find /var/tmp /tmp /opt/frameio -name "6e1c*" 2>/dev/null)
if [ -n "$MALICIOUS_FILES" ]; then
    check_fail "Malicious files found:"
    echo "$MALICIOUS_FILES"
else
    check_pass "No malicious files found"
fi

echo ""
echo "4. Checking cron jobs..."
if crontab -l 2>/dev/null | grep -E "wget|curl|sh.*\.sh" > /dev/null; then
    check_fail "Suspicious cron jobs found!"
    crontab -l | grep -E "wget|curl|sh.*\.sh"
else
    check_pass "No suspicious cron jobs"
fi

echo ""
echo "5. Checking systemd services..."
SUSPICIOUS_SERVICES=$(systemctl list-units --type=service --all | grep -v "frameio" | grep -E "6e1c|suspicious")
if [ -n "$SUSPICIOUS_SERVICES" ]; then
    check_warn "Review these systemd services:"
    echo "$SUSPICIOUS_SERVICES"
else
    check_pass "No suspicious systemd services"
fi

echo ""
echo "6. Checking file permissions..."
if [ -f "/opt/frameio/.env" ]; then
    PERMS=$(stat -c "%a" /opt/frameio/.env)
    if [ "$PERMS" != "600" ]; then
        check_fail ".env file permissions are $PERMS (should be 600)"
    else
        check_pass ".env file permissions are secure"
    fi
else
    check_warn ".env file not found"
fi

echo ""
echo "7. Checking for outdated dependencies..."
cd /opt/frameio/frontend 2>/dev/null && npm outdated > /tmp/npm-outdated.txt 2>&1
if [ -s /tmp/npm-outdated.txt ]; then
    OUTDATED_COUNT=$(grep -c "Wanted" /tmp/npm-outdated.txt || echo "0")
    if [ "$OUTDATED_COUNT" -gt 0 ]; then
        check_warn "$OUTDATED_COUNT outdated npm packages found"
        echo "Run: cd frontend && npm audit"
    else
        check_pass "npm dependencies are up to date"
    fi
else
    check_warn "Could not check npm dependencies"
fi

cd /opt/frameio/backend 2>/dev/null
if [ -f "requirements.txt" ]; then
    source /opt/frameio/venv/bin/activate 2>/dev/null
    pip list --outdated > /tmp/pip-outdated.txt 2>&1
    if [ -s /tmp/pip-outdated.txt ]; then
        OUTDATED_COUNT=$(wc -l < /tmp/pip-outdated.txt)
        if [ "$OUTDATED_COUNT" -gt 2 ]; then  # Header lines
            check_warn "$((OUTDATED_COUNT - 2)) outdated pip packages found"
            echo "Run: pip list --outdated"
        else
            check_pass "pip dependencies are up to date"
        fi
    fi
fi

echo ""
echo "8. Checking for security vulnerabilities..."
cd /opt/frameio/frontend 2>/dev/null
if [ -f "package.json" ]; then
    npm audit --audit-level=moderate > /tmp/npm-audit.txt 2>&1
    if grep -q "found" /tmp/npm-audit.txt; then
        VULN_COUNT=$(grep -oP '\d+(?= vulnerabilities found)' /tmp/npm-audit.txt | head -1)
        if [ -n "$VULN_COUNT" ] && [ "$VULN_COUNT" -gt 0 ]; then
            check_fail "$VULN_COUNT vulnerabilities found in npm packages"
            echo "Run: cd frontend && npm audit"
        else
            check_pass "No npm vulnerabilities found"
        fi
    else
        check_pass "No npm vulnerabilities found"
    fi
fi

echo ""
echo "9. Checking service status..."
if systemctl is-active --quiet frameio-frontend; then
    check_pass "frameio-frontend service is running"
else
    check_warn "frameio-frontend service is not running"
fi

if systemctl is-active --quiet frameio-backend; then
    check_pass "frameio-backend service is running"
else
    check_warn "frameio-backend service is not running"
fi

echo ""
echo "10. Checking disk space..."
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    check_fail "Disk usage is ${DISK_USAGE}% (critical)"
elif [ "$DISK_USAGE" -gt 80 ]; then
    check_warn "Disk usage is ${DISK_USAGE}% (warning)"
else
    check_pass "Disk usage is ${DISK_USAGE}% (healthy)"
fi

echo ""
echo "=========================================="
echo "Audit complete!"
echo "=========================================="

# Cleanup
rm -f /tmp/npm-outdated.txt /tmp/pip-outdated.txt /tmp/npm-audit.txt

