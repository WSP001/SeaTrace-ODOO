# 📮 POSTMAN WORKFLOW GUIDE: SeaTrace API Network Development

**Date:** October 25, 2025  
**Purpose:** PUBLIC vs PRIVATE Postman workspace structure for seatrace.worldseafoodproducers.com  
**Status:** READY TO EXECUTE

---

## 🎯 **WHAT I FOUND IN YOUR REPO**

### ✅ **Current Postman Assets:**

**PUBLIC Repo (SeaTrace-ODOO):**
- ✅ `demo/postman/SeaTrace-INVESTOR.collection.json` - Found
- ✅ `demo/postman/SeaTrace-INVESTOR.env.json` - Found
- ❓ `staging/postman.collection.json` - Status unknown (need to verify)

**Local Postman Data (AppData):**
- ✅ `C:\Users\Roberto002\AppData\Roaming\Postman\` - Directory exists
- ✅ UUID: `62489eb5-f0bc-4a80-bdd1-8cf31cd93a06.uuid` - User ID found
- ✅ `storage/`, `Local Storage/`, `Postman_Config` - Local collections may exist here

---

## 🚨 **CRITICAL CLASSIFICATION ISSUE**

### **Problem:** SeaTrace-INVESTOR collection is in PUBLIC repo

**Files at risk:**
- `demo/postman/SeaTrace-INVESTOR.collection.json` - Contains PRIVATE endpoint details
- `demo/postman/SeaTrace-INVESTOR.env.json` - May contain PRIVATE credentials

**Classification:**
- **INVESTOR** collections = PRIVATE-LIMITED (belong in SeaTrace003)
- **COMMONS** collections = PUBLIC-UNLIMITED (belong in SeaTrace-ODOO)

**Action needed:** Separate into two collections (see Phase 3 below)

---

## 📋 **RECOMMENDED POSTMAN WORKSPACE STRUCTURE**

### **PUBLIC Workspace: "SeaTrace Commons KPI Demo"**

**Purpose:** Developer adoption, QR verification, regulatory transparency

**Collections:**
```
SeaTrace_Commons_KPI_Demo.postman_collection.json
├── 📁 Health & Status
│   ├── GET {{baseUrl}}/health
│   └── GET {{baseUrl}}/status
│
├── 📁 JWKS (Public Keys)
│   └── GET {{baseUrl}}/.well-known/jwks.json
│
├── 📁 MarketSide (QR Verification)
│   ├── POST {{baseUrl}}/api/v1/marketside/qr/verify
│   └── GET {{baseUrl}}/api/v1/marketside/qr/{qr_code}/status
│
├── 📁 Public Models (Read-Only)
│   ├── GET {{baseUrl}}/api/v1/public/vessels
│   ├── GET {{baseUrl}}/api/v1/public/catch/{packet_id}
│   └── GET {{baseUrl}}/api/v1/public/verification/{verification_id}
│
└── 📁 Load Testing Endpoints
    └── GET {{baseUrl}}/api/v1/metrics/prometheus
```

**Variables (NO SECRETS):**
- `baseUrl` = `https://dev.seatrace.worldseafoodproducers.com`
- `qr_demo_code` = `DEMO-QR-0001`
- `vessel_demo_id` = `F/V 000`

**Tests (PUBLIC-safe):**
```javascript
// Every endpoint has these tests
pm.test("Status code is 200 or 429 (rate limited)", () => {
    pm.expect([200, 429]).to.include(pm.response.code);
});

pm.test("Content-Type is JSON", () => {
    pm.expect(pm.response.headers.get("content-type")).to.match(/application\/json/i);
});

pm.test("Response time under 500ms", () => {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

// Rate limit headers
["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"].forEach(h => {
    pm.test(`${h} header present`, () => {
        pm.expect(pm.response.headers.has(h)).to.be.true;
    });
});
```

---

### **PRIVATE Workspace: "SeaTrace Investor Dashboard"**

**Purpose:** Investor value, financial data, ML insights, precise GPS

**Collections:**
```
SeaTrace_Investor_Dashboard.postman_collection.json
├── 📁 Authentication
│   ├── POST {{baseUrl}}/api/v1/auth/login
│   └── POST {{baseUrl}}/api/v1/auth/refresh
│
├── 📁 DeckSide (PRIVATE Fork Logic)
│   ├── POST {{baseUrl}}/api/v1/deckside/elog/submit
│   ├── GET {{baseUrl}}/api/v1/deckside/catch/{catch_id}/precise
│   └── GET {{baseUrl}}/api/v1/deckside/pricing/{catch_id}
│
├── 📁 Prospectus Calculations
│   ├── POST {{baseUrl}}/api/v1/prospectus/calculate
│   └── GET {{baseUrl}}/api/v1/prospectus/valuation
│
├── 📁 ML Models (PRIVATE)
│   ├── POST {{baseUrl}}/api/v1/ml/quality/predict
│   └── GET {{baseUrl}}/api/v1/ml/pricing/forecast
│
└── 📁 Odoo Integration
    ├── GET {{baseUrl}}/api/v1/odoo/inventory
    └── POST {{baseUrl}}/api/v1/odoo/financial/transaction
```

**Variables (SECRETS - Environment only, never in collection):**
- `baseUrl` = `https://api-private.seatrace.worldseafoodproducers.com`
- `auth_token` = `{{$randomUUID}}` (set dynamically after login)
- `license_key` = `SEATRACE_LIMITED_{{$timestamp}}`
- `hmac_secret` = `<from environment or CI secrets>`

**Pre-request Script (All requests):**
```javascript
// Trace ID for audit trail
if (!pm.variables.get("traceId")) {
    const seed = Date.now().toString() + pm.info.requestName;
    pm.variables.set("traceId", CryptoJS.SHA256(seed).toString().slice(0,16));
}
pm.request.headers.upsert({ key: "X-Trace-Id", value: pm.variables.get("traceId") });

// Auth token from environment
const authToken = pm.environment.get("auth_token");
if (authToken) {
    pm.request.headers.upsert({ key: "Authorization", value: `Bearer ${authToken}` });
}
```

---

## 🔧 **PHASE 1: RECOVERY - Find Your Missing Postman Data**

### **Step 1.1: Account Audit (5 minutes)**

**Run these checks:**

```powershell
# Check which Postman accounts you have locally
$PostmanConfig = "$env:APPDATA\Postman\Postman_Config"
if (Test-Path $PostmanConfig) {
    Get-Content $PostmanConfig | Select-String "email|account|user"
}

# Check UUID (user identifier)
$UUID = Get-ChildItem "$env:APPDATA\Postman" -Filter "*.uuid" | Select-Object -First 1
Write-Host "Postman User UUID: $($UUID.BaseName)"
```

**Accounts to check:**
- [ ] `scott@worldseafoodproducers.com`
- [ ] `worldseafood@gmail.com` (check spelling)
- [ ] Any company SSO (Google/Microsoft/Okta)

**Action:** Sign out of Postman everywhere, sign back into **each** account, check **Workspaces → All**

---

### **Step 1.2: Local Data Search (10 minutes)**

**Search for collections in local storage:**

```powershell
# Search for Postman collection files in AppData
$SearchPaths = @(
    "$env:APPDATA\Postman\storage",
    "$env:APPDATA\Postman\Local Storage",
    "$env:APPDATA\Postman\IndexedDB"
)

foreach ($path in $SearchPaths) {
    if (Test-Path $path) {
        Write-Host "`n🔍 Searching: $path"
        Get-ChildItem $path -Recurse -Include "*.json","*.postman_collection*","*.postman_environment*" -ErrorAction SilentlyContinue |
            Where-Object { $_.Length -gt 1KB } |
            ForEach-Object {
                Write-Host "   📄 Found: $($_.FullName) ($([math]::Round($_.Length/1KB))KB)"
            }
    }
}

# Search for exported backups
Write-Host "`n🔍 Searching for exported Postman files..."
Get-ChildItem C:\Users\Roberto002\Documents -Recurse -Include "*.postman_collection.json","*.postman_environment.json","postman_data_dump.json" -ErrorAction SilentlyContinue -Depth 3 |
    ForEach-Object {
        Write-Host "   📄 Found: $($_.FullName)"
    }
```

---

### **Step 1.3: Trash Recovery (2 minutes)**

**In Postman:**
1. Click your avatar (top-right) → **Trash**
2. Look for:
   - SeaTrace collections
   - Worldseafoodproducers environments
   - Any "000-001" prototype items
3. **Restore** anything found

**Desktop app:** Check status bar at bottom → **Trash icon** → Restore

---

### **Step 1.4: API Enumeration (AUTHORITATIVE - 5 minutes)**

**Generate Postman API Key:**
1. Postman web → **Settings** → **API Keys** → **Generate API key**
2. Copy key → Store in environment variable

**Run enumeration:**

```powershell
# Set your Postman API key
$POSTMAN_API_KEY = "PMAK-xxxxxxxxxxxxxxxx" # <-- PASTE YOUR KEY HERE

# List all workspaces
$Workspaces = Invoke-RestMethod -Uri "https://api.getpostman.com/workspaces" -Headers @{ "X-Api-Key" = $POSTMAN_API_KEY }
$Workspaces.workspaces | Format-Table name, id, type, visibility

# List all collections
$Collections = Invoke-RestMethod -Uri "https://api.getpostman.com/collections" -Headers @{ "X-Api-Key" = $POSTMAN_API_KEY }
$Collections.collections | Format-Table name, id, owner

# Save results
$Collections.collections | ConvertTo-Json -Depth 10 | Out-File "postman_collections_found.json"
Write-Host "✅ Collections saved to: postman_collections_found.json"
```

---

## 🛠️ **PHASE 2: SEPARATION - Split INVESTOR into PUBLIC + PRIVATE**

### **Step 2.1: Analyze Current INVESTOR Collection**

**Manual review:**

```powershell
# Check if INVESTOR collection contains sensitive data
$InvestorFile = "demo\postman\SeaTrace-INVESTOR.collection.json"
if (Test-Path $InvestorFile) {
    $Content = Get-Content $InvestorFile -Raw | ConvertFrom-Json
    
    Write-Host "📋 Collection Name: $($Content.info.name)"
    Write-Host "📋 Requests Count: $($Content.item.Count)"
    
    # Search for sensitive patterns
    $RawContent = Get-Content $InvestorFile -Raw
    $Patterns = @("password", "secret", "token", "api_key", "hmac", "private", "investor", "precise", "gps")
    
    Write-Host "`n🔍 Sensitive patterns found:"
    foreach ($pattern in $Patterns) {
        if ($RawContent -match $pattern) {
            Write-Host "   ⚠️  Found: $pattern"
        }
    }
}
```

---

### **Step 2.2: Create PUBLIC Commons Collection**

**I'll create this for you:**

```json
{
  "info": {
    "name": "SeaTrace Commons KPI Demo (PUBLIC)",
    "description": "PUBLIC-UNLIMITED: Developer adoption, QR verification, regulatory transparency. No secrets, no private endpoints.",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://dev.seatrace.worldseafoodproducers.com",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Health & Status",
      "item": [
        {
          "name": "Health Check",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/health",
              "host": ["{{baseUrl}}"],
              "path": ["health"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status code is 200', () => pm.response.to.have.status(200));",
                  "pm.test('Response time under 500ms', () => pm.expect(pm.response.responseTime).to.be.below(500));",
                  "pm.test('Content-Type is JSON', () => pm.expect(pm.response.headers.get('content-type')).to.match(/application\\/json/i));"
                ]
              }
            }
          ]
        }
      ]
    },
    {
      "name": "JWKS (Public Keys)",
      "item": [
        {
          "name": "Get JWKS",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/.well-known/jwks.json",
              "host": ["{{baseUrl}}"],
              "path": [".well-known", "jwks.json"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status code is 200', () => pm.response.to.have.status(200));",
                  "pm.test('Has keys array', () => {",
                  "    const jwks = pm.response.json();",
                  "    pm.expect(jwks).to.have.property('keys');",
                  "    pm.expect(jwks.keys).to.be.an('array').with.lengthOf.at.least(1);",
                  "});",
                  "['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset'].forEach(h => {",
                  "    pm.test(h + ' header present', () => pm.expect(pm.response.headers.has(h)).to.be.true);",
                  "});"
                ]
              }
            }
          ]
        }
      ]
    },
    {
      "name": "MarketSide (QR Verification)",
      "item": [
        {
          "name": "Verify QR Code",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "X-License-ID",
                "value": "PUBLIC-DEMO-LICENSE"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\"qr_code\": \"DEMO-QR-0001\"}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/v1/marketside/qr/verify",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "marketside", "qr", "verify"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status is 200 (verified) or 429 (rate-limited)', () => {",
                  "    pm.expect([200, 429]).to.include(pm.response.code);",
                  "});",
                  "if (pm.response.code === 200) {",
                  "    pm.test('Response has verification_status', () => {",
                  "        const res = pm.response.json();",
                  "        pm.expect(res).to.have.property('verification_status');",
                  "    });",
                  "}"
                ]
              }
            }
          ]
        }
      ]
    }
  ]
}
```

**Save as:** `postman/collections/SeaTrace_Commons_KPI_Demo.postman_collection.json`

---

## 🚀 **PHASE 3: AUTOMATION - Scripts for Backup & Testing**

### **Choice A: Swap to postman-enumerate-v2.ps1 + Upload Artifact**

**File:** `scripts/postman-enumerate-v2.ps1`

```powershell
# Purpose: Enumerate all Postman workspaces/collections via API and upload as GitHub artifact
# Classification: PRIVATE-LIMITED (API key required)
# Usage: .\postman-enumerate-v2.ps1 -WorkspaceName "SeaTrace" -UploadArtifact

param(
    [string]$WorkspaceName = "SeaTrace",
    [string]$OutputDir = "postman_backup",
    [switch]$UploadArtifact
)

$POSTMAN_API_KEY = $env:POSTMAN_API_KEY
if (-not $POSTMAN_API_KEY) {
    Write-Error "❌ POSTMAN_API_KEY environment variable not set"
    exit 1
}

$Headers = @{ "X-Api-Key" = $POSTMAN_API_KEY }

# Create output directories
New-Item -ItemType Directory -Path "$OutputDir/workspaces" -Force | Out-Null
New-Item -ItemType Directory -Path "$OutputDir/collections" -Force | Out-Null
New-Item -ItemType Directory -Path "$OutputDir/environments" -Force | Out-Null

Write-Host "🔍 Enumerating Postman workspaces..."

# Get all workspaces
$WorkspacesResponse = Invoke-RestMethod -Uri "https://api.getpostman.com/workspaces" -Headers $Headers
$FilteredWorkspaces = $WorkspacesResponse.workspaces | Where-Object { $_.name -like "*$WorkspaceName*" }

$WorkspacesIndex = @()

foreach ($ws in $FilteredWorkspaces) {
    Write-Host "📁 Workspace: $($ws.name) ($($ws.id))"
    
    # Get workspace details
    $WsDetail = Invoke-RestMethod -Uri "https://api.getpostman.com/workspaces/$($ws.id)" -Headers $Headers
    
    $WorkspacesIndex += @{
        id = $ws.id
        name = $ws.name
        type = $ws.type
        visibility = $ws.visibility
        collections_count = $WsDetail.workspace.collections.Count
        environments_count = $WsDetail.workspace.environments.Count
    }
    
    # Download each collection
    foreach ($col in $WsDetail.workspace.collections) {
        Write-Host "   📄 Collection: $($col.name)"
        $ColDetail = Invoke-RestMethod -Uri "https://api.getpostman.com/collections/$($col.id)" -Headers $Headers
        $ColDetail | ConvertTo-Json -Depth 100 | Out-File "$OutputDir/collections/$($col.id).json"
    }
    
    # Download each environment
    foreach ($env in $WsDetail.workspace.environments) {
        Write-Host "   🌍 Environment: $($env.name)"
        $EnvDetail = Invoke-RestMethod -Uri "https://api.getpostman.com/environments/$($env.id)" -Headers $Headers
        
        # SANITIZE: Remove secret values before saving
        if ($EnvDetail.environment.values) {
            $EnvDetail.environment.values = $EnvDetail.environment.values | ForEach-Object {
                if ($_.type -eq "secret") {
                    $_.value = "<REDACTED>"
                }
                $_
            }
        }
        
        $EnvDetail | ConvertTo-Json -Depth 100 | Out-File "$OutputDir/environments/$($env.id).json"
    }
}

# Write indexes
$WorkspacesIndex | ConvertTo-Json -Depth 10 | Out-File "$OutputDir/workspaces/index.json"

Write-Host "`n✅ Backup complete: $OutputDir"
Write-Host "   📁 Workspaces: $($WorkspacesIndex.Count)"
Write-Host "   📄 Collections: $(Get-ChildItem "$OutputDir/collections" -File | Measure-Object | Select-Object -ExpandProperty Count)"
Write-Host "   🌍 Environments: $(Get-ChildItem "$OutputDir/environments" -File | Measure-Object | Select-Object -ExpandProperty Count)"

# Upload as GitHub artifact (if running in CI)
if ($UploadArtifact -and $env:GITHUB_ACTIONS) {
    Write-Host "`n📤 Uploading artifact to GitHub..."
    gh run upload-artifact "$OutputDir" --name "postman-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
}
```

---

### **Choice B: Add PR Smoke Test to PUBLIC Repo**

**File:** `.github/workflows/postman-smoke-test.yml`

```yaml
name: Postman Smoke Test (PUBLIC)

on:
  pull_request:
    paths:
      - 'postman/collections/**'
      - '.github/workflows/postman-smoke-test.yml'

jobs:
  smoke-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Newman
        run: npm install -g newman newman-reporter-htmlextra

      - name: Run PUBLIC Commons Collection
        env:
          BASE_URL: ${{ secrets.PUBLIC_BASE_URL || 'https://dev.seatrace.worldseafoodproducers.com' }}
        run: |
          newman run postman/collections/SeaTrace_Commons_KPI_Demo.postman_collection.json \
            --env-var "baseUrl=$BASE_URL" \
            --reporters cli,htmlextra \
            --reporter-htmlextra-export newman-report.html \
            --bail

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: newman-report
          path: newman-report.html

      - name: Comment PR
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.name,
              body: '❌ Postman smoke test failed. Check the [Newman report](../actions/runs/${{ github.run_id }}) for details.'
            })
```

---

### **Choice C: JWKS Exporter + README** ✅ **RECOMMENDED**

**File:** `scripts/jwks-export.cjs` (PUBLIC-safe, no secrets)

```javascript
#!/usr/bin/env node
// Purpose: Export public JWK from private key (RSA or EC)
// Classification: PUBLIC-UNLIMITED (no private keys exposed)
// Usage: node scripts/jwks-export.cjs ./keys/private.pem ./public/.well-known/jwks.json kid-001

const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");

const [, , pemPath, outPath, kid = "kid-001"] = process.argv;

if (!pemPath || !outPath) {
  console.error("Usage: node scripts/jwks-export.cjs <private.pem> <out.json> [kid]");
  process.exit(1);
}

// Load private key, derive public key JWK
const privPem = fs.readFileSync(pemPath, "utf8");
const priv = crypto.createPrivateKey({ key: privPem });
const pub = crypto.createPublicKey(priv);

// Export public key as JWK
const pubJwk = pub.export({ format: "jwk" });

// Normalize to a public signing JWK
let jwk;
if (pubJwk.kty === "RSA") {
  jwk = {
    kty: "RSA",
    n: pubJwk.n,
    e: pubJwk.e,
    use: "sig",
    alg: "RS256",
    kid
  };
} else if (pubJwk.kty === "EC") {
  const alg = pub.asymmetricKeyDetails?.namedCurve === "P-256" ? "ES256" : "ES384";
  jwk = {
    kty: "EC",
    crv: pubJwk.crv,
    x: pubJwk.x,
    y: pubJwk.y,
    use: "sig",
    alg,
    kid
  };
} else {
  console.error(`Unsupported key type: ${pubJwk.kty}`);
  process.exit(2);
}

const body = { keys: [jwk] };
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, JSON.stringify(body, null, 2));

console.log(`✅ JWKS written → ${outPath}`);
```

**Usage:**

```powershell
# Generate key (run once, keep private.pem in PRIVATE repo or local only)
openssl ecparam -genkey -name prime256v1 -noout -out keys/private.pem

# Export JWKS to PUBLIC location
node scripts/jwks-export.cjs ./keys/private.pem ./staging/.well-known/jwks.json kid-001
```

**README for PUBLIC repo:** `postman/README.md`

```markdown
# SeaTrace Commons KPI Demo (PUBLIC)

This repo publishes a **Postman collection only** — no environments, secrets, or scripts.

## Import & Run

1. Import `postman/collections/SeaTrace_Commons_KPI_Demo.postman_collection.json` into Postman.
2. Provide a runtime variable for the base URL:
   - **GUI:** Runner → Variables → `baseUrl = https://dev.seatrace.worldseafoodproducers.com`
   - **CLI:** `newman run postman/collections/SeaTrace_Commons_KPI_Demo.postman_collection.json --env-var baseUrl=https://dev.seatrace.worldseafoodproducers.com`

## Endpoints

- **Health** → `GET {{baseUrl}}/health` → Expects **200**
- **JWKS** → `GET {{baseUrl}}/.well-known/jwks.json` → Expects at least **1** key
- **QR Verify** → `POST {{baseUrl}}/api/v1/marketside/qr/verify`  
  Headers: `Content-Type: application/json`, `X-License-ID: PUBLIC-DEMO-LICENSE`  
  Body: `{ "qr_code": "DEMO-QR-0001" }`  
  Tests allow **200** (verified) or **429** (rate-limited)

## Security & Scope

- **No environment files** are published here.
- Private variables, keys, and CI scripts live in the **PRIVATE** repo.
- JWKS is expected at `{{baseUrl}}/.well-known/jwks.json`.

## CI (Public)

Pull Requests that modify collection JSON run a smoke test with Newman using `PUBLIC_BASE_URL`.
```

---

### **Choice D: k6 Load Test in PRIVATE CI**

**File:** `.github/workflows/k6-load-test.yml` (PRIVATE repo only)

```yaml
name: k6 Load Test (PRIVATE)

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run k6
        uses: grafana/k6-action@v0.3.1
        with:
          filename: tests/k6/k6-verify-burst.js
        env:
          BASE_URL: ${{ secrets.PRIVATE_BASE_URL }}
          LICENSE_KEY: ${{ secrets.LICENSE_KEY }}

      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: k6-results
          path: k6-results.json
```

---

### **Choice E: Gitleaks Policy + Pre-commit Rules**

**File:** `.gitleaks.toml` (both PUBLIC and PRIVATE repos)

```toml
title = "SeaTrace Gitleaks Config"

[[rules]]
id = "postman-api-key"
description = "Postman API Key"
regex = '''PMAK-[a-f0-9]{24}-[a-f0-9]{34}'''
tags = ["key", "postman"]

[[rules]]
id = "generic-api-key"
description = "Generic API Key"
regex = '''(?i)(api[_-]?key|apikey|api[_-]?token)['"]?\s*[:=]\s*['"]?([a-z0-9]{32,})'''
tags = ["key", "api"]

[[rules]]
id = "mongodb-connection-string"
description = "MongoDB Connection String"
regex = '''mongodb(\+srv)?:\/\/[^\s]+'''
tags = ["database", "mongodb"]

[[rules]]
id = "hmac-secret"
description = "HMAC Secret Key"
regex = '''(?i)(hmac[_-]?secret|hmac[_-]?key)['"]?\s*[:=]\s*['"]?([a-z0-9+/=]{32,})'''
tags = ["key", "hmac"]

[allowlist]
description = "Allowlist for false positives"
paths = [
    '''^\.gitleaks\.toml$''',
    '''(.*?)(jpg|gif|doc|pdf|bin)$'''
]
```

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-json
      - id: check-yaml
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: detect-private-key
        exclude: ^(keys/|\.env)
```

**Setup:**

```powershell
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test run
pre-commit run --all-files
```

---

## ✅ **READY-TO-PUSH PR PRACTICES**

### **PR #1: PUBLIC Commons Postman Collection** (SeaTrace-ODOO)

**Files to commit:**
```
postman/
├── README.md (NEW)
└── collections/
    └── SeaTrace_Commons_KPI_Demo.postman_collection.json (NEW)

scripts/
└── jwks-export.cjs (NEW)

.github/workflows/
└── postman-smoke-test.yml (NEW)

.gitleaks.toml (NEW)
.pre-commit-config.yaml (MODIFIED)
```

**Commit message:**
```
feat: Add PUBLIC Commons Postman collection + JWKS exporter

PUBLIC-UNLIMITED additions:
- postman/collections/SeaTrace_Commons_KPI_Demo.postman_collection.json
  * Health check, JWKS endpoint, QR verification
  * No secrets, no environment files
  * Tests for rate limiting, response time, headers
- scripts/jwks-export.cjs: Export public JWK from private key (Node 18+)
- .github/workflows/postman-smoke-test.yml: PR smoke tests with Newman
- .gitleaks.toml: Secret scanning policy
- postman/README.md: Usage guide for developers

Purpose: Enable Commons Good developer adoption
Target: seatrace.worldseafoodproducers.com demo readiness

Classification: PUBLIC-UNLIMITED (Commons Good)
FOR THE COMMONS GOOD! 🌍🐟🚀
```

---

### **PR #2: PRIVATE Investor Postman Workspace** (SeaTrace003)

**Files to commit:**
```
postman_backup/
├── workspaces/
│   └── index.json
├── collections/
│   └── index.json
└── environments/
    └── index.json (sanitized, no secrets)

scripts/
├── postman-enumerate-v2.ps1 (NEW)
└── postman-smoke-test.ps1 (NEW)

.github/workflows/
├── postman-backup.yml (NEW - nightly)
└── k6-load-test.yml (NEW - daily)

tests/k6/
└── k6-verify-burst.js (MOVED from PUBLIC repo)

.env.example (MODIFIED - add POSTMAN_API_KEY)
.gitleaks.toml (NEW)
```

**Commit message:**
```
feat(PRIVATE): Add Postman workspace backup + automation

PRIVATE-LIMITED additions:
- scripts/postman-enumerate-v2.ps1: Nightly backup via Postman API
- scripts/postman-smoke-test.ps1: Smoke test runner for investor endpoints
- postman_backup/: Sanitized workspace/collection/environment indexes
- .github/workflows/postman-backup.yml: Nightly GitHub Action
- .github/workflows/k6-load-test.yml: Daily load testing
- tests/k6/k6-verify-burst.js: MOVED from PUBLIC repo (contains license keys)
- .gitleaks.toml: Secret scanning (Postman API keys, HMAC secrets, MongoDB URIs)

Security:
- POSTMAN_API_KEY stored in GitHub secrets only
- Environment files sanitized (secrets redacted)
- Pre-commit hooks prevent credential leakage

Classification: PRIVATE-LIMITED (Investor Value)
FOR THE COMMONS GOOD (by protecting investor value)!
```

---

## 🎯 **YOUR DECISION MATRIX**

**Tell me which choices you want (A, B, C, D, E):**

- **Choice A:** Postman enumeration v2 + artifact upload → **PRIVATE repo**
- **Choice B:** PR smoke test → **PUBLIC repo**
- **Choice C:** JWKS exporter + README → **PUBLIC repo** ✅ **STRONGLY RECOMMENDED**
- **Choice D:** k6 load test → **PRIVATE repo**
- **Choice E:** Gitleaks + pre-commit → **BOTH repos**

**Example response:**
> "I want **C & E** for PUBLIC repo, and **A & D & E** for PRIVATE repo"

Then I'll create the exact files ready to commit.

---

## 🌊 **FOR THE COMMONS GOOD!**

This structure ensures:
- ✅ **PUBLIC repo:** Developer-friendly, no secrets, demo-ready
- ✅ **PRIVATE repo:** Investor value protected, automated backups, CI/CD
- ✅ **Separation:** Clear classification, audit trails, gitleaks protection
- ✅ **Recovery:** Multiple backup strategies, API enumeration, local search

**Classification:** PUBLIC-UNLIMITED (This guide)  
**FOR THE COMMONS GOOD!** 🌍🐟🚀

**Your move:** Tell me which choices (A/B/C/D/E) you want, and I'll generate the files.
