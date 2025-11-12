# MySQL Migration Guide for Frameio

This guide will help you migrate your Frameio application to use MySQL database.

## Prerequisites

- MySQL 8.0 or higher installed
- Python 3.8+ with virtual environment activated
- Backup of your existing data (if migrating from SQLite/PostgreSQL)

## Quick Setup (Recommended)

### Option 1: Automated Setup Script

Run the Python setup script (easiest method):

```bash
# Make sure you're in the project root directory
python setup_mysql.py
```

This script will:
- Check if MySQL is installed
- Prompt you for MySQL credentials
- Create the database with proper character encoding
- Update your `.env` file with database credentials
- Run Django migrations automatically

### Option 2: Manual Setup Using SQL Script

```bash
# 1. Create the database
mysql -u root -p < setup_mysql.sql

# 2. Update your .env file with database credentials
# See the Environment Configuration section below

# 3. Run migrations
cd backend
python manage.py migrate
```

## Detailed Setup Instructions

### Step 1: Install MySQL

#### Windows
1. Download MySQL Installer from https://dev.mysql.com/downloads/installer/
2. Run the installer and choose "Developer Default"
3. Set a root password during installation (remember this!)
4. Complete the installation and start MySQL service

```powershell
# Verify MySQL is running
net start MySQL80
```

#### macOS
```bash
# Install via Homebrew
brew install mysql@8.0
brew services start mysql@8.0

# Secure your installation
mysql_secure_installation
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
sudo mysql_secure_installation
```

### Step 2: Create MySQL Database

#### Method 1: Using MySQL Command Line
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Verify database
SHOW DATABASES;

# Exit MySQL
EXIT;
```

#### Method 2: Create a Dedicated User (Recommended for Production)
```sql
-- Login to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create dedicated user
CREATE USER 'frameio_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON frameio_db.* TO 'frameio_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SHOW GRANTS FOR 'frameio_user'@'localhost';

EXIT;
```

### Step 3: Configure Environment Variables

Create or update your `.env` file in the project root:

```env
# MySQL Database Configuration
DB_NAME=frameio_db
DB_USER=root                  # or frameio_user if you created a dedicated user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### Step 4: Verify MySQL Client Library

The project already includes `mysqlclient==2.2.7` in `requirements.txt`. 

If you need to reinstall it:

```bash
# Activate virtual environment
startup_env\Scripts\activate  # Windows
# source startup_env/bin/activate  # macOS/Linux

# Install MySQL client
pip install mysqlclient==2.2.7
```

**Note for Windows:** If you encounter issues installing `mysqlclient`, you may need to:
1. Install Microsoft C++ Build Tools
2. Or use the pre-built wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient

### Step 5: Run Migrations

```bash
# Navigate to backend directory
cd backend

# Run migrations to create all tables
python manage.py migrate

# Verify migrations
python manage.py showmigrations
```

### Step 6: Create Superuser (Optional)

```bash
# Create admin user
python manage.py createsuperuser

# Follow the prompts to set username, email, and password
```

## Migrating Existing Data

If you're migrating from SQLite or PostgreSQL and want to keep your data:

### Method 1: Using Django's dumpdata/loaddata

```bash
# 1. Export data from old database (before changing settings)
cd backend
python manage.py dumpdata --natural-foreign --natural-primary \
    --exclude contenttypes --exclude auth.permission \
    --output data_backup.json

# 2. Update settings.py to use MySQL (already done)

# 3. Run migrations on new MySQL database
python manage.py migrate

# 4. Load data into MySQL
python manage.py loaddata data_backup.json
```

### Method 2: Using Database-Specific Tools

#### From SQLite:
```bash
# Install sqlite3-to-mysql (if needed)
pip install sqlite3-to-mysql

# Convert database
sqlite3mysql -f backend/db.sqlite3 -d frameio_db -u root -p
```

#### From PostgreSQL:
Use tools like `pgloader` or export/import via CSV files.

## Testing the Setup

### 1. Test Database Connection
```bash
cd backend
python manage.py shell

# In the Django shell:
from django.db import connection
connection.ensure_connection()
print("✓ Database connection successful!")
exit()
```

### 2. Test Creating a Record
```bash
cd backend
python manage.py shell

# In the Django shell:
from django.contrib.auth import get_user_model
User = get_user_model()
print(f"Total users: {User.objects.count()}")
exit()
```

### 3. Run the Development Server
```bash
# Terminal 1: Backend
cd backend
python manage.py runserver

# Terminal 2: Frontend
cd frontend
npm run dev
```

Visit http://localhost:3000 and test the application functionality.

## MySQL Best Practices for Django

### 1. Character Encoding
Always use `utf8mb4` for full Unicode support (including emojis):
```sql
CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. MySQL Configuration
Add to your MySQL config file (`my.cnf` or `my.ini`):

```ini
[mysqld]
# Character encoding
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# InnoDB settings
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2

# Connection settings
max_connections = 500
max_allowed_packet = 64M

[client]
default-character-set = utf8mb4
```

### 3. Connection Pooling (for production)
Consider using `django-mysql` for additional MySQL-specific features:

```bash
pip install django-mysql
```

Add to `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'django_mysql',
]

DATABASES = {
    'default': {
        # ... your config ...
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

### 4. Regular Backups
```bash
# Backup database
mysqldump -u root -p frameio_db > frameio_backup_$(date +%Y%m%d).sql

# Restore database
mysql -u root -p frameio_db < frameio_backup_20240101.sql
```

## Troubleshooting

### Connection Issues

**Error: "Can't connect to MySQL server"**
```bash
# Check if MySQL is running
# Windows:
net start MySQL80

# macOS/Linux:
brew services list  # macOS
sudo systemctl status mysql  # Linux

# Check MySQL port
mysql -u root -p -e "SHOW VARIABLES LIKE 'port';"
```

**Error: "Access denied for user"**
- Verify username and password in `.env`
- Check user has correct privileges:
```sql
SHOW GRANTS FOR 'your_user'@'localhost';
```

### Migration Issues

**Error: "Unknown collation: 'utf8mb4_0900_ai_ci'"**
- Update MySQL to version 8.0+
- Or change collation to `utf8mb4_unicode_ci`

**Error: "Table already exists"**
```bash
# Reset migrations (CAREFUL: This deletes data)
cd backend
python manage.py migrate --fake-initial
```

### Character Encoding Issues

If you see garbled text:
```sql
-- Check database encoding
SHOW VARIABLES LIKE 'character_set%';
SHOW VARIABLES LIKE 'collation%';

-- Fix existing tables
ALTER DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Performance Issues

**Slow queries:**
```bash
# Enable MySQL slow query log
mysql -u root -p

SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

**Check Django query performance:**
```python
# In Django shell
from django.db import connection
from django.test.utils import override_settings

with override_settings(DEBUG=True):
    # Your queries here
    print(len(connection.queries))
    for query in connection.queries:
        print(query['sql'], query['time'])
```

## Production Deployment

### Cloud MySQL Providers

1. **AWS RDS for MySQL**
   - Managed MySQL with automatic backups
   - Multi-AZ deployment for high availability
   - Easy scaling

2. **Google Cloud SQL for MySQL**
   - Fully managed MySQL database
   - Automatic replication and backups
   - Integration with Google Cloud services

3. **DigitalOcean Managed MySQL**
   - Simple pricing and setup
   - Automatic backups and updates
   - Good for small to medium applications

4. **PlanetScale**
   - Serverless MySQL platform
   - Branch-based development workflow
   - Excellent for modern applications

### Production Environment Variables

```env
# Production MySQL Configuration
DB_NAME=frameio_production
DB_USER=frameio_prod_user
DB_PASSWORD=strong_secure_password_here
DB_HOST=your-mysql-host.example.com
DB_PORT=3306

# SSL Connection (recommended for production)
DB_SSL_CA=/path/to/ca-cert.pem
DB_SSL_CERT=/path/to/client-cert.pem
DB_SSL_KEY=/path/to/client-key.pem
```

Update `settings.py` for SSL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'ssl': {
                'ca': os.getenv('DB_SSL_CA'),
                'cert': os.getenv('DB_SSL_CERT'),
                'key': os.getenv('DB_SSL_KEY'),
            },
        },
    }
}
```

## Support

If you encounter any issues:
1. Check the Django logs: `backend/logs/django.log`
2. Check MySQL error log (location varies by platform)
3. Refer to Django MySQL documentation: https://docs.djangoproject.com/en/stable/ref/databases/#mysql-notes
4. Refer to MySQL documentation: https://dev.mysql.com/doc/

## Summary Checklist

- [ ] MySQL 8.0+ installed and running
- [ ] Database created with utf8mb4 encoding
- [ ] `.env` file updated with MySQL credentials
- [ ] `mysqlclient` library installed
- [ ] Django migrations completed
- [ ] Superuser created (optional)
- [ ] Data migrated (if applicable)
- [ ] Application tested and working
- [ ] Backups configured for production

Congratulations! Your Frameio application is now running on MySQL! 🎉

