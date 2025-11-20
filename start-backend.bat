@echo off
echo ========================================
echo Starting Framio Backend Server
echo ========================================
echo.

cd backend

echo Checking database connection...
python -c "import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings'); django.setup(); from django.db import connection; connection.ensure_connection(); print('✅ Database connected')"

if errorlevel 1 (
    echo ❌ Database connection failed!
    echo Please check your MySQL database is running and configured in .env
    pause
    exit /b 1
)

echo.
echo Checking for pending migrations...
python manage.py showmigrations --plan | find "[ ]" > nul
if not errorlevel 1 (
    echo ⚠️  Pending migrations found. Running migrations...
    python manage.py migrate
) else (
    echo ✅ All migrations applied
)

echo.
echo Checking test user...
python -c "import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings'); django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.filter(email='test@example.com').first(); print(f'✅ Test user: {user.email}' if user else '⚠️  No test user found')"

echo.
echo ========================================
echo Starting Django development server...
echo ========================================
echo.
echo Server will be available at: http://localhost:8000
echo Admin panel: http://localhost:8000/admin/
echo API docs: http://localhost:8000/api/docs/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver







