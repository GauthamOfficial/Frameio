#!/bin/bash
# Initial setup script for Frameio on AWS EC2
# Run this once to set up the server environment
# Usage: sudo ./setup.sh

set -e

PROJECT_DIR="/opt/frameio"
VENV_DIR="$PROJECT_DIR/venv"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "=========================================="
echo "Frameio Server Setup Script"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update system packages
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required packages
echo "Installing required packages..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    mysql-server \
    redis-server \
    nodejs \
    npm \
    git \
    build-essential \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config

# Create project directory
echo "Creating project directory..."
mkdir -p $PROJECT_DIR
mkdir -p $BACKEND_DIR/logs
mkdir -p $BACKEND_DIR/media
mkdir -p $BACKEND_DIR/staticfiles

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv $VENV_DIR
fi

# Set permissions
echo "Setting permissions..."
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR

# Create log directories
echo "Creating log directories..."
mkdir -p /var/log/gunicorn
chown -R www-data:www-data /var/log/gunicorn

# Install Gunicorn in virtual environment
echo "Installing Gunicorn..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install gunicorn

# Copy systemd service file
if [ -f "$PROJECT_DIR/deployment/frameio-backend.service" ]; then
    echo "Installing systemd service..."
    cp $PROJECT_DIR/deployment/frameio-backend.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable frameio-backend
fi

# Copy Nginx configuration
if [ -f "$PROJECT_DIR/nginx.conf" ]; then
    echo "Installing Nginx configuration..."
    cp $PROJECT_DIR/nginx.conf /etc/nginx/sites-available/frameio
    ln -sf /etc/nginx/sites-available/frameio /etc/nginx/sites-enabled/
    
    # Remove default Nginx site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx configuration
    nginx -t
    
    if [ $? -eq 0 ]; then
        echo "Nginx configuration is valid"
    else
        echo "WARNING: Nginx configuration test failed!"
    fi
fi

# Setup MySQL (if needed)
echo ""
echo "MySQL setup:"
echo "  - Make sure MySQL is running: systemctl status mysql"
echo "  - Create database: mysql -u root -p"
echo "  - Run: CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Setup Redis
echo "Starting Redis..."
systemctl enable redis-server
systemctl start redis-server

echo ""
echo "=========================================="
echo "Setup completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy your project files to $PROJECT_DIR"
echo "2. Create .env file in $PROJECT_DIR with your configuration"
echo "3. Activate venv: source $VENV_DIR/bin/activate"
echo "4. Install dependencies: cd $BACKEND_DIR && pip install -r requirements.txt"
echo "5. Run migrations: python manage.py migrate"
echo "6. Create superuser: python manage.py createsuperuser"
echo "7. Collect static files: python manage.py collectstatic"
echo "8. Start services:"
echo "   - systemctl start frameio-backend"
echo "   - systemctl start nginx"
echo ""

