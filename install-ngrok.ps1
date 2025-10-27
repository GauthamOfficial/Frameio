# Ngrok Installation Script for Windows
Write-Host "🔧 Installing ngrok for Facebook sharing..." -ForegroundColor Green

# Create ngrok directory
$ngrokDir = "$env:USERPROFILE\ngrok"
if (!(Test-Path $ngrokDir)) {
    New-Item -ItemType Directory -Path $ngrokDir -Force
    Write-Host "✅ Created ngrok directory: $ngrokDir" -ForegroundColor Green
}

# Download ngrok
$ngrokUrl = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
$zipFile = "$ngrokDir\ngrok.zip"
$exeFile = "$ngrokDir\ngrok.exe"

Write-Host "📥 Downloading ngrok..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $ngrokUrl -OutFile $zipFile -UseBasicParsing
    Write-Host "✅ Downloaded ngrok successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to download ngrok: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please download manually from: https://ngrok.com/download" -ForegroundColor Yellow
    exit 1
}

# Extract ngrok
Write-Host "📦 Extracting ngrok..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $zipFile -DestinationPath $ngrokDir -Force
    Remove-Item $zipFile -Force
    Write-Host "✅ Extracted ngrok successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to extract ngrok: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test ngrok
if (Test-Path $exeFile) {
    Write-Host "✅ Ngrok installed successfully!" -ForegroundColor Green
    Write-Host "📍 Location: $exeFile" -ForegroundColor Cyan
    
    # Add to PATH for current session
    $env:PATH += ";$ngrokDir"
    
    Write-Host "`n🚀 Starting ngrok..." -ForegroundColor Green
    Write-Host "This will create a public URL for your localhost:3000" -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop ngrok when done testing" -ForegroundColor Yellow
    
    # Start ngrok
    & $exeFile http 3000
} else {
    Write-Host "❌ Ngrok installation failed" -ForegroundColor Red
    Write-Host "Please install manually from: https://ngrok.com/download" -ForegroundColor Yellow
}

