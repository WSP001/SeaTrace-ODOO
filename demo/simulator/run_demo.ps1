# EMR Simulator - PowerShell Runner
# Starts the EMR usage simulator for investor demo

Write-Host "🌊 SeaTrace EMR Simulator" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Configuration
$env:EMR_API = "http://localhost:8001"
$env:EMR_TOKEN = "<PASTE_DEMO_TOKEN_HERE>"

# Check for demo token
if ($env:EMR_TOKEN -eq "<PASTE_DEMO_TOKEN_HERE>") {
    Write-Host "⚠️  WARNING: Demo token not configured!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To get a demo token:" -ForegroundColor White
    Write-Host "1. Navigate to SeaTrace-ODOO-Private repository" -ForegroundColor Gray
    Write-Host "2. Run: python demo/scripts/gen_demo_token.py" -ForegroundColor Gray
    Write-Host "3. Copy the token and paste it in this script" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y") {
        exit
    }
}

# Check Python
try {
    python --version | Out-Null
    Write-Host "✅ Python found" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found - please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -q requests pymongo

# Run simulator
Write-Host ""
Write-Host "🚀 Starting EMR simulator..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

python .\demo\simulator\emr_simulator.py
