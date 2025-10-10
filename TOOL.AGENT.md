# Tool Agent (SeaTrace-ODOO - PUBLIC)

**Purpose:** Define available tools and workflows for AI agents  
**Scope:** PUBLIC Commons Good features only  
**Integration:** 4-Pillar Microservices + Postman Collection

---

## 🎯 **4-PILLAR MICROSERVICES ARCHITECTURE**

### **Pillar 1: SeaSide (HOLD)** 🌊
**Purpose:** Vessel tracking and initial data capture  
**Port:** 8000  
**Endpoints:**
- `GET /api/v1/seaside/vessels` - List all vessels
- `GET /api/v1/seaside/vessels/{vessel_id}` - Get vessel details
- `POST /api/v1/seaside/vessels/{vessel_id}/positions` - Submit position
- `POST /api/v1/seaside/quality/score` - Generate quality score

**Agent Use Cases:**
```python
# IF vessel position received THEN record in database
if vessel_position_update:
    await post("/api/v1/seaside/vessels/{vessel_id}/positions", data)
    
# IF quality check requested THEN calculate score
if quality_check_requested:
    score = await post("/api/v1/seaside/quality/score", fishing_data)
```

---

### **Pillar 2: DeckSide (RECORD)** 📋
**Purpose:** Catch verification and certification  
**Port:** 8001  
**Endpoints:**
- `GET /api/v1/deckside/catches` - List all catches
- `GET /api/v1/deckside/catches/{catch_id}` - Get catch details
- `POST /api/v1/deckside/catches` - Submit catch data
- `POST /api/v1/deckside/qrcode` - Generate QR code

**Agent Use Cases:**
```python
# IF catch recorded THEN generate QR code
if catch_recorded:
    catch_id = await post("/api/v1/deckside/catches", catch_data)
    qr_code = await post("/api/v1/deckside/qrcode", {"catch_id": catch_id})
    
# IF species verification needed THEN check database
if species_verification:
    catch = await get(f"/api/v1/deckside/catches/{catch_id}")
    verify_species(catch["items"])
```

---

### **Pillar 3: DockSide (STORE)** 🏭
**Purpose:** Supply chain and storage management  
**Port:** 8002  
**Endpoints:**
- `GET /api/v1/dockside/processing` - List processing records
- `GET /api/v1/dockside/processing/{processing_id}` - Get processing details
- `POST /api/v1/dockside/processing` - Submit processing data
- `POST /api/v1/dockside/bone/files` - Store BONE file

**Agent Use Cases:**
```python
# IF temperature alert THEN log and notify
if temperature_out_of_range:
    await post("/api/v1/dockside/processing", {
        "temperature_logs": [{"temperature_celsius": temp, "alert": True}]
    })
    send_alert(facility_manager)
    
# IF quality certificate generated THEN store in BONE
if quality_certificate_ready:
    await post("/api/v1/dockside/bone/files", {
        "file_name": "certificate.pdf",
        "processing_id": processing_id,
        "file_content": base64_encode(pdf)
    })
```

---

### **Pillar 4: MarketSide (EXCHANGE)** 💰
**Purpose:** Trading platform and consumer interface  
**Port:** 8003  
**Endpoints:**
- `GET /api/v1/marketside/transactions` - List transactions
- `GET /api/v1/marketside/transactions/{transaction_id}` - Get transaction details
- `POST /api/v1/marketside/transactions` - Submit transaction
- `GET /api/v1/marketside/verify/{product_id}` - Verify product authenticity

**Agent Use Cases:**
```python
# IF product verification requested THEN check blockchain
if consumer_scans_qr:
    product = await get(f"/api/v1/marketside/verify/{product_id}")
    display_traceability(product)
    
# IF transaction completed THEN record and update inventory
if transaction_completed:
    await post("/api/v1/marketside/transactions", transaction_data)
    update_inventory(product_id, -quantity)
```

---

## 🛠️ **AVAILABLE TOOLS**

### **1. Postman Collection Generator**
**Location:** `scripts/postman_seatrace_collection.ps1`  
**Purpose:** Generate Postman API collection for testing  
**Usage:**
```powershell
# Generate Postman collection
.\scripts\postman_seatrace_collection.ps1

# Output:
# - postman/SeaTrace_Collection.json
# - postman/Local_Development_Environment.json
# - postman/Kubernetes_Development_Environment.json
# - postman/Production_Environment.json
```

**Agent Integration:**
```python
# IF API testing needed THEN generate Postman collection
if api_testing_required:
    run_command("pwsh scripts/postman_seatrace_collection.ps1")
    import_to_postman("postman/SeaTrace_Collection.json")
```

---

### **2. Health Check Script**
**Location:** `scripts/check_health.ps1` (to be created)  
**Purpose:** Verify all 4 pillars are running  
**Usage:**
```powershell
# Check health of all services
.\scripts\check_health.ps1

# Expected output:
# ✅ SeaSide (HOLD): http://localhost:8000/health
# ✅ DeckSide (RECORD): http://localhost:8001/health
# ✅ DockSide (STORE): http://localhost:8002/health
# ✅ MarketSide (EXCHANGE): http://localhost:8003/health
```

**Agent Integration:**
```python
# IF deployment complete THEN verify health
if deployment_complete:
    health_status = run_command("pwsh scripts/check_health.ps1")
    if not all_services_healthy(health_status):
        rollback_deployment()
```

---

### **3. License Validator**
**Location:** `src/common/licensing/middleware.py`  
**Purpose:** Validate JWS licenses (PUL or PL)  
**Usage:**
```python
from src.common.licensing.middleware import LicenseMiddleware

# Validate license
middleware = LicenseMiddleware(app)
is_valid = await middleware._verify_jws(license_token)

# Check tier
if license_payload["tier"] == "PUL":
    # Free tier - basic features only
    allow_vessel_tracking()
elif license_payload["tier"] == "PL":
    # Paid tier - advanced features
    allow_advanced_analytics()
```

**Agent Integration:**
```python
# IF API request received THEN validate license
if api_request:
    license = extract_license_from_header(request)
    if not validate_license(license):
        return 401  # Unauthorized
    
    # IF license valid THEN check tier and apply limits
    tier = license["tier"]
    if tier == "PUL":
        apply_rate_limit(free_tier_limits)
    elif tier == "PL":
        apply_rate_limit(paid_tier_limits)
```

---

## 🤖 **AGENT WORKFLOWS**

### **Workflow 1: Vessel-to-Market Traceability**
```python
# Step 1: Vessel reports position (SeaSide)
vessel_position = await post("/api/v1/seaside/vessels/{vessel_id}/positions", {
    "latitude": 42.3601,
    "longitude": -71.0589,
    "timestamp": now()
})

# Step 2: Catch recorded (DeckSide)
catch_data = await post("/api/v1/deckside/catches", {
    "vessel_id": vessel_id,
    "species_code": "COD",
    "weight_kg": 450.5
})

# Step 3: Processing at facility (DockSide)
processing_data = await post("/api/v1/dockside/processing", {
    "catch_id": catch_data["catch_id"],
    "facility_name": "Coastal Processing Plant",
    "products": [{"description": "Atlantic cod fillets", "weight_kg": 300.2}]
})

# Step 4: Sale to consumer (MarketSide)
transaction = await post("/api/v1/marketside/transactions", {
    "product_id": processing_data["products"][0]["product_id"],
    "buyer_id": "CONSUMER-001",
    "price_per_unit": 12.50
})

# Step 5: Consumer verifies product (MarketSide)
verification = await get(f"/api/v1/marketside/verify/{product_id}")
# Returns: vessel, catch, processing, transaction history
```

---

### **Workflow 2: Quality Alert Automation**
```python
# IF temperature out of range THEN alert and log
if temperature > 4.0:  # Celsius
    # Log temperature violation
    await post("/api/v1/dockside/processing", {
        "temperature_logs": [{
            "temperature_celsius": temperature,
            "alert": True,
            "location": sensor_location
        }]
    })
    
    # Send alert to facility manager
    send_email(facility_manager, "Temperature Alert", f"Temp: {temperature}°C")
    
    # IF critical THEN stop processing
    if temperature > 7.0:
        await post("/api/v1/dockside/processing/{processing_id}/stop", {
            "reason": "Critical temperature violation"
        })
```

---

### **Workflow 3: License Tier Enforcement**
```python
# IF API request THEN check license tier
license = extract_license(request)
tier = license["tier"]

if tier == "PUL":  # Free tier
    # Allow basic features only
    if endpoint in ["/api/v1/seaside/vessels", "/api/v1/deckside/catches"]:
        allow_request()
    else:
        return 402  # Payment Required
        
elif tier == "PL":  # Paid tier
    # Allow all features
    allow_request()
    
    # Apply rate limits based on tier
    if tier == "PL-BASIC":
        rate_limit = 100  # requests/hour
    elif tier == "PL-ENTERPRISE":
        rate_limit = 10000  # requests/hour
```

---

## 📋 **TOOL DISCOVERY**

### **Available Scripts:**
```powershell
# List all available scripts
Get-ChildItem scripts/*.ps1

# Expected:
# - postman_seatrace_collection.ps1 (✅ Available)
# - check_health.ps1 (⏳ To be created)
# - start_all.ps1 (⏳ To be created)
# - preflight.ps1 (⏳ To be created)
```

### **Available Endpoints:**
```python
# Discover all endpoints
endpoints = [
    # SeaSide (HOLD)
    "GET /api/v1/seaside/vessels",
    "POST /api/v1/seaside/vessels/{vessel_id}/positions",
    
    # DeckSide (RECORD)
    "GET /api/v1/deckside/catches",
    "POST /api/v1/deckside/catches",
    
    # DockSide (STORE)
    "GET /api/v1/dockside/processing",
    "POST /api/v1/dockside/processing",
    
    # MarketSide (EXCHANGE)
    "GET /api/v1/marketside/transactions",
    "POST /api/v1/marketside/transactions"
]
```

---

## 🌊 **FOR THE COMMONS GOOD**

### **Agent Principles:**
1. ✅ **Transparency** - All actions logged with correlation IDs
2. ✅ **Accountability** - Every transaction traceable
3. ✅ **Optimization** - Automated quality checks
4. ✅ **Collaboration** - Multi-agent workflows

### **Agent Boundaries:**
- ✅ **PUBLIC features only** - No private enterprise logic
- ✅ **PUL tier enforcement** - Free tier gets basic features
- ✅ **Rate limiting** - Prevent abuse
- ✅ **Audit logging** - All actions recorded

---

**© 2025 SeaTrace-ODOO Tool Agent**  
**Status:** Active  
**Review Cycle:** Quarterly  
**Integration:** 4-Pillar Microservices + Postman Collection
