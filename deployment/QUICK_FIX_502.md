# Quick Fix for 502 Bad Gateway Error

## Immediate Fix Commands

Run these commands on your server to fix the 502 error:

```bash
# SSH to your server
ssh ubuntu@13.213.53.199

# 1. Check if Gunicorn is running
sudo systemctl status frameio-backend

# 2. If not running, start it
sudo systemctl start frameio-backend

# 3. Check if it's listening on port 8000
sudo netstat -tuln | grep 8000

# 4. Check Gunicorn logs for errors
sudo journalctl -u frameio-backend -n 50 --no-pager

# 5. Restart Gunicorn
sudo systemctl restart frameio-backend

# 6. Reload Nginx
sudo systemctl reload nginx

# 7. Test the backend directly
curl http://127.0.0.1:8000/health/
```

## Common Causes and Fixes

### 1. Gunicorn Service Not Running

**Check:**
```bash
sudo systemctl status frameio-backend
```

**Fix:**
```bash
sudo systemctl start frameio-backend
sudo systemctl enable frameio-backend  # Enable on boot
```

### 2. Gunicorn Crashed (Check Logs)

**Check logs:**
```bash
# Systemd logs
sudo journalctl -u frameio-backend -n 100 --no-pager

# Gunicorn error log
tail -50 /opt/frameio/backend/logs/gunicorn_error.log

# Django logs
tail -50 /opt/frameio/backend/logs/django.log
```

**Common issues:**
- Database connection error → Check MySQL is running: `sudo systemctl status mysql`
- Import error → Check Python dependencies: `cd /opt/frameio/backend && source ../venv/bin/activate && pip install -r requirements.txt`
- Permission error → Fix permissions: `sudo chown -R www-data:www-data /opt/frameio/backend`

### 3. Port 8000 Not Listening

**Check:**
```bash
sudo netstat -tuln | grep 8000
```

**If nothing shows:**
```bash
# Restart Gunicorn
sudo systemctl restart frameio-backend

# Wait a few seconds, then check again
sleep 3
sudo netstat -tuln | grep 8000
```

### 4. Database Connection Issue

**Test database:**
```bash
cd /opt/frameio/backend
source /opt/frameio/venv/bin/activate
python manage.py check --database default
```

**If database error:**
```bash
# Check MySQL is running
sudo systemctl status mysql

# Start MySQL if not running
sudo systemctl start mysql

# Test connection
mysql -u frameio_user -p frameio_db
```

### 5. Permission Issues

**Fix permissions:**
```bash
sudo chown -R www-data:www-data /opt/frameio/backend
sudo chmod -R 755 /opt/frameio/backend
sudo chown -R www-data:www-data /opt/frameio/backend/logs
sudo chown -R www-data:www-data /opt/frameio/backend/media
```

### 6. Environment Variables Missing

**Check .env file:**
```bash
cat /opt/frameio/.env | grep -E "SECRET_KEY|DATABASE|DEBUG"
```

**If missing, create/update:**
```bash
sudo nano /opt/frameio/.env
```

### 7. Python Virtual Environment Issue

**Recreate venv if needed:**
```bash
cd /opt/frameio
sudo rm -rf venv
sudo python3 -m venv venv
source venv/bin/activate
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

## Automated Fix Script

Use the diagnostic script:

```bash
cd /opt/frameio/deployment
sudo chmod +x fix-502-error.sh
sudo ./fix-502-error.sh
```

## Manual Gunicorn Start (For Testing)

If systemd service isn't working, test manually:

```bash
cd /opt/frameio/backend
source /opt/frameio/venv/bin/activate
gunicorn --config gunicorn_config.py frameio_backend.wsgi:application
```

If this works, the issue is with the systemd service configuration.

## Check Nginx Configuration

```bash
# Test nginx config
sudo nginx -t

# Check nginx error log
sudo tail -50 /var/log/nginx/error.log

# Check if nginx can reach backend
curl -v http://127.0.0.1:8000/health/
```

## Complete Service Restart

```bash
# Stop everything
sudo systemctl stop frameio-backend
sudo systemctl stop nginx

# Start in order
sudo systemctl start mysql
sudo systemctl start frameio-backend
sleep 5
sudo systemctl start nginx

# Check status
sudo systemctl status frameio-backend
sudo systemctl status nginx
```

## Still Not Working?

1. **Check all services:**
   ```bash
   sudo systemctl status frameio-backend
   sudo systemctl status nginx
   sudo systemctl status mysql
   ```

2. **Check firewall:**
   ```bash
   sudo ufw status
   ```

3. **Check disk space:**
   ```bash
   df -h
   ```

4. **Check memory:**
   ```bash
   free -h
   ```

5. **View real-time logs:**
   ```bash
   # Gunicorn
   sudo journalctl -u frameio-backend -f
   
   # Nginx
   sudo tail -f /var/log/nginx/error.log
   ```

## Quick One-Liner Fix

```bash
sudo systemctl restart frameio-backend && sleep 3 && sudo systemctl reload nginx && curl http://127.0.0.1:8000/health/
```

If this returns a response, the backend is working and the 502 should be resolved.

