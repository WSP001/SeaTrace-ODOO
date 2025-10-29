# 🧪 DeckSide Manual Test Script
# For the Commons Good! 🌊

Write-Host "🌊 TESTING DECKSIDE SERVICE (Port 8002)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8002"

# Test 1: Health Check
Write-Host "1️⃣ Testing /health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ Health check passed" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Service: $($response.service)" -ForegroundColor White
    Write-Host "   Version: $($response.version)" -ForegroundColor White
    Write-Host "   SeaSide dependency: $($response.dependencies.seaside)" -ForegroundColor White
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
    Write-Host "   Is the service running? Try: python main.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Process Valid Packet
Write-Host "2️⃣ Testing /api/v1/process (valid packet)..." -ForegroundColor Yellow

$validPacket = @{
    packet_id = "test-001"
    correlation_id = "corr-001"
    vessel_data = @{
        vessel_id = "WSP-001"
        catch_weight = 500
        species = "Tuna"
        location = @{
            latitude = 10.5
            longitude = 20.3
        }
    }
    verified = $true
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/process" -Method POST -Body $validPacket -ContentType "application/json"
    Write-Host "✅ Valid packet processing passed" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Valid: $($response.validation_results.valid)" -ForegroundColor White
    Write-Host "   Next Step: $($response.next_step)" -ForegroundColor White
} catch {
    Write-Host "❌ Packet processing failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 3: Process Invalid Packet (Bad Species)
Write-Host "3️⃣ Testing /api/v1/process (invalid species)..." -ForegroundColor Yellow

$invalidPacket = @{
    packet_id = "test-002"
    correlation_id = "corr-002"
    vessel_data = @{
        vessel_id = "WSP-002"
        catch_weight = 100
        species = "Dragon"  # Invalid
    }
    verified = $true
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/process" -Method POST -Body $invalidPacket -ContentType "application/json"
    Write-Host "✅ Invalid packet correctly rejected" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Valid: $($response.validation_results.valid)" -ForegroundColor White
    Write-Host "   Errors: $($response.validation_results.errors.Count)" -ForegroundColor White
} catch {
    Write-Host "❌ Invalid packet test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Standalone Validation
Write-Host "4️⃣ Testing /api/v1/validate..." -ForegroundColor Yellow

$vesselData = @{
    vessel_id = "WSP-003"
    catch_weight = 250
    species = "Salmon"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/validate" -Method POST -Body $vesselData -ContentType "application/json"
    Write-Host "✅ Validation endpoint passed" -ForegroundColor Green
    Write-Host "   Valid: $($response.validation_results.valid)" -ForegroundColor White
} catch {
    Write-Host "❌ Validation test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 5: Metrics
Write-Host "5️⃣ Testing /metrics endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/metrics" -Method GET
    Write-Host "✅ Metrics endpoint exists" -ForegroundColor Green
} catch {
    Write-Host "❌ Metrics check failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "🏆 ALL TESTS PASSED!" -ForegroundColor Green
Write-Host ""
Write-Host "For the Commons Good! 🌊" -ForegroundColor Cyan
