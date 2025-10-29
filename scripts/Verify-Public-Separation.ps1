#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Verify public/private repo separation for SeaTrace Commons Good contributions

.DESCRIPTION
    Audits SeaTrace-ODOO (PUBLIC) and SeaTrace003 (PRIVATE) to ensure:
    - Sensitive files are NOT in PUBLIC repo
    - Required documentation IS in PUBLIC repo
    - Crypto separation is maintained (verify keys only, no signing keys)

.PARAMETER PublicRepoPath
    Path to SeaTrace-ODOO (PUBLIC) repo

.PARAMETER PrivateRepoPath
    Path to SeaTrace003 (PRIVATE) repo

.EXAMPLE
    .\Verify-Public-Separation.ps1
    
.EXAMPLE
    .\Verify-Public-Separation.ps1 -PublicRepoPath "C:\repos\SeaTrace-ODOO" -PrivateRepoPath "C:\repos\SeaTrace003"

.NOTES
    For the Commons Good! 🌊🏈
    Compatible with Proceeding Master + Acting Master separation plan
#>

Param(
    [Parameter(Mandatory=$false)]
    [string]$PublicRepoPath = "C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO",
    
    [Parameter(Mandatory=$false)]
    [string]$PrivateRepoPath = "C:\Users\Roberto002\Documents\GitHub\SeaTrace003"
)

# Color functions
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warning-Custom { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error-Custom { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Section { param($msg) Write-Host "`n=== $msg ===" -ForegroundColor Cyan -BackgroundColor Black }

# Track results
$script:errors = 0
$script:warnings = 0
$script:successes = 0

#region PUBLIC REPO CHECKS

Write-Section "PUBLIC REPO FILE CHECK (SeaTrace-ODOO)"

if (-not (Test-Path $PublicRepoPath)) {
    Write-Error-Custom "PUBLIC repo not found: $PublicRepoPath"
    exit 1
}

Set-Location $PublicRepoPath
Write-Info "Checking: $PublicRepoPath"

# Required public documentation
$publicFiles = @(
    "DOCUMENTATION_INDEX.md",
    "REAL_WORKING_EXAMPLES.md",
    "VISUAL_WORKFLOW_GUIDE.md",
    "MASTER_TERMINAL_SUMMARY.md",
    "DEVSHELL_QUICKSTART.md",
    "DEVSHELL_ENGINEERING_PLAN.md",
    ".github/copilot-instructions.md",
    "docs/licensing/verify-keys.json",
    "docs/CRYPTO_QUICK_START.md",
    "docs/KEY_MANAGEMENT_ARCHITECTURE.md",
    "docs/PUBLIC_PRIVATE_KEY_DEVELOPMENT_GUIDE.md",
    ".github/CODEOWNERS",
    ".gitignore"
)

Write-Host "`nRequired Public Files:" -ForegroundColor White
foreach ($file in $publicFiles) {
    if (Test-Path $file) {
        Write-Success "FOUND: $file"
        $script:successes++
    } else {
        Write-Warning-Custom "MISSING: $file"
        $script:warnings++
    }
}

# Sensitive files that should NOT exist in PUBLIC
Write-Section "SENSITIVE FILES (MUST NOT EXIST IN PUBLIC)"

$sensitiveFiles = @(
    "docs/licensing/PRIVATE-LIMITED.md",
    "docs/marketing/INVESTOR_PROSPECTUS.md",
    "src/marketside/licensing/entitlements.py",
    "PRIVATE_ENTITLEMENTS_HANDOFF.md",
    ".env",
    ".env.local",
    "secrets/",
    "keys/private/",
    "*.pem",
    "*.key"
)

foreach ($pattern in $sensitiveFiles) {
    $found = Get-ChildItem -Path . -Filter $pattern -Recurse -ErrorAction SilentlyContinue
    if ($found) {
        Write-Error-Custom "REMOVE: $pattern (sensitive file found in PUBLIC repo!)"
        $script:errors++
    } else {
        Write-Success "OK: $pattern not present"
        $script:successes++
    }
}

# Check for SEATRACE_SIGNING_KEY (private key)
Write-Section "CRYPTO KEY SEPARATION CHECK"

$privateKeyPatterns = @(
    "SEATRACE_SIGNING_KEY",
    "SIGNING_KEY",
    "PRIVATE_KEY",
    "-----BEGIN PRIVATE KEY-----"
)

$cryptoViolations = @()

foreach ($pattern in $privateKeyPatterns) {
    $matches = git grep -n $pattern 2>$null
    if ($matches) {
        foreach ($match in $matches) {
            # Exclude comments, documentation examples, and .md files
            if ($match -notmatch "\.md:" -and $match -notmatch "#.*$pattern" -and $match -notmatch "//.*$pattern") {
                $cryptoViolations += $match
            }
        }
    }
}

if ($cryptoViolations.Count -gt 0) {
    Write-Error-Custom "PRIVATE KEY REFERENCES FOUND IN CODE:"
    foreach ($violation in $cryptoViolations) {
        Write-Host "  $violation" -ForegroundColor Red
    }
    $script:errors += $cryptoViolations.Count
} else {
    Write-Success "No private key references in code (documentation examples OK)"
    $script:successes++
}

# Check for verify key (should be present as environment variable)
Write-Host "`nPublic Key (Verify) Configuration:" -ForegroundColor White
$verifyKeyUsage = git grep -n "SEATRACE_VERIFY_KEY" 2>$null
if ($verifyKeyUsage) {
    Write-Success "SEATRACE_VERIFY_KEY referenced (PUBLIC key - OK)"
    $script:successes++
} else {
    Write-Warning-Custom "SEATRACE_VERIFY_KEY not found (may need crypto setup)"
    $script:warnings++
}

# Check git status
Write-Section "GIT STATUS (PUBLIC)"
$gitStatus = git status --short
if ($gitStatus) {
    Write-Warning-Custom "Uncommitted changes detected:"
    git status --short
    $script:warnings++
} else {
    Write-Success "Working tree clean"
    $script:successes++
}

# Check for large files
Write-Section "LARGE FILE CHECK"
$largeFiles = Get-ChildItem -Path . -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.Length -gt 10MB } | 
    Select-Object FullName, @{Name="SizeMB";Expression={[math]::Round($_.Length/1MB, 2)}}

if ($largeFiles) {
    Write-Warning-Custom "Large files found (consider Git LFS):"
    $largeFiles | ForEach-Object { Write-Host "  $($_.FullName) ($($_.SizeMB) MB)" -ForegroundColor Yellow }
    $script:warnings += $largeFiles.Count
} else {
    Write-Success "No large files (>10MB)"
    $script:successes++
}

#endregion

#region PRIVATE REPO CHECKS

Write-Section "PRIVATE REPO CHECK (SeaTrace003)"

if (-not (Test-Path $PrivateRepoPath)) {
    Write-Warning-Custom "PRIVATE repo not found: $PrivateRepoPath (skipping private checks)"
    $script:warnings++
} else {
    Set-Location $PrivateRepoPath
    Write-Info "Checking: $PrivateRepoPath"
    
    # Expected private files
    $privateFiles = @(
        "PRIVATE_ENTITLEMENTS_HANDOFF.md",
        "src/crypto/key_manager.py",
        "src/crypto/hmac_signer.py"
    )
    
    Write-Host "`nExpected Private Files:" -ForegroundColor White
    foreach ($file in $privateFiles) {
        if (Test-Path $file) {
            Write-Success "FOUND: $file"
            $script:successes++
        } else {
            Write-Warning-Custom "MISSING: $file (may need to create)"
            $script:warnings++
        }
    }
    
    # Check git status
    Write-Host "`nGit Status:" -ForegroundColor White
    $privateGitStatus = git status --short
    if ($privateGitStatus) {
        Write-Info "Uncommitted changes in PRIVATE repo:"
        git status --short
    } else {
        Write-Success "Working tree clean"
        $script:successes++
    }
}

#endregion

#region CROSS-REPO VALIDATION

Write-Section "CROSS-REPO VALIDATION"

# Check that .gitignore in PUBLIC blocks PRIVATE repo paths
Set-Location $PublicRepoPath
$gitignoreContent = Get-Content .gitignore -Raw -ErrorAction SilentlyContinue

if ($gitignoreContent -match "SeaTrace003" -or $gitignoreContent -match "proprietary") {
    Write-Success ".gitignore blocks private repo paths"
    $script:successes++
} else {
    Write-Warning-Custom ".gitignore may not block private repo paths"
    $script:warnings++
}

# Check CODEOWNERS for sensitive path protection
$codeownersContent = Get-Content .github/CODEOWNERS -Raw -ErrorAction SilentlyContinue

$sensitivePathsToProtect = @(
    "/docs/licensing/PRIVATE-LIMITED.md",
    "/docs/marketing/INVESTOR_PROSPECTUS.md",
    "/src/marketside/licensing/entitlements.py"
)

$protectedCount = 0
foreach ($path in $sensitivePathsToProtect) {
    if ($codeownersContent -match [regex]::Escape($path)) {
        $protectedCount++
    }
}

if ($protectedCount -eq $sensitivePathsToProtect.Count) {
    Write-Success "CODEOWNERS protects all sensitive paths"
    $script:successes++
} else {
    Write-Warning-Custom "CODEOWNERS may need additional sensitive path guards ($protectedCount/$($sensitivePathsToProtect.Count))"
    $script:warnings++
}

#endregion

#region SUMMARY

Write-Section "SEPARATION AUDIT SUMMARY"

$totalChecks = $script:successes + $script:warnings + $script:errors

Write-Host "`nResults:" -ForegroundColor White
Write-Host "  ✅ Successes: $($script:successes)" -ForegroundColor Green
Write-Host "  ⚠️  Warnings:  $($script:warnings)" -ForegroundColor Yellow
Write-Host "  ❌ Errors:    $($script:errors)" -ForegroundColor Red
Write-Host "  📊 Total:     $totalChecks" -ForegroundColor Cyan

if ($script:errors -eq 0 -and $script:warnings -eq 0) {
    Write-Host "`n🎉 PERFECT SEPARATION! Ready for Commons Good PR! 🌊🏈" -ForegroundColor Green -BackgroundColor Black
    exit 0
} elseif ($script:errors -eq 0) {
    Write-Host "`n⚠️  SEPARATION OK with warnings. Review before PR." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`n❌ SEPARATION VIOLATIONS FOUND! Fix errors before committing to PUBLIC repo!" -ForegroundColor Red -BackgroundColor Black
    exit 1
}

#endregion
