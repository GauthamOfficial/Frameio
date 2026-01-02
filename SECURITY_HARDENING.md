# Security Hardening Guide

This document outlines the security measures implemented and recovery procedures for the Frameio application.

## ✅ Security Fixes Implemented

### 1. Open Redirect Vulnerability - FIXED
- **Location**: `frontend/src/app/api/auth/set-tokens/route.ts`
- **Fix**: Added `validateRedirectPath()` function to prevent open redirect attacks
- **Protection**: Validates redirect paths, prevents path traversal, and ensures same-origin redirects

### 2. Content Security Policy - HARDENED
- **Location**: `frontend/next.config.ts`
- **Fix**: Removed `'unsafe-eval'` from CSP
- **Protection**: Prevents XSS attacks via eval() and similar functions

### 3. Cookie Security - HARDENED
- **Location**: `frontend/src/app/api/auth/set-tokens/route.ts`
- **Fix**: Set `httpOnly: true` for auth cookies
- **Protection**: Prevents JavaScript access to tokens (XSS protection)

### 4. Input Validation - IMPLEMENTED
- **Location**: `frontend/src/lib/security/input-validation.ts`
- **Features**:
  - Redirect path validation
  - JWT token validation
  - Email validation
  - UUID validation
  - String sanitization
  - Filename sanitization

### 5. Rate Limiting - IMPLEMENTED
- **Location**: `frontend/src/lib/security/rate-limit.ts`
- **Features**:
  - Per-client rate limiting
  - Configurable limits
  - Preset configurations for different endpoint types
  - Rate limit headers in responses

## 🔒 Recovery Steps

### Step 1: Isolate the Server

**If possible, disconnect from network:**

```bash
# On the server, check network interfaces
ip addr show

# Temporarily disable network (USE WITH CAUTION - you'll lose SSH access)
# sudo ifdown eth0  # or your network interface name

# Better: Block all incoming traffic except SSH
sudo ufw default deny incoming
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP (if needed)
sudo ufw allow 443/tcp # HTTPS (if needed)
sudo ufw enable
```

**Or use AWS Security Groups:**
- Modify EC2 Security Group to only allow your IP for SSH
- Block all other incoming traffic

### Step 2: Take Snapshot/Backup

```bash
# Create snapshot of current state for forensics
# On AWS EC2:
# 1. Go to EC2 Console
# 2. Select your instance
# 3. Actions > Image and templates > Create image
# 4. Name it: "frameio-forensics-$(date +%Y%m%d)"

# Or create filesystem snapshot
sudo tar -czf /tmp/frameio-forensics-$(date +%Y%m%d).tar.gz \
  /opt/frameio \
  /var/log \
  /etc/systemd/system/frameio-*.service \
  /etc/nginx/sites-available/frameio \
  2>/dev/null

# Copy to safe location
# scp /tmp/frameio-forensics-*.tar.gz user@backup-server:/backups/
```

### Step 3: Stop All Services

```bash
# Stop all Frameio services
sudo systemctl stop frameio-frontend
sudo systemctl stop frameio-backend

# Kill any remaining malicious processes
sudo pkill -9 -f "6e1c"
sudo pkill -9 -f "wget.*34.236.146.239"
sudo pkill -9 node
sudo pkill -9 npm

# Verify nothing is running
ps aux | grep -E "next|node|npm|6e1c|wget" | grep -v grep
```

### Step 4: Remove Malicious Files

```bash
# Find and remove malicious files
sudo find / -name "6e1c*" -type f -delete 2>/dev/null
sudo find /var/tmp -type f -name "*" -mtime -7 -delete
sudo find /tmp -type f -name "*" -mtime -7 -delete

# Check for suspicious files
sudo find /opt/frameio -type f -name "*.sh" -ls
sudo find /opt/frameio -type f -name "*.py" -exec grep -l "wget\|curl\|exec\|eval" {} \;
```

### Step 5: Check for Persistence Mechanisms

```bash
# Check cron jobs
sudo crontab -l
sudo crontab -l -u root
sudo crontab -l -u ubuntu
sudo ls -la /etc/cron.d/
sudo cat /etc/crontab

# Check systemd timers
systemctl list-timers --all

# Check startup scripts
ls -la /etc/rc.local
ls -la ~/.bashrc
ls -la ~/.profile
ls -la /etc/profile.d/

# Check for new systemd services
systemctl list-units --type=service --all | grep -v "frameio"
```

### Step 6: Rebuild from Clean Source

```bash
# 1. Backup current code (if needed for comparison)
cd /opt/frameio
sudo tar -czf /tmp/frameio-code-backup-$(date +%Y%m%d).tar.gz .

# 2. Remove current code
cd /opt
sudo rm -rf frameio

# 3. Clone fresh from repository (use your actual repo URL)
cd /opt
sudo git clone <your-repo-url> frameio
cd frameio
sudo git checkout <production-branch>

# 4. Verify code integrity
sudo git log --oneline -10
sudo git status
```

### Step 7: Rotate All Credentials

```bash
# Generate new Django secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update .env file with new secrets
sudo nano /opt/frameio/.env

# Rotate these:
# - SECRET_KEY (Django)
# - Database passwords
# - API keys (Gemini, Clerk, etc.)
# - JWT signing keys (if custom)
# - Admin passwords
```

**Update in `.env`:**
```bash
# Generate new secret key
SECRET_KEY=<new-secret-key>

# Rotate API keys
GEMINI_API_KEY=<new-key>
CLERK_SECRET_KEY=<new-key>

# Rotate database password
DB_PASSWORD=<new-password>
```

### Step 8: Reinstall Dependencies

```bash
cd /opt/frameio

# Frontend
cd frontend
sudo rm -rf node_modules package-lock.json
sudo npm install --production

# Backend
cd ../backend
sudo source ../venv/bin/activate
sudo pip install --upgrade pip
sudo pip install -r requirements.txt --force-reinstall
```

### Step 9: Deploy Security Fixes

```bash
cd /opt/frameio

# Pull latest security fixes
sudo git pull origin main  # or your production branch

# Rebuild frontend
cd frontend
sudo npm run build

# Restart services
sudo systemctl restart frameio-backend
sudo systemctl restart frameio-frontend

# Check status
sudo systemctl status frameio-backend
sudo systemctl status frameio-frontend
```

## 🛡️ Prevention Measures

### 1. Web Application Firewall (WAF)

**AWS WAF Setup:**
1. Create WAF Web ACL in AWS Console
2. Add rules:
   - AWS Managed Rules: Core rule set
   - AWS Managed Rules: Known bad inputs
   - Rate-based rules
3. Associate with Application Load Balancer or CloudFront

**Or use Cloudflare:**
- Enable Cloudflare WAF
- Configure security rules
- Enable DDoS protection

### 2. Intrusion Detection

**Install fail2ban:**
```bash
sudo apt update
sudo apt install fail2ban

# Configure for SSH and web services
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Enable SSH and HTTP protection
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

**Monitor logs:**
```bash
# Set up log monitoring
sudo apt install logwatch
sudo logwatch --output mail --mailto admin@frameio.co --detail high
```

### 3. Regular Security Audits

**Automated dependency scanning:**
```bash
# Frontend
cd frontend
npm audit
npm audit fix

# Backend
cd backend
pip list --outdated
pip-audit  # Install: pip install pip-audit
```

**Manual security review checklist:**
- [ ] Review all API endpoints for input validation
- [ ] Check for hardcoded secrets
- [ ] Review authentication/authorization logic
- [ ] Check file upload endpoints
- [ ] Review redirect logic
- [ ] Check for SQL injection vulnerabilities
- [ ] Review XSS protection
- [ ] Check CSRF protection

### 4. Keep Dependencies Updated

**Create update script:**
```bash
#!/bin/bash
# update-dependencies.sh

cd /opt/frameio/frontend
npm outdated
npm update

cd ../backend
source ../venv/bin/activate
pip list --outdated
pip install --upgrade -r requirements.txt
```

**Schedule regular updates:**
```bash
# Add to crontab (monthly)
0 0 1 * * /opt/frameio/scripts/update-dependencies.sh
```

### 5. Least Privilege Principles

**Service user setup:**
```bash
# Create dedicated service user
sudo useradd -r -s /bin/false frameio

# Set ownership
sudo chown -R frameio:frameio /opt/frameio

# Update systemd services to use service user
# Edit: /etc/systemd/system/frameio-*.service
# Add: User=frameio
# Add: Group=frameio
```

**File permissions:**
```bash
# Set secure permissions
sudo find /opt/frameio -type f -exec chmod 644 {} \;
sudo find /opt/frameio -type d -exec chmod 755 {} \;
sudo chmod 600 /opt/frameio/.env
```

## 📊 Monitoring and Alerting

### Set up monitoring:

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor system resources
watch -n 1 'ps aux | grep -E "node|python|gunicorn" | head -20'

# Monitor network connections
sudo netstat -tulpn | grep -E "3000|8000"
```

### Log monitoring:

```bash
# Watch application logs
sudo journalctl -u frameio-frontend -f
sudo journalctl -u frameio-backend -f

# Watch nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔍 Incident Response Checklist

When a security incident is detected:

1. ✅ **Isolate** - Disconnect from network or block traffic
2. ✅ **Document** - Take snapshots, save logs
3. ✅ **Contain** - Stop services, kill malicious processes
4. ✅ **Eradicate** - Remove malicious files, check persistence
5. ✅ **Recover** - Rebuild from clean source, rotate credentials
6. ✅ **Harden** - Apply security fixes, implement WAF
7. ✅ **Monitor** - Set up monitoring and alerting
8. ✅ **Review** - Conduct post-incident review

## 📞 Emergency Contacts

- **Security Team**: [Add contact]
- **DevOps Team**: [Add contact]
- **AWS Support**: [Add support plan details]

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Next.js Security Best Practices](https://nextjs.org/docs/going-to-production#security)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)

---

**Last Updated**: $(date)
**Security Review Date**: [Schedule quarterly reviews]

