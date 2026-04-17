set shell := ["powershell", "-NoProfile", "-Command"]

default:
    just help

help:
    @Write-Host 'SeaTrace-ODOO workspace commands'
    @Write-Host '  just orient                 # entrypoint'
    @Write-Host '  just status                 # workspace truth'
    @Write-Host '  just truth                  # show AGENTS + OMX contract'
    @Write-Host '  just business-safety        # business repo caution rules'
    @Write-Host '  just search PATTERN=<text>  # fast repo search'
    @Write-Host '  just lanes                  # lane guide'

orient: status truth business-safety

status:
    @Write-Host '=== SEATRACE-ODOO STATUS ===' -ForegroundColor Cyan
    @Write-Host "Path: $(Get-Location)"
    @if (Test-Path '.git') { git status -sb } else { Write-Host 'NO_GIT_REPO' -ForegroundColor Yellow }
    @Write-Host ''
    @Get-ChildItem -Force | Select-Object -First 40 Name

truth:
    @Write-Host '=== AGENTS ===' -ForegroundColor Cyan
    @Get-Content 'AGENTS.md' -TotalCount 120
    @if (Test-Path '.omx\\README.md') { Write-Host ''; Write-Host '=== OMX ===' -ForegroundColor Cyan; Get-Content '.omx\\README.md' -TotalCount 80 }

business-safety:
    @Write-Host 'Business repo rules:' -ForegroundColor Yellow
    @Write-Host '  - narrow the file scope'
    @Write-Host '  - do not infer secrets or deploy steps'
    @Write-Host '  - prove with live commands only'
    @Write-Host '  - record next owner'

search PATTERN:
    @rg -n "{{PATTERN}}" .

lanes:
    @Write-Host 'Scott / Acting Master -> governance, business truth, next owner'
    @Write-Host 'Frontend lane         -> UI and static shell'
    @Write-Host 'Backend lane          -> integration, services, scripts'
    @Write-Host 'QA lane               -> verification only'
