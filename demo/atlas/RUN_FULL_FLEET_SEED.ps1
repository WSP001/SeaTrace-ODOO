# SeaTrace Full Fleet Demo Seed Script
# Runs seed_demo_full_fleet.py with correct Python environment
# Creates F/V 000 to F/V 137 (138 vessels) for investor demo

Write-Host "🌊 SeaTrace Full Fleet Demo Seed" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if running from correct directory
$expectedPath = "C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO"
$currentPath = Get-Location

if ($currentPath.Path -ne $expectedPath) {
    Write-Host "⚠️  Warning: Not in expected directory" -ForegroundColor Yellow
    Write-Host "Current: $($currentPath.Path)" -ForegroundColor Yellow
    Write-Host "Expected: $expectedPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Changing to correct directory..." -ForegroundColor Yellow
    Set-Location $expectedPath
}

Write-Host "✅ Current directory: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Check for MongoDB connection string
if (-not $env:MONGODB_URI) {
    Write-Host "❌ ERROR: MONGODB_URI environment variable not set" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set your MongoDB Atlas connection string:" -ForegroundColor Yellow
    Write-Host '  $env:MONGODB_URI = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/seatrace_demo"' -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host "✅ MONGODB_URI environment variable found" -ForegroundColor Green
Write-Host "   Connection: $($env:MONGODB_URI.Split('@')[1])" -ForegroundColor Gray
Write-Host ""

# Use Python from SeaTrace-Docker-Migration venv
$pythonPath = "$env:USERPROFILE\CascadeProjects\SeaTrace-Docker-Migration\.venv\Scripts\python.exe"

if (Test-Path $pythonPath) {
    Write-Host "✅ Using Python from: $pythonPath" -ForegroundColor Green
} else {
    Write-Host "⚠️  Python venv not found at: $pythonPath" -ForegroundColor Yellow
    Write-Host "Attempting to use system Python..." -ForegroundColor Yellow
    $pythonPath = "python"
}

Write-Host ""
Write-Host "📊 Fleet Configuration:" -ForegroundColor Cyan
Write-Host "   Total Vessels: 138 (F/V 000-137)" -ForegroundColor White
Write-Host "   Trips per Vessel: 30" -ForegroundColor White
Write-Host "   Total Trips: 4,140" -ForegroundColor White
Write-Host "   Organizations: bluewave, pelagic, northstar" -ForegroundColor White
Write-Host ""

# Confirm before seeding
$response = Read-Host "This will DROP existing collections and reseed. Continue? (y/N)"
if ($response -ne "y" -and $response -ne "Y") {
    Write-Host "❌ Seed cancelled by user" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🚀 Starting full fleet seed..." -ForegroundColor Cyan
Write-Host ""

# Run the seed script
& $pythonPath "demo\atlas\seed_demo_full_fleet.py"

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✅ FULL FLEET SEED COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Start Docker services: docker-compose up -d" -ForegroundColor White
    Write-Host "2. Run EMR simulator: python demo\simulator\emr_simulator.py" -ForegroundColor White
    Write-Host "3. Open Grafana: http://localhost:3000" -ForegroundColor White
    Write-Host "4. Test Postman: Import demo\postman\SeaTrace-INVESTOR.collection.json" -ForegroundColor White
    Write-Host ""
    Write-Host "Demo URL: https://seatrace.worldseafoodproducers.com" -ForegroundColor Cyan
} else {
    Write-Host "❌ Seed failed with exit code: $exitCode" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check MONGODB_URI is correct" -ForegroundColor White
    Write-Host "2. Ensure pymongo is installed: pip install pymongo" -ForegroundColor White
    Write-Host "3. Verify MongoDB Atlas network access allows your IP" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
