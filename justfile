set shell := ["powershell", "-NoProfile", "-Command"]

default:
    just help

help:
    @Write-Host 'SeaTrace-ODOO workspace commands' -ForegroundColor Cyan
    @Write-Host ''
    @Write-Host '  GOVERNANCE' -ForegroundColor Yellow
    @Write-Host '  just orient                 # full entrypoint'
    @Write-Host '  just status                 # workspace truth'
    @Write-Host '  just truth                  # show AGENTS + OMX contract'
    @Write-Host '  just business-safety        # business repo caution rules'
    @Write-Host '  just lanes                  # lane guide'
    @Write-Host '  just search PATTERN=<text>  # fast repo search'
    @Write-Host ''
    @Write-Host '  ENGINEERING PLAYBOOK' -ForegroundColor Yellow
    @Write-Host '  just playbook               # chapter index'
    @Write-Host '  just playbook-ch N           # open chapter N deep dive'
    @Write-Host '  just playbook-next           # all NEXT STEPS across chapters'
    @Write-Host '  just playbook-status         # MSC version + chapter statuses'
    @Write-Host ''
    @Write-Host '  ETL & COSTING' -ForegroundColor Yellow
    @Write-Host '  just etl-cost                # per-pillar cost model'
    @Write-Host '  just etl-map                 # ETL job registry'
    @Write-Host '  just manifest                # show MSC-V008 manifest'
    @Write-Host ''
    @Write-Host '  TWIN-PARALLEL' -ForegroundColor Yellow
    @Write-Host '  just twin-status             # campaign + dashboard status'
    @Write-Host '  just twin-campaign           # external simulation state'
    @Write-Host '  just twin-dashboard          # internal dashboard state'
    @Write-Host ''
    @Write-Host '  SKILLS (Progressive Disclosure)' -ForegroundColor Yellow
    @Write-Host '  just skill-list              # all agent skills'
    @Write-Host '  just skill-read NAME         # read a specific skill'
    @Write-Host '  just skill-lane              # lane-to-skill mapping'
    @Write-Host ''
    @Write-Host '  MSC RUN SEQUENCE' -ForegroundColor Yellow
    @Write-Host '  just run-status              # Run 1/2/3 branch status'
    @Write-Host '  just handoff                 # Acting Master handoff note'

orient: status truth business-safety playbook-status

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

# ═══════════════════════════════════════════════════
# ENGINEERING PLAYBOOK (Recursive Deep-Dive System)
# Question → Plan → Deep Dive → Next Steps → See Also → Follow-up
# ═══════════════════════════════════════════════════

playbook:
    @Write-Host '=== ENGINEERING PLAYBOOK — Chapter Index ===' -ForegroundColor Cyan
    @Write-Host 'MSC-V008 | Twin-Parallel Stack' -ForegroundColor DarkGray
    @Write-Host ''
    @Write-Host ' Ch 1  SeaSide    (HOLD)      STUDY       — vessel tracking, GFW, AIS' -ForegroundColor Green
    @Write-Host ' Ch 2  DeckSide   (RECORD)    STUDY       — digital fish ticket, EMR' -ForegroundColor Green
    @Write-Host ' Ch 3  DockSide   (STORE)     STUDY       — certification, reconciliation' -ForegroundColor Green
    @Write-Host ' Ch 4  MarketSide (EXCHANGE)  STUDY       — QR trace, settlement' -ForegroundColor Green
    @Write-Host ' Ch 5  Auth       (CROSS)     Phase 1.5A  — Zero Trust, JWT, Ed25519' -ForegroundColor Yellow
    @Write-Host ' Ch 6  ETL        (CROSS)     STUDY       — Prometheus, Grafana, cost' -ForegroundColor Green
    @Write-Host ' Ch 7  Licensing  (CROSS)     Phase 1.5A  — #CATCH/$CHECK enforcement' -ForegroundColor Yellow
    @Write-Host ' Ch 8  Campaign   (TWIN)      ACTIVE      — external simulation app' -ForegroundColor Magenta
    @Write-Host ' Ch 9  Dashboard  (TWIN)      SPEC        — internal SEO measurement' -ForegroundColor Magenta
    @Write-Host ''
    @Write-Host 'Run: just playbook-ch <number> to open a chapter' -ForegroundColor DarkGray

playbook-ch N:
    @Write-Host "=== PLAYBOOK Chapter {{N}} ===" -ForegroundColor Cyan
    @$ch = {{N}}; $lines = Get-Content 'ENGINEERING_PLAYBOOK.md' -Raw; $pattern = "## Ch ${ch}:"; $nextPattern = "## Ch $($ch+1):"; if ($ch -eq 9) { $nextPattern = "## Appendix" }; $start = $lines.IndexOf($pattern); $end = $lines.IndexOf($nextPattern); if ($start -ge 0 -and $end -gt $start) { $lines.Substring($start, $end - $start) } elseif ($start -ge 0) { $lines.Substring($start) } else { Write-Host "Chapter $ch not found" -ForegroundColor Red }

playbook-next:
    @Write-Host '=== ALL NEXT STEPS ===' -ForegroundColor Cyan
    @Select-String -Path 'ENGINEERING_PLAYBOOK.md' -Pattern '^\d+\.' -Context 0,0 | Where-Object { $_.LineNumber -gt ((Select-String -Path 'ENGINEERING_PLAYBOOK.md' -Pattern '### 4\. Next Steps' | Select-Object -First 1).LineNumber) } | ForEach-Object { $_.Line }

playbook-status:
    @Write-Host '=== PLAYBOOK STATUS ===' -ForegroundColor Cyan
    @if (Test-Path 'manifests\\MSC-V008-MANIFEST.json') { $m = Get-Content 'manifests\\MSC-V008-MANIFEST.json' | ConvertFrom-Json; Write-Host "MSC Version: $($m.msc_version) | Date: $($m.date) | Status: $($m.status)" -ForegroundColor Green; $m.chapters | ForEach-Object { Write-Host "  Ch $($_.chapter) $($_.pillar) ($($_.stage_verb)) — $($_.status)" } } else { Write-Host 'No manifest found' -ForegroundColor Red }

# ═══════════════════════════════════════════════════
# ETL & COSTING
# ═══════════════════════════════════════════════════

etl-cost:
    @Write-Host '=== PER-PILLAR COST MODEL ===' -ForegroundColor Cyan
    @Write-Host ''
    @Write-Host ' Pillar      Port  Cost Dimensions' -ForegroundColor Yellow
    @Write-Host ' SeaSide     8000  GFW API calls, AIS ingestion rate'
    @Write-Host ' DeckSide    8003  Fish ticket creation rate, EMR sync ops'
    @Write-Host ' DockSide    8004  Certification events, storage I/O'
    @Write-Host ' MarketSide  8002  QR scans, settlement transactions'
    @Write-Host ''
    @Write-Host ' Counter: seatrace_api_cost_units_total{pillar,operation,license_tier}' -ForegroundColor DarkGray

etl-map:
    @Write-Host '=== ETL JOB REGISTRY ===' -ForegroundColor Cyan
    @if (Test-Path 'manifests\\MSC-V008-MANIFEST.json') { $m = Get-Content 'manifests\\MSC-V008-MANIFEST.json' | ConvertFrom-Json; $m.chapters | Where-Object { $_.etl_jobs } | ForEach-Object { Write-Host "  $($_.pillar) ($($_.stage_verb)):" -ForegroundColor Yellow; $_.etl_jobs | ForEach-Object { Write-Host "    - $_" } } } else { Write-Host 'No manifest found' -ForegroundColor Red }

manifest:
    @Write-Host '=== MSC-V008 MANIFEST ===' -ForegroundColor Cyan
    @if (Test-Path 'manifests\\MSC-V008-MANIFEST.json') { Get-Content 'manifests\\MSC-V008-MANIFEST.json' } else { Write-Host 'No manifest found' -ForegroundColor Red }

# ═══════════════════════════════════════════════════
# TWIN-PARALLEL (Campaign + Dashboard)
# ═══════════════════════════════════════════════════

twin-status:
    @Write-Host '=== TWIN-PARALLEL STATUS ===' -ForegroundColor Cyan
    @Write-Host ''
    @Write-Host '  EXTERNAL (Campaign)' -ForegroundColor Magenta
    @$camp = '..\seatrace-campaign'; if (Test-Path $camp) { Write-Host "    Repo: $camp — EXISTS"; if (Test-Path "$camp\netlify.toml") { Write-Host '    Deploy config: netlify.toml FOUND' -ForegroundColor Green } else { Write-Host '    Deploy config: MISSING' -ForegroundColor Red }; if (Test-Path "$camp\content-store.json") { Write-Host '    Spine: content-store.json FOUND' -ForegroundColor Green } } else { Write-Host "    Repo: NOT FOUND at $camp" -ForegroundColor Red }
    @Write-Host ''
    @Write-Host '  INTERNAL (Dashboard)' -ForegroundColor Magenta
    @$dash = '..\seatrace-campaign-dashboard'; if (Test-Path $dash) { Write-Host "    Repo: $dash — EXISTS"; Get-ChildItem $dash | Select-Object -First 15 Name } else { Write-Host "    Repo: SPEC ONLY (not yet created)" -ForegroundColor Yellow }

twin-campaign:
    @Write-Host '=== EXTERNAL SIMULATION (Campaign) ===' -ForegroundColor Magenta
    @$camp = '..\seatrace-campaign'; if (Test-Path $camp) { Push-Location $camp; if (Test-Path '.git') { git status -sb }; Write-Host ''; Get-ChildItem | Select-Object Name, Length; Pop-Location } else { Write-Host 'Campaign repo not found' -ForegroundColor Red }

twin-dashboard:
    @Write-Host '=== INTERNAL DASHBOARD ===' -ForegroundColor Magenta
    @$dash = '..\seatrace-campaign-dashboard'; if (Test-Path $dash) { Push-Location $dash; Get-ChildItem | Select-Object Name, Length; Pop-Location } else { Write-Host 'Dashboard not yet created (SPEC in ENGINEERING_PLAYBOOK.md Ch 9)' -ForegroundColor Yellow; Write-Host 'Create with: just playbook-ch 9' -ForegroundColor DarkGray }

# ═══════════════════════════════════════════════════
# SKILLS (Progressive Disclosure, Per-Pillar Agents)
# agent → justfile → skill → proof → next disclosure
# ═══════════════════════════════════════════════════

skill-list:
    @Write-Host '=== AGENT SKILLS (Progressive Disclosure) ===' -ForegroundColor Cyan
    @Write-Host ''
    @Get-ChildItem 'skills' -Directory | ForEach-Object { $skill = $_.Name; $md = Join-Path $_.FullName 'SKILL.md'; if (Test-Path $md) { $first = (Get-Content $md | Select-String '> \*\*Role:\*\*' | Select-Object -First 1).Line; Write-Host "  $skill" -ForegroundColor Yellow -NoNewline; Write-Host "  $first" } else { Write-Host "  $skill — NO SKILL.md" -ForegroundColor Red } }

skill-read NAME:
    @Write-Host "=== SKILL: {{NAME}} ===" -ForegroundColor Cyan
    @$path = "skills\\{{NAME}}\\SKILL.md"; if (Test-Path $path) { Get-Content $path } else { Write-Host "Skill not found: {{NAME}}" -ForegroundColor Red; Write-Host 'Available:'; Get-ChildItem 'skills' -Directory | ForEach-Object { Write-Host "  $($_.Name)" } }

skill-lane:
    @Write-Host '=== LANE → SKILL MAPPING ===' -ForegroundColor Cyan
    @Write-Host ''
    @Write-Host '  Claude Code      → seatrace-seaside-agent   (Run 1, SeaSide HOLD)' -ForegroundColor Green
    @Write-Host '  Codex-1          → seatrace-deckside-agent  (Run 1, DeckSide RECORD)' -ForegroundColor Green
    @Write-Host '  Codex-2          → seatrace-dockside-agent  (Run 2, DockSide STORE)' -ForegroundColor Yellow
    @Write-Host '  Cascade/Evidence → seatrace-marketside-agent (Run 3, MarketSide EXCHANGE)' -ForegroundColor Yellow
    @Write-Host '  All agents       → seatrace-justfile-agent  (root governance)' -ForegroundColor Cyan
    @Write-Host ''
    @Write-Host '  Run: just skill-read <skill-name> to open' -ForegroundColor DarkGray

# ═══════════════════════════════════════════════════
# MSC RUN SEQUENCE
# ═══════════════════════════════════════════════════

run-status:
    @Write-Host '=== MSC RUN SEQUENCE STATUS ===' -ForegroundColor Cyan
    @Write-Host ''
    @Write-Host '  Run 1: SeaSide + DeckSide' -ForegroundColor Yellow
    @$r1 = git branch --list 'feat/msc-incoming-run1' 2>$null; if ($r1) { Write-Host "    Branch: feat/msc-incoming-run1 EXISTS" -ForegroundColor Green } else { Write-Host "    Branch: NOT CREATED (blocked: Owner §0)" -ForegroundColor Red }
    @Write-Host ''
    @Write-Host '  Run 2: DockSide' -ForegroundColor Yellow
    @$r2 = git branch --list 'feat/msc-incoming-run2' 2>$null; if ($r2) { Write-Host "    Branch: feat/msc-incoming-run2 EXISTS" -ForegroundColor Green } else { Write-Host "    Branch: NOT CREATED (blocked: Run 1 PASS)" -ForegroundColor Red }
    @Write-Host ''
    @Write-Host '  Run 3: MarketSide' -ForegroundColor Yellow
    @$r3 = git branch --list 'feat/msc-incoming-run3' 2>$null; if ($r3) { Write-Host "    Branch: feat/msc-incoming-run3 EXISTS" -ForegroundColor Green } else { Write-Host "    Branch: NOT CREATED (blocked: Run 2 PASS)" -ForegroundColor Red }

handoff:
    @Write-Host '=== ACTING MASTER HANDOFF ===' -ForegroundColor Cyan
    @if (Test-Path 'ACTING_MASTER_HANDOFF_MSC-V008.md') { Get-Content 'ACTING_MASTER_HANDOFF_MSC-V008.md' } else { Write-Host 'No handoff note found' -ForegroundColor Red }
