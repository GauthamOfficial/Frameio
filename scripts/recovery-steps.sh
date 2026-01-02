#!/bin/bash
#
# Recovery Steps Script for Frameio Security Incident
# Run this script after a security breach to recover the system
#

set -e

echo "=========================================="
echo "Frameio Security Recovery Script"
echo "WARNING: This script will stop services and clean up"
echo "=========================================="
echo ""

read -p "Are you sure you want to proceed? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Step 1: Stop all services
echo ""
echo "Step 1: Stopping all services..."
sudo systemctl stop frameio-frontend || true
sudo systemctl stop frameio-backend || true
echo "✓ Services stopped"

# Step 2: Kill malicious processes
echo ""
echo "Step 2: Killing malicious processes..."
sudo pkill -9 -f "6e1c" || true
sudo pkill -9 -f "wget.*34.236.146.239" || true
sudo pkill -9 node || true
sudo pkill -9 npm || true
echo "✓ Malicious processes killed"

# Step 3: Remove malicious files
echo ""
echo "Step 3: Removing malicious files..."
sudo find /var/tmp -name "6e1c*" -type f -delete 2>/dev/null || true
sudo find /tmp -name "6e1c*" -type f -delete 2>/dev/null || true
sudo find /opt/frameio -name "6e1c*" -type f -delete 2>/dev/null || true
echo "✓ Malicious files removed"

# Step 4: Check for persistence mechanisms
echo ""
echo "Step 4: Checking for persistence mechanisms..."
echo "Checking cron jobs..."
sudo crontab -l 2>/dev/null | grep -v "^#" | grep -E "wget|curl|sh.*\.sh" && echo "⚠ Suspicious cron jobs found!" || echo "✓ No suspicious cron jobs"

echo "Checking systemd timers..."
systemctl list-timers --all | grep -v "frameio" && echo "⚠ Review systemd timers" || echo "✓ No suspicious timers"

# Step 5: Create backup
echo ""
echo "Step 5: Creating backup..."
BACKUP_DIR="/tmp/frameio-recovery-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
sudo cp -r /opt/frameio "$BACKUP_DIR/" 2>/dev/null || true
sudo cp /etc/systemd/system/frameio-*.service "$BACKUP_DIR/" 2>/dev/null || true
echo "✓ Backup created at: $BACKUP_DIR"

# Step 6: Clean and reinstall dependencies
echo ""
read -p "Do you want to reinstall dependencies? (yes/no): " REINSTALL
if [ "$REINSTALL" = "yes" ]; then
    echo "Reinstalling dependencies..."
    
    if [ -d "/opt/frameio/frontend" ]; then
        cd /opt/frameio/frontend
        sudo rm -rf node_modules package-lock.json
        sudo npm install --production
        echo "✓ Frontend dependencies reinstalled"
    fi
    
    if [ -d "/opt/frameio/backend" ] && [ -f "/opt/frameio/venv/bin/activate" ]; then
        cd /opt/frameio/backend
        source /opt/frameio/venv/bin/activate
        sudo pip install --upgrade pip
        sudo pip install -r requirements.txt --force-reinstall
        echo "✓ Backend dependencies reinstalled"
    fi
fi

# Step 7: Rotate credentials reminder
echo ""
echo "=========================================="
echo "Step 7: CRITICAL - Rotate all credentials"
echo "=========================================="
echo "You must manually rotate:"
echo "  - Django SECRET_KEY"
echo "  - Database passwords"
echo "  - API keys (Gemini, Clerk, etc.)"
echo "  - Admin passwords"
echo ""
echo "Edit: /opt/frameio/.env"
echo ""

# Step 8: Restart services
echo ""
read -p "Do you want to restart services? (yes/no): " RESTART
if [ "$RESTART" = "yes" ]; then
    echo "Restarting services..."
    sudo systemctl restart frameio-backend
    sleep 2
    sudo systemctl restart frameio-frontend
    echo "✓ Services restarted"
    
    echo ""
    echo "Checking service status..."
    sudo systemctl status frameio-backend --no-pager -l
    echo ""
    sudo systemctl status frameio-frontend --no-pager -l
fi

echo ""
echo "=========================================="
echo "Recovery steps complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review backup at: $BACKUP_DIR"
echo "2. Rotate all credentials in .env"
echo "3. Review logs for suspicious activity"
echo "4. Run security audit: ./scripts/security-audit.sh"
echo "5. Monitor services closely"
echo ""

