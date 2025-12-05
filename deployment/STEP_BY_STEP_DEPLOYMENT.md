# Complete Step-by-Step Deployment Guide

## 📋 Overview

This guide will walk you through deploying Frameio to AWS EC2 with Nginx and Gunicorn. Follow each step carefully.

**Your IP:** 13.213.53.199  
**Estimated Time:** 1-2 hours (first time)

---

## Phase 1: Preparation (On Your Local Machine)

### Step 1.1: Verify Your Project Files

Make sure you have all the deployment files:

```bash
# Check these files exist:
✅ backend/requirements.txt (with gunicorn)
✅ backend/gunicorn_config.py
✅ backend/frameio_backend/settings.py (with production settings)
✅ nginx.conf (with IP 13.213.53.199)
✅ deployment/setup.sh
✅ deployment/deploy.sh
✅ deployment/frameio-backend.service
✅ deployment/env.production.template
```

### Step 1.2: Prepare Environment Variables

1. **Open** `deployment/env.production.template`
2. **Copy** it to create your production `.env` file (locally, for reference)
3. **Fill in** all the required values:

**Critical values to set:**
- `SECRET_KEY` - Generate one:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- `DEBUG=False`
- `ALLOWED_HOSTS=13.213.53.199,localhost,127.0.0.1`
- Database credentials (you'll create these on EC2)
- All API keys (Clerk, Gemini, etc.)

### Step 1.3: Test Your Project Locally (Optional but Recommended)

```bash
# Make sure everything works before deploying
cd backend
python manage.py check
python manage.py collectstatic --noinput
```

### Step 1.4: Prepare for Upload

**Option A: Using Git (Recommended)**
```bash
# If using Git, make sure everything is committed
git add .
git commit -m "Prepare for EC2 deployment"
git push
```

**Option B: Create Archive**
```bash
# Create a zip file (exclude unnecessary files)
# On Windows, use 7-Zip or WinRAR
# Exclude: node_modules, startup_env, __pycache__, .next, etc.
```

---

## Phase 2: AWS EC2 Setup

### Step 2.1: Access Your EC2 Instance

**Using SSH (Windows - PowerShell or Git Bash):**

```bash
# Navigate to where your .pem key is located
cd path/to/your/keys

# Connect to EC2
ssh -i your-key.pem ubuntu@13.213.53.199

# If permission denied, fix key permissions (on Git Bash):
chmod 400 your-key.pem
```

**Alternative: Using PuTTY (Windows)**
1. Download PuTTY and PuTTYgen
2. Convert .pem to .ppk using PuTTYgen
3. Connect using PuTTY with the .ppk file

### Step 2.2: Update System Packages

Once connected to EC2:

```bash
# Update package list
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget
```

### Step 2.3: Create Project Directory

```bash
# Create the project directory
sudo mkdir -p /opt/frameio

# Set ownership (replace 'ubuntu' with your username if different)
sudo chown -R ubuntu:ubuntu /opt/frameio

# Navigate to it
cd /opt/frameio
```

---

## Phase 3: Upload Project Files

### Step 3.1: Upload Files to EC2

**Option A: Using SCP (From Your Local Machine)**

Open a **new terminal** on your local machine (keep SSH session open):

```bash
# Navigate to your project root
cd "D:\My Files\Yarl IT Hub\Framio"

# Upload entire project (exclude node_modules, etc.)
scp -i path/to/your-key.pem -r \
  --exclude 'node_modules' \
  --exclude 'startup_env' \
  --exclude '__pycache__' \
  --exclude '.next' \
  . ubuntu@13.213.53.199:/opt/frameio/
```

**Option B: Using Git (If Using GitHub)**

On EC2:
```bash
cd /opt/frameio
git clone https://github.com/yourusername/Framio.git .
```

**Option C: Using WinSCP (Windows GUI)**

1. Download WinSCP
2. Connect to 13.213.53.199
3. Drag and drop files to `/opt/frameio/`

### Step 3.2: Verify Files Uploaded

On EC2, check:
```bash
cd /opt/frameio
ls -la

# Should see:
# backend/
# frontend/
# deployment/
# nginx.conf
# etc.
```

---

## Phase 4: Initial Server Setup

### Step 4.1: Run Setup Script

```bash
cd /opt/frameio/deployment

# Make script executable
chmod +x setup.sh

# Run setup (this will take 5-10 minutes)
sudo ./setup.sh
```

**What this does:**
- Installs Python, Nginx, MySQL, Redis, Node.js
- Creates virtual environment
- Sets up directories
- Installs Gunicorn
- Configures systemd service
- Sets up Nginx configuration

### Step 4.2: Verify Setup

```bash
# Check Python
python3 --version

# Check virtual environment
ls -la /opt/frameio/venv

# Check Nginx
sudo nginx -t

# Check MySQL
sudo systemctl status mysql

# Check Redis
sudo systemctl status redis-server
```

---

## Phase 5: Database Configuration

### Step 5.1: Secure MySQL Installation

```bash
# Run MySQL secure installation
sudo mysql_secure_installation

# Follow prompts:
# - Set root password (remember this!)
# - Remove anonymous users: Yes
# - Disallow root login remotely: Yes
# - Remove test database: Yes
# - Reload privilege tables: Yes
```

### Step 5.2: Create Database and User

```bash
# Login to MySQL
sudo mysql -u root -p
# Enter the root password you just set
```

**In MySQL prompt, run:**

```sql
-- Create database
CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (replace 'strong_password' with your password)
CREATE USER 'frameio_user'@'localhost' IDENTIFIED BY 'strong_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON frameio_db.* TO 'frameio_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SELECT user, host FROM mysql.user WHERE user = 'frameio_user';

-- Exit
EXIT;
```

### Step 5.3: Test Database Connection

```bash
# Test connection
mysql -u frameio_user -p frameio_db
# Enter password when prompted
# Type EXIT; to leave
```

---

## Phase 6: Environment Configuration

### Step 6.1: Create Production .env File

```bash
cd /opt/frameio

# Copy template
cp deployment/env.production.template .env

# Edit the file
nano .env
# OR use: sudo nano .env
```

### Step 6.2: Configure Environment Variables

**In nano editor, update these values:**

```env
# Django Settings
SECRET_KEY=your_generated_secret_key_here
DEBUG=False
ALLOWED_HOSTS=13.213.53.199,localhost,127.0.0.1

# Database (use the credentials you just created)
DB_NAME=frameio_db
DB_USER=frameio_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=3306

# Clerk (your actual keys)
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_CLERK_FRONTEND_API=...

# Gemini (your actual key)
GEMINI_API_KEY=AIzaSy...

# Other API keys...
```

**To save in nano:**
- Press `Ctrl + O` (save)
- Press `Enter` (confirm filename)
- Press `Ctrl + X` (exit)

### Step 6.3: Secure .env File

```bash
# Set proper permissions (only owner can read/write)
chmod 600 /opt/frameio/.env

# Verify
ls -la /opt/frameio/.env
# Should show: -rw------- (only you can read it)
```

---

## Phase 7: Backend Deployment

### Step 7.1: Activate Virtual Environment

```bash
cd /opt/frameio

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

### Step 7.2: Install Python Dependencies

```bash
cd /opt/frameio/backend

# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# This will take a few minutes
# Verify Gunicorn is installed
pip list | grep gunicorn
```

### Step 7.3: Run Database Migrations

```bash
# Make sure you're in backend directory
cd /opt/frameio/backend

# Run migrations
python manage.py migrate

# You should see output like:
# Operations to perform:
#   Apply all migrations: ...
# Running migrations:
#   ...
```

### Step 7.4: Create Superuser

```bash
# Create admin user
python manage.py createsuperuser

# Follow prompts:
# Username: admin (or your choice)
# Email: your@email.com
# Password: (enter strong password)
```

### Step 7.5: Collect Static Files

```bash
# Collect all static files
python manage.py collectstatic --noinput

# This will create/update /opt/frameio/backend/staticfiles/
# You should see: "X static files copied to ..."
```

### Step 7.6: Set Permissions

```bash
# Set ownership for www-data user (Nginx/Gunicorn user)
sudo chown -R www-data:www-data /opt/frameio/backend/media
sudo chown -R www-data:www-data /opt/frameio/backend/staticfiles
sudo chown -R www-data:www-data /opt/frameio/backend/logs

# Set permissions
sudo chmod -R 755 /opt/frameio/backend/media
sudo chmod -R 755 /opt/frameio/backend/staticfiles
```

### Step 7.7: Test Gunicorn Manually (Optional)

```bash
# Test Gunicorn can start
cd /opt/frameio/backend
gunicorn --config gunicorn_config.py frameio_backend.wsgi:application

# If it starts without errors, press Ctrl+C to stop
# This confirms everything is configured correctly
```

---

## Phase 8: Configure and Start Services

### Step 8.1: Install Systemd Service

```bash
# Copy service file
sudo cp /opt/frameio/deployment/frameio-backend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable frameio-backend
```

### Step 8.2: Configure Nginx

```bash
# Copy Nginx config
sudo cp /opt/frameio/nginx.conf /etc/nginx/sites-available/frameio

# Create symbolic link
sudo ln -sf /etc/nginx/sites-available/frameio /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Should see: "syntax is ok" and "test is successful"
```

### Step 8.3: Start Services

```bash
# Start Gunicorn
sudo systemctl start frameio-backend

# Start Nginx
sudo systemctl start nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx
```

### Step 8.4: Check Service Status

```bash
# Check Gunicorn
sudo systemctl status frameio-backend

# Check Nginx
sudo systemctl status nginx

# Both should show "active (running)"
```

---

## Phase 9: Testing and Verification

### Step 9.1: Test Backend API

```bash
# From your local machine or EC2
curl http://13.213.53.199/api/

# Should return JSON response or API documentation
```

### Step 9.2: Test Admin Panel

```bash
# Open in browser
http://13.213.53.199/admin/

# Login with superuser credentials you created
```

### Step 9.3: Test Static Files

```bash
# Test static file serving
curl -I http://13.213.53.199/static/admin/css/base.css

# Should return 200 OK
```

### Step 9.4: Check Logs

```bash
# Gunicorn logs
sudo tail -f /opt/frameio/backend/logs/gunicorn_error.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# System logs
sudo journalctl -u frameio-backend -f
```

---

## Phase 10: AWS Security Group Configuration

### Step 10.1: Configure Security Group

1. **Go to AWS Console** → EC2 → Security Groups
2. **Select your instance's security group**
3. **Edit Inbound Rules:**

**Add these rules:**
- **Type:** SSH, **Port:** 22, **Source:** Your IP address
- **Type:** HTTP, **Port:** 80, **Source:** 0.0.0.0/0
- **Type:** HTTPS, **Port:** 443, **Source:** 0.0.0.0/0 (if using SSL)

4. **Save rules**

### Step 10.2: Test from Browser

Open in your browser:
- `http://13.213.53.199/api/`
- `http://13.213.53.199/admin/`

---

## Phase 11: Frontend Deployment (If on Same Server)

### Step 11.1: Install Node.js Dependencies

```bash
cd /opt/frameio/frontend

# Install dependencies
npm install

# This will take a few minutes
```

### Step 11.2: Build Next.js Application

```bash
# Build for production
npm run build

# This creates .next/ directory
```

### Step 11.3: Start Frontend (Using PM2)

```bash
# Install PM2 globally
sudo npm install -g pm2

# Start Next.js with PM2
cd /opt/frameio/frontend
pm2 start npm --name "frameio-frontend" -- start

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the command it outputs
```

**OR use systemd** (create service similar to backend)

---

## Phase 12: Final Verification

### Step 12.1: Complete System Check

```bash
# Check all services
sudo systemctl status frameio-backend
sudo systemctl status nginx
sudo systemctl status mysql
sudo systemctl status redis-server

# Check ports
sudo netstat -tulpn | grep :8000  # Gunicorn
sudo netstat -tulpn | grep :80     # Nginx
```

### Step 12.2: Test All Endpoints

```bash
# API endpoint
curl http://13.213.53.199/api/

# Admin panel
curl http://13.213.53.199/admin/

# Static files
curl http://13.213.53.199/static/admin/css/base.css
```

### Step 12.3: Monitor Logs

```bash
# Watch logs in real-time
sudo journalctl -u frameio-backend -f
```

---

## Phase 13: Troubleshooting Common Issues

### Issue 1: Gunicorn Won't Start

```bash
# Check logs
sudo journalctl -u frameio-backend -n 50

# Check permissions
ls -la /opt/frameio/backend/

# Test manually
cd /opt/frameio/backend
source /opt/frameio/venv/bin/activate
gunicorn --config gunicorn_config.py frameio_backend.wsgi:application
```

### Issue 2: Nginx 502 Bad Gateway

```bash
# Check if Gunicorn is running
sudo systemctl status frameio-backend

# Check Gunicorn logs
tail -f /opt/frameio/backend/logs/gunicorn_error.log

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log
```

### Issue 3: Database Connection Error

```bash
# Test MySQL connection
mysql -u frameio_user -p frameio_db

# Check MySQL is running
sudo systemctl status mysql

# Check .env file has correct credentials
cat /opt/frameio/.env | grep DB_
```

### Issue 4: Permission Denied Errors

```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/frameio/backend/media
sudo chown -R www-data:www-data /opt/frameio/backend/staticfiles
sudo chown -R www-data:www-data /opt/frameio/backend/logs

# Fix permissions
sudo chmod -R 755 /opt/frameio/backend/media
sudo chmod -R 755 /opt/frameio/backend/staticfiles
```

### Issue 5: Static Files Not Loading

```bash
# Recollect static files
cd /opt/frameio/backend
source /opt/frameio/venv/bin/activate
python manage.py collectstatic --noinput

# Check Nginx config path
sudo nginx -t

# Check static files exist
ls -la /opt/frameio/backend/staticfiles/
```

---

## Phase 14: Maintenance Commands

### Daily Operations

```bash
# Restart backend
sudo systemctl restart frameio-backend

# Restart Nginx
sudo systemctl restart nginx

# View logs
sudo journalctl -u frameio-backend -f
tail -f /opt/frameio/backend/logs/gunicorn_error.log
```

### Updating Code

```bash
# 1. Upload new code
# 2. Activate venv
source /opt/frameio/venv/bin/activate

# 3. Install new dependencies (if any)
cd /opt/frameio/backend
pip install -r requirements.txt

# 4. Run migrations (if any)
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Restart services
sudo systemctl restart frameio-backend
sudo systemctl reload nginx
```

---

## ✅ Deployment Checklist

Use this checklist to track your progress:

- [ ] Phase 1: Preparation complete
- [ ] Phase 2: EC2 access established
- [ ] Phase 3: Files uploaded
- [ ] Phase 4: Setup script run successfully
- [ ] Phase 5: Database created and configured
- [ ] Phase 6: Environment variables configured
- [ ] Phase 7: Backend deployed (migrations, static files)
- [ ] Phase 8: Services started (Gunicorn, Nginx)
- [ ] Phase 9: Testing successful
- [ ] Phase 10: Security group configured
- [ ] Phase 11: Frontend deployed (if applicable)
- [ ] Phase 12: Final verification complete

---

## 🎉 Success Indicators

You'll know deployment is successful when:

1. ✅ `sudo systemctl status frameio-backend` shows "active (running)"
2. ✅ `sudo systemctl status nginx` shows "active (running)"
3. ✅ `curl http://13.213.53.199/api/` returns valid response
4. ✅ `http://13.213.53.199/admin/` loads in browser
5. ✅ No errors in logs
6. ✅ Static files load correctly

---

## 📞 Next Steps After Deployment

1. **Setup SSL** (recommended):
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

2. **Setup Domain** (if you have one):
   - Point DNS A record to 13.213.53.199
   - Update ALLOWED_HOSTS in .env
   - Update CORS_ALLOWED_ORIGINS

3. **Setup Monitoring**:
   - Configure CloudWatch
   - Setup error tracking (Sentry)
   - Setup log rotation

4. **Setup Backups**:
   - Database backups
   - Media file backups
   - Configuration backups

---

## 📚 Additional Resources

- Full documentation: `deployment/README.md`
- Quick start: `deployment/QUICK_START.md`
- Structure explanation: `deployment/STRUCTURE_EXPLANATION.md`

---

**Good luck with your deployment!** 🚀

If you encounter any issues, refer to the troubleshooting section or check the logs.

