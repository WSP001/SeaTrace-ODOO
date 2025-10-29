# 🌊 SeaSide Service

**For the Commons Good!**

---

## 🎯 Purpose

**SeaSide** is the first pillar of the SeaTrace 4-pillar architecture:
- **Role**: HOLD - Vessel Operations
- **Security**: PUBLIC KEY INCOMING (verify signatures)
- **Port**: 8001

---

## 🚀 Quick Start

### **Run the Service**

```bash
# From SeaTrace-ODOO root
cd C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO

# Install dependencies
pip install fastapi uvicorn pydantic

# Run service
cd src\services\seaside
python main.py
```

**Service will start on**: `http://localhost:8001`

---

## 📡 API Endpoints

### **GET /health**
Health check endpoint

```bash
curl http://localhost:8001/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "seaside",
  "version": "1.0.0",
  "timestamp": "2025-01-20T10:00:00Z"
}
```

### **POST /api/v1/ingest**
Ingest packet from vessel

```bash
curl -X POST http://localhost:8001/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "correlation_id": "test-uuid-123",
    "source": "vessel",
    "payload": {
      "vessel_id": "WSP-001",
      "catch_weight": 500,
      "species": "Tuna"
    }
  }'
```

**Response**:
```json
{
  "status": "ingested",
  "packet_id": "generated-uuid",
  "correlation_id": "test-uuid-123",
  "timestamp": "2025-01-20T10:00:00Z",
  "verified": false
}
```

### **GET /api/v1/metrics**
Prometheus metrics

```bash
curl http://localhost:8001/api/v1/metrics
```

### **GET /docs**
Interactive API documentation (Swagger UI)

Visit: `http://localhost:8001/docs`

---

## 🔐 Signature Verification

If `PacketCryptoHandler` is available, incoming packets can include signatures:

```json
{
  "correlation_id": "uuid",
  "source": "vessel",
  "payload": {...},
  "signature": "base64-encoded-rsa-signature"
}
```

**Verification Flow**:
1. Packet received
2. Signature extracted
3. Payload hashed with BLAKE2
4. RSA signature verified with PUBLIC KEY
5. If valid → accept, if not → reject (401)

---

## 🧪 Testing

### **Basic Test**
```bash
# Test health endpoint
curl http://localhost:8001/health

# Test ingest endpoint
curl -X POST http://localhost:8001/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"correlation_id":"test","source":"vessel","payload":{"vessel_id":"WSP-001","catch_weight":500,"species":"Tuna"}}'
```

### **With Tests**
```bash
# Run pytest tests
pytest tests/test_seaside.py -v
```

---

## 🏗️ Architecture

```
SeaSide (Port 8001)
├── /health (GET)
├── /api/v1/ingest (POST)
├── /api/v1/packets/{id} (GET)
└── /api/v1/metrics (GET)

Integration:
→ Receives packets from vessels
→ Verifies signatures (PUBLIC KEY)
→ Routes to DeckSide (8002)
```

---

## 📊 4-Pillar Integration

```
Vessels → SeaSide (8001) → DeckSide (8002) → DockSide (8003) → MarketSide (8004)
          [HOLD]            [RECORD]          [STORE]           [EXCHANGE]
```

---

## 🔧 Configuration

### **Environment Variables**
```bash
PORT=8001
HOST=0.0.0.0
LOG_LEVEL=info
CRYPTO_ENABLED=true
```

### **Dependencies**
```
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
python-multipart>=0.0.6
```

---

## 🚀 Deployment

### **Docker** (coming soon)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### **Docker Compose** (coming soon)
```yaml
services:
  seaside:
    build: ./src/services/seaside
    ports:
      - "8001:8001"
    environment:
      - CRYPTO_ENABLED=true
```

---

## 📝 Next Steps

1. ✅ Service running on port 8001
2. ✅ `/health` and `/ingest` endpoints working
3. ⏳ Connect to DeckSide service
4. ⏳ Add database persistence
5. ⏳ Add rate limiting
6. ⏳ Add Prometheus metrics
7. ⏳ Deploy with Docker

---

**For the Commons Good!** 🌊🏈
