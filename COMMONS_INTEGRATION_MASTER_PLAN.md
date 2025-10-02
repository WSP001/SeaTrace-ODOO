# 🌊 COMMONS WORKFLOW + ACTING MASTER INTEGRATION PLAN

**Created:** October 2, 2025  
**Purpose:** Integrate Commons Good workflow with Acting Master ETL discovery  
**Status:** ✅ READY FOR EXECUTION

---

## 📊 EXECUTIVE SUMMARY

This plan integrates:
1. **Commons Charter governance** (SeaTrace-ODOO PUBLIC repo)
2. **Acting Master ETL discovery** (project inventory and automation)
3. **DevShell.ps1 workflow** (context switching and project management)

**Goal:** Create a unified workflow where Commons documentation, agent configurations, and project boundaries work together seamlessly.

---

## 🎯 THE INTEGRATION CHALLENGE

### What We Have Now
✅ **Commons Charter** - Governance for FREE pillars (SeaSide, DeckSide, DockSide)  
✅ **Acting Master Discovery** - Complete project inventory (3 repos, 650-line DevShell)  
✅ **DevShell.ps1** - Working context switching system  
✅ **Copilot Instructions** - PUBLIC/PRIVATE repo boundaries  

### What We Need
❌ Agent config files (CODE.AGENT.md, TOOL.AGENT.md) in Commons context  
❌ .gitignore files that respect Commons boundaries  
❌ Integration between Commons workflow and DevShell automation  
❌ Clear ETL patterns for Commons-specific data  

---

## 🔄 INTEGRATION PHASES

### PHASE 1: SECURITY FOUNDATION (15 minutes)
**Goal:** Protect Commons Charter and PUBLIC/PRIVATE boundaries

#### Task 1.1: Create .gitignore for SeaTrace-ODOO (Commons/PUBLIC)
```powershell
# Step 1: Switch to PUBLIC Commons repo
cd-seatrace-prod

# Step 2: Verify context
Write-Host "`n📍 Current Location:" -ForegroundColor Cyan
Get-Location
project-context

# Step 3: Check if .gitignore exists
if (Test-Path .gitignore) {
    Write-Host "`n✅ .gitignore already exists" -ForegroundColor Green
    Get-Content .gitignore | Select-Object -First 20
} else {
    Write-Host "`n🔧 Creating Commons-aware .gitignore..." -ForegroundColor Yellow
    
    # Create .gitignore with Commons boundaries
    @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/

# Virtual environments
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment variables
.env
.env.local
.env.*.local

# COMMONS CHARTER PROTECTION
# ❌ NEVER commit private keys (Commons uses public verification only)
keys/private/**
*.key
*.pem
*.p12
*.pfx
*secret*
*credential*
*password*

# ❌ NEVER commit LIMITED/PRIVATE content (belongs in SeaTrace003)
*pricing*
*emr*
*enterprise*
*investor*
*limited*
*private*
src/marketside/**
docs/licensing/PRIVATE-LIMITED.md

# ✅ ALLOWED: Commons Charter, PUL, public routes
# docs/COMMONS_CHARTER.md          ← COMMIT THIS
# docs/licensing/PUBLIC-UNLIMITED.md  ← COMMIT THIS
# src/common/licensing/commons.py     ← COMMIT THIS

# Database
*.db
*.sqlite
*.sqlite3

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Documentation builds
docs/_build/
site/

# Temporary
*.tmp
*.bak
.cache/
"@ | Out-File -FilePath .gitignore -Encoding UTF8

    Write-Host "`n✅ .gitignore created with Commons boundaries!" -ForegroundColor Green
    
    # Show what was created
    Write-Host "`n📄 File preview:" -ForegroundColor Cyan
    Get-Content .gitignore | Select-Object -First 30
    
    # Stage and commit
    git add .gitignore
    git commit -m "security: Add .gitignore with Commons Charter boundaries"
    git push origin main
    
    Write-Host "`n✅ TASK 1.1 COMPLETE!" -ForegroundColor Green
}

# Return to Sir James
cd-sirjames
```

#### Task 1.2: Create .gitignore for SeaTrace003 (PRIVATE)
```powershell
# Switch to PRIVATE repo
cd-seatrace003

# Verify context
Write-Host "`n🔒 Switched to PRIVATE repo" -ForegroundColor Yellow
project-context

# Create .gitignore for PRIVATE repo
if (-not (Test-Path .gitignore)) {
    @"
# Python
__pycache__/
*.py[cod]
*.so
build/
dist/
*.egg-info/

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# PRIVATE REPO PROTECTION
# ❌ CRITICAL: Private keys, credentials
keys/private/**
*.key
*.pem
*secret*
*credential*
*password*

# ❌ CRITICAL: Environment files
.env
.env.*
!.env.example

# ❌ CRITICAL: Confidential data
*pricing*
*investor*
*financial*
customer_data/
emr_data/

# Database
*.db
*.sqlite
dump.rdb

# Testing
.pytest_cache/
.coverage

# Temporary
*.tmp
*.bak
"@ | Out-File -FilePath .gitignore -Encoding UTF8

    git add .gitignore
    git commit -m "security: Add .gitignore for PRIVATE repo"
    git push origin main
    
    Write-Host "`n✅ TASK 1.2 COMPLETE!" -ForegroundColor Green
}

# Return to Sir James
cd-sirjames
```

#### Task 1.3: Create .gitignore for SirJamesAdventures
```powershell
# Navigate to Sir James GitHub repo
cd C:\Users\Roberto002\Documents\GitHub\SirJamesAdventures

# Verify location
Get-Location
git remote get-url origin

# Create Swift/iOS .gitignore
if (-not (Test-Path .gitignore)) {
    @"
# Xcode
build/
*.pbxuser
xcuserdata/
*.xcworkspace
!default.xcworkspace
DerivedData/

# Swift Package Manager
.build/
Packages/

# CocoaPods
Pods/

# macOS
.DS_Store
._*

# IDE
.vscode/
.idea/

# Environment
.env

# Secrets
*.key
*secret*

# App data
*.sqlite

# Logs
*.log
"@ | Out-File -FilePath .gitignore -Encoding UTF8

    git add .gitignore
    git commit -m "chore: Add Swift/iOS .gitignore"
    git push origin main
    
    Write-Host "`n✅ TASK 1.3 COMPLETE!" -ForegroundColor Green
}

# Return to Sir James OneDrive
cd-sirjames
```

**✅ Phase 1 Checkpoint:**
- .gitignore protects Commons Charter in PUBLIC repo
- .gitignore protects confidential data in PRIVATE repo
- .gitignore prevents Xcode clutter in Sir James repo

---

### PHASE 2: AGENT CONFIGURATION (30 minutes)
**Goal:** Create CODE.AGENT.md and TOOL.AGENT.md with Commons awareness

#### Task 2.1: CODE.AGENT.md for SeaTrace-ODOO (Commons/PUBLIC)
```powershell
# Switch to PUBLIC Commons repo
cd-seatrace-prod

# Create CODE.AGENT.md
@"
# CODE.AGENT.md - SeaTrace-ODOO (PUBLIC Commons Repository)

**Last Updated:** $(Get-Date -Format 'yyyy-MM-dd')  
**Project:** SeaTrace Maritime Tracking Platform  
**Type:** PUBLIC COMMONS (Free Forever)  
**Governance:** Commons Charter  
**License:** PUL (Public Unlimited License)

---

## 🌊 COMMONS CHARTER IDENTITY

### Mission
Keep **SeaSide, DeckSide, and DockSide FREE** as a public good for the global seafood supply chain.

### Four Pillars Architecture

| Pillar | Status | Repository |
|--------|--------|------------|
| **SeaSide (HOLD)** | ✅ FREE | THIS REPO |
| **DeckSide (RECORD)** | ✅ FREE | THIS REPO |
| **DockSide (STORE)** | ✅ FREE | THIS REPO |
| **MarketSide (EXCHANGE)** | 💰 PAID | SeaTrace003 (PRIVATE) |

---

## 💻 LANGUAGE & FRAMEWORK

### Primary Stack
- **Language:** Python 3.11+
- **Framework:** FastAPI (microservices) OR ODOO 19.0+ (monolith)
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy OR ODOO ORM
- **API:** RESTful

### Coding Standards
- **Style Guide:** PEP 8
- **Formatting:** black (line length: 88)
- **Type Hints:** Required for all functions
- **Docstrings:** Google style
- **Linting:** pylint + mypy (strict mode)

---

## 🔒 COMMONS SECURITY RULES

### ❌ NEVER COMMIT TO THIS REPO
- Private keys (*.key, *.pem)
- API credentials
- .env files with secrets
- **MarketSide code** (that's PRIVATE repo)
- **Pricing algorithms**
- **EMR metering logic**
- **Investor documentation**
- **Enterprise features**

### ✅ ALLOWED IN THIS REPO
- Commons Charter documentation
- PUL (Public Unlimited License) implementation
- Public API routes for SeaSide, DeckSide, DockSide
- License verification middleware (public keys only)
- Integration guides
- Public scope digest

---

## 🏗️ ARCHITECTURE PATTERNS

### Commons Pillar Pattern
\`\`\`python
# src/common/licensing/commons.py

from typing import Dict, Optional
from datetime import datetime

class CommonsPillar:
    \"\"\"Base class for Commons-governed pillars.
    
    All SeaSide, DeckSide, and DockSide services inherit this.
    Ensures FREE access under PUL.
    \"\"\"
    
    pillar_name: str  # "SeaSide", "DeckSide", or "DockSide"
    is_commons: bool = True
    requires_payment: bool = False
    
    async def verify_access(self, token: str) -> Dict[str, any]:
        \"\"\"Verify PUL token for Commons access.
        
        Args:
            token: Signed JWT token with PUL claims
            
        Returns:
            {
                'allowed': True,
                'pillar': self.pillar_name,
                'license': 'PUBLIC_UNLIMITED',
                'expires': None  # Commons never expires
            }
        \"\"\"
        # Implementation uses public key verification only
        pass
\`\`\`

### API Route Pattern (Commons)
\`\`\`python
# src/common/licensing/routes.py

from fastapi import APIRouter, Depends
from .commons import verify_pul_license

router = APIRouter(prefix="/commons", tags=["Commons"])

@router.get("/verify")
async def verify_commons_access(token: str = Depends(verify_pul_license)):
    \"\"\"PUBLIC endpoint for PUL license verification.
    
    This endpoint is FREE and always will be.
    Used by SeaSide, DeckSide, DockSide pillars.
    \"\"\"
    return {
        "status": "ok",
        "license": "PUBLIC_UNLIMITED",
        "pillars": ["SeaSide", "DeckSide", "DockSide"],
        "expires": None
    }

# ❌ DON'T add MarketSide endpoints here - wrong repo!
# MarketSide belongs in SeaTrace003 (PRIVATE)
\`\`\`

---

## 🧪 TESTING REQUIREMENTS

### Unit Tests
- **Coverage:** Minimum 80% for Commons code
- **Framework:** pytest
- **Location:** \`tests/\`
- **Focus:** PUL license verification, Commons pillar access

### Example Test
\`\`\`python
# tests/test_commons.py

import pytest
from src.common.licensing.commons import verify_pul_license

@pytest.mark.asyncio
async def test_pul_license_always_valid():
    \"\"\"Test that PUL licenses never expire.\"\"\"
    token = generate_pul_token()  # Uses public key signing
    result = await verify_pul_license(token)
    
    assert result['allowed'] is True
    assert result['license'] == 'PUBLIC_UNLIMITED'
    assert result['expires'] is None  # Never expires!

@pytest.mark.asyncio
async def test_commons_pillars_free():
    \"\"\"Test that Commons pillars require no payment.\"\"\"
    for pillar in ['SeaSide', 'DeckSide', 'DockSide']:
        access = await check_pillar_access(pillar)
        assert access['requires_payment'] is False
\`\`\`

---

## 🎯 AI ASSISTANT GUIDELINES

### When Working on Commons Code

1. **Verify Context:**
   \`\`\`powershell
   project-context  # Should show: SeaTrace-ODOO (PUBLIC)
   \`\`\`

2. **Check Git Remote:**
   \`\`\`powershell
   git remote get-url origin  # Should show: SeaTrace-ODOO
   \`\`\`

3. **Read Commons Charter First:**
   - File: \`docs/COMMONS_CHARTER.md\`
   - Understand FREE pillars vs PAID MarketSide

### When You Need MarketSide/Pricing Features

**STOP and redirect:**
> "MarketSide, pricing, and enterprise features belong in SeaTrace003 (PRIVATE repo).  
> Switch context: \`cd-seatrace003\`  
> Then I can assist with LIMITED license implementation."

### Commons Workflow Pattern

\`\`\`powershell
# 1. Load DevShell
& "C:\Users\Roberto002\OneDrive\Sir James\LOGIC SirJames_Interactive_Prototype_With_Chapter10\scripts\DevShell.ps1" -Project SeaTraceProduction

# 2. Navigate to Commons repo
cd-seatrace-prod

# 3. Verify context
project-context

# 4. Create feature branch
git checkout -b feature/commons-enhancement

# 5. Make changes (Commons pillars only)
# ... edit code ...

# 6. Test
pytest tests/test_commons.py -v

# 7. Commit
git add .
git commit -m "feat(commons): Add SeaSide tracking enhancement"
git push origin feature/commons-enhancement

# 8. Return to Sir James
cd-sirjames
\`\`\`

---

## 📚 DOCUMENTATION

### Required Documentation (PUBLIC)
1. **COMMONS_CHARTER.md** - Governance model
2. **docs/licensing/PUBLIC-UNLIMITED.md** - PUL terms
3. **LICENSE.unlimited** - License text
4. **API.md** - Public API documentation

### Inline Documentation
- Every Commons pillar class needs docstring
- Every public route needs docstring
- Use type hints everywhere

---

## 🔄 INTEGRATION WITH ACTING MASTER

### DevShell.ps1 Integration
This repo works with DevShell.ps1 master script:
- **Load Commons Context:** \`cd-seatrace-prod\`
- **Check Context:** \`project-context\`
- **Open in VS Code:** \`seatrace-prod-code\`

### Project Boundaries
- **SeaTrace-ODOO (THIS REPO):** Commons Charter, FREE pillars
- **SeaTrace003 (PRIVATE):** MarketSide, pricing, EMR
- **SirJames:** Educational game (separate project)

---

**© 2025 SeaTrace-ODOO Code Agent Configuration**  
**Governance:** Commons Charter v1.0  
**Status:** ✅ Active
"@ | Out-File -FilePath CODE.AGENT.md -Encoding UTF8

Write-Host "`n✅ CODE.AGENT.md created with Commons awareness!" -ForegroundColor Green

# Commit
git add CODE.AGENT.md
git commit -m "docs: Add CODE.AGENT.md for Commons Charter workflow"
git push origin main

Write-Host "`n✅ TASK 2.1 COMPLETE!" -ForegroundColor Green

# Return to Sir James
cd-sirjames
```

#### Task 2.2: TOOL.AGENT.md for SeaTrace-ODOO (Commons/PUBLIC)
```powershell
# Switch to PUBLIC Commons repo
cd-seatrace-prod

# Create TOOL.AGENT.md
@"
# TOOL.AGENT.md - SeaTrace-ODOO (PUBLIC Commons Repository)

**Last Updated:** $(Get-Date -Format 'yyyy-MM-dd')  
**Purpose:** Define tools, scripts, and automation for Commons workflow

---

## 🛠️ DEVSHELL.PS1 - Master Orchestration

### Location
\`C:\Users\Roberto002\OneDrive\Sir James\LOGIC SirJames_Interactive_Prototype_With_Chapter10\scripts\DevShell.ps1\`

### Load Commons Context
\`\`\`powershell
# Load SeaTrace-ODOO (PUBLIC Commons) context
& "C:\Users\Roberto002\OneDrive\Sir James\LOGIC SirJames_Interactive_Prototype_With_Chapter10\scripts\DevShell.ps1" -Project SeaTraceProduction

# Verify context
project-context
# Should output:
# 🌊 Active Project: SeaTrace-PRODUCTION
# 📂 Path: C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO
# 🎯 Context: SeaTraceProduction (PUBLIC COMMONS)
\`\`\`

### Available Commands

#### Navigation Aliases
\`\`\`powershell
cd-seatrace-prod      # Navigate to Commons repo (PUBLIC)
cd-seatrace003        # Navigate to PRIVATE repo (MarketSide)
cd-sirjames           # Navigate to Sir James project
\`\`\`

#### Context Management
\`\`\`powershell
project-context       # Show current project details
show-context          # Alias for project-context
\`\`\`

#### IDE Shortcuts
\`\`\`powershell
seatrace-prod-code    # Open Commons repo in VS Code
seatrace003-code      # Open PRIVATE repo in VS Code
sirjames-code         # Open Sir James in VS Code
\`\`\`

---

## 🔧 COMMONS-SPECIFIC SCRIPTS

### 1. Generate Public Scope Digest
\`\`\`powershell
# Script: scripts/licensing/generate_public_scope_from_app.py
# Purpose: Build manifest of PUBLIC API routes

python scripts/licensing/generate_public_scope_from_app.py

# Output: docs/licensing/public_scope_digest.txt
# Contains: List of all Commons API endpoints
\`\`\`

### 2. Verify Commons Charter
\`\`\`powershell
# Script: scripts/licensing/verify_commons_charter.py (create this)
# Purpose: Validate Commons Charter compliance

python scripts/licensing/verify_commons_charter.py --check-pillars

# Checks:
# - SeaSide routes are FREE
# - DeckSide routes are FREE
# - DockSide routes are FREE
# - No MarketSide code in PUBLIC repo
\`\`\`

### 3. Sign PUL Token (Ed25519)
\`\`\`powershell
# Script: scripts/licensing/sign_token_ed25519.py
# Purpose: Generate PUL license tokens

python scripts/licensing/sign_token_ed25519.py \
  --claims scripts/licensing/pul_claims.sample.json \
  --public-key-only  # Never use private keys in PUBLIC repo!

# Output: PUL token for testing
\`\`\`

---

## 🧪 TESTING TOOLS

### Run Commons Tests
\`\`\`powershell
# Test Commons license verification
pytest tests/test_commons.py -v

# Test public API routes
pytest tests/test_routes.py -k "commons" -v

# Test all Commons pillars
pytest tests/test_pillars.py -v
\`\`\`

### Coverage Report
\`\`\`powershell
pytest tests/ --cov=src/common/licensing --cov-report=html
# Opens htmlcov/index.html
\`\`\`

---

## 🔍 GIT WORKFLOW TOOLS

### Pre-Commit Checks (Commons-Aware)
\`\`\`bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Running Commons Charter pre-commit checks..."

# 1. Check for secrets
if git diff --cached | grep -iE "(private.*key|secret|credential)" > /dev/null; then
    echo "❌ ERROR: Potential secret detected"
    exit 1
fi

# 2. Check for MarketSide code (belongs in PRIVATE repo)
if git diff --cached | grep -iE "(marketside|pricing|emr_meter)" > /dev/null; then
    echo "❌ ERROR: MarketSide code detected in PUBLIC repo!"
    echo "MarketSide belongs in SeaTrace003 (PRIVATE)"
    exit 1
fi

# 3. Verify correct repository
REMOTE_URL=\$(git remote get-url origin)
if [[ ! "\$REMOTE_URL" =~ "SeaTrace-ODOO" ]]; then
    echo "❌ ERROR: Wrong repository!"
    exit 1
fi

echo "✅ Commons Charter checks passed"
exit 0
\`\`\`

---

## 🎯 COMMONS WORKFLOW PATTERNS

### Pattern 1: Add New Commons Feature
\`\`\`powershell
# 1. Load Commons context
cd-seatrace-prod

# 2. Verify context
project-context

# 3. Create feature branch
git checkout -b feature/commons-enhancement

# 4. Make changes (FREE pillars only)
# ... edit code ...

# 5. Test
pytest tests/test_commons.py -v

# 6. Pre-commit checks run automatically
git add .
git commit -m "feat(commons): Add SeaSide tracking enhancement"

# 7. Push
git push origin feature/commons-enhancement

# 8. Return to Sir James
cd-sirjames
\`\`\`

### Pattern 2: Fix Commons Bug
\`\`\`powershell
# 1. Load context
cd-seatrace-prod

# 2. Create bugfix branch
git checkout -b bugfix/commons-license-validation

# 3. Run specific tests
pytest tests/test_commons.py::test_pul_license_validation -v

# 4. Fix and test
# ... edit code ...
pytest tests/test_commons.py -v

# 5. Commit
git add .
git commit -m "fix(commons): Improve PUL license validation"
git push origin bugfix/commons-license-validation

# 6. Return
cd-sirjames
\`\`\`

### Pattern 3: Document Commons API
\`\`\`powershell
# 1. Load context
cd-seatrace-prod

# 2. Generate public scope digest
python scripts/licensing/generate_public_scope_from_app.py

# 3. Verify output
cat docs/licensing/public_scope_digest.txt

# 4. Commit documentation
git add docs/licensing/
git commit -m "docs(commons): Update public API scope digest"
git push origin main

# 5. Return
cd-sirjames
\`\`\`

---

## 🚨 TROUBLESHOOTING

### Issue: Wrong Repo Context
\`\`\`powershell
# Solution: Reload DevShell with correct project
& "C:\Users\Roberto002\OneDrive\Sir James\LOGIC SirJames_Interactive_Prototype_With_Chapter10\scripts\DevShell.ps1" -Project SeaTraceProduction

# Verify
project-context
\`\`\`

### Issue: MarketSide Code Appearing
\`\`\`powershell
# Solution: This is WRONG repo!
# MarketSide belongs in SeaTrace003 (PRIVATE)

cd-seatrace003  # Switch to PRIVATE repo
project-context  # Verify you're in 🔒 SeaTrace003-PRIVATE
\`\`\`

---

**© 2025 SeaTrace-ODOO Tool Agent Configuration**  
**Governance:** Commons Charter v1.0  
**Integration:** DevShell.ps1 Master Script
"@ | Out-File -FilePath TOOL.AGENT.md -Encoding UTF8

Write-Host "`n✅ TOOL.AGENT.md created!" -ForegroundColor Green

# Commit
git add TOOL.AGENT.md
git commit -m "docs: Add TOOL.AGENT.md for Commons workflow automation"
git push origin main

Write-Host "`n✅ TASK 2.2 COMPLETE!" -ForegroundColor Green

# Return to Sir James
cd-sirjames
```

**✅ Phase 2 Checkpoint:**
- CODE.AGENT.md defines Commons Charter boundaries
- TOOL.AGENT.md documents DevShell integration
- Pre-commit hooks prevent MarketSide code in PUBLIC repo

---

### PHASE 3: ETL PATTERNS FOR COMMONS (20 minutes)
**Goal:** Document data flows and MCP tool configurations for Commons workflow

#### Task 3.1: Create COMMONS_ETL_PATTERNS.md
```powershell
cd-seatrace-prod

@"
# Commons ETL Patterns - SeaTrace-ODOO

**Purpose:** Document Extract/Transform/Load patterns for Commons Charter data  
**Scope:** PUBLIC pillars only (SeaSide, DeckSide, DockSide)

---

## 📊 COMMONS DATA FLOWS

### Extract: Public API Routes
\`\`\`
┌──────────────────┐
│  Public Clients  │
│  (Vessels, Apps) │
└────────┬─────────┘
         │
         │ GET /commons/verify
         │ GET /api/v1/seaside/vessels
         │ POST /api/v1/deckside/catch
         │ GET /api/v1/dockside/storage
         ▼
┌────────────────────┐
│  FastAPI/ODOO      │
│  Public Routes     │
│  (FREE Forever)    │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  PostgreSQL        │
│  Commons Data      │
└────────────────────┘
\`\`\`

### Transform: Commons License Verification
\`\`\`python
# Input: JWT token from client
# Process: Verify PUL signature (Ed25519 public key)
# Output: Access granted (always, for Commons pillars)

from src.common.licensing.commons import verify_pul_license

async def extract_claims(token: str):
    \"\"\"Extract: Parse JWT token.\"\"\"
    return jwt.decode(token, options={"verify_signature": False})

async def transform_to_commons_access(claims: dict):
    \"\"\"Transform: Validate Commons Charter compliance.\"\"\"
    if claims.get('license') == 'PUBLIC_UNLIMITED':
        return {'allowed': True, 'expires': None}
    return {'allowed': False, 'reason': 'Not a PUL token'}

async def load_access_decision(access: dict):
    \"\"\"Load: Grant access to Commons pillars.\"\"\"
    if access['allowed']:
        return {
            'status': 'ok',
            'pillars': ['SeaSide', 'DeckSide', 'DockSide'],
            'tier': 'FREE'
        }
\`\`\`

### Load: Public Scope Digest
\`\`\`bash
# Extract: Scan FastAPI/ODOO routes
# Transform: Filter for PUBLIC routes only
# Load: Generate public_scope_digest.txt

python scripts/licensing/generate_public_scope_from_app.py

# Output: docs/licensing/public_scope_digest.txt
\`\`\`

---

## 🔧 MCP TOOL CONFIGURATIONS

### GitHub MCP Server (Commons)
\`\`\`json
{
  "mcpServers": {
    "github-commons": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<token>",
        "GITHUB_REPO_FILTER": "SeaTrace-ODOO"
      }
    }
  }
}
\`\`\`

### Filesystem MCP Server (Commons)
\`\`\`json
{
  "mcpServers": {
    "filesystem-commons": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\\\Users\\\\Roberto002\\\\Documents\\\\GitHub\\\\SeaTrace-ODOO\\\\src\\\\common\\\\licensing",
        "C:\\\\Users\\\\Roberto002\\\\Documents\\\\GitHub\\\\SeaTrace-ODOO\\\\docs\\\\licensing"
      ],
      "description": "Commons Charter licensing files only"
    }
  }
}
\`\`\`

---

**© 2025 SeaTrace-ODOO Commons ETL Patterns**
"@ | Out-File -FilePath COMMONS_ETL_PATTERNS.md -Encoding UTF8

Write-Host "`n✅ COMMONS_ETL_PATTERNS.md created!" -ForegroundColor Green

git add COMMONS_ETL_PATTERNS.md
git commit -m "docs: Add Commons ETL patterns and MCP configurations"
git push origin main

Write-Host "`n✅ TASK 3.1 COMPLETE!" -ForegroundColor Green

cd-sirjames
```

**✅ Phase 3 Checkpoint:**
- ETL patterns documented for Commons data
- MCP tool configurations scoped to PUBLIC files only

---

## 📊 FINAL PROGRESS TRACKER

Run this after completing all phases:

```powershell
Write-Host "`n🌊 COMMONS + ACTING MASTER INTEGRATION PROGRESS`n" -ForegroundColor Cyan

$tasks = @(
    @{Name=".gitignore (Commons/PUBLIC)"; Path="C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO\.gitignore"; Phase="1"},
    @{Name=".gitignore (PRIVATE)"; Path="C:\Users\Roberto002\Documents\GitHub\SeaTrace003\.gitignore"; Phase="1"},
    @{Name=".gitignore (SirJames)"; Path="C:\Users\Roberto002\Documents\GitHub\SirJamesAdventures\.gitignore"; Phase="1"},
    @{Name="CODE.AGENT.md (Commons)"; Path="C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO\CODE.AGENT.md"; Phase="2"},
    @{Name="TOOL.AGENT.md (Commons)"; Path="C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO\TOOL.AGENT.md"; Phase="2"},
    @{Name="COMMONS_ETL_PATTERNS.md"; Path="C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO\COMMONS_ETL_PATTERNS.md"; Phase="3"}
)

$completed = 0
foreach ($task in $tasks) {
    if (Test-Path $task.Path) {
        Write-Host "✅ [Phase $($task.Phase)] $($task.Name)" -ForegroundColor Green
        $completed++
    } else {
        Write-Host "❌ [Phase $($task.Phase)] $($task.Name)" -ForegroundColor Red
    }
}

Write-Host "`n📊 Progress: $completed / $($tasks.Count) tasks complete" -ForegroundColor Cyan
$percent = [math]::Round(($completed / $tasks.Count) * 100)
Write-Host "📈 Completion: $percent%" -ForegroundColor $(if($percent -eq 100){"Green"}else{"Yellow"})

Write-Host "`n📍 Current Context:" -ForegroundColor Cyan
project-context
```

---

## 🎯 EXECUTION ORDER

### RIGHT NOW (Start Here)
1. **Phase 1 Task 1.1** - Create .gitignore for Commons/PUBLIC (5 min)
2. **Phase 1 Task 1.2** - Create .gitignore for PRIVATE (3 min)
3. **Phase 1 Task 1.3** - Create .gitignore for SirJames (2 min)
4. **Run Progress Tracker** - See Phase 1 complete (1 min)

### THIS SESSION (Next 30 Minutes)
5. **Phase 2 Task 2.1** - CODE.AGENT.md for Commons (10 min)
6. **Phase 2 Task 2.2** - TOOL.AGENT.md for Commons (10 min)
7. **Phase 3 Task 3.1** - COMMONS_ETL_PATTERNS.md (10 min)
8. **Final Progress Tracker** - See 100% complete (1 min)

---

## 🎉 EXPECTED OUTCOMES

After completing all phases:

✅ **Security Foundation**
- .gitignore files protect Commons Charter boundaries
- Pre-commit hooks prevent MarketSide code in PUBLIC repo
- Secrets never committed to any repo

✅ **Agent Configuration**
- AI assistants understand Commons Charter
- Clear PUBLIC/PRIVATE repo boundaries
- DevShell.ps1 integration documented

✅ **ETL Patterns**
- Commons data flows documented
- MCP tools scoped to PUBLIC files
- Public scope digest automation

✅ **Workflow Integration**
- Acting Master discovery connected to Commons workflow
- DevShell aliases work with Commons context
- All documentation in correct repos

---

## 🚀 READY TO START?

Copy Phase 1 Task 1.1 commands and paste into your terminal!

**Current Context:** 📚 SirJames  
**Target:** 🌊 SeaTrace-ODOO (Commons/PUBLIC)  
**Time Estimate:** 10-15 minutes for Phase 1

---

**© 2025 SeaTrace Commons + Acting Master Integration Plan**  
**Status:** ✅ READY FOR EXECUTION  
**Created:** October 2, 2025
