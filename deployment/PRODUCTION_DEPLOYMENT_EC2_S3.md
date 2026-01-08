# Complete Production Deployment Guide - EC2 & S3

## 📋 Overview

This guide provides step-by-step instructions for deploying Frameio to AWS EC2 with S3 for file storage. The guide assumes you'll clone the repository in the root directory of your EC2 instance.

**Architecture:**
- **EC2**: Ubuntu 22.04 LTS (or 20.04)
- **Backend**: Django + Gunicorn + Nginx
- **Frontend**: Next.js (standalone build)
- **Database**: MySQL 8.0+
- **File Storage**: AWS S3
- **Cache**: Redis (optional)

**Estimated Time:** 2-3 hours (first deployment)

---

## Phase 1: AWS Infrastructure Setup

### Step 1.1: Create S3 Bucket

1. **Go to AWS Console** → S3 → Create bucket

2. **Bucket Configuration:**
   - **Bucket name**: `frameio-storage-{your-unique-id}` (must be globally unique)
   - **AWS Region**: Choose your region (e.g., `us-east-1`, `ap-southeast-1`)
   - **Object Ownership**: ACLs disabled (recommended)
   - **Block Public Access**: 
     - ✅ Block all public access (we'll use CloudFront or public URLs later if needed)
   - **Bucket Versioning**: Disabled (unless you need it)
   - **Default encryption**: Enable (SSE-S3 or SSE-KMS)
   - **Object Lock**: Disabled

3. **Click "Create bucket"**

4. **Configure CORS (if needed for frontend):**
   - Go to bucket → Permissions → CORS
   - Add this configuration:
   ```json
   [
       {
           "AllowedHeaders": ["*"],
           "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
           "AllowedOrigins": ["*"],
           "ExposeHeaders": ["ETag"],
           "MaxAgeSeconds": 3000
       }
   ]
   ```

5. **Note your bucket name and region** - you'll need these later

### Step 1.2: Create IAM Role for EC2 (Recommended - Best Practice)

**Why IAM Role?** More secure than access keys - no credentials to manage.

1. **Go to AWS Console** → IAM → Roles → Create role

2. **Select Trust Entity:**
   - **Trusted entity type**: AWS service
   - **Use case**: EC2
   - Click "Next"

3. **Add Permissions:**
   - Search for `AmazonS3FullAccess` (or create custom policy with only your bucket)
   - Select the policy
   - Click "Next"

4. **Role Details:**
   - **Role name**: `FrameioEC2S3Role`
   - **Description**: "EC2 role for Frameio S3 access"
   - Click "Create role"

5. **Attach Role to EC2 Instance:**
   - Go to EC2 → Instances
   - Select your instance
   - Actions → Security → Modify IAM role
   - Select `FrameioEC2S3Role`
   - Click "Update IAM role"

**Alternative: If you prefer access keys** (less secure):
- Go to IAM → Users → Create user
- Attach `AmazonS3FullAccess` policy
- Create access key
- Save Access Key ID and Secret Access Key securely

### Step 1.3: Create EC2 Instance (If Not Already Created)

1. **Launch EC2 Instance:**
   - **AMI**: Ubuntu Server 22.04 LTS (or 20.04)
   - **Instance Type**: t3.medium or larger (recommended: t3.large for production)
   - **Key Pair**: Create new or use existing
   - **Network Settings**: 
     - Create/select security group
     - Allow SSH (port 22) from your IP
     - Allow HTTP (port 80) from anywhere (0.0.0.0/0)
     - Allow HTTPS (port 443) from anywhere (0.0.0.0/0)
   - **Configure Storage**: 20GB minimum (30GB recommended)
   - **Advanced Details**: 
     - IAM instance profile: Select `FrameioEC2S3Role` (if created)

2. **Launch Instance**

3. **Note your instance's:**
   - Public IP address (e.g., `13.213.53.199`)
   - Private IP address
   - Security Group ID

---

## Phase 2: EC2 Initial Setup

### Step 2.1: Connect to EC2 Instance

**From your local machine (Windows PowerShell or Git Bash):**

```bash
# Navigate to where your .pem key is located
cd path/to/your/keys

# Connect to EC2 (replace with your IP and key name)
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# If permission denied, fix key permissions (on Git Bash):
chmod 400 your-key.pem
```

**Alternative: Using PuTTY (Windows)**
1. Download PuTTY and PuTTYgen
2. Convert .pem to .ppk using PuTTYgen
3. Connect using PuTTY with the .ppk file

### Step 2.2: Update System and Install Essential Tools

```bash
# Update package list
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget build-essential software-properties-common
```

### Step 2.3: Install Python 3.10+ and pip

```bash
# Check Python version (should be 3.10+)
python3 --version

# Install Python development packages
sudo apt install -y python3-pip python3-dev python3-venv

# Verify pip
pip3 --version
```

### Step 2.4: Install Node.js 18+ (for Next.js)

```bash
# Install Node.js 18.x using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version  # Should be v18.x or higher
npm --version
```

### Step 2.5: Install MySQL 8.0

```bash
# Install MySQL server
sudo apt install -y mysql-server

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# Check status
sudo systemctl status mysql
```

### Step 2.6: Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

### Step 2.7: Install Redis (Optional but Recommended)

```bash
# Install Redis
sudo apt install -y redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Check status
sudo systemctl status redis-server
```

---

## Phase 3: Clone Repository and Setup Project

### Step 3.1: Clone Repository

**Assuming you'll clone in the home directory or /opt:**

```bash
# Option 1: Clone in home directory (recommended for simplicity)
cd ~
git clone https://github.com/yourusername/Framio.git framio
cd framio

# Option 2: Clone in /opt (more production-like)
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/yourusername/Framio.git framio
sudo chown -R ubuntu:ubuntu /opt/framio
cd /opt/framio
```

**If using private repository:**
```bash
# Setup SSH key or use HTTPS with credentials
git clone git@github.com:yourusername/Framio.git framio
```

### Step 3.2: Verify Project Structure

```bash
# Check project structure
ls -la

# Should see:
# backend/
# frontend/
# deployment/
# nginx.conf
# README.md
# etc.
```

---

## Phase 4: Database Setup

### Step 4.1: Secure MySQL Installation

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

### Step 4.2: Create Database and User

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

### Step 4.3: Test Database Connection

```bash
# Test connection
mysql -u frameio_user -p frameio_db
# Enter password when prompted
# Type EXIT; to leave
```

---

## Phase 5: Python Virtual Environment Setup

### Step 5.1: Install System Dependencies for Python Packages

**IMPORTANT:** Before installing Python packages, install system-level dependencies required for building packages like `mysqlclient`:

```bash
# Update package list
sudo apt update

# Install required system dependencies
sudo apt install -y \
    pkg-config \
    default-libmysqlclient-dev \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev

# Verify pkg-config is installed
pkg-config --version
```

**Note:** These packages are required for:
- `pkg-config`: Helps find library configuration files
- `default-libmysqlclient-dev`: MySQL client development libraries (required for mysqlclient)
- `python3-dev`: Python development headers
- `build-essential`: Compiler tools (gcc, make, etc.)
- `libssl-dev` & `libffi-dev`: SSL and FFI libraries for various Python packages

### Step 5.2: Create Virtual Environment

```bash
# Navigate to project root (wherever you cloned it)
cd ~/framio  # or /opt/framio

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source frameio_env/bin/activate

# You should see (venv) in your prompt
```

### Step 5.3: Upgrade pip and Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install backend dependencies
cd backend
pip install -r requirements.txt

# This will take a few minutes
# Verify Gunicorn is installed
pip list | grep gunicorn
```

---

## Phase 6: Environment Configuration

### Step 6.1: Create Production .env File

```bash
# Navigate to project root
cd ~/framio  # or /opt/framio

# Copy template
cp deployment/env.production.template .env

# Edit the file
nano .env
# OR use: sudo nano .env
```

### Step 6.2: Configure Environment Variables

**In nano editor, update these values:**

```env
# =============================================================================
# DJANGO SETTINGS
# =============================================================================
# Generate secret key: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=your_generated_secret_key_here
DEBUG=False
ALLOWED_HOSTS=YOUR_EC2_IP,localhost,127.0.0.1,yourdomain.com
CORS_ALLOWED_ORIGINS=http://YOUR_EC2_IP,https://yourdomain.com

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DB_NAME=frameio_db
DB_USER=frameio_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=3306

# =============================================================================
# CLERK AUTHENTICATION
# =============================================================================
CLERK_PUBLISHABLE_KEY=pk_test_...or_pk_live_...
CLERK_SECRET_KEY=sk_test_...or_sk_live_...
NEXT_PUBLIC_CLERK_FRONTEND_API=clerk.yourdomain.com

# =============================================================================
# AI SERVICES
# =============================================================================
GEMINI_API_KEY=AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps
ARCJET_KEY=your_arcjet_key_here

# =============================================================================
# AWS S3 CONFIGURATION
# =============================================================================
# If using IAM Role (recommended), leave these empty:
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# Required S3 settings:
AWS_REGION=us-east-1  # Change to your bucket's region
AWS_S3_BUCKET=frameio-storage-your-unique-id  # Your bucket name

# Optional: If you need to use access keys instead of IAM role:
# AWS_ACCESS_KEY_ID=your_access_key_here
# AWS_SECRET_ACCESS_KEY=your_secret_key_here

# =============================================================================
# REDIS (Optional)
# =============================================================================
REDIS_URL=redis://localhost:6379/0

# =============================================================================
# DOMAIN URL CONFIGURATION
# =============================================================================
DOMAIN_URL=http://YOUR_EC2_IP
# When using domain:
# DOMAIN_URL=https://yourdomain.com

# =============================================================================
# EMAIL CONFIGURATION (Optional)
# =============================================================================
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_digit_app_password_here
```

**To save in nano:**
- Press `Ctrl + O` (save)
- Press `Enter` (confirm filename)
- Press `Ctrl + X` (exit)

### Step 6.3: Secure .env File

```bash
# Set proper permissions (only owner can read/write)
chmod 600 .env

# Verify
ls -la .env
# Should show: -rw------- (only you can read it)
```

---

## Phase 7: Backend Deployment

### Step 7.1: Activate Virtual Environment

```bash
# Navigate to project root
cd ~/framio  # or /opt/framio

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
```

### Step 7.2: Run Database Migrations

```bash
# Make sure you're in backend directory
cd backend

# Run migrations
python manage.py migrate

# You should see output like:
# Operations to perform:
#   Apply all migrations: ...
# Running migrations:
#   ...
```

### Step 7.3: Create Superuser

```bash
# Create admin user
python manage.py createsuperuser

# Follow prompts:
# Username: admin (or your choice)
# Email: your@email.com
# Password: (enter strong password)
```

### Step 7.4: Collect Static Files

```bash
# Collect all static files
python manage.py collectstatic --noinput

# This will create/update backend/staticfiles/
# You should see: "X static files copied to ..."
```

### Step 7.5: Test S3 Connection

```bash
# Test S3 connection (optional but recommended)
cd ~/framio/backend  # or /opt/framio/backend
source ../venv/bin/activate
python manage.py shell
```

**In Django shell:**
```python
from utils.s3_storage import get_s3_client
s3_client, bucket_name = get_s3_client()
print(f"S3 Client: {s3_client}")
print(f"Bucket: {bucket_name}")

# Test upload (optional)
from utils.s3_storage import upload_file_to_s3
test_content = b"test file content"
url = upload_file_to_s3(test_content, "test/test.txt", "text/plain")
print(f"Uploaded to: {url}")
exit()
```

### Step 7.6: Set Permissions

```bash
# Set ownership for www-data user (Nginx/Gunicorn user)
sudo chown -R www-data:www-data backend/media
sudo chown -R www-data:www-data backend/staticfiles
sudo chown -R www-data:www-data backend/logs

# Set permissions
sudo chmod -R 755 backend/media
sudo chmod -R 755 backend/staticfiles
```

### Step 7.7: Test Gunicorn Manually (Optional)

```bash
# Test Gunicorn can start
cd backend
gunicorn --config gunicorn_config.py frameio_backend.wsgi:application

# If it starts without errors, press Ctrl+C to stop
# This confirms everything is configured correctly
```

---

## Phase 8: Configure Systemd Service

### Step 8.1: Install Systemd Service

```bash
# Navigate to project root
cd ~/framio  # or /opt/framio

# Copy service file
sudo cp deployment/frameio-backend.service /etc/systemd/system/

# Edit service file to match your project path
sudo nano /etc/systemd/system/frameio-backend.service
```

**Update the paths in the service file:**
- If project is in `~/framio`, paths should be `/home/ubuntu/framio`
- If project is in `/opt/framio`, paths should be `/opt/framio`

**Example service file content:**
```ini
[Unit]
Description=Frameio Django Backend (Gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/ubuntu/framio/backend
Environment="PATH=/home/ubuntu/framio/venv/bin"
ExecStart=/home/ubuntu/framio/venv/bin/gunicorn \
    --config /home/ubuntu/framio/backend/gunicorn_config.py \
    frameio_backend.wsgi:application

Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 8.2: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable frameio-backend

# Start service
sudo systemctl start frameio-backend

# Check status
sudo systemctl status frameio-backend
```

---

## Phase 9: Configure Nginx

### Step 9.1: Update Nginx Configuration

```bash
# Navigate to project root
cd ~/framio  # or /opt/framio

# Edit nginx.conf to match your setup
nano nginx.conf
```

**Update these values in nginx.conf:**
- `server_name`: Your EC2 IP or domain
- `root`: Path to your project (e.g., `/home/ubuntu/framio/backend`)
- `proxy_pass`: Should point to Gunicorn (usually `http://127.0.0.1:8000`)

### Step 9.2: Install Nginx Configuration

```bash
# Copy Nginx config
sudo cp nginx.conf /etc/nginx/sites-available/frameio

# Create symbolic link
sudo ln -sf /etc/nginx/sites-available/frameio /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Should see: "syntax is ok" and "test is successful"
```

### Step 9.3: Start Nginx

```bash
# Start Nginx
sudo systemctl start nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

---

## Phase 10: Frontend Deployment

### Step 10.1: Install Frontend Dependencies

```bash
# Navigate to project root
cd ~/framio  # or /opt/framio

# Navigate to frontend
cd frontend

# Install dependencies
npm install

# This will take a few minutes
```

### Step 10.2: Configure Frontend Environment

```bash
# Create frontend .env.local file
nano .env.local
```

**Add these variables:**
```env
# Clerk Configuration
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...or_pk_live_...
NEXT_PUBLIC_CLERK_FRONTEND_API=clerk.yourdomain.com

# Backend API URL
NEXT_PUBLIC_API_URL=http://YOUR_EC2_IP/api
# Or with domain:
# NEXT_PUBLIC_API_URL=https://yourdomain.com/api

# Other frontend variables
NEXT_PUBLIC_DOMAIN_URL=http://YOUR_EC2_IP
```

### Step 10.3: Build Next.js Application

```bash
# Build for production
npm run build

# This creates .next/ directory
# This will take a few minutes
```

### Step 10.4: Start Frontend (Using PM2 - Recommended)

```bash
# Install PM2 globally
sudo npm install -g pm2

# Start Next.js with PM2
cd ~/framio/frontend  # or /opt/framio/frontend
pm2 start npm --name "frameio-frontend" -- start

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the command it outputs (usually something like):
# sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u ubuntu --hp /home/ubuntu
```

**Alternative: Using systemd (More Production-Like)**

Create a systemd service for frontend:

```bash
sudo nano /etc/systemd/system/frameio-frontend.service
```

**Service file content:**
```ini
[Unit]
Description=Frameio Next.js Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/framio/frontend
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable frameio-frontend
sudo systemctl start frameio-frontend
sudo systemctl status frameio-frontend
```

---

## Phase 11: Configure AWS Security Group

### Step 11.1: Update Security Group Rules

1. **Go to AWS Console** → EC2 → Security Groups
2. **Select your instance's security group**
3. **Edit Inbound Rules:**

**Add/Verify these rules:**
- **Type:** SSH, **Port:** 22, **Source:** Your IP address (for security)
- **Type:** HTTP, **Port:** 80, **Source:** 0.0.0.0/0
- **Type:** HTTPS, **Port:** 443, **Source:** 0.0.0.0/0 (if using SSL)

4. **Save rules**

---

## Phase 12: Testing and Verification

### Step 12.1: Test Backend API

```bash
# From your local machine or EC2
curl http://YOUR_EC2_IP/api/

# Should return JSON response or API documentation
```

### Step 12.2: Test Admin Panel

```bash
# Open in browser
http://YOUR_EC2_IP/admin/

# Login with superuser credentials you created
```

### Step 12.3: Test Static Files

```bash
# Test static file serving
curl -I http://47.129.60.11/static/admin/css/base.css

# Should return 200 OK
```

### Step 12.4: Test S3 Upload

```bash
# Test S3 upload via API (if you have an endpoint)
curl -X POST http://YOUR_EC2_IP/api/upload/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test-image.jpg"

# Check S3 bucket to verify file was uploaded
```

### Step 12.5: Test Frontend

```bash
# Open in browser
http://YOUR_EC2_IP:3000

# Or if configured in Nginx:
http://YOUR_EC2_IP/
```

### Step 12.6: Check Service Status

```bash
# Check all services
sudo systemctl status frameio-backend
sudo systemctl status nginx
sudo systemctl status mysql
sudo systemctl status redis-server  # if installed

# Check PM2 (if using)
pm2 status

# Check ports
sudo netstat -tulpn | grep :8000  # Gunicorn
sudo netstat -tulpn | grep :80     # Nginx
sudo netstat -tulpn | grep :3000   # Next.js
```

### Step 12.7: Check Logs

```bash
# Gunicorn logs
sudo tail -f ~/framio/backend/logs/gunicorn_error.log
# or
sudo journalctl -u frameio-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Frontend logs (if using PM2)
pm2 logs frameio-frontend

# System logs
sudo journalctl -u frameio-frontend -f  # if using systemd
```

---

## Phase 13: SSL/HTTPS Setup (Recommended)

### Step 13.1: Install Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx
```

### Step 13.2: Obtain SSL Certificate

**If you have a domain:**

```bash
# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter your email
# - Agree to terms
# - Choose redirect HTTP to HTTPS: Yes
```

**If you don't have a domain yet:**
- You can use the IP address, but SSL won't work
- Consider using a free domain from Freenom or purchasing one
- Or use AWS Certificate Manager with CloudFront

### Step 13.3: Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up renewal, but verify:
sudo systemctl status certbot.timer
```

---

## Phase 14: Final Configuration

### Step 14.1: Update Environment Variables for Domain (If Using)

```bash
# Edit .env file
nano .env

# Update:
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_EC2_IP,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DOMAIN_URL=https://yourdomain.com

# Restart backend
sudo systemctl restart frameio-backend
```

### Step 14.2: Update Frontend Environment

```bash
# Edit frontend .env.local
cd ~/framio/frontend
nano .env.local

# Update:
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
NEXT_PUBLIC_DOMAIN_URL=https://yourdomain.com

# Rebuild frontend
npm run build

# Restart frontend
pm2 restart frameio-frontend
# or
sudo systemctl restart frameio-frontend
```

---

## Phase 15: Monitoring and Maintenance

### Step 15.1: Setup Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/frameio
```

**Add this content:**
```
/home/ubuntu/Frameio/backend/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### Step 15.2: Setup Automatic Backups

```bash
# Create backup script
nano ~/backup_frameio.sh
```

**Add this content:**
```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u frameio_user -p'YOUR_PASSWORD' frameio_db > $BACKUP_DIR/db_$DATE.sql

# Backup .env file
cp /home/ubuntu/framio/.env $BACKUP_DIR/env_$DATE.env

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete
```

**Make executable and setup cron:**
```bash
chmod +x ~/backup_frameio.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add this line:
0 2 * * * /home/ubuntu/backup_frameio.sh
```

---

## Troubleshooting

### Issue 1: Gunicorn Won't Start

```bash
# Check logs
sudo journalctl -u frameio-backend -n 50

# Check permissions
ls -la ~/framio/backend/

# Test manually
cd ~/framio/backend
source ../venv/bin/activate
gunicorn --config gunicorn_config.py frameio_backend.wsgi:application
```

### Issue 2: Nginx 502 Bad Gateway

```bash
# Check if Gunicorn is running
sudo systemctl status frameio-backend

# Check Gunicorn logs
tail -f ~/framio/backend/logs/gunicorn_error.log

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Verify Gunicorn is listening
sudo netstat -tulpn | grep :8000
```

### Issue 3: S3 Connection Error

```bash
# Check IAM role is attached
aws sts get-caller-identity

# Check environment variables
cat ~/framio/.env | grep AWS_

# Test S3 access
aws s3 ls s3://your-bucket-name/

# If using access keys, verify they're correct
```

### Issue 4: Database Connection Error

```bash
# Test MySQL connection
mysql -u frameio_user -p frameio_db

# Check MySQL is running
sudo systemctl status mysql

# Check .env file has correct credentials
cat ~/framio/.env | grep DB_
```

### Issue 5: Frontend Not Loading

```bash
# Check PM2 status
pm2 status
pm2 logs frameio-frontend

# Check if Next.js is running
sudo netstat -tulpn | grep :3000

# Check frontend build
ls -la ~/framio/frontend/.next

# Rebuild if needed
cd ~/framio/frontend
npm run build
pm2 restart frameio-frontend
```

### Issue 6: Permission Denied Errors

```bash
# Fix ownership
sudo chown -R www-data:www-data ~/framio/backend/media
sudo chown -R www-data:www-data ~/framio/backend/staticfiles
sudo chown -R www-data:www-data ~/framio/backend/logs

# Fix permissions
sudo chmod -R 755 ~/framio/backend/media
sudo chmod -R 755 ~/framio/backend/staticfiles
```

---

## Maintenance Commands

### Daily Operations

```bash
# Restart backend
sudo systemctl restart frameio-backend

# Restart Nginx
sudo systemctl restart nginx

# Restart frontend
pm2 restart frameio-frontend
# or
sudo systemctl restart frameio-frontend

# View logs
sudo journalctl -u frameio-backend -f
pm2 logs frameio-frontend
```

### Updating Code

```bash
# 1. Navigate to project
cd ~/framio  # or /opt/framio

# 2. Pull latest code
git pull origin main

# 3. Activate venv
source venv/bin/activate

# 4. Install new dependencies (if any)
cd backend
pip install -r requirements.txt

# 5. Run migrations (if any)
python manage.py migrate

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Rebuild frontend (if needed)
cd ../frontend
npm install
npm run build

# 8. Restart services
sudo systemctl restart frameio-backend
sudo systemctl reload nginx
pm2 restart frameio-frontend
```

---

## Security Checklist

- [ ] ✅ Changed default MySQL root password
- [ ] ✅ Created dedicated database user (not root)
- [ ] ✅ Set `DEBUG=False` in production
- [ ] ✅ Secured `.env` file (chmod 600)
- [ ] ✅ Configured `ALLOWED_HOSTS` correctly
- [ ] ✅ Setup IAM role for S3 (or secured access keys)
- [ ] ✅ Configured security group (SSH only from your IP)
- [ ] ✅ Installed SSL certificate (if using domain)
- [ ] ✅ Enabled automatic security updates
- [ ] ✅ Setup log rotation
- [ ] ✅ Configured firewall (UFW recommended)
- [ ] ✅ Regular backups configured

---

## Success Indicators

You'll know deployment is successful when:

1. ✅ `sudo systemctl status frameio-backend` shows "active (running)"
2. ✅ `sudo systemctl status nginx` shows "active (running)"
3. ✅ `pm2 status` shows frameio-frontend as "online"
4. ✅ `curl http://YOUR_EC2_IP/api/` returns valid response
5. ✅ `http://YOUR_EC2_IP/admin/` loads in browser
6. ✅ Frontend loads at `http://YOUR_EC2_IP:3000` or configured domain
7. ✅ S3 uploads work correctly
8. ✅ No errors in logs
9. ✅ Static files load correctly

---

## Next Steps

1. **Setup Domain** (if you have one):
   - Point DNS A record to your EC2 IP
   - Update ALLOWED_HOSTS and CORS settings
   - Setup SSL with Certbot

2. **Setup CloudFront** (Optional - for better performance):
   - Create CloudFront distribution
   - Point to your S3 bucket
   - Update CORS settings

3. **Setup Monitoring**:
   - Configure CloudWatch
   - Setup error tracking (Sentry)
   - Setup uptime monitoring

4. **Setup CI/CD** (Optional):
   - GitHub Actions
   - Automated deployments
   - Automated testing

---

## Quick Reference

**Project Path:** `~/framio` or `/opt/framio`

**Key Commands:**
```bash
# Restart backend
sudo systemctl restart frameio-backend

# Restart frontend
pm2 restart frameio-frontend

# View backend logs
sudo journalctl -u frameio-backend -f

# View frontend logs
pm2 logs frameio-frontend

# Check all services
sudo systemctl status frameio-backend nginx mysql redis-server
pm2 status
```

**Important Files:**
- `.env` - Environment variables
- `nginx.conf` - Nginx configuration
- `/etc/systemd/system/frameio-backend.service` - Backend service
- `/etc/nginx/sites-available/frameio` - Nginx site config

---

**Good luck with your deployment!** 🚀

If you encounter any issues, refer to the troubleshooting section or check the logs.

