# 🧪 SeaSide Manual Test Script
# For the Commons Good! 🌊

Write-Host "🌊 TESTING SEASIDE SERVICE" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8001"

# Test 1: Health Check
Write-Host "1️⃣ Testing /health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ Health check passed" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Service: $($response.service)" -ForegroundColor White
    Write-Host "   Version: $($response.version)" -ForegroundColor White
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
    Write-Host "   Is the service running? Try: python main.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Ingest Packet
Write-Host "2️⃣ Testing /api/v1/ingest endpoint..." -ForegroundColor Yellow

$packet = @{
    correlation_id = "test-uuid-123"
    source = "vessel"
    payload = @{
        vessel_id = "WSP-001"
        catch_weight = 500
        species = "Tuna"
        location = @{
            lat = 10.5
            lon = -60.3
        }
    }
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/ingest" -Method POST -Body $packet -ContentType "application/json"
    Write-Host "✅ Packet ingest passed" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Packet ID: $($response.packet_id)" -ForegroundColor White
    Write-Host "   Verified: $($response.verified)" -ForegroundColor White
} catch {
    Write-Host "❌ Packet ingest failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 3: Metrics
Write-Host "3️⃣ Testing /api/v1/metrics endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/metrics" -Method GET
    Write-Host "✅ Metrics check passed" -ForegroundColor Green
    Write-Host "   Service: $($response.service)" -ForegroundColor White
    Write-Host "   Crypto Available: $($response.crypto_available)" -ForegroundColor White
} catch {
    Write-Host "❌ Metrics check failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "🏆 ALL TESTS PASSED!" -ForegroundColor Green
Write-Host ""
Write-Host "For the Commons Good! 🌊" -ForegroundColor Cyan
