#!/bin/bash
# Deployment script for Frameio on AWS EC2
# Usage: sudo ./deploy.sh

set -e

PROJECT_DIR="/opt/frameio"
VENV_DIR="$PROJECT_DIR/venv"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "=========================================="
echo "Frameio Deployment Script"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Activate virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Activating virtual environment..."
    source $VENV_DIR/bin/activate
else
    echo "ERROR: Virtual environment not found at $VENV_DIR"
    echo "Please create it first: python3 -m venv $VENV_DIR"
    exit 1
fi

# Backend deployment
echo ""
echo "--- Backend Deployment ---"
cd $BACKEND_DIR

echo "Installing/updating Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating necessary directories..."
mkdir -p $BACKEND_DIR/logs
mkdir -p $BACKEND_DIR/media
mkdir -p $BACKEND_DIR/staticfiles
chown -R www-data:www-data $BACKEND_DIR/logs
chown -R www-data:www-data $BACKEND_DIR/media
chown -R www-data:www-data $BACKEND_DIR/staticfiles

# Restart Gunicorn service
echo "Restarting Gunicorn service..."
systemctl daemon-reload
systemctl restart frameio-backend
systemctl status frameio-backend --no-pager

# Frontend deployment (if on same server)
if [ -d "$FRONTEND_DIR" ]; then
    echo ""
    echo "--- Frontend Deployment ---"
    cd $FRONTEND_DIR
    
    echo "Installing/updating Node dependencies..."
    npm install
    
    echo "Building Next.js application..."
    npm run build
    
    # If using PM2
    if command -v pm2 &> /dev/null; then
        echo "Restarting PM2 process..."
        pm2 restart frameio-frontend || pm2 start npm --name "frameio-frontend" -- start
    else
        echo "WARNING: PM2 not found. Frontend should be managed separately."
    fi
fi

# Reload Nginx
echo ""
echo "--- Nginx Configuration ---"
echo "Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "Reloading Nginx..."
    systemctl reload nginx
    echo "Nginx reloaded successfully"
else
    echo "ERROR: Nginx configuration test failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Service status:"
echo "  - Gunicorn: systemctl status frameio-backend"
echo "  - Nginx: systemctl status nginx"
echo ""
echo "Logs:"
echo "  - Gunicorn: tail -f $BACKEND_DIR/logs/gunicorn_error.log"
echo "  - Nginx: tail -f /var/log/nginx/error.log"

