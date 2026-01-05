# Production Deployment Checklist - EC2 & S3

Use this checklist to track your deployment progress.

## Pre-Deployment

- [ ] AWS Account created and configured
- [ ] EC2 instance created (Ubuntu 22.04+)
- [ ] Security group configured (SSH, HTTP, HTTPS)
- [ ] S3 bucket created and configured
- [ ] IAM role created and attached to EC2 (or access keys ready)
- [ ] SSH key pair ready
- [ ] Domain name ready (optional)

## Phase 1: AWS Infrastructure

- [ ] S3 bucket created with unique name
- [ ] S3 bucket region noted
- [ ] S3 bucket encryption enabled
- [ ] S3 CORS configured (if needed)
- [ ] IAM role created for EC2 S3 access
- [ ] IAM role attached to EC2 instance
- [ ] EC2 instance launched (if not already)
- [ ] EC2 public IP noted

## Phase 2: EC2 Initial Setup

- [ ] Connected to EC2 via SSH
- [ ] System packages updated (`sudo apt update && sudo apt upgrade`)
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] MySQL 8.0 installed and running
- [ ] Nginx installed and running
- [ ] Redis installed (optional)

## Phase 3: Repository Setup

- [ ] Repository cloned to EC2
- [ ] Project structure verified
- [ ] All files present (backend/, frontend/, deployment/)

## Phase 4: Database Setup

- [ ] MySQL secured (`mysql_secure_installation`)
- [ ] Database created (`frameio_db`)
- [ ] Database user created (`frameio_user`)
- [ ] User privileges granted
- [ ] Database connection tested

## Phase 5: Python Environment

- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] pip upgraded
- [ ] Backend dependencies installed
- [ ] Gunicorn verified installed

## Phase 6: Environment Configuration

- [ ] `.env` file created from template
- [ ] `SECRET_KEY` generated and set
- [ ] `DEBUG=False` set
- [ ] `ALLOWED_HOSTS` configured
- [ ] Database credentials set
- [ ] Clerk keys configured
- [ ] Gemini API key configured
- [ ] AWS S3 configuration set:
  - [ ] `AWS_REGION` set
  - [ ] `AWS_S3_BUCKET` set
  - [ ] IAM role configured OR access keys set
- [ ] `.env` file secured (chmod 600)

## Phase 7: Backend Deployment

- [ ] Virtual environment activated
- [ ] Database migrations run (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] S3 connection tested
- [ ] Permissions set for media/staticfiles/logs
- [ ] Gunicorn tested manually (optional)

## Phase 8: Systemd Service

- [ ] Service file copied to `/etc/systemd/system/`
- [ ] Service file paths updated (project location)
- [ ] Systemd daemon reloaded
- [ ] Service enabled (`systemctl enable`)
- [ ] Service started (`systemctl start`)
- [ ] Service status verified (active/running)

## Phase 9: Nginx Configuration

- [ ] `nginx.conf` updated with correct paths
- [ ] Nginx config copied to `/etc/nginx/sites-available/`
- [ ] Symbolic link created in `/etc/nginx/sites-enabled/`
- [ ] Default site removed
- [ ] Nginx config tested (`nginx -t`)
- [ ] Nginx started and enabled
- [ ] Nginx status verified

## Phase 10: Frontend Deployment

- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend `.env.local` created
- [ ] Frontend environment variables set
- [ ] Frontend built (`npm run build`)
- [ ] PM2 installed globally
- [ ] Frontend started with PM2
- [ ] PM2 startup configured
- [ ] Frontend status verified

## Phase 11: Security Group

- [ ] Security group inbound rules configured:
  - [ ] SSH (22) from your IP
  - [ ] HTTP (80) from anywhere
  - [ ] HTTPS (443) from anywhere (if using SSL)

## Phase 12: Testing

- [ ] Backend API tested (`curl http://IP/api/`)
- [ ] Admin panel accessible (`http://IP/admin/`)
- [ ] Static files loading
- [ ] S3 upload tested
- [ ] Frontend accessible
- [ ] All services status checked
- [ ] Logs reviewed (no errors)

## Phase 13: SSL Setup (Optional)

- [ ] Certbot installed
- [ ] SSL certificate obtained
- [ ] Nginx configured for HTTPS
- [ ] HTTP to HTTPS redirect configured
- [ ] Auto-renewal tested

## Phase 14: Final Configuration

- [ ] Domain configured (if using)
- [ ] Environment variables updated for domain
- [ ] Frontend rebuilt with domain
- [ ] Services restarted

## Phase 15: Monitoring & Maintenance

- [ ] Log rotation configured
- [ ] Backup script created
- [ ] Cron job for backups set
- [ ] Monitoring setup (optional)

## Post-Deployment

- [ ] All URLs tested and working
- [ ] S3 uploads working
- [ ] Database operations working
- [ ] Authentication working (Clerk)
- [ ] AI services working (Gemini)
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Security checklist completed

## Quick Verification Commands

```bash
# Check all services
sudo systemctl status frameio-backend nginx mysql
pm2 status

# Test endpoints
curl http://YOUR_IP/api/
curl http://YOUR_IP/admin/

# Check logs
sudo journalctl -u frameio-backend -n 20
pm2 logs frameio-frontend --lines 20
```

---

**Deployment Date:** _______________

**EC2 IP:** _______________

**S3 Bucket:** _______________

**Domain:** _______________ (if applicable)

**Notes:**
_________________________________
_________________________________
_________________________________

