# Profile Saving Tests with Playwright
# This script runs comprehensive tests for the profile saving functionality

Write-Host "🧪 Running Profile Saving Tests with Playwright..." -ForegroundColor Cyan
Write-Host ""

try {
    # Check if Playwright is installed
    Write-Host "📦 Checking Playwright installation..." -ForegroundColor Yellow
    try {
        $playwrightVersion = npx playwright --version 2>$null
        Write-Host "✅ Playwright is installed: $playwrightVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Playwright not found. Installing..." -ForegroundColor Red
        npm install @playwright/test
        npx playwright install
        Write-Host "✅ Playwright installed successfully" -ForegroundColor Green
    }

    # Check if servers are running
    Write-Host "`n🔍 Checking server status..." -ForegroundColor Yellow
    
    # Check frontend server
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ Frontend server is running (http://localhost:3000)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Frontend server is not running. Please start it with: npm run dev" -ForegroundColor Red
        exit 1
    }
    
    # Check backend server
    try {
        $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ Backend server is running (http://localhost:8000)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Backend server is not running. Please start it with: python manage.py runserver 8000" -ForegroundColor Red
        exit 1
    }

    # Run the profile saving tests
    Write-Host "`n🚀 Running profile saving tests..." -ForegroundColor Cyan
    Write-Host "📋 Test Configuration:" -ForegroundColor Yellow
    Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "   - Backend: http://localhost:8000" -ForegroundColor White
    Write-Host "   - Test File: profile-saving.spec.ts" -ForegroundColor White
    Write-Host "   - Config: playwright.config.profile-saving.ts" -ForegroundColor White
    Write-Host ""

    $testCommand = "npx playwright test --config=playwright.config.profile-saving.ts --reporter=html,json"
    
    Write-Host "🔧 Executing: $testCommand" -ForegroundColor Yellow
    Write-Host ""
    
    Invoke-Expression $testCommand
    
    Write-Host "`n✅ Profile saving tests completed successfully!" -ForegroundColor Green
    Write-Host "📊 Check the test-results directory for detailed reports" -ForegroundColor Cyan
    Write-Host "🌐 Open playwright-report/index.html in your browser to view the HTML report" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Test execution failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

