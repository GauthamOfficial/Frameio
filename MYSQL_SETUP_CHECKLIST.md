# ✅ MySQL Setup Checklist

Use this checklist to ensure your MySQL migration is complete and successful.

## Pre-Migration Checklist

- [ ] **Backup existing data** (if migrating from SQLite/PostgreSQL)
  ```bash
  cd backend
  python manage.py dumpdata --natural-foreign --natural-primary \
      --exclude contenttypes --exclude auth.permission \
      --output data_backup.json
  ```

- [ ] **Review current database size and requirements**
- [ ] **Check MySQL system requirements**
  - Minimum: MySQL 8.0+
  - Recommended: 2GB RAM, 10GB disk space

## MySQL Installation

### Windows
- [ ] Download MySQL Installer from https://dev.mysql.com/downloads/installer/
- [ ] Run installer and choose "Developer Default"
- [ ] Set root password (save it securely!)
- [ ] Complete installation
- [ ] Verify MySQL service is running
  ```cmd
  net start MySQL80
  ```

### macOS
- [ ] Install via Homebrew
  ```bash
  brew install mysql@8.0
  ```
- [ ] Start MySQL service
  ```bash
  brew services start mysql@8.0
  ```
- [ ] Run security script
  ```bash
  mysql_secure_installation
  ```

### Linux (Ubuntu/Debian)
- [ ] Update package list
  ```bash
  sudo apt update
  ```
- [ ] Install MySQL
  ```bash
  sudo apt install mysql-server
  ```
- [ ] Start and enable service
  ```bash
  sudo systemctl start mysql
  sudo systemctl enable mysql
  ```
- [ ] Run security script
  ```bash
  sudo mysql_secure_installation
  ```

## Database Setup

### Option A: Automated Setup (Recommended)
- [ ] Run the setup script
  ```bash
  python setup_mysql.py
  ```
  - [ ] Provide MySQL credentials when prompted
  - [ ] Verify database creation success message
  - [ ] Check .env file was updated

### Option B: Manual Setup
- [ ] Login to MySQL
  ```bash
  mysql -u root -p
  ```
- [ ] Create database
  ```sql
  CREATE DATABASE frameio_db 
      CHARACTER SET utf8mb4 
      COLLATE utf8mb4_unicode_ci;
  ```
- [ ] Create dedicated user (optional but recommended)
  ```sql
  CREATE USER 'frameio_user'@'localhost' IDENTIFIED BY 'secure_password';
  GRANT ALL PRIVILEGES ON frameio_db.* TO 'frameio_user'@'localhost';
  FLUSH PRIVILEGES;
  ```
- [ ] Exit MySQL
  ```sql
  EXIT;
  ```

## Environment Configuration

- [ ] Copy environment template
  ```bash
  cp env.template .env
  ```

- [ ] Update .env file with MySQL credentials:
  - [ ] `DB_NAME=frameio_db`
  - [ ] `DB_USER=root` (or your dedicated user)
  - [ ] `DB_PASSWORD=your_mysql_password`
  - [ ] `DB_HOST=localhost`
  - [ ] `DB_PORT=3306`

- [ ] Update other required environment variables:
  - [ ] `SECRET_KEY` (generate new one if needed)
  - [ ] `GEMINI_API_KEY`
  - [ ] `CLERK_PUBLISHABLE_KEY`
  - [ ] `CLERK_SECRET_KEY`
  - [ ] `ARCJET_KEY`

## Django Configuration

- [ ] Verify settings.py uses MySQL configuration
  - [ ] Check `DATABASES['default']['ENGINE']` is `django.db.backends.mysql`
  - [ ] Verify OPTIONS includes utf8mb4 charset
  - [ ] Confirm environment variables are loaded

- [ ] Install/verify MySQL client library
  ```bash
  pip install mysqlclient==2.2.7
  ```

## Database Migrations

- [ ] Activate virtual environment
  ```bash
  startup_env\Scripts\activate  # Windows
  # source startup_env/bin/activate  # macOS/Linux
  ```

- [ ] Navigate to backend directory
  ```bash
  cd backend
  ```

- [ ] Run migrations
  ```bash
  python manage.py migrate
  ```

- [ ] Verify migrations completed successfully
  ```bash
  python manage.py showmigrations
  ```
  All migrations should have [X] next to them

## Data Migration (if applicable)

- [ ] Load backed up data (if you backed up from previous database)
  ```bash
  python manage.py loaddata data_backup.json
  ```

- [ ] Verify data loaded correctly
  ```bash
  python manage.py shell
  ```
  ```python
  from django.contrib.auth import get_user_model
  User = get_user_model()
  print(f"Users: {User.objects.count()}")
  ```

## Create Admin User

- [ ] Create superuser account
  ```bash
  python manage.py createsuperuser
  ```
  - [ ] Enter username
  - [ ] Enter email
  - [ ] Enter password (twice)

## Verification

- [ ] Run verification script
  ```bash
  cd ..  # Back to project root
  python verify_mysql_setup.py
  ```

- [ ] Verify all checks pass:
  - [ ] ✓ Environment Variables
  - [ ] ✓ Database Connection
  - [ ] ✓ Database Configuration
  - [ ] ✓ Migrations
  - [ ] ✓ Model Operations
  - [ ] ✓ JSONField Support
  - [ ] ✓ UUID Field Support
  - [ ] ✓ Database Indexes
  - [ ] ✓ Query Performance

## Application Testing

- [ ] Start backend server
  ```bash
  cd backend
  python manage.py runserver
  ```
  - [ ] Backend starts without errors
  - [ ] Visit http://localhost:8000/admin
  - [ ] Login with superuser credentials
  - [ ] Admin panel loads correctly

- [ ] Start frontend (in new terminal)
  ```bash
  cd frontend
  npm run dev
  ```
  - [ ] Frontend starts without errors
  - [ ] Visit http://localhost:3000
  - [ ] Application loads correctly

## Functional Testing

- [ ] Test user authentication
  - [ ] Login works
  - [ ] User profile loads
  - [ ] Session persists

- [ ] Test organization features
  - [ ] Create organization
  - [ ] View organizations
  - [ ] Edit organization

- [ ] Test AI services
  - [ ] Generate poster
  - [ ] Generate caption
  - [ ] View AI history

- [ ] Test design features
  - [ ] Create design
  - [ ] Upload images
  - [ ] View designs

## Performance Check

- [ ] Check query performance
  - [ ] Pages load quickly (< 2 seconds)
  - [ ] No slow query warnings in logs
  - [ ] Database responds quickly

- [ ] Monitor resource usage
  - [ ] MySQL memory usage acceptable
  - [ ] No connection errors
  - [ ] No timeout errors

## Security Review

- [ ] Verify security settings:
  - [ ] No credentials in code
  - [ ] .env file in .gitignore
  - [ ] Dedicated database user created (not root)
  - [ ] Strong password used
  - [ ] Only necessary permissions granted

- [ ] Production considerations (if deploying):
  - [ ] SSL/TLS connection configured
  - [ ] Firewall rules in place
  - [ ] Backup strategy defined
  - [ ] Monitoring configured

## Backup Strategy

- [ ] Test database backup
  ```bash
  mysqldump -u root -p frameio_db > test_backup.sql
  ```

- [ ] Test database restore
  ```bash
  mysql -u root -p frameio_db_test < test_backup.sql
  ```

- [ ] Set up automated backups (production):
  - [ ] Daily backups scheduled
  - [ ] Backup retention policy defined
  - [ ] Backup storage location secured
  - [ ] Restore procedure documented

## Documentation

- [ ] Review migration guides:
  - [ ] Read MYSQL_QUICK_START.md
  - [ ] Review MYSQL_MIGRATION_GUIDE.md
  - [ ] Understand MYSQL_CONVERSION_SUMMARY.md

- [ ] Document your setup:
  - [ ] Note any custom configurations
  - [ ] Document backup procedures
  - [ ] Record connection details (securely)

## Cleanup

- [ ] Remove old SQLite database (optional)
  ```bash
  # Backup first!
  cp backend/db.sqlite3 backend/db.sqlite3.backup
  # Then remove if you're sure
  # rm backend/db.sqlite3
  ```

- [ ] Remove temporary files
  - [ ] data_backup.json (after verifying migration)
  - [ ] test_backup.sql

## Final Verification

- [ ] All features work as expected
- [ ] No error logs
- [ ] Performance is acceptable
- [ ] Data integrity verified
- [ ] Team members can access (if applicable)
- [ ] Documentation is up to date

## 🎉 Migration Complete!

Once all items are checked, your MySQL migration is complete!

### Quick Reference Commands

```bash
# Start MySQL
net start MySQL80  # Windows
brew services start mysql@8.0  # macOS
sudo systemctl start mysql  # Linux

# Connect to MySQL
mysql -u root -p

# Backup database
mysqldump -u root -p frameio_db > backup_$(date +%Y%m%d).sql

# Restore database
mysql -u root -p frameio_db < backup.sql

# Run migrations
cd backend && python manage.py migrate

# Start application
cd backend && python manage.py runserver  # Terminal 1
cd frontend && npm run dev  # Terminal 2

# Verify setup
python verify_mysql_setup.py
```

### Support Resources

- [MYSQL_QUICK_START.md](MYSQL_QUICK_START.md) - Quick setup guide
- [MYSQL_MIGRATION_GUIDE.md](MYSQL_MIGRATION_GUIDE.md) - Detailed migration guide
- [MYSQL_CONVERSION_SUMMARY.md](MYSQL_CONVERSION_SUMMARY.md) - What changed

### Need Help?

1. Check Django logs: `backend/logs/django.log`
2. Check MySQL error log (location varies by OS)
3. Run verification: `python verify_mysql_setup.py`
4. Review troubleshooting section in MYSQL_MIGRATION_GUIDE.md

---

**Congratulations on completing your MySQL migration! 🚀**

