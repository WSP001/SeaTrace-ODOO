# DockSide (STORE) — Module Overview

**Pillar:** DockSide (3 of 4)  
**Service Name:** `dockside`  
**Port:** 8002  
**Purpose:** Cold storage, reconciliation, and processing — Fish ticket indexing, H&G/fillet recovery tracking, and "THE SECOND FORK" (PUBLIC #STORE vs PRIVATE $STORE)

---

## 📋 **Quick Reference**

| Property | Value |
|----------|-------|
| **Entry Point** | `src.dockside.main:app` |
| **A2A Handler** | `src.a2a_handlers.dockside_handler:DockSideHandler` |
| **Kafka Topic (Produces)** | `dock.origin_records` |
| **Kafka Topic (Consumes)** | `deck.minds_eye` |
| **Private Key Env** | `DOCKSIDE_PRIVATE_KEY` (Ed25519) |
| **HMAC Key Env** | `SEATRACE_HMAC_KEY` (global) |

---

## 🎯 **What DockSide Does**

DockSide is the **third pillar** and introduces **THE SECOND FORK** 🔓🔐:

1. **PUBLIC tier (#STORE)** 🔓: Basic processing info (product type, approximate recovery %)
2. **PRIVATE tier ($STORE)** 🔐: Precise fish ticket indexing, temperature logs, exact recovery %, cost savings data
3. **Reconciliation:** Correlates incoming raw supply (from DeckSide) with outgoing finished products (SKUs)
4. **Recovery % Tracking:** H&G (70-75%), Filleting (50-60%) — critical for yield engineering
5. **Merge/Split Semantics:** Packet switching handler routes single data source to dual revenue streams

DockSide answers the question: **"How was the catch processed, and what's the yield?"**

---

## 🚀 **Run / Dev Commands**

### Start DockSide service (Docker)

```bash
cd ~/workspaces/SeaTrace003
docker compose up --build dockside
```

### Start DockSide service (local dev)

```bash
# Using .bashrc helper:
dockside python -m uvicorn src.dockside.main:app --host 0.0.0.0 --port 8002

# Or manually:
cd ~/workspaces/SeaTrace003/src/dockside
python -m uvicorn main:app --host 0.0.0.0 --port 8002
```

### Run unit tests

```bash
# Using .bashrc helper:
dockside pytest -q

# Or manually:
cd ~/workspaces/SeaTrace003/src/dockside
pytest -q
```

### Run processing job (batch reconciliation)

```bash
# Using .bashrc helper:
dockside bash scripts/process_incoming.sh

# Or manually:
cd ~/workspaces/SeaTrace003/src/dockside
bash scripts/process_incoming.sh
```

### Test endpoint (curl)

```bash
curl -X POST http://localhost:8002/api/v1/dockside/processing \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DOCKSIDE_API_KEY" \
  -d '{
    "catch_id": "CATCH-2025-10-28-001",
    "processing_type": "H&G",
    "incoming_weight_lbs": 1200,
    "outgoing_weight_lbs": 900,
    "temperature_log": [-2, -1.8, -2.1, -1.9],
    "fish_ticket_number": "FT-2025-12345"
  }'
```

---

## 📁 **Important Files**

| File Path | Purpose |
|-----------|---------|
| `src/dockside/main.py` | FastAPI application entry point |
| `src/a2a_handlers/dockside_handler.py` | DockSide A2A handler (reconciliation logic) |
| `src/building_lot/reconciliation.py` | Incoming→Outgoing reconciliation (fish ticket indexing) |
| `src/dockside/processing.py` | H&G/fillet yield calculations |
| `src/dockside/models.py` | Pydantic models for processing records |
| `tests/unit/a2a_handlers/test_dockside_handler.py` | Unit tests for DockSide handler |
| `openapi/dockside.yaml` | OpenAPI specification for DockSide endpoints |
| `docs/PRIVATE_KEY_CHAIN_ARCHITECTURE.md` | Key-chain architecture docs |

---

## 🧪 **Testing Strategy**

### Unit Tests

- Test PUBLIC #STORE packet creation (approximate recovery %)
- Test PRIVATE $STORE packet creation (exact fish ticket data)
- Test H&G recovery % calculation (70-75% expected)
- Test fillet recovery % calculation (50-60% expected)
- Test reconciliation logic (incoming weight vs outgoing SKU weight)

### Integration Tests

- Test DeckSide catch → DockSide processing → Kafka publish
- Test PUBLIC tier endpoint returns approximate data
- Test PRIVATE tier endpoint requires valid facility license (PK2)
- Test temperature log validation (reject if above -1°C)

### Postman / Newman Tests

- POST `/api/v1/dockside/processing` (create processing record)
- GET `/api/v1/dockside/batches/{batch_id}` (PUBLIC tier)
- GET `/api/v1/dockside/batches/{batch_id}?tier=private` (PRIVATE tier, requires PK2)
- GET `/api/v1/dockside/reconciliation/{fish_ticket}` (PRIVATE tier only)

---

## 🔐 **Security & Keys**

### Private Key Management (Per-Facility)

- **Key Type:** Ed25519 (signing key)
- **Environment Variable:** `DOCKSIDE_PRIVATE_KEY`
- **Purpose:** Sign aggregated origin records (immutable SKU provenance)
- **Key Rotation:** Per-facility quarterly (licensed facilities manage their own PK2 keys)
- **Storage:** Azure Key Vault / AWS Secrets Manager (never in repo)

### PK2 (Facility Keys)

```
PK1 (Vessel Keys) → DeckSide
PK2 (Facility Keys) → DockSide ← THE SECOND FORK
PK3 (Market Keys) → MarketSide
```

---

## 🏗️ **Architecture Context**

### DockSide in the Four-Pillar Chain

```
SeaSide (HOLD) → DeckSide (RECORD) → DockSide (STORE) → MarketSide (EXCHANGE)
     🔓              🔓🔐               🔓🔐              🔓🔐
  PUBLIC ONLY      THE FORK       THE SECOND FORK   THE THIRD FORK
```

### Key Architectural Points

1. **THE SECOND FORK:** DockSide introduces PK2 (Facility Keys) for licensed processors
2. **Reconciliation:** DS2 (Inventory Control) correlates incoming raw supply with outgoing finished products
3. **Recovery % Tracking:** "H&G = ~70-75%, Filleting = ~50-60%, LOGIC DICTATES EVEN HIGHER RECOVERY % LOSS" (Roberto's discovery)
4. **Fish Ticket Indexing:** Standard tally weights (1-2 lbs per fish) mapped to exact fish ticket numbers
5. **33% Cost Savings:** PRIVATE tier customers save 33% on insurance/auditing costs due to precise traceability

---

## 🔗 **Kafka Integration**

### Produces To

- **Topic:** `dock.origin_records`
- **Message Format:**

  ```json
  {
    "event_type": "processing.completed",
    "batch_id": "BATCH-2025-10-28-001",
    "catch_id": "CATCH-2025-10-28-001",
    "processing_type": "H&G",
    "incoming_weight_lbs": 1200,
    "outgoing_weight_lbs": 900,
    "recovery_percent": 75.0,
    "fish_ticket_number": "FT-2025-12345",
    "temperature_log": [-2, -1.8, -2.1, -1.9],
    "origin_record_signature": "...",
    "timestamp": "2025-10-28T16:00:00Z"
  }
  ```

### Consumes From

- **Topic:** `deck.minds_eye`
- **Purpose:** Receive catch records from DeckSide and reconcile with processing batches

---

## 🎓 **Dev Hints for AI Agents**

When working with DockSide:

1. **Read these files first:**
   - `docs/pillars/dockside.md` (this file)
   - `src/dockside/main.py`
   - `src/a2a_handlers/dockside_handler.py`
   - `src/building_lot/reconciliation.py`

2. **Common PR patterns:**
   - Adding new processing type (e.g., "Smoked") → Update `processing.py`, models, tests
   - Modifying recovery % calculation → Update yield engineering logic, tests
   - Changing fish ticket format → Update `reconciliation.py`, OpenAPI spec

3. **Testing checklist:**
   - [ ] Unit tests pass: `dockside pytest -q`
   - [ ] Recovery % calculations match expected ranges (H&G: 70-75%, Fillet: 50-60%)
   - [ ] PRIVATE tier requires valid PK2 (Facility Key)
   - [ ] Temperature logs reject values above -1°C
   - [ ] Fish ticket numbers validate correctly

4. **Security checklist:**
   - [ ] No private keys in repo
   - [ ] All licensed facilities have unique PK2 keys
   - [ ] PRIVATE tier endpoints require authentication
   - [ ] Gitleaks scan passes: `gitleaks detect --source .`

---

## 💰 **Business Model Context**

### Revenue from DockSide

- **FREE Tier (PUBLIC #STORE):** $0/month (Commons Good)
- **PAID Tier (PRIVATE $STORE):** $1,200/month per licensed facility (PK2: Facility Keys)
- **Typical Customer:** 285 licensed facilities = $342,000/month revenue
- **Cost Savings:** PRIVATE tier customers save 33% on insurance/auditing costs (precise traceability)
- **Cross-Subsidy:** Every $1 on FREE tier generates $34 profit from PAID tier (34:1 ratio)

---

## 📚 **Related Documentation**

- [Four Pillars Architecture](../PROCEEDING_TEAM_DISCOVERIES.md)
- [DeckSide Module](./deckside.md)
- [MarketSide Module](./marketside.md)
- [Business Model Economics](../BUSINESS_MODEL_ECONOMICS.md)
- [Roberto's Discovery: Recovery % Impact](../VALIDATION_REPORT.md)

---

**Last Updated:** 2025-10-28  
**Maintainer:** SeaTrace Programming Team  
**Status:** Production-ready  
**Critical Context:** "H&G recovery 70-75%, fillet 50-60%, LOGIC DICTATES EVEN HIGHER RECOVERY % LOSS" — Roberto's yield engineering breakthrough
