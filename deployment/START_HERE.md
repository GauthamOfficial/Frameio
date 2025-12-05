# 🚀 START HERE - Deployment Guide

## What You Need Before Starting

✅ AWS EC2 instance running (IP: 13.213.53.199)  
✅ SSH access to EC2 (your .pem key file)  
✅ All your API keys ready (Clerk, Gemini, etc.)  
✅ 1-2 hours of time  

---

## Quick Overview: What We're Going to Do

1. **Prepare** your project locally
2. **Connect** to your EC2 server
3. **Upload** your project files
4. **Setup** the server (install software)
5. **Configure** database and environment
6. **Deploy** the application
7. **Test** everything works

---

## 📖 Which Guide Should You Use?

### For First-Time Deployment:
👉 **Use:** `STEP_BY_STEP_DEPLOYMENT.md` (Most Detailed)
- Complete step-by-step instructions
- Explains every command
- Includes troubleshooting
- **Time:** 1-2 hours

### For Quick Reference:
👉 **Use:** `QUICK_START.md` (Condensed)
- Quick commands only
- Assumes you know basics
- **Time:** 30-45 minutes

### For Understanding:
👉 **Use:** `STRUCTURE_EXPLANATION.md`
- Why structure doesn't need changes
- How everything connects

---

## 🎯 Your Next Steps (In Order)

### Step 1: Read the Full Guide
Open and read: `deployment/STEP_BY_STEP_DEPLOYMENT.md`

### Step 2: Prepare Locally
- Generate SECRET_KEY
- Prepare your API keys
- Test project locally (optional)

### Step 3: Connect to EC2
```bash
ssh -i your-key.pem ubuntu@13.213.53.199
```

### Step 4: Follow Phase by Phase
Follow each phase in `STEP_BY_STEP_DEPLOYMENT.md`:
- Phase 1: Preparation ✅
- Phase 2: EC2 Setup
- Phase 3: Upload Files
- Phase 4: Server Setup
- Phase 5: Database
- Phase 6: Environment
- Phase 7: Backend
- Phase 8: Services
- Phase 9: Testing
- ... and so on

---

## ⚡ Quick Command Reference

### Essential Commands You'll Use:

```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@13.213.53.199

# Upload files (from local machine)
scp -r -i your-key.pem . ubuntu@13.213.53.199:/opt/frameio/

# Run setup
cd /opt/frameio/deployment
sudo ./setup.sh

# Activate virtual environment
source /opt/frameio/venv/bin/activate

# Install dependencies
cd /opt/frameio/backend
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start services
sudo systemctl start frameio-backend
sudo systemctl start nginx

# Check status
sudo systemctl status frameio-backend
```

---

## 📋 Pre-Deployment Checklist

Before you start, make sure you have:

- [ ] AWS EC2 instance running
- [ ] SSH key (.pem file)
- [ ] SECRET_KEY generated
- [ ] Database password ready
- [ ] Clerk API keys
- [ ] Gemini API key
- [ ] All other API keys
- [ ] Read `STEP_BY_STEP_DEPLOYMENT.md`

---

## 🆘 Need Help?

1. **Check logs:**
   ```bash
   sudo journalctl -u frameio-backend -n 50
   tail -f /opt/frameio/backend/logs/gunicorn_error.log
   ```

2. **Troubleshooting section:**
   See Phase 13 in `STEP_BY_STEP_DEPLOYMENT.md`

3. **Common issues:**
   - Permission errors → Fix ownership
   - Database errors → Check credentials
   - Service won't start → Check logs
   - 502 errors → Check Gunicorn is running

---

## 🎉 Success Looks Like:

When you're done, you should be able to:

✅ Visit `http://13.213.53.199/api/` and see API response  
✅ Visit `http://13.213.53.199/admin/` and login  
✅ See `sudo systemctl status frameio-backend` shows "active (running)"  
✅ See `sudo systemctl status nginx` shows "active (running)"  

---

## 📚 Documentation Files

- **START_HERE.md** ← You are here
- **STEP_BY_STEP_DEPLOYMENT.md** ← Full detailed guide
- **QUICK_START.md** ← Quick reference
- **README.md** ← Complete documentation
- **STRUCTURE_EXPLANATION.md** ← Why structure is fine
- **DEPLOYMENT_SUMMARY.md** ← What was changed

---

## ⏭️ Ready to Start?

1. Open `deployment/STEP_BY_STEP_DEPLOYMENT.md`
2. Start with Phase 1
3. Follow each step carefully
4. Check off items as you complete them

**Good luck! 🚀**

