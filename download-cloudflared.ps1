# PowerShell script to download Cloudflare Tunnel
Write-Host "📥 Downloading Cloudflare Tunnel for Windows..." -ForegroundColor Green

# Download URL for Windows AMD64
$downloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
$outputPath = "cloudflared.exe"

Write-Host "⏳ Downloading from: $downloadUrl" -ForegroundColor Yellow
Write-Host "📍 Saving to: $outputPath" -ForegroundColor Yellow

try {
    # Download the file
    Invoke-WebRequest -Uri $downloadUrl -OutFile $outputPath -UseBasicParsing
    
    Write-Host "✅ Download completed successfully!" -ForegroundColor Green
    Write-Host "📍 File saved as: $outputPath" -ForegroundColor Cyan
    
    # Check file size
    $fileSize = (Get-Item $outputPath).Length
    Write-Host "📊 File size: $([math]::Round($fileSize/1MB, 2)) MB" -ForegroundColor Cyan
    
    Write-Host "`n🚀 Starting Cloudflare Tunnel..." -ForegroundColor Green
    Write-Host "This will create a public URL for Facebook sharing." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to stop the tunnel.`n" -ForegroundColor Yellow
    
    # Start the tunnel
    & ".\$outputPath" tunnel --url http://localhost:3000
    
} catch {
    Write-Host "❌ Download failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n💡 Manual download:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://github.com/cloudflare/cloudflared/releases" -ForegroundColor White
    Write-Host "2. Download cloudflared-windows-amd64.exe" -ForegroundColor White
    Write-Host "3. Rename to cloudflared.exe" -ForegroundColor White
    Write-Host "4. Run: .\cloudflared.exe tunnel --url http://localhost:3000" -ForegroundColor White
}










