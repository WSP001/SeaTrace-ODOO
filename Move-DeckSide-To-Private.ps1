# Move-DeckSide-To-Private.ps1
# Purpose: Safely move PRIVATE DeckSide service from SeaTrace-ODOO to SeaTrace003
# Classification: CRITICAL (P0+ - IP Leakage Prevention)
# Date: October 24, 2025
# FOR THE COMMONS GOOD (by protecting investor value)

<#
.SYNOPSIS
    Moves PRIVATE DeckSide microservice to the correct PRIVATE repository.

.DESCRIPTION
    The DeckSide service contains PRIVATE-LIMITED IP including:
    - $CHECK KEY logic (prospectus.py)
    - PUBLIC/PRIVATE fork handler (processor.py)
    - Financial algorithms (models.py)
    - Licensing middleware (middleware.py)
    
    This script:
    1. Copies all DeckSide files to SeaTrace003 (PRIVATE repo)
    2. Verifies the copy succeeded
    3. Lists files ready for git commit
    
    DOES NOT:
    - Delete files from SeaTrace-ODOO (you do that after commit)
    - Run git commands (you review and run manually)
    - Modify any files (just copies)

.EXAMPLE
    .\Move-DeckSide-To-Private.ps1
    
.NOTES
    SAFETY: This script only COPIES files. Original files remain in SeaTrace-ODOO
    until you manually delete them after verifying the PRIVATE repo commit.
#>

param(
    [string]$PublicRepo = "C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO",
    [string]$PrivateRepo = "C:\Users\Roberto002\Documents\GitHub\SeaTrace003"
)

# Colors for output
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

Write-Host "`n🔐 REPO SEPARATION: PHASE 1.1 - Copy DeckSide to PRIVATE Repo" -ForegroundColor $InfoColor
Write-Host "=" * 80 -ForegroundColor $InfoColor

# Step 1: Validate paths
Write-Host "`n📋 Step 1: Validating paths..." -ForegroundColor $InfoColor

if (-not (Test-Path $PublicRepo)) {
    Write-Host "❌ ERROR: PUBLIC repo not found at: $PublicRepo" -ForegroundColor $ErrorColor
    exit 1
}
Write-Host "✅ PUBLIC repo found: $PublicRepo" -ForegroundColor $SuccessColor

if (-not (Test-Path $PrivateRepo)) {
    Write-Host "❌ ERROR: PRIVATE repo not found at: $PrivateRepo" -ForegroundColor $ErrorColor
    Write-Host "   Create SeaTrace003 repo first, then run this script." -ForegroundColor $WarningColor
    exit 1
}
Write-Host "✅ PRIVATE repo found: $PrivateRepo" -ForegroundColor $SuccessColor

# Step 2: Check source directory exists
Write-Host "`n📋 Step 2: Checking source directory..." -ForegroundColor $InfoColor

$SourceDir = Join-Path $PublicRepo "src\services\deckside"
if (-not (Test-Path $SourceDir)) {
    Write-Host "❌ ERROR: DeckSide source not found at: $SourceDir" -ForegroundColor $ErrorColor
    Write-Host "   This may mean the files were already moved." -ForegroundColor $WarningColor
    exit 1
}
Write-Host "✅ Source directory found: $SourceDir" -ForegroundColor $SuccessColor

# Count source files
$SourceFiles = Get-ChildItem $SourceDir -Recurse -File
$SourceFileCount = $SourceFiles.Count
Write-Host "📁 Source files: $SourceFileCount files in DeckSide/" -ForegroundColor $InfoColor

# List key files
Write-Host "`n📄 Key PRIVATE files to copy:" -ForegroundColor $InfoColor
@(
    "prospectus.py",
    "routes.py",
    "processor.py",
    "models.py",
    "middleware.py",
    "test_prospectus.py",
    "test_deckside.py"
) | ForEach-Object {
    $FilePath = Join-Path $SourceDir $_
    if (Test-Path $FilePath) {
        Write-Host "   ✅ $_" -ForegroundColor $SuccessColor
    } else {
        Write-Host "   ⚠️  $_ (not found)" -ForegroundColor $WarningColor
    }
}

# Step 3: Create target directory
Write-Host "`n📋 Step 3: Creating target directory in PRIVATE repo..." -ForegroundColor $InfoColor

$TargetDir = Join-Path $PrivateRepo "src\services\deckside"
if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    Write-Host "✅ Created: $TargetDir" -ForegroundColor $SuccessColor
} else {
    Write-Host "⚠️  Directory already exists: $TargetDir" -ForegroundColor $WarningColor
    Write-Host "   Files will be overwritten." -ForegroundColor $WarningColor
}

# Step 4: Copy DeckSide files
Write-Host "`n📋 Step 4: Copying DeckSide files..." -ForegroundColor $InfoColor

try {
    Copy-Item -Path "$SourceDir\*" -Destination $TargetDir -Recurse -Force
    Write-Host "✅ Copied all DeckSide files to PRIVATE repo" -ForegroundColor $SuccessColor
} catch {
    Write-Host "❌ ERROR: Copy failed: $_" -ForegroundColor $ErrorColor
    exit 1
}

# Step 5: Copy test_prospectus_manual.py from root
Write-Host "`n📋 Step 5: Copying test_prospectus_manual.py..." -ForegroundColor $InfoColor

$SourceTestFile = Join-Path $PublicRepo "test_prospectus_manual.py"
if (Test-Path $SourceTestFile) {
    $TargetTestsDir = Join-Path $PrivateRepo "tests"
    if (-not (Test-Path $TargetTestsDir)) {
        New-Item -ItemType Directory -Path $TargetTestsDir -Force | Out-Null
    }
    
    $TargetTestFile = Join-Path $TargetTestsDir "test_prospectus_manual.py"
    Copy-Item -Path $SourceTestFile -Destination $TargetTestFile -Force
    Write-Host "✅ Copied test_prospectus_manual.py to PRIVATE repo" -ForegroundColor $SuccessColor
} else {
    Write-Host "⚠️  test_prospectus_manual.py not found in root (skipping)" -ForegroundColor $WarningColor
}

# Step 6: Verify copy
Write-Host "`n📋 Step 6: Verifying copy..." -ForegroundColor $InfoColor

$TargetFiles = Get-ChildItem $TargetDir -Recurse -File
$TargetFileCount = $TargetFiles.Count

if ($TargetFileCount -gt 0) {
    Write-Host "✅ Verified: $TargetFileCount files copied to PRIVATE repo" -ForegroundColor $SuccessColor
} else {
    Write-Host "❌ ERROR: No files found in target directory!" -ForegroundColor $ErrorColor
    exit 1
}

# Step 7: Compare file counts
Write-Host "`n📋 Step 7: Comparing file counts..." -ForegroundColor $InfoColor

if ($TargetFileCount -eq $SourceFileCount) {
    Write-Host "✅ File counts match: $SourceFileCount files" -ForegroundColor $SuccessColor
} else {
    Write-Host "⚠️  File count mismatch!" -ForegroundColor $WarningColor
    Write-Host "   Source: $SourceFileCount files" -ForegroundColor $WarningColor
    Write-Host "   Target: $TargetFileCount files" -ForegroundColor $WarningColor
    Write-Host "   Review the copy results before proceeding." -ForegroundColor $WarningColor
}

# Step 8: Display copied files
Write-Host "`n📄 Files copied to PRIVATE repo:" -ForegroundColor $InfoColor
$TargetFiles | ForEach-Object {
    $RelativePath = $_.FullName.Replace($TargetDir + "\", "")
    Write-Host "   - $RelativePath" -ForegroundColor $SuccessColor
}

# Final summary
Write-Host "`n" + ("=" * 80) -ForegroundColor $InfoColor
Write-Host "🎉 PHASE 1.1 COMPLETE: DeckSide copied to PRIVATE repo" -ForegroundColor $SuccessColor
Write-Host ("=" * 80) -ForegroundColor $InfoColor

Write-Host "`n📍 Files are now in:" -ForegroundColor $InfoColor
Write-Host "   $TargetDir" -ForegroundColor $SuccessColor

Write-Host "`n🎯 NEXT STEPS:" -ForegroundColor $WarningColor
Write-Host "   1. Review copied files in: $TargetDir" -ForegroundColor $WarningColor
Write-Host "   2. Change directory: cd $PrivateRepo" -ForegroundColor $WarningColor
Write-Host "   3. Check git status: git status" -ForegroundColor $WarningColor
Write-Host "   4. Stage files: git add src/services/deckside/" -ForegroundColor $WarningColor
Write-Host "   5. Commit: git commit -m 'feat(PRIVATE): Add DeckSide microservice'" -ForegroundColor $WarningColor
Write-Host "   6. Push: git push origin main" -ForegroundColor $WarningColor
Write-Host "   7. THEN delete from PUBLIC repo (see REPO_SEPARATION_ACTION_PLAN.md Phase 1.3)" -ForegroundColor $WarningColor

Write-Host "`n⚠️  IMPORTANT: DO NOT delete from PUBLIC repo until PRIVATE commit is pushed!" -ForegroundColor $ErrorColor
Write-Host "   Original files remain in: $SourceDir" -ForegroundColor $InfoColor

Write-Host "`n🔐 Classification: PRIVATE-LIMITED (Investor Value)" -ForegroundColor $InfoColor
Write-Host "🌊 FOR THE COMMONS GOOD! 🌍🐟🚀" -ForegroundColor $SuccessColor
Write-Host ""
