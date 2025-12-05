# Frameio AWS EC2 Deployment Guide

This guide will help you deploy Frameio on AWS EC2 using Nginx and Gunicorn.

## Prerequisites

- AWS EC2 instance running Ubuntu 20.04 or later
- SSH access to the EC2 instance
- Domain name (optional, can use IP: 13.213.53.199)

## Quick Start

### 1. Initial Server Setup

On your EC2 instance, run:

```bash
# Clone or upload your project to /opt/frameio
sudo mkdir -p /opt/frameio
# Upload your project files here

# Run the setup script
cd /opt/frameio/deployment
sudo chmod +x setup.sh
sudo ./setup.sh
```

### 2. Configure Environment Variables

Create `/opt/frameio/.env` file:

```bash
sudo nano /opt/frameio/.env
```

Add your configuration (see `env.template` for reference):

```env
# Django Settings
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=13.213.53.199,localhost,127.0.0.1

# Database
DB_NAME=frameio_db
DB_USER=frameio_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306

# Clerk Authentication
CLERK_PUBLISHABLE_KEY=your_key
CLERK_SECRET_KEY=your_key
NEXT_PUBLIC_CLERK_FRONTEND_API=your_api_url

# AI Services
GEMINI_API_KEY=your_key

# Security
ARCJET_KEY=your_key

# Production Settings
SECURE_SSL_REDIRECT=False  # Set to True when SSL is configured
CORS_ALLOWED_ORIGINS=http://13.213.53.199,https://13.213.53.199
```

### 3. Setup Database

```bash
# Login to MySQL
sudo mysql -u root -p

# Create database and user
CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'frameio_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON frameio_db.* TO 'frameio_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Deploy Application

```bash
# Activate virtual environment
source /opt/frameio/venv/bin/activate

# Navigate to backend
cd /opt/frameio/backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Run deployment script
cd /opt/frameio/deployment
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

### 5. Start Services

```bash
# Start Gunicorn
sudo systemctl start frameio-backend
sudo systemctl enable frameio-backend

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status frameio-backend
sudo systemctl status nginx
```

## File Structure on EC2

```
/opt/frameio/
├── venv/                    # Python virtual environment
├── backend/                  # Django backend
│   ├── frameio_backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── gunicorn_config.py
│   ├── staticfiles/         # Collected static files
│   ├── media/               # User uploaded files
│   └── logs/                # Application logs
├── frontend/                # Next.js frontend (if on same server)
├── deployment/              # Deployment scripts
│   ├── setup.sh
│   ├── deploy.sh
│   └── frameio-backend.service
├── nginx.conf               # Nginx configuration
└── .env                     # Environment variables
```

## Service Management

### Gunicorn (Backend)

```bash
# Start
sudo systemctl start frameio-backend

# Stop
sudo systemctl stop frameio-backend

# Restart
sudo systemctl restart frameio-backend

# Status
sudo systemctl status frameio-backend

# View logs
sudo journalctl -u frameio-backend -f
# Or
tail -f /opt/frameio/backend/logs/gunicorn_error.log
```

### Nginx

```bash
# Start
sudo systemctl start nginx

# Stop
sudo systemctl stop nginx

# Restart
sudo systemctl restart nginx

# Reload (without downtime)
sudo systemctl reload nginx

# Test configuration
sudo nginx -t

# View logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Updating the Application

After making changes to your code:

```bash
# Pull latest changes (if using git)
cd /opt/frameio
git pull

# Run deployment script
cd deployment
sudo ./deploy.sh
```

Or manually:

```bash
source /opt/frameio/venv/bin/activate
cd /opt/frameio/backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart frameio-backend
sudo systemctl reload nginx
```

## SSL/HTTPS Setup (Optional but Recommended)

1. Install Certbot:

```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. Get SSL certificate:

```bash
# If you have a domain name
sudo certbot --nginx -d your-domain.com

# Follow the prompts to configure SSL
```

3. Update `.env`:

```env
SECURE_SSL_REDIRECT=True
```

4. Restart services:

```bash
sudo systemctl restart frameio-backend
sudo systemctl reload nginx
```

## Troubleshooting

### Check if services are running

```bash
sudo systemctl status frameio-backend
sudo systemctl status nginx
sudo systemctl status mysql
sudo systemctl status redis-server
```

### View logs

```bash
# Gunicorn logs
tail -f /opt/frameio/backend/logs/gunicorn_error.log
tail -f /opt/frameio/backend/logs/gunicorn_access.log

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Django logs
tail -f /opt/frameio/backend/logs/django.log

# System logs
sudo journalctl -u frameio-backend -f
```

### Test Nginx configuration

```bash
sudo nginx -t
```

### Check port usage

```bash
sudo netstat -tulpn | grep :8000  # Gunicorn
sudo netstat -tulpn | grep :80    # Nginx
```

### Permission issues

```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/frameio/backend/media
sudo chown -R www-data:www-data /opt/frameio/backend/staticfiles
sudo chown -R www-data:www-data /opt/frameio/backend/logs

# Fix permissions
sudo chmod -R 755 /opt/frameio/backend/media
sudo chmod -R 755 /opt/frameio/backend/staticfiles
```

## Security Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with your IP/domain
- [ ] Set up SSL/HTTPS (recommended)
- [ ] Configure firewall (AWS Security Groups)
- [ ] Use strong database passwords
- [ ] Restrict database user permissions
- [ ] Regularly update system packages
- [ ] Set up log rotation
- [ ] Configure backups

## AWS Security Group Configuration

Make sure your EC2 Security Group allows:

- **Inbound:**
  - Port 80 (HTTP) from 0.0.0.0/0
  - Port 443 (HTTPS) from 0.0.0.0/0 (if using SSL)
  - Port 22 (SSH) from your IP only

- **Outbound:**
  - All traffic (for API calls, package downloads, etc.)

## Performance Tuning

### Gunicorn Workers

Edit `/opt/frameio/backend/gunicorn_config.py`:

```python
# Adjust based on your server's CPU cores
workers = multiprocessing.cpu_count() * 2 + 1
```

### Nginx

Edit `/etc/nginx/nginx.conf` for global settings like:

```nginx
worker_processes auto;
worker_connections 1024;
```

## Monitoring

Consider setting up:

- **PM2** for frontend process management (if serving Next.js on same server)
- **Supervisor** for additional process management
- **CloudWatch** for AWS monitoring
- **Sentry** for error tracking

## Support

For issues, check:
1. Service logs (see Troubleshooting section)
2. Nginx error logs
3. Django/Gunicorn logs
4. System logs: `sudo journalctl -xe`

