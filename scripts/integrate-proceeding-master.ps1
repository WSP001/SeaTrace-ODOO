# 🏈 Proceeding Master Integration Script
# For the Commons Good! 🌊
#
# Integrates cryptography and key rotation from SeaTrace002 (Proceeding Master)
# into SeaTrace-ODOO (Public)

param(
    [string]$SourceRepo = "C:\Users\Roberto002\OneDrive\Documents\GitHub\SeaTrace002",
    [string]$TargetRepo = "C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO",
    [switch]$DryRun
)

Write-Host "🏈 PROCEEDING MASTER INTEGRATION" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check source repo exists
if (-not (Test-Path $SourceRepo)) {
    Write-Host "❌ Source repo not found: $SourceRepo" -ForegroundColor Red
    exit 1
}

Write-Host "📊 Source: $SourceRepo" -ForegroundColor Yellow
Write-Host "📊 Target: $TargetRepo" -ForegroundColor Yellow
Write-Host ""

# Step 1: Copy Key Rotation Module
Write-Host "1️⃣ FIRST DOWN - Copy Key Rotation Module" -ForegroundColor Cyan
$sourceKeyRotation = Join-Path $SourceRepo "services\core\security\key_rotation.py"
$targetKeyRotation = Join-Path $TargetRepo "src\security\key_rotation.py"

if (Test-Path $sourceKeyRotation) {
    Write-Host "  ✓ Found key_rotation.py in source" -ForegroundColor Green
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would copy to: $targetKeyRotation" -ForegroundColor Gray
    } else {
        # Create target directory
        $targetDir = Split-Path $targetKeyRotation -Parent
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        # Copy file
        Copy-Item $sourceKeyRotation $targetKeyRotation -Force
        Write-Host "  ✓ Copied to: $targetKeyRotation" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠️  key_rotation.py not found in source" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Update requirements.txt
Write-Host "2️⃣ SECOND DOWN - Update Cryptography Dependencies" -ForegroundColor Cyan
$targetRequirements = Join-Path $TargetRepo "requirements.txt"

$cryptoDeps = @"

# Proceeding Master Cryptography (from SeaTrace002)
cryptography==42.0.2
python-jose[cryptography]>=3.3.0
bcrypt==4.1.2
structlog>=23.2.0
motor>=3.3.2
pymongo[srv]>=4.6.1
"@

if ($DryRun) {
    Write-Host "  [DRY RUN] Would add to requirements.txt:" -ForegroundColor Gray
    Write-Host $cryptoDeps -ForegroundColor Gray
} else {
    Add-Content -Path $targetRequirements -Value $cryptoDeps
    Write-Host "  ✓ Added cryptography dependencies to requirements.txt" -ForegroundColor Green
}

Write-Host ""

# Step 3: Create Packet Security Module
Write-Host "3️⃣ THIRD DOWN - Create Packet Security Module" -ForegroundColor Cyan
$packetSecurityDir = Join-Path $TargetRepo "src\security\packet"

if ($DryRun) {
    Write-Host "  [DRY RUN] Would create: $packetSecurityDir" -ForegroundColor Gray
} else {
    if (-not (Test-Path $packetSecurityDir)) {
        New-Item -ItemType Directory -Path $packetSecurityDir -Force | Out-Null
        Write-Host "  ✓ Created: $packetSecurityDir" -ForegroundColor Green
    } else {
        Write-Host "  ✓ Directory exists: $packetSecurityDir" -ForegroundColor Green
    }
}

Write-Host ""

# Step 4: Summary
Write-Host "🏆 TOUCHDOWN - Integration Summary" -ForegroundColor Green
Write-Host ""
Write-Host "Files Integrated:" -ForegroundColor Yellow
Write-Host "  1. src/security/key_rotation.py (from SeaTrace002)" -ForegroundColor White
Write-Host "  2. requirements.txt (updated with crypto deps)" -ForegroundColor White
Write-Host "  3. src/security/packet/ (directory created)" -ForegroundColor White
Write-Host ""

if ($DryRun) {
    Write-Host "🔍 DRY RUN COMPLETE - No changes made" -ForegroundColor Yellow
    Write-Host "Run without -DryRun to apply changes" -ForegroundColor Yellow
} else {
    Write-Host "✅ INTEGRATION COMPLETE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Review: git status" -ForegroundColor White
    Write-Host "  2. Install: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "  3. Test: python -m pytest tests/" -ForegroundColor White
    Write-Host "  4. Commit: git add . && git commit -m 'feat: Integrate Proceeding Master cryptography'" -ForegroundColor White
}

Write-Host ""
