@echo off
REM Quick script to create a test user for development
REM Fixes the "Permission denied" error

echo.
echo ================================================
echo Creating Test User for Development
echo ================================================
echo.

cd backend
python create_test_user.py

echo.
echo ================================================
echo Done!
echo ================================================
echo.
echo If you see "Created test user successfully",
echo you can now use the app without permission errors.
echo.
echo Next steps:
echo 1. Make sure backend is running: python manage.py runserver
echo 2. Go to http://localhost:3000/dashboard/settings
echo 3. Try saving your company profile
echo.

pause




