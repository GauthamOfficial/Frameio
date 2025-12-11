# Configuration Files Setup Guide

This document lists all configuration files that need to be set up for Frameio deployment, including their source paths, destination paths, and setup instructions.

## 📍 Important: Project Location

**Your project is located at:** `~/Frameio/` (which expands to `/home/ubuntu/Frameio/`)

All paths in this document use `~/Frameio/` for user-relative paths and `/home/ubuntu/Frameio/` for absolute paths required by system services (systemd, nginx).

**Note:** If your project is in a different location, replace all `~/Frameio/` references with your actual project path.

---

## 📋 Configuration Files Overview

| # | Config File | Source Path | Destination Path | Required | Auto-Setup |
|---|-------------|-------------|------------------|----------|------------|
| 1 | Environment Variables | `deployment/env.production.template` | `~/Frameio/.env` | ✅ Yes | ❌ Manual |
| 2 | Nginx Configuration | `nginx.conf` | `/etc/nginx/sites-available/frameio` | ✅ Yes | ✅ Yes (setup.sh) |
| 3 | Systemd Service | `deployment/frameio-backend.service` | `/etc/systemd/system/frameio-backend.service` | ✅ Yes | ✅ Yes (setup.sh) |
| 4 | Gunicorn Config | `backend/gunicorn_config.py` | `~/Frameio/backend/gunicorn_config.py` | ✅ Yes | ✅ Already exists |
| 5 | Django Settings | `backend/frameio_backend/settings.py` | `~/Frameio/backend/frameio_backend/settings.py` | ✅ Yes | ✅ Already exists |
| 6 | Next.js Config | `frontend/next.config.ts` | `~/Frameio/frontend/next.config.ts` | ⚠️ If frontend on server | ✅ Already exists |

---

## 1. Environment Variables (`.env`)

### Source
**Path:** `deployment/env.production.template`

### Destination
**Path:** `~/Frameio/.env` (or `/home/ubuntu/Frameio/.env`)

### Purpose
Contains all production environment variables including:
- Django secret key
- Database credentials
- API keys (Gemini, Arcjet, etc.)
- Security settings
- CORS configuration

### Setup Instructions

```bash
# 1. Navigate to project directory
cd ~/Frameio

# 2. Copy template to production location
cp deployment/env.production.template .env

# 3. Edit with your production values
nano .env
# OR
vim .env

# 4. Set secure permissions (only owner can read/write)
chmod 600 .env

# 5. Verify permissions
ls -la .env
# Should show: -rw------- (only you can read it)
```

### Required Variables to Configure

```env
# Django Core
SECRET_KEY=your_django_secret_key_here
DEBUG=False
ALLOWED_HOSTS=13.213.53.199,localhost,127.0.0.1

# Database
DB_NAME=frameio_db
DB_USER=frameio_user
DB_PASSWORD=your_secure_mysql_password_here
DB_HOST=localhost
DB_PORT=3306

# AI Services
GEMINI_API_KEY=your_gemini_api_key_here

# Security
ARCJET_KEY=your_arcjet_key_here

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# Production Settings
SECURE_SSL_REDIRECT=False
CORS_ALLOWED_ORIGINS=http://13.213.53.199,https://13.213.53.199
```

### Generate Secret Key

```bash
# Generate Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Status
- ❌ **Manual Setup Required** - Must be created and configured manually
- ⚠️ **Critical** - Application will not work without this file

---

## 2. Nginx Configuration

### Source
**Path:** `nginx.conf` (project root)

### Destination
**Path:** `/etc/nginx/sites-available/frameio`  
**Symlink:** `/etc/nginx/sites-enabled/frameio`

### Purpose
- Reverse proxy for Django/Gunicorn
- Serves static files (`/static/`)
- Serves media files (`/media/`)
- Handles SSL/HTTPS (when configured)
- CORS headers for media files

### Setup Instructions

```bash
# 1. Navigate to project directory
cd ~/Frameio

# 2. Copy Nginx config to system location
sudo cp nginx.conf /etc/nginx/sites-available/frameio

# 3. Create symbolic link to enable site
sudo ln -sf /etc/nginx/sites-available/frameio /etc/nginx/sites-enabled/

# 4. Remove default Nginx site (optional but recommended)
sudo rm -f /etc/nginx/sites-enabled/default

# 5. Test Nginx configuration
sudo nginx -t

# 6. If test passes, reload Nginx
sudo systemctl reload nginx
```

### Key Configuration Settings

**Important:** Make sure your `nginx.conf` file uses the correct paths. Update it if needed:

```nginx
# Server
server_name 13.213.53.199;
listen 80;

# Static files
location /static/ {
    alias /home/ubuntu/Frameio/backend/staticfiles/;
}

# Media files
location /media/ {
    alias /home/ubuntu/Frameio/backend/media/;
}

# API proxy to Gunicorn
location / {
    proxy_pass http://127.0.0.1:8000;
}
```

**Before copying nginx.conf, verify the paths match your server structure:**
```bash
cd ~/Frameio
grep -n "/opt/frameio" nginx.conf
# If you see any results, update them to /home/ubuntu/Frameio
```

### Status
- ✅ **Auto-Setup** - Handled by `deployment/setup.sh`
- ✅ **Can be manually configured** - If setup.sh doesn't run

---

## 3. Systemd Service File

### Source
**Path:** `deployment/frameio-backend.service`

### Destination
**Path:** `/etc/systemd/system/frameio-backend.service`

### Purpose
- Manages Gunicorn process as a system service
- Auto-starts on boot
- Handles restarts on failure
- Manages logging

### Setup Instructions

```bash
# 1. Navigate to project directory
cd ~/Frameio

# 2. Copy service file to systemd directory
sudo cp deployment/frameio-backend.service /etc/systemd/system/

# 3. Edit the service file to use correct paths (if needed)
# Update paths in the service file to match your project location
sudo nano /etc/systemd/system/frameio-backend.service

# 4. Reload systemd to recognize new service
sudo systemctl daemon-reload

# 5. Enable service to start on boot
sudo systemctl enable frameio-backend

# 6. Start the service
sudo systemctl start frameio-backend

# 7. Check status
sudo systemctl status frameio-backend
```

### Service Configuration

```ini
[Unit]
Description=Frameio Django Backend (Gunicorn)
After=network.target mysql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/ubuntu/Frameio/backend
Environment="PATH=/home/ubuntu/Frameio/venv/bin"
ExecStart=/home/ubuntu/Frameio/venv/bin/gunicorn \
    --config /home/ubuntu/Frameio/backend/gunicorn_config.py \
    frameio_backend.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

### Management Commands

```bash
# Start service
sudo systemctl start frameio-backend

# Stop service
sudo systemctl stop frameio-backend

# Restart service
sudo systemctl restart frameio-backend

# Check status
sudo systemctl status frameio-backend

# View logs
sudo journalctl -u frameio-backend -f
```

### Status
- ✅ **Auto-Setup** - Handled by `deployment/setup.sh`
- ✅ **Can be manually configured** - If setup.sh doesn't run

---

## 4. Gunicorn Configuration

### Source
**Path:** `backend/gunicorn_config.py`

### Destination
**Path:** `~/Frameio/backend/gunicorn_config.py` (or `/home/ubuntu/Frameio/backend/gunicorn_config.py`)

### Purpose
- Configures Gunicorn WSGI server
- Sets worker processes
- Configures logging
- Sets timeouts and limits

### Setup Instructions

```bash
# File is already in your project
# No setup needed - just ensure it's in the correct location
cd ~/Frameio
ls -la backend/gunicorn_config.py
```

### Key Configuration Settings

```python
# Server socket
bind = "127.0.0.1:8000"

# Worker processes (auto-calculated)
workers = multiprocessing.cpu_count() * 2 + 1

# Logging
accesslog = "/home/ubuntu/Frameio/backend/logs/gunicorn_access.log"
errorlog = "/home/ubuntu/Frameio/backend/logs/gunicorn_error.log"

# Timeouts
timeout = 30
graceful_timeout = 30
```

### Status
- ✅ **Already Configured** - File exists in project
- ✅ **No Changes Needed** - Works as-is

---

## 5. Django Settings

### Source
**Path:** `backend/frameio_backend/settings.py`

### Destination
**Path:** `~/Frameio/backend/frameio_backend/settings.py` (or `/home/ubuntu/Frameio/backend/frameio_backend/settings.py`)

### Purpose
- Django application configuration
- Database settings
- Static/media file paths
- Security settings
- Installed apps and middleware

### Setup Instructions

```bash
# File is already in your project
# No setup needed - Django reads from .env automatically
```

### Key Settings (Reads from .env)

```python
# From .env file
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Database (from .env)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Status
- ✅ **Already Configured** - File exists in project
- ✅ **No Changes Needed** - Reads from `.env` automatically

---

## 6. Next.js Configuration (Optional)

### Source
**Path:** `frontend/next.config.ts`

### Destination
**Path:** `~/Frameio/frontend/next.config.ts` (or `/home/ubuntu/Frameio/frontend/next.config.ts`)

### Purpose
- Next.js build configuration
- API URL configuration
- Image domain settings
- Security headers
- CORS configuration

### Setup Instructions

```bash
# File is already in your project
# May need to update API URL if different from default
```

### Key Configuration Settings

```typescript
// API Base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://13.213.53.199/api';

// Image domains
images: {
  remotePatterns: [
    {
      protocol: 'http',
      hostname: '13.213.53.199',
      pathname: '/**',
    },
  ],
}
```

### Update if Needed

If your server IP or domain changes, update:
- `NEXT_PUBLIC_API_URL` in `.env` file
- Image remote patterns in `next.config.ts`

### Status
- ⚠️ **Optional** - Only needed if frontend is on same server
- ✅ **Already Configured** - File exists in project
- ⚠️ **May Need Update** - Check API URL matches server IP

---

## 7. MySQL Database Configuration

### Source
**Path:** N/A (created via MySQL commands)

### Destination
**Path:** MySQL database server (localhost)

### Purpose
- Database for application data
- User accounts and permissions

### Setup Instructions

```bash
# 1. Login to MySQL as root
sudo mysql -u root -p

# 2. Create database
CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 3. Create user (replace 'strong_password' with your password)
CREATE USER 'frameio_user'@'localhost' IDENTIFIED BY 'strong_password_here';

# 4. Grant privileges
GRANT ALL PRIVILEGES ON frameio_db.* TO 'frameio_user'@'localhost';

# 5. Apply changes
FLUSH PRIVILEGES;

# 6. Verify
SHOW DATABASES;
SELECT user, host FROM mysql.user WHERE user = 'frameio_user';

# 7. Exit
EXIT;
```

### Test Connection

```bash
# Test database connection
mysql -u frameio_user -p frameio_db
# Enter password when prompted
# Type EXIT; to leave
```

### Status
- ✅ **Manual Setup Required** - Must be created via MySQL commands
- ⚠️ **Critical** - Application will not work without database

---

## 8. Redis Configuration (Optional)

### Source
**Path:** `/etc/redis/redis.conf` (system default)

### Destination
**Path:** Redis server (localhost:6379)

### Purpose
- Caching
- Background task queue (Celery)
- Session storage

### Setup Instructions

```bash
# 1. Install Redis (if not already installed)
sudo apt-get install redis-server

# 2. Start Redis service
sudo systemctl start redis-server

# 3. Enable Redis on boot
sudo systemctl enable redis-server

# 4. Check status
sudo systemctl status redis-server

# 5. Test connection
redis-cli ping
# Should return: PONG
```

### Configuration

Default configuration usually works. Connection string:
```
REDIS_URL=redis://localhost:6379/0
```

### Status
- ⚠️ **Optional** - Not required but recommended for performance
- ✅ **Default Config Works** - Usually no changes needed

---

## 📝 Quick Setup Checklist

### Required Files (Must Setup)

- [ ] **`.env`** - Create from template and configure
- [ ] **Nginx Config** - Copy to `/etc/nginx/sites-available/frameio`
- [ ] **Systemd Service** - Copy to `/etc/systemd/system/`
- [ ] **MySQL Database** - Create database and user

### Already Configured (No Setup Needed)

- [x] **Gunicorn Config** - Already in project
- [x] **Django Settings** - Already in project
- [x] **Next.js Config** - Already in project (may need IP update)

### Optional Files

- [ ] **Redis** - Optional but recommended
- [ ] **SSL Certificates** - For HTTPS (Let's Encrypt)

---

## 🚀 Automated Setup

Most configuration files are set up automatically by the setup script:

```bash
cd ~/Frameio/deployment
sudo chmod +x setup.sh
sudo ./setup.sh
```

**Note:** If `setup.sh` uses `/opt/frameio/` paths, you'll need to update it to use `~/Frameio/` or `/home/ubuntu/Frameio/` paths.

**What `setup.sh` does:**
- ✅ Installs system packages (Python, Nginx, MySQL, Redis, Node.js)
- ✅ Creates virtual environment
- ✅ Copies Nginx config to system location
- ✅ Copies systemd service file
- ✅ Sets up directories and permissions

**What you still need to do manually:**
- ❌ Create and configure `.env` file
- ❌ Set up MySQL database and user
- ❌ Configure environment variables in `.env`

---

## 📍 File Locations Summary

### On Your Local Machine (Development)

```
Framio/
├── deployment/
│   ├── env.production.template    # Template for .env
│   └── frameio-backend.service    # Systemd service file
├── nginx.conf                     # Nginx configuration
├── backend/
│   ├── gunicorn_config.py        # Gunicorn config
│   └── frameio_backend/
│       └── settings.py           # Django settings
└── frontend/
    └── next.config.ts            # Next.js config
```

### On Production Server (EC2)

```
/home/ubuntu/Frameio/            # Project root (or ~/Frameio/)
├── .env                         # Production environment variables
├── venv/                        # Python virtual environment (if created)
├── backend/
│   ├── gunicorn_config.py      # Gunicorn config
│   ├── staticfiles/             # Collected static files
│   ├── media/                   # User uploads
│   ├── logs/                    # Application logs
│   └── frameio_backend/
│       └── settings.py          # Django settings
├── frontend/
│   └── next.config.ts           # Next.js config
├── deployment/
│   ├── env.production.template  # Template for .env
│   └── frameio-backend.service  # Systemd service file
└── nginx.conf                   # Nginx configuration

/etc/nginx/sites-available/
└── frameio                      # Nginx config (copied from nginx.conf)

/etc/systemd/system/
└── frameio-backend.service      # Systemd service (copied from deployment/)
```

---

## 🔍 Verification Commands

After setup, verify all configuration files:

```bash
# 1. Navigate to project directory
cd ~/Frameio

# 2. Check .env file exists and has correct permissions
ls -la .env
# Should show: -rw------- (600)

# 3. Check Nginx config
sudo nginx -t
sudo ls -la /etc/nginx/sites-available/frameio
sudo ls -la /etc/nginx/sites-enabled/frameio

# 4. Check systemd service
sudo systemctl status frameio-backend
sudo ls -la /etc/systemd/system/frameio-backend.service

# 5. Check Gunicorn config
ls -la backend/gunicorn_config.py

# 6. Check Django settings
ls -la backend/frameio_backend/settings.py

# 7. Test database connection
mysql -u frameio_user -p frameio_db

# 8. Test Redis connection
redis-cli ping
```

---

## 📚 Related Documentation

- **Full Deployment Structure:** [`FULL_STACK_DEPLOYMENT_STRUCTURE.md`](FULL_STACK_DEPLOYMENT_STRUCTURE.md)
- **Step-by-Step Deployment:** [`STEP_BY_STEP_DEPLOYMENT.md`](STEP_BY_STEP_DEPLOYMENT.md)
- **Quick Start Guide:** [`QUICK_START.md`](QUICK_START.md)
- **Main Deployment README:** [`README.md`](README.md)

---

**Last Updated:** 2024  
**Server IP:** 13.213.53.199  
**Deployment Platform:** AWS EC2 (Ubuntu)

