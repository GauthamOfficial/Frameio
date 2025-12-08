#!/bin/bash
# Script to diagnose and fix 502 Bad Gateway errors
# Run this on your server: sudo ./fix-502-error.sh

set -e

echo "=========================================="
echo "502 Bad Gateway Diagnostic & Fix Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

PROJECT_DIR="/opt/frameio"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$PROJECT_DIR/venv"

echo "Step 1: Checking Gunicorn service status..."
echo "-------------------------------------------"
if systemctl is-active --quiet frameio-backend; then
    echo -e "${GREEN}✓ Gunicorn service is running${NC}"
else
    echo -e "${RED}✗ Gunicorn service is NOT running${NC}"
    echo "Attempting to start..."
    systemctl start frameio-backend
    sleep 2
    if systemctl is-active --quiet frameio-backend; then
        echo -e "${GREEN}✓ Gunicorn service started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start Gunicorn service${NC}"
    fi
fi
echo ""

echo "Step 2: Checking if Gunicorn is listening on port 8000..."
echo "-------------------------------------------"
if netstat -tuln | grep -q ":8000"; then
    echo -e "${GREEN}✓ Port 8000 is in use${NC}"
    netstat -tuln | grep ":8000"
else
    echo -e "${RED}✗ Port 8000 is NOT in use - Gunicorn is not listening${NC}"
fi
echo ""

echo "Step 3: Checking Gunicorn service logs..."
echo "-------------------------------------------"
echo "Recent error logs:"
journalctl -u frameio-backend -n 20 --no-pager | tail -20
echo ""

echo "Step 4: Checking Gunicorn error log file..."
echo "-------------------------------------------"
if [ -f "$BACKEND_DIR/logs/gunicorn_error.log" ]; then
    echo "Last 20 lines of error log:"
    tail -20 "$BACKEND_DIR/logs/gunicorn_error.log"
else
    echo -e "${YELLOW}⚠ Error log file not found${NC}"
fi
echo ""

echo "Step 5: Checking Nginx configuration..."
echo "-------------------------------------------"
if nginx -t 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
else
    echo -e "${RED}✗ Nginx configuration has errors${NC}"
    nginx -t
fi
echo ""

echo "Step 6: Checking Nginx error logs..."
echo "-------------------------------------------"
echo "Recent Nginx errors:"
tail -20 /var/log/nginx/error.log | grep -i "502\|upstream\|connect" || echo "No 502 errors found in recent logs"
echo ""

echo "Step 7: Testing backend connection..."
echo "-------------------------------------------"
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health/ | grep -q "200\|404"; then
    echo -e "${GREEN}✓ Backend is responding on port 8000${NC}"
    curl -s http://127.0.0.1:8000/health/ | head -5
else
    echo -e "${RED}✗ Backend is NOT responding on port 8000${NC}"
    echo "Attempting to test connection..."
    timeout 5 curl -v http://127.0.0.1:8000/health/ || echo "Connection failed"
fi
echo ""

echo "Step 8: Checking database connection..."
echo "-------------------------------------------"
source $VENV_DIR/bin/activate
cd $BACKEND_DIR
if python manage.py check --database default 2>&1 | grep -q "System check identified no issues"; then
    echo -e "${GREEN}✓ Database connection is working${NC}"
else
    echo -e "${RED}✗ Database connection issue detected${NC}"
    python manage.py check --database default
fi
echo ""

echo "Step 9: Attempting to restart services..."
echo "-------------------------------------------"
echo "Restarting Gunicorn..."
systemctl restart frameio-backend
sleep 3

if systemctl is-active --quiet frameio-backend; then
    echo -e "${GREEN}✓ Gunicorn restarted successfully${NC}"
else
    echo -e "${RED}✗ Gunicorn failed to restart${NC}"
    echo "Checking status..."
    systemctl status frameio-backend --no-pager -l
fi

echo "Reloading Nginx..."
systemctl reload nginx
echo -e "${GREEN}✓ Nginx reloaded${NC}"
echo ""

echo "Step 10: Final status check..."
echo "-------------------------------------------"
echo "Gunicorn status:"
systemctl status frameio-backend --no-pager | head -10

echo ""
echo "Testing endpoint again..."
sleep 2
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health/ | grep -q "200\|404"; then
    echo -e "${GREEN}✓ Backend is now responding${NC}"
else
    echo -e "${RED}✗ Backend is still not responding${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check Gunicorn logs: sudo journalctl -u frameio-backend -f"
    echo "2. Check error log: tail -f $BACKEND_DIR/logs/gunicorn_error.log"
    echo "3. Check Django logs: tail -f $BACKEND_DIR/logs/django.log"
    echo "4. Try manual start: cd $BACKEND_DIR && source $VENV_DIR/bin/activate && gunicorn --config gunicorn_config.py frameio_backend.wsgi:application"
fi

echo ""
echo "=========================================="
echo "Diagnostic complete!"
echo "=========================================="

