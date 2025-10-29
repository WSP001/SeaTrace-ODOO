# DeckSide (RECORD) — Module Overview

**Pillar:** DeckSide (2 of 4)  
**Service Name:** `deckside`  
**Port:** 8001  
**Purpose:** Catch verification and recording — At-sea catch tallying, QR code generation, and "THE FORK" (PUBLIC #CATCH vs PRIVATE $CHECK)

---

## 📋 **Quick Reference**

| Property | Value |
|----------|-------|
| **Entry Point** | `src.deckside.main:app` |
| **A2A Handler** | `src.a2a_handlers.deckside_handler:DeckSideHandler` |
| **Kafka Topic (Produces)** | `deck.minds_eye` |
| **Kafka Topic (Consumes)** | `sea.gfw.traces` |
| **Private Key Env** | `DECKSIDE_PRIVATE_KEY` (Ed25519, per-actor) |
| **HMAC Key Env** | `SEATRACE_HMAC_KEY` (global) |

---

## 🎯 **What DeckSide Does**

DeckSide is the **second pillar** and introduces **THE FORK** 🔓🔐:

1. **PUBLIC tier (#CATCH)** 🔓: Basic catch tally visible to everyone (species, approximate location)
2. **PRIVATE tier ($CHECK)** 🔐: Precise GPS, vessel ID, captain signature, licensed customer access
3. **QR code generation:** Each catch event gets a QR code for consumer verification
4. **ML validation:** 96% accuracy species classification (computer vision on catch photos)
5. **Publishes to Kafka:** `deck.minds_eye` topic consumed by DockSide

DeckSide answers the question: **"What was caught, where, and by whom?"**

---

## 🚀 **Run / Dev Commands**

### Start DeckSide service (Docker)

```bash
cd ~/workspaces/SeaTrace003
docker compose up --build deckside
```

### Start DeckSide service (local dev)

```bash
# Using .bashrc helper:
deckside python -m uvicorn src.deckside.main:app --host 0.0.0.0 --port 8001

# Or manually:
cd ~/workspaces/SeaTrace003/src/deckside
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

### Run unit tests

```bash
# Using .bashrc helper:
deckside pytest -q

# Or manually:
cd ~/workspaces/SeaTrace003/src/deckside
pytest -q
```

### Test endpoint (curl)

```bash
curl -X POST http://localhost:8001/api/v1/deckside/catches \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DECKSIDE_API_KEY" \
  -d '{
    "vessel_id": "FV-12345",
    "species": "Pacific Halibut",
    "weight_lbs": 1200,
    "catch_lat": 42.123,
    "catch_lon": -71.456,
    "photo_url": "s3://catches/photo123.jpg"
  }'
```

---

## 📁 **Important Files**

| File Path | Purpose |
|-----------|---------|
| `src/deckside/main.py` | FastAPI application entry point |
| `src/a2a_handlers/deckside_handler.py` | DeckSide A2A handler (dual-key router) |
| `src/deckside/qrcode.py` | QR code generation and verification |
| `src/deckside/ml_validator.py` | ML species classification (96% accuracy) |
| `src/deckside/models.py` | Pydantic models for catch records |
| `tests/unit/a2a_handlers/test_deckside_handler.py` | Unit tests for DeckSide handler |
| `openapi/deckside.yaml` | OpenAPI specification for DeckSide endpoints |

---

## 🧪 **Testing Strategy**

### Unit Tests

- Test PUBLIC #CATCH packet creation (no precise GPS)
- Test PRIVATE $CHECK packet creation (full data)
- Test QR code generation and signature validation
- Test ML species classification accuracy
- Test dual-key routing logic (packet switching handler)

### Integration Tests

- Test SeaSide origin packet → DeckSide catch record → Kafka publish
- Test PUBLIC tier endpoint returns obfuscated GPS
- Test PRIVATE tier endpoint requires valid license key
- Test QR verification endpoint (consumer-facing)

### Postman / Newman Tests

- POST `/api/v1/deckside/catches` (create catch record)
- GET `/api/v1/deckside/catches/{catch_id}` (PUBLIC tier)
- GET `/api/v1/deckside/catches/{catch_id}?tier=private` (PRIVATE tier, requires license)
- GET `/api/v1/deckside/qr/{qr_code}` (QR verification)

---

## 🔐 **Security & Keys**

### Private Key Management (Per-Actor)

- **Key Type:** Ed25519 (signing key)
- **Environment Variable:** `DECKSIDE_PRIVATE_KEY`
- **Purpose:** Sign catch tallies and QR tokens
- **Key Rotation:** Per-vessel quarterly (licensed customers manage their own keys)
- **Storage:** Azure Key Vault / AWS Secrets Manager (never in repo)

### Dual-Key Architecture

```
                     SINGLE DATA SOURCE
                            |
                    [Packet Switching Handler]
                            |
                +-----------+-----------+
                |                       |
         PUBLIC #CATCH           PRIVATE $CHECK
              🔓                        🔐
    (no precise GPS)           (full vessel data)
    (free tier)                (licensed customers)
```

---

## 🏗️ **Architecture Context**

### DeckSide in the Four-Pillar Chain

```
SeaSide (HOLD) → DeckSide (RECORD) → DockSide (STORE) → MarketSide (EXCHANGE)
     🔓              🔓🔐               🔓🔐              🔓🔐
  PUBLIC ONLY      THE FORK       THE SECOND FORK   THE THIRD FORK
```

### Key Architectural Points

1. **THE FORK:** First appearance of dual-key routing (PUBLIC vs PRIVATE)
2. **PK1 (Vessel Keys):** Each licensed vessel has its own Ed25519 key pair
3. **ML Validation:** Computer vision model (96% accuracy) validates species claims
4. **QR Issuance:** Each catch gets a consumer-facing QR code for traceability
5. **Recovery % Baseline:** DeckSide establishes the "at-sea weight" that DockSide uses for yield calculations

---

## 🔗 **Kafka Integration**

### Produces To

- **Topic:** `deck.minds_eye`
- **Message Format:**
  ```json
  {
    "event_type": "catch.recorded",
    "catch_id": "CATCH-2025-10-28-001",
    "vessel_id": "FV-12345",
    "species": "Pacific Halibut",
    "weight_lbs": 1200,
    "catch_lat_public": 42.1,  # obfuscated
    "catch_lon_public": -71.5, # obfuscated
    "qr_code": "QR-ABC123",
    "sentinel_signature": "...",
    "timestamp": "2025-10-28T14:30:00Z"
  }
  ```

### Consumes From

- **Topic:** `sea.gfw.traces`
- **Purpose:** Correlate catch records with vessel origin packets (Sentinels)

---

## 🎓 **Dev Hints for AI Agents**

When working with DeckSide:

1. **Read these files first:**
   - `docs/pillars/deckside.md` (this file)
   - `src/deckside/main.py`
   - `src/a2a_handlers/deckside_handler.py`
   - `src/deckside/qrcode.py`

2. **Common PR patterns:**
   - Adding new species → Update `ml_validator.py`, species enum, tests
   - Modifying QR format → Update `qrcode.py`, tests, and consumer-facing docs
   - Changing dual-key routing logic → Update handler, tests, OpenAPI spec

3. **Testing checklist:**
   - [ ] Unit tests pass: `deckside pytest -q`
   - [ ] PUBLIC tier returns obfuscated GPS
   - [ ] PRIVATE tier requires valid license key
   - [ ] QR codes validate correctly
   - [ ] ML model accuracy ≥ 96% on test dataset

4. **Security checklist:**
   - [ ] No private keys in repo
   - [ ] All licensed customers have unique Ed25519 keys
   - [ ] PRIVATE tier endpoints require authentication
   - [ ] Gitleaks scan passes: `gitleaks detect --source .`

---

## 💰 **Business Model Context**

### Revenue from DeckSide

- **FREE Tier (PUBLIC #CATCH):** $0/month (Commons Good)
- **PAID Tier (PRIVATE $CHECK):** $1,200/month per licensed vessel (PK1: Vessel Keys)
- **Typical Customer:** 285 licensed vessels = $342,000/month revenue
- **Cross-Subsidy:** Every $1 on FREE tier generates $34 profit from PAID tier (34:1 ratio)

---

## 📚 **Related Documentation**

- [Four Pillars Architecture](../PROCEEDING_TEAM_DISCOVERIES.md)
- [SeaSide Module](./seaside.md)
- [DockSide Module](./dockside.md)
- [Business Model Economics](../BUSINESS_MODEL_ECONOMICS.md)

---

**Last Updated:** 2025-10-28  
**Maintainer:** SeaTrace Programming Team  
**Status:** Production-ready
