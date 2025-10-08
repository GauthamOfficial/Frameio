@echo off
echo 🚀 Frameio Environment File Restoration
echo ================================================

REM Check if .env already exists
if exist .env (
    echo ⚠️  .env file already exists!
    set /p overwrite="Do you want to overwrite it? (y/N): "
    if /i not "%overwrite%"=="y" (
        echo ❌ Operation cancelled.
        pause
        exit /b
    )
)

REM Check if template exists
if not exist env.template (
    echo ❌ Template file 'env.template' not found!
    pause
    exit /b
)

REM Copy template to .env
copy env.template .env
if %errorlevel% equ 0 (
    echo ✅ .env file restored successfully!
    echo 📁 Created: %cd%\.env
    echo.
    echo 📋 Next Steps:
    echo 1. Edit the .env file with your actual API keys
    echo 2. Update database credentials if needed
    echo 3. Configure Clerk authentication keys
    echo 4. Set up AI service API keys (NanoBanana, etc.)
) else (
    echo ❌ Error restoring .env file!
)

echo.
pause
