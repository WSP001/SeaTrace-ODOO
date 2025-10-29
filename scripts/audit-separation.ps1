# 🔍 Repository Separation Audit Script
# For the Commons Good! 🌊
#
# Automated contamination checking for all repos
# Run this monthly or before major releases

param(
    [switch]$Verbose
)

Write-Host "🔍 REPOSITORY SEPARATION AUDIT" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

$auditPassed = $true
$issues = @()

# Define repos to check
$repos = @(
    @{
        Name = "SirJamesAdventures (PERSONAL)"
        Path = "C:\Users\Roberto002\Documents\GitHub\SirJamesAdventures"
        Type = "PERSONAL"
        ExpectedRemote = "https://github.com/WSP001/SirJamesAdventures.git"
        ForbiddenPatterns = @("*seatrace*", "*packet_switching*", "*.pem", "*.key")
    },
    @{
        Name = "SeaTrace-ODOO (PUBLIC)"
        Path = "C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO"
        Type = "PUBLIC"
        ExpectedRemote = "https://github.com/WSP001/SeaTrace-ODOO.git"
        ForbiddenPatterns = @("*.pem", "*.key", "*sirjames*", "*_secret*", "*_private*")
    },
    @{
        Name = "SeaTrace002 (LEGACY PRIVATE)"
        Path = "C:\Users\Roberto002\Documents\GitHub\SeaTrace002"
        Type = "PRIVATE"
        ExpectedRemote = "https://github.com/WSP001/SeaTrace002.git"
        ForbiddenPatterns = @()
    },
    @{
        Name = "SeaTrace003 (ACTIVE PRIVATE)"
        Path = "C:\Users\Roberto002\Documents\GitHub\SeaTrace003"
        Type = "PRIVATE"
        ExpectedRemote = "https://github.com/WSP001/SeaTrace003.git"
        ForbiddenPatterns = @()
    }
)

foreach ($repo in $repos) {
    Write-Host "📁 Checking: $($repo.Name)" -ForegroundColor Yellow
    
    if (-not (Test-Path $repo.Path)) {
        Write-Host "  ❌ Directory not found" -ForegroundColor Red
        $auditPassed = $false
        $issues += "Missing directory: $($repo.Name)"
        continue
    }
    
    Push-Location $repo.Path
    
    # Check git remote
    $remote = git remote get-url origin 2>&1
    if ($remote -ne $repo.ExpectedRemote) {
        Write-Host "  ❌ Wrong remote: $remote" -ForegroundColor Red
        Write-Host "     Expected: $($repo.ExpectedRemote)" -ForegroundColor Gray
        $auditPassed = $false
        $issues += "Wrong remote for $($repo.Name)"
    } else {
        Write-Host "  ✓ Remote correct" -ForegroundColor Green
    }
    
    # Check for forbidden patterns
    if ($repo.ForbiddenPatterns.Count -gt 0) {
        $contamination = @()
        foreach ($pattern in $repo.ForbiddenPatterns) {
            $found = Get-ChildItem -Recurse -Include $pattern -File -ErrorAction SilentlyContinue |
                     Where-Object { $_.FullName -notmatch "node_modules|\.git|venv|__pycache__" } |
                     Select-Object -First 5
            
            if ($found) {
                $contamination += $found
            }
        }
        
        if ($contamination.Count -gt 0) {
            Write-Host "  ❌ Contamination detected:" -ForegroundColor Red
            foreach ($file in $contamination) {
                Write-Host "     - $($file.Name)" -ForegroundColor Red
                if ($Verbose) {
                    Write-Host "       $($file.FullName)" -ForegroundColor Gray
                }
            }
            $auditPassed = $false
            $issues += "Contamination in $($repo.Name): $($contamination.Count) files"
        } else {
            Write-Host "  ✓ No contamination" -ForegroundColor Green
        }
    }
    
    # Check for uncommitted secrets (PUBLIC repos only)
    if ($repo.Type -eq "PUBLIC") {
        $staged = git diff --cached --name-only 2>&1
        if ($staged) {
            $suspiciousFiles = $staged | Where-Object { 
                $_ -match "\.(pem|key|p12|pfx)$" -or 
                $_ -match "_secret|_private|api_key" 
            }
            
            if ($suspiciousFiles) {
                Write-Host "  ⚠️  Suspicious files staged:" -ForegroundColor Yellow
                foreach ($file in $suspiciousFiles) {
                    Write-Host "     - $file" -ForegroundColor Yellow
                }
                $issues += "Suspicious files staged in $($repo.Name)"
            }
        }
    }
    
    # Check for large files
    $largeFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
                  Where-Object { $_.Length -gt 10MB -and $_.FullName -notmatch "\.git|node_modules" } |
                  Select-Object -First 5
    
    if ($largeFiles) {
        Write-Host "  ⚠️  Large files detected (consider Git LFS):" -ForegroundColor Yellow
        foreach ($file in $largeFiles) {
            $sizeMB = [math]::Round($file.Length / 1MB, 2)
            Write-Host "     - $($file.Name) ($sizeMB MB)" -ForegroundColor Yellow
        }
    }
    
    Pop-Location
    Write-Host ""
}

# Summary
Write-Host "==============================" -ForegroundColor Cyan
if ($auditPassed) {
    Write-Host "✅ AUDIT PASSED - ALL CLEAR!" -ForegroundColor Green
    Write-Host ""
    Write-Host "All repositories are properly separated." -ForegroundColor Green
    Write-Host "No contamination detected." -ForegroundColor Green
    Write-Host "No security risks found." -ForegroundColor Green
} else {
    Write-Host "❌ AUDIT FAILED - ISSUES FOUND" -ForegroundColor Red
    Write-Host ""
    Write-Host "Issues detected:" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Please fix these issues before committing or deploying." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "For the Commons Good! 🌊" -ForegroundColor Cyan

# Exit with appropriate code
if ($auditPassed) {
    exit 0
} else {
    exit 1
}
