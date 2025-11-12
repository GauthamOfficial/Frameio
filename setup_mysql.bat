@echo off
REM ============================================================================
REM Frameio MySQL Database Setup Script for Windows
REM ============================================================================

echo.
echo ======================================================================
echo   Frameio MySQL Database Setup
echo ======================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if MySQL is available
mysql --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] MySQL is not installed or not in PATH
    echo Please install MySQL 8.0+ and try again
    echo Download from: https://dev.mysql.com/downloads/installer/
    pause
    exit /b 1
)

echo [OK] Python and MySQL are installed
echo.

REM Check if virtual environment is activated
python -c "import sys; sys.exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)"
if errorlevel 1 (
    echo [WARNING] Virtual environment is not activated
    echo Activating virtual environment...
    call startup_env\Scripts\activate.bat
    if errorlevel 1 (
        echo [ERROR] Failed to activate virtual environment
        echo Please run: startup_env\Scripts\activate
        pause
        exit /b 1
    )
)

echo [OK] Virtual environment is active
echo.

REM Run the Python setup script
echo Running MySQL setup script...
echo.
python setup_mysql.py

if errorlevel 1 (
    echo.
    echo [ERROR] Setup failed
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo   Setup Complete!
echo ======================================================================
echo.
echo Your MySQL database is ready to use!
echo.
echo Next steps:
echo   1. Review your .env file for database configuration
echo   2. Start the backend: cd backend ^&^& python manage.py runserver
echo   3. Start the frontend: cd frontend ^&^& npm run dev
echo.
pause

