# 🌊 DockSide Service

**For the Commons Good!**

---

## 🎯 Overview

**DockSide** is the STORE layer (Pillar 3) of the SeaTrace-ODOO system.

### **Role**
- Receives validated packets from DeckSide
- Stores packet data persistently
- Provides retrieval by packet ID
- Provides query capabilities with filters
- Routes stored data to MarketSide (future)

### **Port**
- **8003** (localhost development)

---

## 🚀 Running the Service

```bash
cd C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO\src\services\dockside
python main.py
```

Service will start on `http://localhost:8003`

---

## 📡 API Endpoints

### **GET /health**
Health check with dependency status

```bash
curl http://localhost:8003/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "dockside",
  "version": "1.0.0",
  "correlation_id": "uuid",
  "dependencies": {
    "deckside": "reachable"
  },
  "storage": {
    "mode": "memory",
    "packet_count": 42
  }
}
```

### **POST /api/v1/store**
Store validated packet from DeckSide

```bash
curl -X POST http://localhost:8003/api/v1/store \
  -H "Content-Type: application/json" \
  -d '{
    "packet_id": "uuid",
    "correlation_id": "uuid",
    "vessel_data": {
      "vessel_id": "WSP-001",
      "catch_weight": 500.0,
      "species": "Tuna",
      "verified": true
    },
    "validation_passed": true,
    "enriched_data": {...}
  }'
```

**Response**:
```json
{
  "status": "stored",
  "packet_id": "uuid",
  "correlation_id": "uuid",
  "stored_at": "2025-10-16T00:00:00Z",
  "storage_location": "memory://uuid"
}
```

### **GET /api/v1/retrieve/{packet_id}**
Retrieve packet by ID

```bash
curl http://localhost:8003/api/v1/retrieve/uuid-123
```

**Response**:
```json
{
  "status": "found",
  "packet_id": "uuid-123",
  "correlation_id": "uuid",
  "found": true,
  "data": {
    "packet_id": "uuid-123",
    "vessel_id": "WSP-001",
    "catch_weight": 500.0,
    "species": "Tuna",
    "stored_at": "2025-10-16T00:00:00Z",
    ...
  }
}
```

### **POST /api/v1/query**
Query packets with filters

```bash
curl -X POST http://localhost:8003/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "vessel_id": "WSP-001",
    "species": "Tuna",
    "verified_only": true,
    "limit": 10
  }'
```

**Response**:
```json
{
  "status": "success",
  "correlation_id": "uuid",
  "total_count": 5,
  "returned_count": 5,
  "packets": [...]
}
```

### **GET /api/v1/stats**
Get storage statistics

```bash
curl http://localhost:8003/api/v1/stats
```

**Response**:
```json
{
  "total_packets": 100,
  "verified_packets": 85,
  "unverified_packets": 15,
  "total_catch_weight": 50000.0,
  "species_breakdown": {
    "Tuna": 50,
    "Salmon": 30,
    "Cod": 20
  },
  "storage_utilization": 1.0,
  "oldest_packet_date": "2025-10-01T00:00:00Z",
  "newest_packet_date": "2025-10-16T00:00:00Z"
}
```

### **GET /metrics**
Prometheus metrics endpoint

```bash
curl http://localhost:8003/metrics
```

---

## 🗄️ Storage

### **Phase 1: In-Memory Storage** ✅
- Fast access
- No external dependencies
- Limited capacity (10,000 packets default)
- Data lost on restart

### **Phase 2: PostgreSQL** (Future)
- Persistent storage
- Unlimited capacity
- ACID compliance
- Advanced queries

---

## 🔍 Query Capabilities

### **Available Filters**:
- `vessel_id` - Filter by specific vessel
- `species` - Filter by species
- `date_from` / `date_to` - Date range
- `verified_only` - Only verified packets
- `limit` / `offset` - Pagination

### **Query Examples**:

**All packets from a vessel**:
```json
{
  "vessel_id": "WSP-001",
  "limit": 100
}
```

**Verified Tuna catches**:
```json
{
  "species": "Tuna",
  "verified_only": true
}
```

**Recent catches (last 7 days)**:
```json
{
  "date_from": "2025-10-09T00:00:00Z",
  "date_to": "2025-10-16T00:00:00Z"
}
```

---

## 🏗️ Architecture

### **Structured Logging**
All operations logged with correlation IDs in JSON format.

### **Storage Layer**
- Abstracted storage interface
- Easy to swap implementations (memory → PostgreSQL)
- Statistics and monitoring built-in

### **Error Handling**
- Validation failures handled gracefully
- Storage failures logged and reported
- Correlation IDs in all errors

---

## 🧪 Testing

### **Manual Test (PowerShell)**
```powershell
.\test_dockside_manual.ps1
```

### **Automated Tests**
```bash
pytest test_dockside.py -v
```

---

## 🔗 Dependencies

### **Upstream**
- **DeckSide (8002)** - Source of validated packets

### **Downstream**
- **MarketSide (8004)** - Destination for exchange (future)

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

1. ✅ DockSide service complete (in-memory storage)
2. ⏳ Build MarketSide (8004)
3. ⏳ Integrate all 4 pillars
4. ⏳ Add PostgreSQL storage
5. ⏳ Add real Prometheus metrics
6. ⏳ Deploy with Docker Compose

---

**For the Commons Good!** 🌊🏈
