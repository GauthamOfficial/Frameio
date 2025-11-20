Write-Host "🧪 Testing Gemini Image Generation Directly..." -ForegroundColor Green
Write-Host ""

$API_BASE_URL = "http://localhost:8000/api/ai"

try {
    # Test 1: Check service status
    Write-Host "1️⃣ Checking AI poster service status..." -ForegroundColor Yellow
    $statusResponse = Invoke-WebRequest -Uri "$API_BASE_URL/ai-poster/status/" -Method GET
    $statusData = $statusResponse.Content | ConvertFrom-Json
    Write-Host "✅ Status check passed" -ForegroundColor Green
    Write-Host "   Service available: $($statusData.service_available)"
    Write-Host "   Message: $($statusData.message)"
    
    # Test 2: Generate a simple poster
    Write-Host ""
    Write-Host "2️⃣ Generating a simple poster..." -ForegroundColor Yellow
    $testData = @{
        prompt = "Simple red circle on white background"
        aspect_ratio = "1:1"
    } | ConvertTo-Json
    
    $startTime = Get-Date
    $generateResponse = Invoke-WebRequest -Uri "$API_BASE_URL/ai-poster/generate_poster/" -Method POST -Body $testData -ContentType "application/json" -TimeoutSec 120
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    $generateData = $generateResponse.Content | ConvertFrom-Json
    Write-Host "✅ Poster generation successful!" -ForegroundColor Green
    Write-Host "⏱️  Generation took $([math]::Round($duration, 2)) seconds"
    Write-Host "   Success: $($generateData.success)"
    Write-Host "   Message: $($generateData.message)"
    Write-Host "   Image path: $($generateData.image_path)"
    Write-Host "   Image URL: $($generateData.image_url)"
    Write-Host "   Filename: $($generateData.filename)"
    
    # Test 3: Generate another poster with different aspect ratio
    Write-Host ""
    Write-Host "3️⃣ Testing different aspect ratio..." -ForegroundColor Yellow
    $testData2 = @{
        prompt = "Modern textile design with geometric patterns"
        aspect_ratio = "4:5"
    } | ConvertTo-Json
    
    $startTime2 = Get-Date
    $generateResponse2 = Invoke-WebRequest -Uri "$API_BASE_URL/ai-poster/generate_poster/" -Method POST -Body $testData2 -ContentType "application/json" -TimeoutSec 120
    $endTime2 = Get-Date
    $duration2 = ($endTime2 - $startTime2).TotalSeconds
    
    $generateData2 = $generateResponse2.Content | ConvertFrom-Json
    Write-Host "✅ Second poster generation successful!" -ForegroundColor Green
    Write-Host "⏱️  Generation took $([math]::Round($duration2, 2)) seconds"
    Write-Host "   Aspect ratio: $($generateData2.aspect_ratio)"
    Write-Host "   Filename: $($generateData2.filename)"
    
    Write-Host ""
    Write-Host "🎉 All Gemini image generation tests passed!" -ForegroundColor Green
    Write-Host "✅ Gemini 2.5 Flash is working correctly for image generation" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "   Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
    exit 1
}
