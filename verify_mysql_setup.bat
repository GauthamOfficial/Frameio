@echo off
REM ============================================================================
REM Frameio MySQL Verification Script for Windows
REM ============================================================================

echo.
echo ======================================================================
echo   Frameio MySQL Setup Verification
echo ======================================================================
echo.

REM Check if virtual environment is activated
python -c "import sys; sys.exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)"
if errorlevel 1 (
    echo [INFO] Activating virtual environment...
    call startup_env\Scripts\activate.bat
    if errorlevel 1 (
        echo [ERROR] Failed to activate virtual environment
        echo Please run: startup_env\Scripts\activate
        pause
        exit /b 1
    )
)

REM Run the verification script
python verify_mysql_setup.py

if errorlevel 1 (
    echo.
    echo [ERROR] Verification failed - please review the errors above
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Verification complete!
pause

