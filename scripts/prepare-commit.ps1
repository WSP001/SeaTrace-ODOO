# 🏈 SeaTrace Commit Preparation Script
# For the Commons Good! 🌊

param(
    [string]$Message = "feat: Add 4-pillar architecture with monitoring",
    [switch]$DryRun
)

Write-Host "🏈 PREPARING COMMIT TO MASTER REPO" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Change to repo directory
$RepoPath = "C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO"
Set-Location $RepoPath

# Check git status
Write-Host "📊 Current Status:" -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "📋 Files to Add:" -ForegroundColor Yellow
Write-Host "  ✓ Makefile" -ForegroundColor Green
Write-Host "  ✓ templates/fastapi_pillar/app.py.tmpl" -ForegroundColor Green
Write-Host "  ✓ scripts/scaffold.py" -ForegroundColor Green
Write-Host "  ✓ scripts/redzone.sh" -ForegroundColor Green
Write-Host "  ✓ tests/test_health_metrics.py" -ForegroundColor Green
Write-Host "  ✓ services/common/ratelimit.py" -ForegroundColor Green
Write-Host "  ✓ src/seaside.py" -ForegroundColor Green
Write-Host "  ✓ src/deckside.py" -ForegroundColor Green
Write-Host "  ✓ src/dockside.py" -ForegroundColor Green
Write-Host "  ✓ src/marketside.py" -ForegroundColor Green
Write-Host "  ✓ services/*/Dockerfile" -ForegroundColor Green
Write-Host "  ✓ docker-compose.yml" -ForegroundColor Green
Write-Host "  ✓ infra/nginx/nginx.conf" -ForegroundColor Green
Write-Host "  ✓ infra/prometheus/prometheus.yml" -ForegroundColor Green
Write-Host ""

if ($DryRun) {
    Write-Host "🔍 DRY RUN - No changes will be made" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands that would run:" -ForegroundColor Yellow
    Write-Host "  git add Makefile" -ForegroundColor Gray
    Write-Host "  git add templates/" -ForegroundColor Gray
    Write-Host "  git add scripts/" -ForegroundColor Gray
    Write-Host "  git add tests/" -ForegroundColor Gray
    Write-Host "  git add services/" -ForegroundColor Gray
    Write-Host "  git add src/" -ForegroundColor Gray
    Write-Host "  git add infra/" -ForegroundColor Gray
    Write-Host "  git add docker-compose.yml" -ForegroundColor Gray
    Write-Host "  git commit -m '$Message'" -ForegroundColor Gray
    exit 0
}

# Confirm
Write-Host "⚠️  Ready to stage and commit?" -ForegroundColor Yellow
$Confirm = Read-Host "Type 'yes' to continue"

if ($Confirm -ne "yes") {
    Write-Host "❌ Aborted" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Staging files..." -ForegroundColor Cyan

# Stage files
git add Makefile
git add templates/
git add scripts/
git add tests/
git add services/
git add src/
git add infra/
git add docker-compose.yml
git add .env.dev

Write-Host "✅ Files staged" -ForegroundColor Green
Write-Host ""

# Show what will be committed
Write-Host "📝 Changes to be committed:" -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "💾 Creating commit..." -ForegroundColor Cyan

# Commit
git commit -m "$Message"

Write-Host ""
Write-Host "🏆 COMMIT READY!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review: git log -1 --stat" -ForegroundColor White
Write-Host "  2. Push: git push origin main" -ForegroundColor White
Write-Host "  3. Test: make smoke" -ForegroundColor White
Write-Host ""
