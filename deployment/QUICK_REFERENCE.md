# Quick Reference - Production Deployment Commands

## 🔧 Common Commands

### Service Management

```bash
# Backend Service
sudo systemctl status frameio-backend
sudo systemctl start frameio-backend
sudo systemctl stop frameio-backend
sudo systemctl restart frameio-backend
sudo systemctl enable frameio-backend
sudo systemctl disable frameio-backend

# Nginx
sudo systemctl status nginx
sudo systemctl restart nginx
sudo systemctl reload nginx
sudo nginx -t  # Test configuration

# MySQL
sudo systemctl status mysql
sudo systemctl restart mysql

# Redis
sudo systemctl status redis-server
sudo systemctl restart redis-server

# Frontend (PM2)
pm2 status
pm2 restart frameio-frontend
pm2 stop frameio-frontend
pm2 start frameio-frontend
pm2 logs frameio-frontend
pm2 logs frameio-frontend --lines 50
```

### View Logs

```bash
# Backend logs
sudo journalctl -u frameio-backend -f
sudo journalctl -u frameio-backend -n 50
tail -f ~/framio/backend/logs/gunicorn_error.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Frontend logs (PM2)
pm2 logs frameio-frontend
pm2 logs frameio-frontend --lines 100

# System logs
sudo journalctl -u frameio-frontend -f  # if using systemd
```

### Database Operations

```bash
# Connect to MySQL
mysql -u frameio_user -p frameio_db

# Backup database
mysqldump -u frameio_user -p frameio_db > backup_$(date +%Y%m%d).sql

# Restore database
mysql -u frameio_user -p frameio_db < backup_20240101.sql

# Check database size
mysql -u frameio_user -p -e "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.TABLES WHERE table_schema = 'frameio_db' GROUP BY table_schema;"
```

### Django Management

```bash
# Activate virtual environment
cd ~/framio  # or /opt/framio
source venv/bin/activate

# Run migrations
cd backend
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Django shell
python manage.py shell

# Check Django configuration
python manage.py check --deploy
```

### Code Updates

```bash
# Pull latest code
cd ~/framio  # or /opt/framio
git pull origin main

# Update backend
source venv/bin/activate
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart frameio-backend

# Update frontend
cd ~/framio/frontend  # or /opt/framio/frontend
npm install
npm run build
pm2 restart frameio-frontend
```

### S3 Testing

```bash
# Test S3 connection (from Django shell)
cd ~/framio/backend
source ../venv/bin/activate
python manage.py shell
```

```python
# In Django shell:
from utils.s3_storage import get_s3_client, upload_file_to_s3
s3_client, bucket_name = get_s3_client()
print(f"Bucket: {bucket_name}")

# Test upload
test_content = b"test file"
url = upload_file_to_s3(test_content, "test/test.txt", "text/plain")
print(f"URL: {url}")
exit()
```

```bash
# Test S3 with AWS CLI (if installed)
aws s3 ls s3://your-bucket-name/
aws s3 cp test.txt s3://your-bucket-name/test/
```

### Network & Ports

```bash
# Check what's listening on ports
sudo netstat -tulpn | grep :8000  # Gunicorn
sudo netstat -tulpn | grep :80    # Nginx
sudo netstat -tulpn | grep :3000  # Next.js
sudo netstat -tulpn | grep :3306  # MySQL

# Check process on port
sudo lsof -i :8000
```

### Testing Endpoints

```bash
# Test backend API
curl http://YOUR_EC2_IP/api/
curl http://YOUR_EC2_IP/api/organizations/

# Test admin
curl http://YOUR_EC2_IP/admin/

# Test static files
curl -I http://YOUR_EC2_IP/static/admin/css/base.css

# Test with authentication (if you have token)
curl -H "Authorization: Bearer YOUR_TOKEN" http://YOUR_EC2_IP/api/organizations/
```

### File Permissions

```bash
# Fix ownership
sudo chown -R www-data:www-data ~/framio/backend/media
sudo chown -R www-data:www-data ~/framio/backend/staticfiles
sudo chown -R www-data:www-data ~/framio/backend/logs

# Fix permissions
sudo chmod -R 755 ~/framio/backend/media
sudo chmod -R 755 ~/framio/backend/staticfiles
sudo chmod 600 ~/framio/.env
```

### Environment Variables

```bash
# View environment variables (be careful with secrets)
cat ~/framio/.env | grep -v PASSWORD
cat ~/framio/.env | grep AWS_

# Edit environment file
nano ~/framio/.env

# Check if variables are loaded
cd ~/framio/backend
source ../venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv('../../.env'); print(os.getenv('AWS_S3_BUCKET'))"
```

### Disk Space & Monitoring

```bash
# Check disk space
df -h

# Check directory sizes
du -sh ~/framio/*
du -sh ~/framio/backend/*
du -sh ~/framio/frontend/*

# Check memory usage
free -h

# Check CPU usage
top
htop  # if installed

# Check system load
uptime
```

### SSL Certificate (Let's Encrypt)

```bash
# Renew certificate
sudo certbot renew

# Test renewal (dry run)
sudo certbot renew --dry-run

# Check certificate status
sudo certbot certificates
```

### Backup & Restore

```bash
# Quick backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/backups
mkdir -p $BACKUP_DIR

# Database backup
mysqldump -u frameio_user -p'PASSWORD' frameio_db > $BACKUP_DIR/db_$DATE.sql

# Environment backup
cp ~/framio/.env $BACKUP_DIR/env_$DATE.env

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

### Troubleshooting

```bash
# Check all services status
sudo systemctl status frameio-backend nginx mysql redis-server
pm2 status

# Check recent errors
sudo journalctl -u frameio-backend --since "1 hour ago" | grep -i error
sudo tail -100 /var/log/nginx/error.log | grep -i error

# Check if services are enabled
systemctl list-unit-files | grep frameio
systemctl list-unit-files | grep enabled

# Restart all services
sudo systemctl restart frameio-backend nginx mysql
pm2 restart frameio-frontend
```

### Quick Health Check

```bash
# Run this to check everything is working
echo "=== Service Status ==="
sudo systemctl status frameio-backend --no-pager | head -3
sudo systemctl status nginx --no-pager | head -3
pm2 status

echo -e "\n=== Ports ==="
sudo netstat -tulpn | grep -E ':(80|443|8000|3000|3306)' | grep LISTEN

echo -e "\n=== Disk Space ==="
df -h | grep -E '/$|/home'

echo -e "\n=== Recent Errors ==="
sudo journalctl -u frameio-backend --since "10 minutes ago" | grep -i error | tail -5
```

---

## 📍 Common File Locations

```
Project Root:        ~/framio or /opt/framio
Backend:             ~/framio/backend
Frontend:            ~/framio/frontend
Virtual Env:         ~/framio/venv
Environment File:    ~/framio/.env
Nginx Config:        /etc/nginx/sites-available/frameio
Systemd Service:    /etc/systemd/system/frameio-backend.service
Logs:                ~/framio/backend/logs/
Static Files:        ~/framio/backend/staticfiles/
Media Files:         ~/framio/backend/media/ (or S3)
```

---

## 🔄 Typical Update Workflow

```bash
# 1. Pull latest code
cd ~/framio
git pull origin main

# 2. Update backend
source venv/bin/activate
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart frameio-backend

# 3. Update frontend
cd ../frontend
npm install
npm run build
pm2 restart frameio-frontend

# 4. Verify
curl http://YOUR_EC2_IP/api/
pm2 status
sudo systemctl status frameio-backend
```

---

## 🆘 Emergency Commands

```bash
# Stop everything
sudo systemctl stop frameio-backend nginx
pm2 stop frameio-frontend

# Start everything
sudo systemctl start frameio-backend nginx
pm2 start frameio-frontend

# Complete restart
sudo systemctl restart frameio-backend nginx mysql
pm2 restart frameio-frontend

# Check what's wrong
sudo journalctl -u frameio-backend -n 100
sudo tail -100 /var/log/nginx/error.log
pm2 logs frameio-frontend --lines 100
```

---

**Save this file for quick reference during deployment and maintenance!**

