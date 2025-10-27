# 🧹 SeaTrace PUBLIC Repo Housekeeping Plan
## Separating PUBLIC (Commons Good) from PRIVATE (Investor Value)

**Date:** October 26, 2025  
**Objective:** Clean SeaTrace-ODOO (PUBLIC repo) by removing all PRIVATE IP and service implementations

---

## 🎯 **The Problem:**

The current `SeaTrace-ODOO` PUBLIC repository contains **PRIVATE intellectual property** that should be in `SeaTrace003` (PRIVATE repo):

- ❌ `services/` directory - Contains Four Pillars microservice implementations (seaside, deckside, dockside, marketside)
- ❌ Private deployment scripts - Scripts that reveal infrastructure details
- ❌ ML models and algorithms - NetworkX graph-based quality scoring
- ❌ $CHECK KEY logic - Prospectus calculations (investor value IP)

---

## ✅ **The Solution: PUBLIC vs PRIVATE Separation**

### **PUBLIC REPO (SeaTrace-ODOO) - KEEPS:**

```
SeaTrace-ODOO/
├── public_models/          # Pydantic schemas (PUBLIC data structures only)
├── public_api/             # Verification proxy (QR verification endpoints)
├── staging/                # Demo website files (seatrace.worldseafoodproducers.com)
├── demo/                   # Demo seeds, sample data
├── docs/                   # PUBLIC architecture guides, API documentation
├── tests/                  # PUBLIC contract tests (NO private logic tests)
├── postman/
│   ├── collections/
│   │   └── SeaTrace_Commons_KPI_Demo.postman_collection.json
│   └── README.md
├── scripts/
│   ├── jwks-export.cjs                     # PUBLIC key exporter (KEEP)
│   ├── audit-separation.ps1                # PUBLIC/PRIVATE validation (KEEP)
│   └── Verify-Public-Separation.ps1        # Separation checker (KEEP)
├── .gitleaks.toml
├── .pre-commit-config.yaml
├── INFRASTRUCTURE_SSL_FIX.md
└── README.md
```

### **PRIVATE REPO (SeaTrace003) - MOVES:**

```
SeaTrace003/
├── services/                               # ⬅️ MOVE FROM PUBLIC
│   ├── common/
│   │   └── ratelimit.py                    # Rate limiting logic
│   ├── seaside/
│   │   ├── Dockerfile
│   │   ├── packet_handler.py               # Precise GPS tracking
│   │   ├── app.py
│   │   └── models.py
│   ├── deckside/
│   │   ├── Dockerfile
│   │   ├── prospectus.py                   # $CHECK KEY logic (CRITICAL IP)
│   │   ├── processor.py                    # Packet switching handler
│   │   ├── models.py                       # Financial algorithms
│   │   └── middleware.py
│   ├── dockside/
│   │   ├── Dockerfile
│   │   ├── reconciliation.py               # Prospectus vs actual
│   │   ├── financial.py                    # Investor payouts
│   │   └── app.py
│   └── marketside/
│       ├── Dockerfile
│       ├── qr_verification.py
│       ├── investor_dashboard.py           # ROI dashboards
│       └── app.py
├── scripts/                                # ⬅️ MOVE PRIVATE SCRIPTS
│   ├── initialize_packet_switching.ps1     # PRIVATE: Infrastructure setup
│   ├── postman_seatrace_collection.ps1     # PRIVATE: API enumeration
│   └── deploy_*.ps1                        # PRIVATE: Deployment scripts (if found)
├── venv/Lib/site-packages/networkx/        # ⬅️ MOVE ML MODELS
├── .gitleaks.toml
├── .pre-commit-config.yaml
├── .github/workflows/
│   └── k6-load-test.yml                    # PRIVATE: Load testing
└── *.key, *.pem                            # PRIVATE: Encryption keys
```

---

## 📋 **Housekeeping Execution Plan**

### **Step 1: Remove PRIVATE Files from Git Tracking**

```powershell
# Current Directory: C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO

# Remove services/ directory (Four Pillars implementations)
git rm --cached -r "services/" -f

# Remove private scripts
git rm --cached "scripts/initialize_packet_switching.ps1" -f
git rm --cached "scripts/postman_seatrace_collection.ps1" -f
git rm --cached "scripts/integrate-proceeding-master.ps1" -f

# Note: Keep jwks-export.cjs, audit-separation.ps1, Verify-Public-Separation.ps1
```

### **Step 2: Update .gitignore to Block Future Private Commits**

```gitignore
# --- Private Implementation (MUST stay in SeaTrace003) ---
/services/
/scripts/initialize_packet_switching.ps1
/scripts/postman_seatrace_collection.ps1
/scripts/integrate-proceeding-master.ps1
/scripts/deploy_*.ps1

# Private keys and secrets
*.key
*.pem
.env
.env.local
.env.production

# Python virtual environments
/.venv/
/venv/
/Lib/

# ML models (NetworkX)
/networkx/

# Private test files
/tests/services/

# Python cache
*.pyc
__pycache__/
.pytest_cache/
.mypy_cache/
```

### **Step 3: Commit the Cleanup**

```powershell
git add .gitignore
git commit -m "refactor(housekeeping): Migrate private service logic to SeaTrace003

WHAT WAS REMOVED (moved to PRIVATE repo):
- services/ directory (all Four Pillars microservice implementations)
- scripts/initialize_packet_switching.ps1 (infrastructure setup)
- scripts/postman_seatrace_collection.ps1 (API enumeration)
- scripts/integrate-proceeding-master.ps1 (integration logic)

WHAT STAYS (PUBLIC Integration Toolkit):
- public_models/ (PUBLIC Pydantic schemas)
- public_api/ (QR verification proxy)
- staging/ (demo website)
- demo/ (demo seeds)
- docs/ (PUBLIC architecture guides)
- tests/ (PUBLIC contract tests)
- postman/ (Commons KPI Demo collection)
- scripts/jwks-export.cjs (PUBLIC key exporter)
- scripts/audit-separation.ps1 (validation)
- scripts/Verify-Public-Separation.ps1 (separation checker)

WHY:
The DeckSide Fork is the core innovation ($4.2M valuation):
- PUBLIC (#CATCH KEY): Estimated catch weight (deckhand tally) → Commons Good
- PRIVATE ($CHECK KEY): Prospectus calculations (ML quality, ROI) → Investor Value

This separation protects our IP while enabling Commons Good transparency.

CLASSIFICATION:
- PUBLIC-UNLIMITED: Approximate GPS, QR verification, JWKS public keys
- PRIVATE-LIMITED: Precise GPS, $CHECK KEY logic, ML models, financial dashboards

NEXT STEPS:
1. Deploy SSL wildcard certificate (fix net::ERR_CERT_COMMON_NAME_INVALID)
2. Configure seatrace.worldseafoodproducers.com PUBLIC demo
3. Build SeaTrace003 PRIVATE repo with investor dashboard

For the Commons Good! 🌍🐟🚀"
```

### **Step 4: Push to Remote**

```powershell
git push origin main
```

---

## 🔐 **Security Validation Checklist**

After housekeeping, verify:

- [ ] `services/` directory is no longer tracked by git
- [ ] Private scripts are removed from git tracking
- [ ] `.gitignore` blocks `/services/`, `/scripts/initialize_*`, `*.key`, `*.pem`
- [ ] `gitleaks protect --staged` returns 0 leaks
- [ ] `scripts/Verify-Public-Separation.ps1` passes all checks
- [ ] PUBLIC repo contains ONLY Commons Good integration toolkit
- [ ] No $CHECK KEY logic, ML models, or precise GPS in PUBLIC repo

---

## 📊 **Separation Scorecard**

### **PUBLIC-UNLIMITED (SeaTrace-ODOO)**
- ✅ Approximate GPS only (FAO zones)
- ✅ QR verification endpoints
- ✅ JWKS public keys (NO private `d` component)
- ✅ Postman Commons KPI Demo collection
- ✅ Health checks and status endpoints
- ✅ Demo website files (staging/)
- ✅ PUBLIC architecture documentation

### **PRIVATE-LIMITED (SeaTrace003)**
- 🔒 Precise GPS coordinates (6 decimal places)
- 🔒 $CHECK KEY logic (prospectus calculations)
- 🔒 ML model predictions (quality scores)
- 🔒 Financial dashboards (ROI tracking)
- 🔒 Packet switching handler (DeckSide Fork)
- 🔒 Rate limiting logic
- 🔒 Deployment scripts
- 🔒 Load testing (k6 workflows)

---

## 🚀 **What Happens After Housekeeping?**

### **Phase 1.2: Fix Security (SSL Certificate)**
Implement `INFRASTRUCTURE_SSL_FIX.md` to fix `net::ERR_CERT_COMMON_NAME_INVALID`

### **Phase 1.3: Deploy PUBLIC Demo V1**
Configure `seatrace.worldseafoodproducers.com` with:
- Four Pillars visualization
- QR scan demo (approximate GPS only)
- Postman collection download link
- Commons Good messaging

### **Phase 2: Build PRIVATE Files**
Create in SeaTrace003:
- `scripts/postman-enumerate-v2.ps1` (Choice A)
- `.github/workflows/k6-load-test.yml` (Choice D)
- `.gitleaks.toml` + `.pre-commit-config.yaml` (Choice E)

### **Phase 3: Link Demos**
Add "Investor Access" button on PUBLIC demo → PRIVATE dashboard

### **Phase 4: Layer $10M+ Revenue Streams**
Add to demo:
- Institutions & Insurers section (GFW/MCP Flywheel - $10k/month SaaS)
- $CHECK KEY 2.0 (Tradable Asset Reports with Urner Barry pricing)
- MarketSide EXCHANGE "Coming Soon" page (2% transaction fee)
- Platform Status page (Grafana dashboard showing 10k req/sec)

---

## 📞 **Support**

- **Email:** scott@worldseafoodproducers.com
- **Demo:** https://seatrace.worldseafoodproducers.com
- **Postman:** `postman/collections/SeaTrace_Commons_KPI_Demo.postman_collection.json`

---

**For the Commons Good! 🌍🐟🚀**
