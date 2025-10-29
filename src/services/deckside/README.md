# 🌊 DeckSide Service

**For the Commons Good!**

---

## 🎯 Overview

**DeckSide** is the RECORD layer (Pillar 2) of the SeaTrace-ODOO system.

### **Role**
- Receives processed packets from SeaSide
- Validates vessel catch data against business rules
- Enriches data with additional context
- Routes valid records to DockSide for storage

### **Port**
- **8002** (localhost development)

---

## 🚀 Running the Service

```bash
cd C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO\src\services\deckside
python main.py
```

Service will start on `http://localhost:8002`

---

## 📡 API Endpoints

### **GET /health**
Health check with dependency status

```bash
curl http://localhost:8002/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "deckside",
  "version": "1.0.0",
  "correlation_id": "uuid",
  "dependencies": {
    "seaside": "reachable"
  }
}
```

### **POST /api/v1/process**
Process vessel packet from SeaSide

```bash
curl -X POST http://localhost:8002/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "packet_id": "uuid",
    "correlation_id": "uuid",
    "vessel_data": {
      "vessel_id": "WSP-001",
      "catch_weight": 500.0,
      "species": "Tuna",
      "location": {
        "latitude": 10.5,
        "longitude": 20.3
      }
    },
    "verified": true
  }'
```

**Response**:
```json
{
  "status": "processed",
  "packet_id": "uuid",
  "correlation_id": "uuid",
  "vessel_data_enriched": {...},
  "validation_results": {
    "valid": true,
    "errors": [],
    "warnings": []
  },
  "next_step": "route_to_dockside",
  "timestamp": "2025-10-16T00:00:00Z",
  "processing_duration_ms": 12.5
}
```

### **POST /api/v1/validate**
Standalone validation (pre-check)

```bash
curl -X POST http://localhost:8002/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "vessel_id": "WSP-001",
    "catch_weight": 500.0,
    "species": "Tuna"
  }'
```

### **GET /metrics**
Prometheus metrics endpoint

```bash
curl http://localhost:8002/metrics
```

---

## 🔍 Validation Rules

### **Catch Weight**
- Minimum: **0.1 kg**
- Maximum: **1,000,000 kg**
- Warning: Unusually large catch (>500,000 kg)

### **Species**
Approved list:
- Tuna, Salmon, Cod, Herring, Pollock
- Mackerel, Sardine, Anchovy, Haddock

### **Vessel ID**
- Convention: WSP- prefix
- Warning if not following convention

### **Location**
- Optional but recommended
- Latitude: -90 to 90
- Longitude: -180 to 180

---

## 🏗️ Architecture

### **Structured Logging**
All logs are JSON-formatted with correlation IDs for tracing across services.

```json
{
  "timestamp": "2025-10-16T00:00:00Z",
  "correlation_id": "uuid",
  "service": "deckside",
  "event": "packet_processing_completed",
  "packet_id": "uuid",
  "status": "processed"
}
```

### **Error Handling**
- Validation errors: 400-level status codes
- Processing errors: 500-level codes
- All errors include correlation_id

### **Security Headers**
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Strict-Transport-Security: max-age=31536000

---

## 🧪 Testing

### **Manual Test (PowerShell)**
```powershell
.\test_deckside_manual.ps1
```

### **Automated Tests**
```bash
pytest test_deckside.py -v
```

---

## 🔗 Dependencies

### **Upstream**
- **SeaSide (8001)** - Source of packets

### **Downstream**
- **DockSide (8003)** - Destination for validated records (future)

---

## 📊 4-Pillar Integration

```
Vessels → SeaSide (8001) → DeckSide (8002) → DockSide (8003) → MarketSide (8004)
          [HOLD]            [RECORD]          [STORE]           [EXCHANGE]
```

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

1. ✅ DeckSide service complete
2. ⏳ Build DockSide (8003)
3. ⏳ Build MarketSide (8004)
4. ⏳ Integrate all 4 pillars
5. ⏳ Add real Prometheus metrics
6. ⏳ Deploy with Docker Compose

---

**For the Commons Good!** 🌊🏈
