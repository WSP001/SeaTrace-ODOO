# 🧪 DockSide Manual Test Script
# For the Commons Good! 🌊

Write-Host "🌊 TESTING DOCKSIDE SERVICE (Port 8003)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8003"

# Test 1: Health Check
Write-Host "1️⃣ Testing /health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ Health check passed" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Service: $($response.service)" -ForegroundColor White
    Write-Host "   Version: $($response.version)" -ForegroundColor White
    Write-Host "   Storage mode: $($response.storage.mode)" -ForegroundColor White
    Write-Host "   Packet count: $($response.storage.packet_count)" -ForegroundColor White
    Write-Host "   DeckSide dependency: $($response.dependencies.deckside)" -ForegroundColor White
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
    Write-Host "   Is the service running? Try: python main.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Store Valid Packet
Write-Host "2️⃣ Testing /api/v1/store (valid packet)..." -ForegroundColor Yellow

$validPacket = @{
    packet_id = "test-001"
    correlation_id = "corr-001"
    vessel_data = @{
        vessel_id = "WSP-001"
        catch_weight = 500
        species = "Tuna"
        verified = $true
        location = @{
            latitude = 10.5
            longitude = 20.3
        }
    }
    validation_passed = $true
    enriched_data = @{
        validated_at = "2025-10-16T00:00:00Z"
        enrichment_level = "basic"
    }
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/store" -Method POST -Body $validPacket -ContentType "application/json"
    Write-Host "✅ Packet storage passed" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Packet ID: $($response.packet_id)" -ForegroundColor White
    Write-Host "   Storage location: $($response.storage_location)" -ForegroundColor White
    
    $storedPacketId = $response.packet_id
} catch {
    Write-Host "❌ Packet storage failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 3: Retrieve Stored Packet
Write-Host "3️⃣ Testing /api/v1/retrieve/{packet_id}..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/retrieve/$storedPacketId" -Method GET
    Write-Host "✅ Packet retrieval passed" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Found: $($response.found)" -ForegroundColor White
    Write-Host "   Vessel ID: $($response.data.vessel_id)" -ForegroundColor White
    Write-Host "   Species: $($response.data.species)" -ForegroundColor White
} catch {
    Write-Host "❌ Packet retrieval failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Store Another Packet for Query Test
Write-Host "4️⃣ Storing additional packets for query test..." -ForegroundColor Yellow

$packet2 = @{
    packet_id = "test-002"
    correlation_id = "corr-002"
    vessel_data = @{
        vessel_id = "WSP-001"
        catch_weight = 300
        species = "Salmon"
        verified = $true
    }
    validation_passed = $true
} | ConvertTo-Json -Depth 5

try {
    Invoke-RestMethod -Uri "$baseUrl/api/v1/store" -Method POST -Body $packet2 -ContentType "application/json" | Out-Null
    Write-Host "✅ Additional packet stored" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Additional packet storage failed (continuing): $_" -ForegroundColor Yellow
}

Write-Host ""

# Test 5: Query Packets
Write-Host "5️⃣ Testing /api/v1/query..." -ForegroundColor Yellow

$query = @{
    vessel_id = "WSP-001"
    verified_only = $true
    limit = 10
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/query" -Method POST -Body $query -ContentType "application/json"
    Write-Host "✅ Query passed" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Total count: $($response.total_count)" -ForegroundColor White
    Write-Host "   Returned count: $($response.returned_count)" -ForegroundColor White
} catch {
    Write-Host "❌ Query failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 6: Storage Statistics
Write-Host "6️⃣ Testing /api/v1/stats..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/stats" -Method GET
    Write-Host "✅ Stats retrieval passed" -ForegroundColor Green
    Write-Host "   Total packets: $($response.total_packets)" -ForegroundColor White
    Write-Host "   Verified packets: $($response.verified_packets)" -ForegroundColor White
    Write-Host "   Total catch weight: $($response.total_catch_weight) kg" -ForegroundColor White
    Write-Host "   Storage utilization: $($response.storage_utilization)%" -ForegroundColor White
} catch {
    Write-Host "❌ Stats retrieval failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 7: Metrics
Write-Host "7️⃣ Testing /metrics endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/metrics" -Method GET
    Write-Host "✅ Metrics endpoint passed" -ForegroundColor Green
    Write-Host "   Storage mode: $($response.storage_mode)" -ForegroundColor White
    Write-Host "   Total packets: $($response.total_packets)" -ForegroundColor White
} catch {
    Write-Host "❌ Metrics check failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 8: Retrieve Non-existent Packet
Write-Host "8️⃣ Testing /api/v1/retrieve (non-existent)..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/retrieve/nonexistent-id" -Method GET
    if ($response.status -eq "not_found" -and $response.found -eq $false) {
        Write-Host "✅ Non-existent packet correctly handled" -ForegroundColor Green
        Write-Host "   Status: $($response.status)" -ForegroundColor White
        Write-Host "   Found: $($response.found)" -ForegroundColor White
    } else {
        Write-Host "⚠️  Unexpected response for non-existent packet" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Non-existent packet test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "🏆 ALL TESTS COMPLETED!" -ForegroundColor Green
Write-Host ""
Write-Host "For the Commons Good! 🌊" -ForegroundColor Cyan
