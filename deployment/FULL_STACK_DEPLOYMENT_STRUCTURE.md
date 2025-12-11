# Full-Stack Server Deployment Structure

## 🏗️ Complete Deployment Architecture

This document provides a comprehensive overview of the Frameio full-stack deployment structure on AWS EC2.

---

## 📁 Server Directory Structure

```
/opt/frameio/                                    # Project root on EC2
│
├── venv/                                        # Python virtual environment
│   ├── bin/
│   │   ├── python                              # Python interpreter
│   │   ├── pip                                 # Package manager
│   │   ├── gunicorn                            # WSGI HTTP server
│   │   └── activate                            # Virtual env activation script
│   ├── lib/
│   │   └── python3.x/
│   │       └── site-packages/                 # Installed Python packages
│   └── pyvenv.cfg                              # Virtual env config
│
├── backend/                                     # Django Backend Application
│   ├── frameio_backend/                        # Django project package
│   │   ├── __init__.py
│   │   ├── settings.py                         # Django settings (production-ready)
│   │   ├── urls.py                             # URL routing
│   │   ├── wsgi.py                             # WSGI application entry point
│   │   ├── asgi.py                             # ASGI application (if needed)
│   │   └── celery.py                           # Celery configuration
│   │
│   ├── organizations/                         # Organizations app
│   ├── users/                                  # Users app
│   ├── designs/                                # Designs app
│   ├── ai_services/                            # AI services app
│   ├── design_export/                          # Design export app
│   ├── collaboration/                          # Collaboration app
│   │
│   ├── manage.py                               # Django management script
│   ├── requirements.txt                        # Python dependencies
│   ├── gunicorn_config.py                      # Gunicorn configuration
│   │
│   ├── staticfiles/                            # Collected static files (CSS, JS, images)
│   │   ├── admin/                              # Django admin static files
│   │   ├── rest_framework/                     # DRF static files
│   │   └── [app static files]                  # App-specific static files
│   │
│   ├── media/                                  # User-uploaded files
│   │   ├── posters/                            # Generated posters
│   │   ├── catalogs/                           # Generated catalogs
│   │   ├── logos/                              # Generated logos
│   │   └── [user uploads]                      # Other user content
│   │
│   └── logs/                                   # Application logs
│       ├── gunicorn_access.log                 # Gunicorn access log
│       ├── gunicorn_error.log                  # Gunicorn error log
│       ├── django.log                          # Django application log
│       └── frameio_backend.pid                 # Gunicorn process ID
│
├── frontend/                                    # Next.js Frontend Application
│   ├── src/                                    # Source code
│   │   ├── app/                                # Next.js app directory
│   │   ├── components/                         # React components
│   │   ├── lib/                                # Utility libraries
│   │   └── styles/                             # CSS/styling files
│   │
│   ├── public/                                 # Static public assets
│   │   ├── images/                             # Images
│   │   ├── icons/                              # Icons
│   │   └── [other assets]                      # Other static files
│   │
│   ├── .next/                                  # Next.js build output (generated)
│   │   ├── static/                             # Static assets
│   │   ├── server/                             # Server-side code
│   │   └── cache/                              # Build cache
│   │
│   ├── package.json                            # Node.js dependencies
│   ├── next.config.ts                          # Next.js configuration
│   ├── tsconfig.json                           # TypeScript configuration
│   └── tailwind.config.js                      # Tailwind CSS configuration
│
├── deployment/                                  # Deployment scripts and configs
│   ├── setup.sh                                # Initial server setup script
│   ├── deploy.sh                               # Deployment automation script
│   ├── frameio-backend.service                 # Systemd service file
│   ├── env.production.template                 # Environment variables template
│   ├── README.md                               # Deployment documentation
│   └── [other deployment docs]                 # Additional deployment files
│
├── nginx.conf                                   # Nginx configuration file
│                                                # (copied to /etc/nginx/sites-available/frameio)
│
└── .env                                        # Production environment variables
    # Contains: SECRET_KEY, DB credentials, API keys, etc.
```

---

## 🔗 Service Architecture & Network Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet Users                            │
└────────────────────────────┬──────────────────────────────────────┘
                            │
                            │ HTTP (Port 80) / HTTPS (Port 443)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS EC2 Instance                              │
│                    IP: 13.213.53.199                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Nginx (Port 80/443)                    │   │
│  │  Location: /etc/nginx/sites-available/frameio            │   │
│  │                                                           │   │
│  │  Routes:                                                  │   │
│  │  ├── /static/  → /opt/frameio/backend/staticfiles/      │   │
│  │  ├── /media/   → /opt/frameio/backend/media/             │   │
│  │  └── /api/     → Proxy to Gunicorn (127.0.0.1:8000)     │   │
│  └───────────────────────┬──────────────────────────────────┘   │
│                          │                                        │
│                          │ Proxy (127.0.0.1:8000)                │
│                          ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Gunicorn (Port 8000)                         │   │
│  │  Service: frameio-backend.service                        │   │
│  │  User: www-data                                          │   │
│  │  Config: /opt/frameio/backend/gunicorn_config.py        │   │
│  │  Workers: (CPU cores × 2) + 1                           │   │
│  │                                                           │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │         Django Application                        │   │   │
│  │  │         WSGI: frameio_backend.wsgi:application   │   │   │
│  │  │         Working Dir: /opt/frameio/backend/       │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └───────────────────────┬──────────────────────────────────┘   │
│                          │                                        │
│                          │ Database Connection                    │
│                          ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    MySQL Database                         │   │
│  │  Service: mysql.service                                  │   │
│  │  Database: frameio_db                                    │   │
│  │  User: frameio_user                                      │   │
│  │  Host: localhost:3306                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Redis Cache                             │   │
│  │  Service: redis-server.service                           │   │
│  │  Port: 6379                                               │   │
│  │  (Optional - for caching and Celery)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Next.js Frontend (Optional)                  │   │
│  │  Process Manager: PM2 or systemd                          │   │
│  │  Port: 3000 (internal)                                    │   │
│  │  Build: /opt/frameio/frontend/.next/                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ System Services

### 1. Gunicorn (Django Backend)

**Service File:** `/etc/systemd/system/frameio-backend.service`

**Configuration:**
- **Working Directory:** `/opt/frameio/backend`
- **User:** `www-data`
- **Group:** `www-data`
- **Executable:** `/opt/frameio/venv/bin/gunicorn`
- **Config File:** `/opt/frameio/backend/gunicorn_config.py`
- **WSGI Application:** `frameio_backend.wsgi:application`
- **Bind Address:** `127.0.0.1:8000` (internal, proxied by Nginx)
- **Workers:** `(CPU cores × 2) + 1`
- **Logs:** `/opt/frameio/backend/logs/`

**Management Commands:**
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
tail -f /opt/frameio/backend/logs/gunicorn_error.log
```

### 2. Nginx (Reverse Proxy & Static Files)

**Configuration File:** `/etc/nginx/sites-available/frameio`

**Key Features:**
- **Port:** 80 (HTTP), 443 (HTTPS when SSL configured)
- **Server Name:** `13.213.53.199` (or domain name)
- **Static Files:** Serves from `/opt/frameio/backend/staticfiles/`
- **Media Files:** Serves from `/opt/frameio/backend/media/`
- **API Proxy:** Proxies `/api/*` to Gunicorn at `127.0.0.1:8000`
- **CORS Headers:** Configured for media files (Facebook sharing)
- **Client Max Body Size:** 100M (for file uploads)

**Management Commands:**
```bash
# Test configuration
sudo nginx -t

# Start service
sudo systemctl start nginx

# Stop service
sudo systemctl stop nginx

# Restart service
sudo systemctl restart nginx

# Reload (no downtime)
sudo systemctl reload nginx

# View logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 3. MySQL Database

**Service:** `mysql.service`

**Configuration:**
- **Database Name:** `frameio_db`
- **User:** `frameio_user`
- **Host:** `localhost`
- **Port:** `3306`
- **Character Set:** `utf8mb4`
- **Collation:** `utf8mb4_unicode_ci`

**Management Commands:**
```bash
# Start service
sudo systemctl start mysql

# Check status
sudo systemctl status mysql

# Connect to database
mysql -u frameio_user -p frameio_db
```

### 4. Redis (Optional - Caching)

**Service:** `redis-server.service`

**Configuration:**
- **Port:** `6379`
- **Host:** `localhost`

**Management Commands:**
```bash
# Start service
sudo systemctl start redis-server

# Check status
sudo systemctl status redis-server

# Connect to Redis
redis-cli
```

### 5. Next.js Frontend (Optional - if on same server)

**Process Manager:** PM2 or systemd

**Configuration:**
- **Port:** `3000` (internal)
- **Build Directory:** `/opt/frameio/frontend/.next/`
- **Node Environment:** `production`

**Management Commands (PM2):**
```bash
# Start
pm2 start npm --name "frameio-frontend" -- start

# Stop
pm2 stop frameio-frontend

# Restart
pm2 restart frameio-frontend

# Status
pm2 status

# Logs
pm2 logs frameio-frontend
```

---

## 📋 Configuration Files

### 1. Gunicorn Configuration

**File:** `/opt/frameio/backend/gunicorn_config.py`

**Key Settings:**
- **Bind:** `127.0.0.1:8000`
- **Workers:** `multiprocessing.cpu_count() * 2 + 1`
- **Worker Class:** `sync`
- **Timeout:** `30` seconds
- **Max Requests:** `1000` (per worker before restart)
- **Access Log:** `/opt/frameio/backend/logs/gunicorn_access.log`
- **Error Log:** `/opt/frameio/backend/logs/gunicorn_error.log`
- **Preload App:** `True` (for better performance)

### 2. Nginx Configuration

**File:** `/etc/nginx/sites-available/frameio`

**Key Settings:**
- **Upstream:** `django` → `127.0.0.1:8000`
- **Static Files:** `/opt/frameio/backend/staticfiles/` → `/static/`
- **Media Files:** `/opt/frameio/backend/media/` → `/media/`
- **API Proxy:** `/api/*` → `http://django`
- **Client Max Body Size:** `100M`
- **CORS Headers:** Enabled for media files
- **Security Headers:** X-Frame-Options, X-Content-Type-Options, etc.

### 3. Django Settings

**File:** `/opt/frameio/backend/frameio_backend/settings.py`

**Key Production Settings:**
- **DEBUG:** `False` (from `.env`)
- **ALLOWED_HOSTS:** `13.213.53.199,localhost,127.0.0.1` (from `.env`)
- **SECRET_KEY:** (from `.env`)
- **Database:** MySQL (credentials from `.env`)
- **Static Root:** `/opt/frameio/backend/staticfiles/`
- **Media Root:** `/opt/frameio/backend/media/`
- **CORS:** Configured for production origins
- **Security Middleware:** Enabled
- **WhiteNoise:** Enabled (static file serving fallback)

### 4. Environment Variables

**File:** `/opt/frameio/.env`

**Required Variables:**
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
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_CLERK_FRONTEND_API=...

# AI Services
GEMINI_API_KEY=AIzaSy...

# Security
ARCJET_KEY=your_arcjet_key

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# Production Settings
SECURE_SSL_REDIRECT=False  # Set to True when SSL is configured
CORS_ALLOWED_ORIGINS=http://13.213.53.199,https://13.213.53.199
```

---

## 🔄 Request Flow

### 1. Static File Request

```
User Request: http://13.213.53.199/static/admin/css/base.css
    │
    ▼
Nginx (Port 80)
    │
    ├─ Matches: location /static/
    │
    ▼
Serves directly from: /opt/frameio/backend/staticfiles/admin/css/base.css
    │
    ▼
Response to User (200 OK)
```

### 2. Media File Request

```
User Request: http://13.213.53.199/media/posters/poster_123.jpg
    │
    ▼
Nginx (Port 80)
    │
    ├─ Matches: location /media/
    │
    ├─ Adds CORS headers (for Facebook sharing)
    │
    ▼
Serves directly from: /opt/frameio/backend/media/posters/poster_123.jpg
    │
    ▼
Response to User (200 OK with CORS headers)
```

### 3. API Request

```
User Request: http://13.213.53.199/api/designs/
    │
    ▼
Nginx (Port 80)
    │
    ├─ Matches: location / (default)
    │
    ├─ Proxies to: http://django (127.0.0.1:8000)
    │
    ▼
Gunicorn (Port 8000)
    │
    ├─ Receives request
    │
    ├─ Routes to Django application
    │
    ▼
Django Application
    │
    ├─ Processes request
    │
    ├─ Queries MySQL database (if needed)
    │
    ├─ Returns JSON response
    │
    ▼
Gunicorn
    │
    ▼
Nginx (proxies response)
    │
    ▼
Response to User (200 OK with JSON data)
```

---

## 📊 Port Allocation

| Service | Port | Protocol | Access | Purpose |
|---------|------|----------|--------|---------|
| Nginx | 80 | HTTP | Public | Web server (HTTP) |
| Nginx | 443 | HTTPS | Public | Web server (HTTPS - when SSL configured) |
| Gunicorn | 8000 | HTTP | Localhost only | Django application server |
| MySQL | 3306 | TCP | Localhost only | Database |
| Redis | 6379 | TCP | Localhost only | Cache/Queue |
| Next.js | 3000 | HTTP | Localhost only | Frontend (if on same server) |
| SSH | 22 | TCP | Restricted (your IP) | Server access |

---

## 🔐 Security Configuration

### 1. File Permissions

```bash
# Environment file (sensitive)
chmod 600 /opt/frameio/.env

# Static and media files (readable by Nginx)
chown -R www-data:www-data /opt/frameio/backend/staticfiles
chown -R www-data:www-data /opt/frameio/backend/media
chmod -R 755 /opt/frameio/backend/staticfiles
chmod -R 755 /opt/frameio/backend/media

# Logs (writable by Gunicorn)
chown -R www-data:www-data /opt/frameio/backend/logs
chmod -R 755 /opt/frameio/backend/logs
```

### 2. AWS Security Group

**Inbound Rules:**
- **SSH (22):** Your IP only
- **HTTP (80):** 0.0.0.0/0 (all)
- **HTTPS (443):** 0.0.0.0/0 (all) - when SSL configured

**Outbound Rules:**
- **All Traffic:** 0.0.0.0/0 (for API calls, package downloads)

### 3. Firewall (UFW - if enabled)

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

---

## 🚀 Deployment Workflow

### Initial Deployment

1. **Server Setup**
   ```bash
   cd /opt/frameio/deployment
   sudo chmod +x setup.sh
   sudo ./setup.sh
   ```

2. **Database Setup**
   ```bash
   sudo mysql -u root -p
   # Create database and user
   ```

3. **Environment Configuration**
   ```bash
   cp deployment/env.production.template .env
   nano .env  # Edit with production values
   chmod 600 .env
   ```

4. **Backend Deployment**
   ```bash
   source venv/bin/activate
   cd backend
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   ```

5. **Service Configuration**
   ```bash
   sudo cp deployment/frameio-backend.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable frameio-backend
   
   sudo cp nginx.conf /etc/nginx/sites-available/frameio
   sudo ln -sf /etc/nginx/sites-available/frameio /etc/nginx/sites-enabled/
   sudo nginx -t
   ```

6. **Start Services**
   ```bash
   sudo systemctl start frameio-backend
   sudo systemctl start nginx
   ```

### Update Deployment

```bash
cd /opt/frameio/deployment
sudo ./deploy.sh
```

**Or manually:**
```bash
source /opt/frameio/venv/bin/activate
cd /opt/frameio/backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart frameio-backend
sudo systemctl reload nginx
```

---

## 📝 Log Locations

| Service | Log File | Purpose |
|---------|----------|---------|
| Gunicorn Access | `/opt/frameio/backend/logs/gunicorn_access.log` | HTTP access logs |
| Gunicorn Error | `/opt/frameio/backend/logs/gunicorn_error.log` | Error logs |
| Django | `/opt/frameio/backend/logs/django.log` | Application logs |
| Nginx Access | `/var/log/nginx/access.log` | Web server access logs |
| Nginx Error | `/var/log/nginx/error.log` | Web server error logs |
| Systemd | `journalctl -u frameio-backend` | Service logs |

**View Logs:**
```bash
# Gunicorn logs
tail -f /opt/frameio/backend/logs/gunicorn_error.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log

# Systemd logs
sudo journalctl -u frameio-backend -f
```

---

## 🔍 Monitoring & Health Checks

### Service Status Check

```bash
# Check all services
sudo systemctl status frameio-backend
sudo systemctl status nginx
sudo systemctl status mysql
sudo systemctl status redis-server
```

### Port Check

```bash
# Check if services are listening
sudo netstat -tulpn | grep :8000  # Gunicorn
sudo netstat -tulpn | grep :80    # Nginx
sudo netstat -tulpn | grep :3306  # MySQL
```

### Health Endpoint

```bash
# Test API endpoint
curl http://13.213.53.199/api/

# Test admin panel
curl http://13.213.53.199/admin/

# Test static files
curl -I http://13.213.53.199/static/admin/css/base.css
```

---

## 🎯 Key Takeaways

1. **Separation of Concerns:**
   - Nginx handles static files and reverse proxying
   - Gunicorn handles Django application
   - MySQL handles data persistence
   - Redis handles caching (optional)

2. **Security:**
   - Gunicorn only listens on localhost (not exposed publicly)
   - Nginx is the only public-facing service
   - Environment variables are secured with proper permissions
   - Database is only accessible from localhost

3. **Performance:**
   - Static files served directly by Nginx (fast)
   - Gunicorn workers scale with CPU cores
   - Redis caching reduces database load
   - Nginx handles SSL termination (when configured)

4. **Scalability:**
   - Can add more Gunicorn workers
   - Can deploy frontend separately (Vercel, etc.)
   - Can use load balancer for multiple backend instances
   - Can scale database separately

---

## 📚 Related Documentation

- **Quick Start:** `deployment/QUICK_START.md`
- **Step-by-Step Guide:** `deployment/STEP_BY_STEP_DEPLOYMENT.md`
- **Structure Explanation:** `deployment/STRUCTURE_EXPLANATION.md`
- **Main README:** `deployment/README.md`

---

**Last Updated:** 2024
**Server IP:** 13.213.53.199
**Deployment Platform:** AWS EC2 (Ubuntu)

