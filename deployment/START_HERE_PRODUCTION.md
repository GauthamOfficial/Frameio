# 🚀 Production Deployment - Start Here

Welcome! This guide will help you deploy Frameio to AWS EC2 with S3 storage.

## 📚 Documentation Structure

### **Main Deployment Guide** ⭐
👉 **[PRODUCTION_DEPLOYMENT_EC2_S3.md](PRODUCTION_DEPLOYMENT_EC2_S3.md)** - Complete step-by-step guide

This is your primary reference. It covers:
- AWS infrastructure setup (EC2, S3, IAM)
- EC2 server configuration
- Database setup
- Backend deployment (Django + Gunicorn)
- Frontend deployment (Next.js)
- Nginx configuration
- SSL setup
- Monitoring and maintenance

### **Supporting Documents**

1. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Track your progress
   - Use this to check off each step as you complete it
   - Helps ensure nothing is missed

2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Common commands
   - Quick access to frequently used commands
   - Service management, logs, troubleshooting

3. **[STEP_BY_STEP_DEPLOYMENT.md](STEP_BY_STEP_DEPLOYMENT.md)** - Alternative detailed guide
   - More detailed explanations
   - Additional troubleshooting tips

## 🎯 Quick Start (TL;DR)

If you're experienced and just need the essentials:

1. **Create AWS Resources:**
   - EC2 instance (Ubuntu 22.04+)
   - S3 bucket
   - IAM role for EC2 → S3 access

2. **Setup EC2:**
   ```bash
   ssh -i key.pem ubuntu@YOUR_EC2_IP
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-pip python3-venv nodejs npm mysql-server nginx git
   ```

3. **Clone & Setup:**
   ```bash
   cd ~
   git clone https://github.com/yourusername/Framio.git framio
   cd framio
   python3 -m venv venv
   source venv/bin/activate
   cd backend && pip install -r requirements.txt
   ```

4. **Configure:**
   - Create `.env` from `deployment/env.production.template`
   - Set up MySQL database
   - Configure S3 settings

5. **Deploy:**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   sudo systemctl start frameio-backend
   ```

6. **Frontend:**
   ```bash
   cd ~/framio/frontend
   npm install && npm run build
   pm2 start npm --name "frameio-frontend" -- start
   ```

**For complete details, follow [PRODUCTION_DEPLOYMENT_EC2_S3.md](PRODUCTION_DEPLOYMENT_EC2_S3.md)**

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] AWS account with EC2 and S3 access
- [ ] SSH key pair for EC2
- [ ] Domain name (optional, but recommended)
- [ ] All API keys ready:
  - [ ] Clerk (authentication)
  - [ ] Gemini (AI services)
  - [ ] Arcjet (API protection)
- [ ] 2-3 hours for first deployment
- [ ] Basic knowledge of:
  - Linux command line
  - Git
  - AWS basics

## 🗺️ Deployment Flow

```
1. AWS Setup
   ├── Create S3 bucket
   ├── Create IAM role
   └── Launch EC2 instance

2. EC2 Initial Setup
   ├── Connect via SSH
   ├── Install system packages
   └── Install Python, Node.js, MySQL, Nginx

3. Project Setup
   ├── Clone repository
   ├── Create virtual environment
   └── Install dependencies

4. Database Setup
   ├── Secure MySQL
   ├── Create database
   └── Create user

5. Configuration
   ├── Create .env file
   ├── Configure environment variables
   └── Set up S3 credentials

6. Backend Deployment
   ├── Run migrations
   ├── Create superuser
   ├── Collect static files
   └── Configure systemd service

7. Frontend Deployment
   ├── Install dependencies
   ├── Build Next.js app
   └── Start with PM2

8. Nginx Configuration
   ├── Update nginx.conf
   ├── Install configuration
   └── Start Nginx

9. Testing & Verification
   ├── Test all endpoints
   ├── Verify S3 uploads
   └── Check logs

10. SSL Setup (Optional)
    ├── Install Certbot
    ├── Obtain certificate
    └── Configure HTTPS
```

## ⏱️ Estimated Time

- **First-time deployment:** 2-3 hours
- **Subsequent updates:** 10-15 minutes
- **Troubleshooting:** Varies

## 🆘 Need Help?

1. **Check the main guide:** [PRODUCTION_DEPLOYMENT_EC2_S3.md](PRODUCTION_DEPLOYMENT_EC2_S3.md)
2. **Review troubleshooting section** in the main guide
3. **Check logs:**
   ```bash
   sudo journalctl -u frameio-backend -n 50
   pm2 logs frameio-frontend
   sudo tail -f /var/log/nginx/error.log
   ```
4. **Use quick reference:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

## ✅ Success Criteria

Your deployment is successful when:

- ✅ All services are running (`systemctl status` shows active)
- ✅ Backend API responds (`curl http://IP/api/`)
- ✅ Admin panel loads (`http://IP/admin/`)
- ✅ Frontend loads (`http://IP:3000` or configured domain)
- ✅ S3 uploads work
- ✅ No errors in logs
- ✅ SSL certificate installed (if using domain)

## 📝 Notes

- **Project Location:** The guide assumes you'll clone the repo in `~/framio` or `/opt/framio`
- **IAM Role:** Recommended over access keys for better security
- **S3 Bucket:** Must be in the same region as your EC2 instance for best performance
- **Domain:** Optional but recommended for production

## 🎓 Learning Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)

---

**Ready to start?** Open [PRODUCTION_DEPLOYMENT_EC2_S3.md](PRODUCTION_DEPLOYMENT_EC2_S3.md) and begin with Phase 1!

**Good luck! 🚀**

