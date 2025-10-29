# 🧪 MarketSide Manual Test Script
# For the Commons Good! 🌊

Write-Host "🌊 TESTING MARKETSIDE SERVICE (Port 8004)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8004"

# Test 1: Health Check
Write-Host "1️⃣ Testing /health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ Health check passed" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Service: $($response.service)" -ForegroundColor White
    Write-Host "   Version: $($response.version)" -ForegroundColor White
    Write-Host "   DockSide dependency: $($response.dependencies.dockside)" -ForegroundColor White
    Write-Host "   PM Tokens enabled: $($response.features.pm_tokens_enabled)" -ForegroundColor White
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
    Write-Host "   Is the service running? Try: python main.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Publish Listing
Write-Host "2️⃣ Testing /api/v1/publish (listing)..." -ForegroundColor Yellow

$publishListing = @{
    packet_id = "test-001"
    correlation_id = "corr-001"
    publish_type = "listing"
    data = @{
        vessel_id = "WSP-001"
        product = "Tuna"
        weight_kg = 500
        price_per_kg = 15.00
    }
    signature_required = $true
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/publish" -Method POST -Body $publishListing -ContentType "application/json"
    Write-Host "✅ Listing published" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Packet ID: $($response.packet_id)" -ForegroundColor White
    Write-Host "   Signature: $($response.signature.Substring(0, [Math]::Min(20, $response.signature.Length)))..." -ForegroundColor White
} catch {
    Write-Host "❌ Listing publication failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 3: Publish Transaction
Write-Host "3️⃣ Testing /api/v1/publish (transaction)..." -ForegroundColor Yellow

$publishTransaction = @{
    packet_id = "test-002"
    correlation_id = "corr-002"
    publish_type = "transaction"
    data = @{
        buyer = "Restaurant A"
        seller = "WSP-001"
        amount = 7500.00
    }
    signature_required = $true
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/publish" -Method POST -Body $publishTransaction -ContentType "application/json"
    Write-Host "✅ Transaction published" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
} catch {
    Write-Host "❌ Transaction publication failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 4: Verify Valid PM Token
Write-Host "4️⃣ Testing /api/v1/pm/verify (valid token)..." -ForegroundColor Yellow

$validToken = @{
    token = "PM-MARK-2024-004"
    requested_access = "dashboard"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/pm/verify" -Method POST -Body $validToken -ContentType "application/json"
    Write-Host "✅ PM Token verified" -ForegroundColor Green
    Write-Host "   Valid: $($response.valid)" -ForegroundColor White
    Write-Host "   Access Level: $($response.access_level)" -ForegroundColor White
    Write-Host "   Pillar Access: $($response.pillar_access -join ', ')" -ForegroundColor White
    Write-Host "   Dashboard URL: $($response.dashboard_url)" -ForegroundColor White
} catch {
    Write-Host "❌ PM Token verification failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 5: Verify Invalid PM Token
Write-Host "5️⃣ Testing /api/v1/pm/verify (invalid token)..." -ForegroundColor Yellow

$invalidToken = @{
    token = "INVALID-TOKEN-123"
    requested_access = "dashboard"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/pm/verify" -Method POST -Body $invalidToken -ContentType "application/json"
    Write-Host "⚠️  Invalid token was accepted (unexpected)" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✅ Invalid token correctly rejected (401)" -ForegroundColor Green
    } else {
        Write-Host "❌ Unexpected error: $_" -ForegroundColor Red
    }
}

Write-Host ""

# Test 6: List PM Tokens
Write-Host "6️⃣ Testing /api/v1/pm/tokens..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/pm/tokens" -Method GET
    Write-Host "✅ PM Tokens listed" -ForegroundColor Green
    Write-Host "   Total tokens: $($response.tokens.Count)" -ForegroundColor White
    foreach ($token in $response.tokens) {
        Write-Host "   - $($token.token): $($token.access_level)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ PM Token listing failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 7: Issue Certificate
Write-Host "7️⃣ Testing /api/v1/certificate..." -ForegroundColor Yellow

$certificateRequest = @{
    packet_id = "cert-001"
    correlation_id = "corr-cert-001"
    vessel_id = "WSP-001"
    include_full_chain = $true
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/certificate" -Method POST -Body $certificateRequest -ContentType "application/json"
    Write-Host "✅ Certificate issued" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Certificate ID: $($response.certificate_id)" -ForegroundColor White
    Write-Host "   Vessel ID: $($response.vessel_id)" -ForegroundColor White
    Write-Host "   Chain steps: $($response.traceability_chain.Count)" -ForegroundColor White
    Write-Host "   Signature: $($response.signature.Substring(0, [Math]::Min(20, $response.signature.Length)))..." -ForegroundColor White
} catch {
    Write-Host "❌ Certificate issuance failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 8: Market Statistics
Write-Host "8️⃣ Testing /api/v1/stats..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/stats" -Method GET
    Write-Host "✅ Market stats retrieved" -ForegroundColor Green
    Write-Host "   Total transactions: $($response.total_transactions)" -ForegroundColor White
    Write-Host "   Total listings: $($response.total_listings)" -ForegroundColor White
    Write-Host "   Total certificates: $($response.total_certificates)" -ForegroundColor White
} catch {
    Write-Host "❌ Stats retrieval failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 9: Metrics
Write-Host "9️⃣ Testing /metrics endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/metrics" -Method GET
    Write-Host "✅ Metrics endpoint passed" -ForegroundColor Green
    Write-Host "   Total published: $($response.total_published)" -ForegroundColor White
} catch {
    Write-Host "❌ Metrics check failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "🏆 ALL TESTS COMPLETED!" -ForegroundColor Green
Write-Host ""
Write-Host "For the Commons Good! 🌊" -ForegroundColor Cyan
