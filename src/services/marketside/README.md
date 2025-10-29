# 🌊 MarketSide Service

**For the Commons Good!**

---

## 🎯 Overview

**MarketSide** is the EXCHANGE layer (Pillar 4) of the SeaTrace-ODOO system.

### **Role**
- Publishes data to external markets
- Issues traceability certificates
- Manages PM Token verification (investor/endorser access)
- **PRIVATE KEY OUTGOING** - Signs all outgoing data
- Market exchange integration

### **Port**
- **8004** (localhost development)

---

## 🚀 Running the Service

```bash
cd C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO\src\services\marketside
python main.py
```

Service will start on `http://localhost:8004`

---

## 📡 API Endpoints

### **GET /health**
Health check with dependency status

```bash
curl http://localhost:8004/health
```

### **POST /api/v1/publish**
Publish data to market (PRIVATE KEY OUTGOING - signed)

```bash
curl -X POST http://localhost:8004/api/v1/publish \
  -H "Content-Type: application/json" \
  -d '{
    "packet_id": "uuid",
    "correlation_id": "uuid",
    "publish_type": "listing",
    "data": {...},
    "signature_required": true
  }'
```

### **POST /api/v1/pm/verify**
Verify PM Token for investor access

```bash
curl -X POST http://localhost:8004/api/v1/pm/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "PM-MARK-2024-004",
    "requested_access": "dashboard"
  }'
```

### **GET /api/v1/pm/tokens**
List available PM tokens (demo)

```bash
curl http://localhost:8004/api/v1/pm/tokens
```

### **POST /api/v1/certificate**
Issue traceability certificate (PRIVATE KEY OUTGOING - signed)

```bash
curl -X POST http://localhost:8004/api/v1/certificate \
  -H "Content-Type: application/json" \
  -d '{
    "packet_id": "uuid",
    "correlation_id": "uuid",
    "vessel_id": "WSP-001",
    "include_full_chain": true
  }'
```

### **GET /api/v1/stats**
Market statistics

```bash
curl http://localhost:8004/api/v1/stats
```

---

## 🔐 PM Tokens (Proceeding Master)

### **Available Tokens (Demo)**:

1. **PM-SEAS-2024-001** - Fisheries Digital Monitoring
   - Access: SeaSide only
   - Role: Fisheries Monitor

2. **PM-DECK-2024-002** - Seafood Contributors
   - Access: SeaSide + DeckSide
   - Role: Contributor

3. **PM-DOCK-2024-003** - Business Managers
   - Access: SeaSide + DeckSide + DockSide
   - Role: Manager

4. **PM-MARK-2024-004** - Investors (Full Access)
   - Access: All 4 pillars
   - Role: Investor
   - Dashboard access included

---

## 🔑 PRIVATE KEY OUTGOING

### **What Gets Signed**:
- Published listings
- Market transactions
- Traceability certificates
- External API responses

### **Signature Flow**:
```
Data → Hash (BLAKE2) → Sign (RSA Private Key) → Base64 → Include in response
```

### **Verification**:
External parties use SeaTrace PUBLIC KEY to verify signatures.

---

## 📊 4-Pillar Integration

```
Vessels → SeaSide (8001) → DeckSide (8002) → DockSide (8003) → MarketSide (8004) → External Markets
          [HOLD]            [RECORD]          [STORE]           [EXCHANGE]
          PUBLIC KEY        Validation        Database          PRIVATE KEY
          INCOMING          Logic             Storage           OUTGOING
```

---

## 🧪 Testing

### **Manual Test (PowerShell)**
```powershell
.\test_marketside_manual.ps1
```

### **Automated Tests**
```bash
pytest test_marketside.py -v
```

---

## 🔗 Dependencies

### **Upstream**
- **DockSide (8003)** - Source of stored data

### **Downstream**
- External markets
- Consumer APIs
- Investor dashboards

---

## 📦 Dependencies

```
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
structlog>=23.2.0
httpx>=0.25.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

---

## 🎯 Next Steps

1. ✅ MarketSide service complete
2. ⏳ Integrate PacketCryptoHandler (PRIVATE KEY OUTGOING)
3. ⏳ Connect to real market APIs
4. ⏳ Add PM Token database
5. ⏳ Deploy all 4 pillars together
6. ⏳ Docker Compose setup

---

**For the Commons Good!** 🌊🏈
