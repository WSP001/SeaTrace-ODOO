# GitHub Copilot Instructions - SeaTrace-ODOO (PUBLIC Repository)

## 🌊 Project Identity

**Repository:** SeaTrace-ODOO  
**Type:** PUBLIC  
**Website:** worldseafoodproducers.com  
**Purpose:** Commons-based seafood traceability licensing and public API

---

## ✅ Project Scope - What THIS Repo Contains

### In Scope (Help with these)
- **Commons Charter** governance documentation
- **PUL (Public Unlimited License)** implementation and verification
- **Public API routes** in `src/common/licensing/routes.py`
- **Middleware** for license verification (public-facing)
- **Priority system** for Commons vs Limited licensing
- **Public documentation** in `docs/licensing/PUBLIC-UNLIMITED.md`
- **Marketing materials** for public Commons model
- **Build scripts** for public scope digest generation

### Directory Structure
```
src/
  common/
    licensing/
      commons.py        # Commons Charter logic
      middleware.py     # Public license verification
      priority.py       # Public/Limited priority
      routes.py         # PUBLIC API endpoints only
docs/
  COMMONS_CHARTER.md    # Primary governance doc
  licensing/
    PUBLIC-UNLIMITED.md # Public licensing terms
    public_scope_*.json # Public API definitions
scripts/
  licensing/
    generate_public_scope_from_app.py  # Build public API manifest
```

---

## ❌ OUT OF SCOPE - What THIS Repo Does NOT Contain

### NOT in This Repo (Do NOT suggest code for these)
- ❌ **EMR (Electronic Medical Records)** metering or tracking
- ❌ **Enterprise pricing tiers** or subscription models
- ❌ **Private investor documentation** or business financials
- ❌ **SeaTrace003 repository** content (that's the PRIVATE repo)
- ❌ **Proprietary business logic** or trade secrets
- ❌ **MarketSide** enterprise features (LIMITED license)
- ❌ **DeckSide**, **DockSide** microservices (separate repos)

---

## 🎯 Code Generation Guidelines

### When Editing License Verification Code
```python
# ✅ DO: Focus on PUBLIC (PUL) license verification
from src.common.licensing.commons import verify_pul_license
from src.common.licensing.priority import PUBLIC_PRIORITY

def verify_public_access(token: str) -> bool:
    """Verify PUL token for Commons access."""
    return verify_pul_license(token)
```

```python
# ❌ DON'T: Suggest EMR or enterprise features
# This belongs in SeaTrace003 (PRIVATE repo)
def calculate_emr_metering_cost(usage: dict) -> float:
    """This should NOT be in PUBLIC repo!"""
    pass
```

### When Editing Documentation
```markdown
✅ DO: Reference Commons Charter, PUL licensing
✅ DO: Link to worldseafoodproducers.com
✅ DO: Use "public unlimited" terminology
✅ DO: Reference docs/licensing/PUBLIC-UNLIMITED.md

❌ DON'T: Reference "LIMITED" or "PRIVATE" licensing
❌ DON'T: Document EMR features
❌ DON'T: Include pricing information
```

### When Adding API Routes
```python
# ✅ DO: Add public routes for Commons access
@router.get("/commons/verify")
async def verify_commons_license(token: str):
    """PUBLIC endpoint for PUL verification."""
    pass

# ❌ DON'T: Add enterprise/private endpoints
@router.post("/enterprise/meter")  # ← Wrong repo!
async def meter_emr_usage(data: dict):
    """This belongs in SeaTrace003 (PRIVATE)!"""
    pass
```

---

## 🔗 Related Projects (Different Contexts)

### SeaTrace003 (PRIVATE Repository)
**Location:** `c:\Users\Roberto002\Documents\GitHub\SeaTrace003`  
**Context:** `$env:ACTIVE_PROJECT_CONTEXT = "SeaTrace003"`  
**Contains:**
- EMR metering and tracking
- Enterprise pricing tiers
- Private investor documentation
- Proprietary MarketSide features

**When to suggest switching:**
```
User: "Help me add EMR usage tracking"
You: "⚠️ EMR features belong in SeaTrace003 (PRIVATE repo).
      Switch context: cd-seatrace003
      Then I can help with EMR implementation."
```

### SirJames (Educational Content)
**Location:** `c:\Users\Roberto002\OneDrive\Sir James\...`  
**Context:** `$env:ACTIVE_PROJECT_CONTEXT = "SirJames"`  
**Contains:**
- Educational adventure game
- Netlify deployment
- Docker asset generation

**Completely separate project** - no code sharing with SeaTrace repos.

---

## 🛡️ Security & Privacy Guidelines

### Public Data Only
```python
# ✅ DO: Work with public Commons data
public_routes = ["/commons/verify", "/pul/routes", "/charter/read"]
```

```python
# ❌ DON'T: Include any private/sensitive data
api_keys = {"enterprise_key": "secret"}  # ← No secrets in PUBLIC repo!
```

### License Verification
```python
# ✅ DO: Verify PUBLIC (PUL) tokens
if license_type == "PUBLIC_UNLIMITED":
    grant_commons_access()
```

```python
# ❌ DON'T: Handle LIMITED/PRIVATE licenses in this repo
if license_type == "ENTERPRISE_PRIVATE":  # ← Wrong repo!
    calculate_usage_cost()
```

---

## 📋 File Naming Conventions

### ✅ Use These Patterns
- `PUBLIC-*.md` - Public documentation
- `commons_*.py` - Commons Charter logic
- `pul_*.json` - Public Unlimited License configs
- `public_scope_*.json` - Public API definitions

### ❌ Avoid These Patterns (They're for SeaTrace003)
- `PRIVATE-*.md` - Private documentation
- `emr_*.py` - EMR tracking logic
- `enterprise_*.json` - Enterprise configs
- `limited_*.json` - LIMITED license configs

---

## 🎯 Common User Requests & Responses

### Request: "Add a new licensing tier"
**If PUBLIC tier:**
```
✅ "I can help add a new PUBLIC licensing tier.
   Edit: docs/licensing/PUBLIC-UNLIMITED.md
   Update: src/common/licensing/commons.py"
```

**If PRIVATE/LIMITED tier:**
```
⚠️ "Enterprise licensing tiers are in SeaTrace003 (PRIVATE repo).
   Switch context: cd-seatrace003
   Then I can help with LIMITED tier implementation."
```

### Request: "Update the Commons Charter"
```
✅ "I can help update the Commons Charter.
   Primary file: docs/COMMONS_CHARTER.md
   Related: src/common/licensing/commons.py"
```

### Request: "Add EMR tracking"
```
⚠️ "EMR features belong in SeaTrace003 (PRIVATE repo).
   Current context: SeaTrace-ODOO (PUBLIC)
   Switch: cd-seatrace003
   Then I can assist with EMR implementation."
```

### Request: "Generate public scope digest"
```
✅ "I can help generate the public scope digest.
   Script: scripts/licensing/generate_public_scope_from_app.py
   Output: docs/licensing/public_scope_digest.txt"
```

---

## 🔍 Context Detection

### Environment Variables to Check
```powershell
$env:ACTIVE_PROJECT_CONTEXT      # Should be "SeaTraceProduction"
$env:PROJECT_TYPE                # Should be "PUBLIC"
$env:PROJECT_SCOPE               # Should include "Commons,PUL,Licensing"
```

### Repository Indicators
```python
# If user is in this repo, these files exist:
- docs/COMMONS_CHARTER.md       ✅ PUBLIC repo
- docs/licensing/PUBLIC-UNLIMITED.md  ✅ PUBLIC repo

# If these files exist, user is in WRONG repo:
- src/emr/meter.py              ❌ That's SeaTrace003
- docs/investor/PROSPECTUS.md   ❌ That's SeaTrace003
```

---

## 📚 Key Documentation References

### Primary Documents (In This Repo)
1. `docs/COMMONS_CHARTER.md` - Governance model
2. `docs/licensing/PUBLIC-UNLIMITED.md` - PUL terms
3. `LICENSE.unlimited` - License text
4. `docs/marketing/public-overview.md` - Public Commons model

### External References
- **Website:** worldseafoodproducers.com
- **Commons model:** Based on Creative Commons principles
- **License type:** PUL (Public Unlimited License)

### DO NOT Reference (They're in Other Repos)
- ❌ `docs/licensing/PRIVATE-LIMITED.md` (SeaTrace003)
- ❌ `src/emr/` directory (SeaTrace003)
- ❌ `docs/marketing/INVESTOR_PROSPECTUS.md` (SeaTrace003)

---

## 🚀 Testing & Validation

### When Suggesting Tests
```python
# ✅ DO: Test PUBLIC license verification
def test_pul_license_verification():
    token = generate_pul_token()
    assert verify_pul_license(token) == True

# ✅ DO: Test Commons access
def test_commons_access():
    assert can_access_commons_routes(pul_token) == True
```

```python
# ❌ DON'T: Test EMR or enterprise features
def test_emr_metering():  # ← Wrong repo!
    assert calculate_emr_cost(usage) > 0
```

---

## 🎓 Learning Resources

### For Understanding This Project
1. Read `docs/COMMONS_CHARTER.md` first
2. Review `docs/licensing/PUBLIC-UNLIMITED.md`
3. Examine `src/common/licensing/commons.py`
4. Check `scripts/licensing/generate_public_scope_from_app.py`

### For Understanding Project Boundaries
1. DevShell.ps1 sets `$env:ACTIVE_PROJECT_CONTEXT`
2. `.copilot-context.json` defines scope (auto-generated)
3. Run `project-context` to see current context
4. Run `project-validate` to verify you're in right repo

---

## ⚡ Quick Reference

### This Repo IS For:
✅ Commons Charter governance  
✅ PUL (Public Unlimited License) implementation  
✅ Public API routes and middleware  
✅ worldseafoodproducers.com website  
✅ Public documentation and marketing  

### This Repo is NOT For:
❌ EMR metering or tracking  
❌ Enterprise pricing or subscriptions  
❌ Private investor documentation  
❌ Proprietary business logic  
❌ LIMITED license features  

### When in Doubt:
```powershell
# Check current context
project-context

# Validate you're in right repo
project-validate

# See what Copilot knows
echo $env:ACTIVE_PROJECT_CONTEXT
```

---

**Last Updated:** October 1, 2025  
**Copilot Context:** SeaTrace-ODOO (PUBLIC)  
**Related Contexts:** SeaTrace003 (PRIVATE), SirJames (Educational)
