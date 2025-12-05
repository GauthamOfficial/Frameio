# Quick Start Guide - Frameio AWS EC2 Deployment

## Prerequisites
- AWS EC2 instance (Ubuntu 20.04+)
- SSH access
- Your IP: **13.213.53.199**

## Step-by-Step Deployment

### 1. Connect to Your EC2 Instance

```bash
ssh -i your-key.pem ubuntu@13.213.53.199
```

### 2. Upload Project Files

```bash
# On your local machine, upload project to EC2
scp -r -i your-key.pem /path/to/Framio ubuntu@13.213.53.199:/tmp/

# On EC2, move to /opt/frameio
sudo mv /tmp/Framio /opt/frameio
sudo chown -R ubuntu:ubuntu /opt/frameio
```

### 3. Run Initial Setup

```bash
cd /opt/frameio/deployment
sudo chmod +x setup.sh
sudo ./setup.sh
```

### 4. Configure Environment

```bash
# Copy production template
sudo cp deployment/env.production.template /opt/frameio/.env

# Edit with your values
sudo nano /opt/frameio/.env
```

**Important values to set:**
- `SECRET_KEY` - Generate: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DEBUG=False`
- `ALLOWED_HOSTS=13.213.53.199,localhost,127.0.0.1`
- Database credentials
- API keys (Clerk, Gemini, etc.)

### 5. Setup MySQL Database

```bash
sudo mysql -u root -p
```

```sql
CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'frameio_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON frameio_db.* TO 'frameio_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 6. Deploy Application

```bash
# Activate virtual environment
source /opt/frameio/venv/bin/activate

# Install dependencies
cd /opt/frameio/backend
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Run deployment script
cd /opt/frameio/deployment
sudo ./deploy.sh
```

### 7. Start Services

```bash
# Start and enable services
sudo systemctl start frameio-backend
sudo systemctl enable frameio-backend
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status frameio-backend
sudo systemctl status nginx
```

### 8. Configure AWS Security Group

In AWS Console → EC2 → Security Groups:

**Inbound Rules:**
- Type: SSH, Port: 22, Source: Your IP
- Type: HTTP, Port: 80, Source: 0.0.0.0/0
- Type: HTTPS, Port: 443, Source: 0.0.0.0/0 (if using SSL)

### 9. Test Your Deployment

```bash
# Test backend
curl http://13.213.53.199/api/

# Check logs if issues
sudo tail -f /opt/frameio/backend/logs/gunicorn_error.log
sudo tail -f /var/log/nginx/error.log
```

## Common Commands

```bash
# Restart backend
sudo systemctl restart frameio-backend

# Restart nginx
sudo systemctl restart nginx

# View logs
sudo journalctl -u frameio-backend -f
tail -f /opt/frameio/backend/logs/gunicorn_error.log

# Update code
cd /opt/frameio
git pull  # or upload new files
sudo ./deployment/deploy.sh
```

## Troubleshooting

**Service won't start:**
```bash
sudo systemctl status frameio-backend
sudo journalctl -u frameio-backend -n 50
```

**Permission errors:**
```bash
sudo chown -R www-data:www-data /opt/frameio/backend/media
sudo chown -R www-data:www-data /opt/frameio/backend/staticfiles
```

**Database connection issues:**
```bash
sudo systemctl status mysql
mysql -u frameio_user -p frameio_db
```

**Nginx errors:**
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

## Next Steps

1. **Setup SSL** (recommended):
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

2. **Configure Domain** (if you have one):
   - Update DNS A record to point to 13.213.53.199
   - Update `.env` with domain name
   - Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`

3. **Setup Monitoring:**
   - Configure CloudWatch
   - Setup error tracking (Sentry)
   - Setup log rotation

## Your Application URLs

- **Backend API:** http://13.213.53.199/api/
- **Admin Panel:** http://13.213.53.199/admin/
- **Media Files:** http://13.213.53.199/media/

