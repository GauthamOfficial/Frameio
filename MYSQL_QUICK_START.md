# MySQL Quick Start Guide

## 🚀 Super Quick Setup (3 Steps)

### Step 1: Install MySQL (if not already installed)

**Windows:**
```powershell
# Download and run MySQL Installer from:
# https://dev.mysql.com/downloads/installer/

# After installation, start MySQL service:
net start MySQL80
```

**macOS:**
```bash
brew install mysql@8.0
brew services start mysql@8.0
```

**Linux:**
```bash
sudo apt update && sudo apt install mysql-server
sudo systemctl start mysql
```

### Step 2: Run Automated Setup

**Option A: Python Script (Recommended)**
```bash
python setup_mysql.py
```
This will:
- Create the database
- Update your .env file
- Run migrations automatically

**Option B: Windows Batch Script**
```cmd
setup_mysql.bat
```

**Option C: Manual SQL Setup**
```bash
mysql -u root -p < setup_mysql.sql
```
Then manually update your `.env` file with:
```env
DB_NAME=frameio_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### Step 3: Verify Setup

```bash
python verify_mysql_setup.py
# or on Windows:
verify_mysql_setup.bat
```

## ✅ That's It!

If verification passes, start your application:

**Terminal 1 - Backend:**
```bash
startup_env\Scripts\activate  # Windows
# source startup_env/bin/activate  # macOS/Linux
cd backend
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit: http://localhost:3000

---

## 🔧 Troubleshooting

### "Can't connect to MySQL server"
```bash
# Check if MySQL is running
net start MySQL80                    # Windows
brew services list                   # macOS
sudo systemctl status mysql          # Linux
```

### "Access denied"
- Double-check your password in `.env`
- Try resetting MySQL root password

### "Unknown database"
```bash
mysql -u root -p
CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### "Migration errors"
```bash
cd backend
python manage.py migrate --fake-initial
```

---

## 📚 Need More Details?

See the comprehensive [MySQL Migration Guide](MYSQL_MIGRATION_GUIDE.md) for:
- Detailed installation instructions
- Data migration from SQLite/PostgreSQL
- Production deployment
- Performance optimization
- Security best practices

---

## 🆘 Quick Commands Reference

```bash
# Create database manually
mysql -u root -p -e "CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run migrations
cd backend && python manage.py migrate

# Create admin user
cd backend && python manage.py createsuperuser

# Test database connection
cd backend && python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('✓ Connected!')"

# Backup database
mysqldump -u root -p frameio_db > backup.sql

# Restore database
mysql -u root -p frameio_db < backup.sql

# Check MySQL status
mysql -u root -p -e "SELECT VERSION(); SHOW DATABASES;"
```

---

## 📋 Environment Variables

Make sure your `.env` file has these variables:

```env
# MySQL Configuration
DB_NAME=frameio_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Other required variables
SECRET_KEY=your_django_secret_key
GEMINI_API_KEY=your_gemini_api_key
CLERK_PUBLISHABLE_KEY=your_clerk_key
CLERK_SECRET_KEY=your_clerk_secret
```

---

## ✨ What Changed?

### Files Modified:
1. `backend/frameio_backend/settings.py` - Database configuration
2. `env.template` - Environment variables template
3. `README.md` - Updated with MySQL setup instructions

### Files Created:
1. `setup_mysql.sql` - SQL script for database creation
2. `setup_mysql.py` - Automated Python setup script
3. `setup_mysql.bat` - Windows batch setup script
4. `verify_mysql_setup.py` - Verification script
5. `verify_mysql_setup.bat` - Windows verification script
6. `MYSQL_MIGRATION_GUIDE.md` - Comprehensive migration guide
7. `MYSQL_QUICK_START.md` - This quick start guide

---

**Your database is now configured for MySQL! 🎉**

