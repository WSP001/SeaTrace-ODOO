<# 
  Purpose: Remove DeckSide implementation from PUBLIC repo (SeaTrace-ODOO)
  Usage :  pwsh ./scripts/public/purge_deckside.ps1
  Notes :  Run from repo root. Creates new branch and adds tombstone pointer.
#>

param(
  [string]$DecksidePath = 'src/services/deckside'
)

Write-Host 'Starting DeckSide purge script…' -ForegroundColor Cyan

if (-not (Test-Path '.git')) {
  throw 'Run this script from the SeaTrace-ODOO repo root.'
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw 'git is not available in PATH.'
}

$branch = 'chore/purge-deckside'

Write-Host "Creating branch $branch" -ForegroundColor Yellow
git checkout -b $branch

Write-Host 'Running git-filter-repo (DeckSide removal)…' -ForegroundColor Yellow
$filterArgs = @('--path', $DecksidePath, '--invert-paths')
& git filter-repo @filterArgs

if (-not (Test-Path $DecksidePath)) {
  New-Item -ItemType Directory -Path $DecksidePath | Out-Null
}

'Moved to PRIVATE (SeaTrace003). See scripts/public/purge_deckside.ps1 for instructions.' |
  Set-Content -Path (Join-Path $DecksidePath 'README.md') -Encoding utf8

Write-Host 'Staging tombstone README…' -ForegroundColor Yellow
git add -A

git commit -m 'chore: purge DeckSide history; pointer to PRIVATE repo'

Write-Host 'Purge complete. Review the branch then push:' -ForegroundColor Green
Write-Host "  git push -u origin $branch" -ForegroundColor Green
