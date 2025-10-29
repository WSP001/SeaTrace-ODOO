# SeaSide (HOLD) — Module Overview

**Pillar:** SeaSide (1 of 4)  
**Service Name:** `seaside`  
**Port:** 8000  
**Purpose:** Vessel tracking and chain originator — F/V (Fishing Vessel) data collection, AIS telemetry processing, and creation of origin packets (Sentinels)

---

## 📋 **Quick Reference**

| Property | Value |
|----------|-------|
| **Entry Point** | `src.seaside.main:app` |
| **A2A Handler** | `src.a2a_handlers.seaside_handler:SeaSideHandler` |
| **Kafka Topic (Produces)** | `sea.gfw.traces` |
| **Kafka Topic (Consumes)** | None (chain originator) |
| **Private Key Env** | `SEASIDE_PRIVATE_KEY` (Ed25519) |
| **HMAC Key Env** | `SEATRACE_HMAC_KEY` (global) |

---

## 🎯 **What SeaSide Does**

SeaSide is the **first pillar** in the Four-Pillar architecture. It:

1. **Collects vessel telemetry** from AIS (Automatic Identification System) and Global Fishing Watch (GFW) traces
2. **Creates origin packets (Sentinels)** that establish the immutable starting point of the supply chain
3. **Publishes to Kafka** (`sea.gfw.traces` topic) for consumption by DeckSide
4. **Provides PUBLIC-only access** 🔓 (no dual-key fork at this layer)

SeaSide answers the question: **"Where did this catch originate?"**

---

## 🚀 **Run / Dev Commands**

### Start SeaSide service (Docker)
```bash
cd ~/workspaces/SeaTrace003
docker compose up --build seaside
```

### Start SeaSide service (local dev)
```bash
cd ~/workspaces/SeaTrace003
# Using .bashrc helper:
seaside python -m uvicorn src.seaside.main:app --host 0.0.0.0 --port 8000

# Or manually:
cd ~/workspaces/SeaTrace003/src/seaside
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Run unit tests
```bash
# Using .bashrc helper:
seaside pytest -q

# Or manually:
cd ~/workspaces/SeaTrace003/src/seaside
pytest -q
```

### Test endpoint (curl)
```bash
curl -X POST http://localhost:8000/api/v1/seaside/vessels \
  -H "Content-Type: application/json" \
  -d '{
    "vessel_id": "FV-12345",
    "vessel_name": "Pacific Explorer",
    "imo_number": "IMO1234567",
    "flag_state": "USA",
    "ais_mmsi": "367123456"
  }'
```

---

## 📁 **Important Files**

| File Path | Purpose |
|-----------|---------|
| `src/seaside/main.py` | FastAPI application entry point |
| `src/a2a_handlers/seaside_handler.py` | SeaSide A2A handler (chain originator) |
| `src/seaside/models.py` | Pydantic models for vessel data |
| `src/seaside/kafka_producer.py` | Kafka producer for `sea.gfw.traces` topic |
| `tests/unit/a2a_handlers/test_seaside_handler.py` | Unit tests for SeaSide handler |
| `docs/a2a_architecture/README.md` | A2A architecture documentation (private) |
| `openapi/seaside.yaml` | OpenAPI specification for SeaSide endpoints |

---

## 🧪 **Testing Strategy**

### Unit Tests
- Test origin packet creation (Sentinel generation)
- Test vessel data validation (IMO number, MMSI format)
- Test Ed25519 signature verification
- Test Kafka producer message formatting

### Integration Tests
- Test AIS telemetry ingestion → Sentinel creation → Kafka publish
- Test GFW trace processing pipeline
- Test endpoint authentication (API key validation)

### Postman / Newman Tests
- POST `/api/v1/seaside/vessels` (create vessel)
- GET `/api/v1/seaside/vessels/{vessel_id}` (fetch vessel details)
- GET `/api/v1/seaside/traces` (fetch GFW traces)

---

## 🔐 **Security & Keys**

### Private Key Management
- **Key Type:** Ed25519 (signing key)
- **Environment Variable:** `SEASIDE_PRIVATE_KEY`
- **Purpose:** Sign origin packets (Sentinels) to establish immutable chain-of-custody
- **Key Rotation:** Quarterly (follow key rotation schedule)
- **Storage:** AWS Secrets Manager / Azure Key Vault (never in repo)

### HMAC Key
- **Environment Variable:** `SEATRACE_HMAC_KEY`
- **Purpose:** HMAC-SHA256 signing for inter-service communication
- **Shared by:** All four pillars (SeaSide, DeckSide, DockSide, MarketSide)

---

## 🏗️ **Architecture Context**

### SeaSide in the Four-Pillar Chain
```
SeaSide (HOLD) → DeckSide (RECORD) → DockSide (STORE) → MarketSide (EXCHANGE)
     🔓              🔓🔐               🔓🔐              🔓🔐
  PUBLIC ONLY      THE FORK       THE SECOND FORK   THE THIRD FORK
```

### Key Architectural Points
1. **Chain Originator:** SeaSide creates the first packet (Sentinel) that all other pillars reference
2. **Immutability:** Origin packets are signed with Ed25519 and cannot be altered
3. **PUBLIC-only tier:** SeaSide intentionally has no dual-key fork (no PRIVATE tier) to maximize transparency
4. **Recovery % Baseline:** SeaSide establishes the "100% baseline" weight that DockSide uses to calculate recovery percentages

---

## 🔗 **Kafka Integration**

### Produces To
- **Topic:** `sea.gfw.traces`
- **Message Format:**
  ```json
  {
    "event_type": "vessel.origin",
    "vessel_id": "FV-12345",
    "timestamp": "2025-10-28T14:30:00Z",
    "lat": 42.123,
    "lon": -71.456,
    "sentinel_signature": "...",
    "gfw_trace_id": "..."
  }
  ```

### Consumes From
- None (SeaSide is the chain originator)

---

## 🎓 **Dev Hints for AI Agents**

When working with SeaSide:

1. **Read these files first:**
   - `docs/pillars/seaside.md` (this file)
   - `src/seaside/main.py`
   - `src/a2a_handlers/seaside_handler.py`

2. **Common PR patterns:**
   - Adding new vessel data fields → Update `models.py`, `openapi/seaside.yaml`, tests
   - Adding new GFW trace sources → Update `kafka_producer.py`, handler logic
   - Modifying signature algorithm → Update handler, tests, and coordinate with DeckSide team

3. **Testing checklist:**
   - [ ] Unit tests pass: `seaside pytest -q`
   - [ ] Postman collection passes: `newman run postman/collection.json`
   - [ ] Origin packet signature validates correctly
   - [ ] Kafka messages arrive in `sea.gfw.traces` topic

4. **Security checklist:**
   - [ ] No private keys in repo
   - [ ] All signing keys use Ed25519 (not RSA)
   - [ ] API endpoints require authentication
   - [ ] Gitleaks scan passes: `gitleaks detect --source .`

---

## 📚 **Related Documentation**

- [Four Pillars Architecture](../PROCEEDING_TEAM_DISCOVERIES.md)
- [DeckSide Module](./deckside.md)
- [A2A Architecture](../a2a_architecture/README.md)
- [Business Model Economics](../BUSINESS_MODEL_ECONOMICS.md)

---

**Last Updated:** 2025-10-28  
**Maintainer:** SeaTrace Programming Team  
**Status:** Production-ready
