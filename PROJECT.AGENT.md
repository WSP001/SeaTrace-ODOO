# Project Agent (SeaTrace-ODOO - PUBLIC)

**Project Type:** PUBLIC Commons Good Repository  
**Scope:** Maritime tracking, Commons Charter, PUL licensing  
**Boundary:** Never include private enterprise features

---

## 🌊 **PROJECT SCOPE**

### **What Belongs Here (PUBLIC):**
- ✅ SeaSide (HOLD) - Vessel tracking, quota management
- ✅ DeckSide (RECORD) - Catch recording, species tracking
- ✅ DockSide (STORE) - Cold storage, port logistics
- ✅ Commons Charter - Public licensing framework
- ✅ PUL (Public Unlimited License) - Free tier access
- ✅ JWK/JWS - License verification (public keys only)
- ✅ Health endpoints - Service monitoring
- ✅ Public API documentation

### **What Does NOT Belong Here (PRIVATE):**
- ❌ MarketSide (EXCHANGE) - Pricing/trading → SeaTrace003
- ❌ EMR Metering - Usage tracking → SeaTrace003
- ❌ Entitlements - Quota enforcement → SeaTrace003
- ❌ Billing - Stripe integration → SeaTrace003
- ❌ Investor Dashboard - Financial metrics → SeaTrace003
- ❌ Pricing Algorithms - Dynamic tiers → SeaTrace003
- ❌ Private Keys - License signing → SeaTrace003

---

## 🌐 **INTERFACES**

### **REST API to PRIVATE Repo:**
```python
# SeaTrace-ODOO (PUBLIC) calls SeaTrace003 (PRIVATE) for enterprise features

# Example: PUBLIC vessel tracking triggers PRIVATE EMR metering
async def record_vessel_activity(vessel_id: int):
    # PUBLIC: Track vessel (this repo)
    vessel_data = await track_vessel(vessel_id)
    
    # PRIVATE: Meter EMR usage (API call to SeaTrace003)
    if has_enterprise_license():
        async with aiohttp.ClientSession() as session:
            await session.post(
                "https://api.seatrace003.private/emr/meter",
                json={"vessel_id": vessel_id, "activity": vessel_data},
                headers={"Authorization": f"Bearer {PRIVATE_API_KEY}"}
            )
```

---

## 🛡️ **SECURITY BOUNDARIES**

### **Safe to Commit (PUBLIC):**
1. ✅ **Public verification keys** - For JWS license validation
2. ✅ **API endpoint URLs** - Public endpoints only
3. ✅ **Configuration templates** - With placeholders, no secrets
4. ✅ **Documentation** - Architecture, API docs, Commons Charter
5. ✅ **Test data** - Synthetic/anonymized data only

### **Never Commit (KEEP PRIVATE):**
1. ❌ **Private signing keys** - Keep in SeaTrace003 or Vault
2. ❌ **Real API keys** - Use environment variables
3. ❌ **Customer data** - No PII, no real vessel data
4. ❌ **Pricing models** - Keep in SeaTrace003
5. ❌ **Database credentials** - Use `.env` (gitignored)

---

## 🎯 **COMMONS CHARTER PRINCIPLES**

### **10-15% Revenue Sharing:**
```python
# PUBLIC repo implements transparency endpoint
@router.get("/api/commons/fund")
async def get_commons_fund_status():
    """
    Public endpoint showing Commons Fund contributions.
    Data comes from PRIVATE repo but is made public here.
    """
    return {
        "total_contributed": await get_total_contributions(),
        "current_balance": await get_fund_balance(),
        "projects_funded": await get_funded_projects(),
        "transparency_report_url": "https://worldseafoodproducers.com/commons/report"
    }
```

### **Free Tier (PUL):**
- ✅ Unlimited vessel tracking
- ✅ Unlimited catch recording
- ✅ Basic cold storage tracking
- ✅ Community support
- ❌ No advanced analytics (enterprise only)
- ❌ No EMR metering (enterprise only)

---

## 🎯 **DEVSHELL INTEGRATION**

### **Use `$env:ACTIVE_PROJECT_CONTEXT` for AI Safety:**
```powershell
# When in SeaTrace-ODOO (PUBLIC)
$env:ACTIVE_PROJECT_CONTEXT = "SeaTrace-ODOO"

# AI assistants check this before suggesting code
if ($env:ACTIVE_PROJECT_CONTEXT -eq "SeaTrace-ODOO") {
    # OK to suggest vessel tracking, catch recording, public features
    # NOT OK to suggest pricing, EMR metering, billing
} else {
    # Redirect: "That belongs in SeaTrace003 (PRIVATE repo)"
}
```

---

## 📋 **GOVERNANCE**

### **Source of Truth Documents:**
- **CODE.AGENT.md** - Coding standards (already exists)
- **PROJECT.AGENT.md** - This file (project scope)
- **PROJECT_MANIFEST.json** - Service configuration
- **README.md** - Public documentation
- **CONTRIBUTING.md** - Contribution guidelines

### **Roadmap:**
- [x] Commons Charter implementation
- [x] PUL (Public Unlimited License)
- [x] JWK/JWS license validation
- [ ] CI/CD: Lint, test, secret scan
- [ ] Public API documentation (OpenAPI)
- [ ] Community contribution guidelines
- [ ] Docker Compose for local development

---

## 🌊 **FOR THE COMMONS GOOD**

**Remember:** This PUBLIC repo is the foundation for the Commons!

- **Free tier** enables community access
- **Transparent reporting** builds trust
- **Open architecture** encourages contributions
- **Private enterprise** sustains public good

**We build public features to serve the Commons!** 🌊

---

**© 2025 SeaTrace-ODOO Project Agent**  
**Status:** Active  
**Review Cycle:** Quarterly  
**License:** Commons Charter + PUL
