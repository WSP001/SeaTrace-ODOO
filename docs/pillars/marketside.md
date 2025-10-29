# MarketSide (EXCHANGE) — Module Overview

**Pillar:** MarketSide (4 of 4)  
**Service Name:** `marketside`  
**Port:** 8003  
**Purpose:** Pricing, marketplace, and consumer verification — QR verification, market entitlements, and "THE THIRD FORK" (PUBLIC verification vs PRIVATE trading platform)

---

## 📋 **Quick Reference**

| Property | Value |
|----------|-------|
| **Entry Point** | `src.marketside.main:app` |
| **A2A Handler** | `src.a2a_handlers.marketside_handler:MarketSideHandler` |
| **Kafka Topic (Produces)** | `market.transactions` |
| **Kafka Topic (Consumes)** | `dock.origin_records` |
| **Private Key Env** | `MARKETSIDE_PRIVATE_KEY` (Ed25519) |
| **HMAC Key Env** | `SEATRACE_HMAC_KEY` (global) |

---

## 🎯 **What MarketSide Does**

MarketSide is the **fourth and final pillar** and introduces **THE THIRD FORK** 🔓🔐:

1. **PUBLIC tier (QR Verification)** 🔓: Consumer-facing QR code lookup (species, origin, sustainability score)
2. **PRIVATE tier (Trading Platform)** 🔐: B2B marketplace with pricing, quota enforcement, market entitlements
3. **Consumer Verification:** Anyone can scan a QR code to see catch provenance
4. **Market Entitlements:** PK3 (Market Keys) grant access to wholesale pricing and quota management
5. **Transaction Signing:** All market transactions are signed with Ed25519 for audit trails

MarketSide answers the question: **"Where can I buy this, and how do I verify it's authentic?"**

---

## 🚀 **Run / Dev Commands**

### Start MarketSide service (Docker)

```bash
cd ~/workspaces/SeaTrace003
docker compose up --build marketside
```

### Start MarketSide service (local dev)

```bash
# Using .bashrc helper:
marketside python -m uvicorn src.marketside.main:app --host 0.0.0.0 --port 8003

# Or manually:
cd ~/workspaces/SeaTrace003/src/marketside
python -m uvicorn main:app --host 0.0.0.0 --port 8003
```

### Run unit tests

```bash
# Using .bashrc helper:
marketside pytest -q

# Or manually:
cd ~/workspaces/SeaTrace003/src/marketside
pytest -q
```

### Test consumer verification endpoint (curl)

```bash
# PUBLIC tier (no auth required)
curl -X GET "http://localhost:8003/api/v1/marketside/verification?qr=QR-ABC123"
```

### Test marketplace endpoint (curl)

```bash
# PRIVATE tier (requires PK3: Market Key)
curl -X GET "http://localhost:8003/api/v1/marketside/pricing/CATCH-2025-10-28-001" \
  -H "Authorization: Bearer $MARKETSIDE_API_KEY"
```

---

## 📁 **Important Files**

| File Path | Purpose |
|-----------|---------|
| `src/marketside/main.py` | FastAPI application entry point |
| `src/a2a_handlers/marketside_handler.py` | MarketSide A2A handler (transaction signing) |
| `src/marketside/verification.py` | QR verification logic (PUBLIC tier) |
| `src/marketside/pricing.py` | Pricing and entitlement connectors (PRIVATE tier) |
| `src/marketside/models.py` | Pydantic models for market transactions |
| `tests/unit/a2a_handlers/test_marketside_handler.py` | Unit tests for MarketSide handler |
| `openapi/marketside.yaml` | OpenAPI specification for MarketSide endpoints |
| `docs/licensing/EMR-METERED.md` | Usage metering documentation |

---

## 🧪 **Testing Strategy**

### Unit Tests

- Test PUBLIC QR verification endpoint (no auth required)
- Test PRIVATE marketplace endpoint requires PK3 (Market Key)
- Test pricing calculation logic
- Test quota enforcement (reject over-quota transactions)
- Test Ed25519 transaction signatures

### Integration Tests

- Test DockSide origin record → MarketSide pricing
- Test PUBLIC tier returns consumer-friendly data
- Test PRIVATE tier requires valid market entitlement
- Test transaction signing and audit trail

### Postman / Newman Tests

- GET `/api/v1/marketside/verification?qr={qr_code}` (PUBLIC tier)
- GET `/api/v1/marketside/pricing/{catch_id}` (PRIVATE tier, requires PK3)
- POST `/api/v1/marketside/transactions` (PRIVATE tier, create transaction)
- GET `/api/v1/marketside/quota/{customer_id}` (PRIVATE tier, quota status)

---

## 🔐 **Security & Keys**

### Private Key Management (Per-Market-Participant)

- **Key Type:** Ed25519 (signing key)
- **Environment Variable:** `MARKETSIDE_PRIVATE_KEY`
- **Purpose:** Sign market transactions and issuance of marketplace entitlements
- **Key Rotation:** Per-participant quarterly (licensed market participants manage their own PK3 keys)
- **Storage:** Azure Key Vault / AWS Secrets Manager (never in repo)

### PK3 (Market Keys)

```
PK1 (Vessel Keys) → DeckSide
PK2 (Facility Keys) → DockSide
PK3 (Market Keys) → MarketSide ← THE THIRD FORK
```

---

## 🏗️ **Architecture Context**

### MarketSide in the Four-Pillar Chain

```
SeaSide (HOLD) → DeckSide (RECORD) → DockSide (STORE) → MarketSide (EXCHANGE)
     🔓              🔓🔐               🔓🔐              🔓🔐
  PUBLIC ONLY      THE FORK       THE SECOND FORK   THE THIRD FORK
```

### Key Architectural Points

1. **THE THIRD FORK:** MarketSide introduces PK3 (Market Keys) for licensed market participants (wholesalers, retailers)
2. **Consumer Verification:** PUBLIC tier is intentionally free and open (QR code lookup)
3. **B2B Marketplace:** PRIVATE tier is where revenue is generated (pricing, quota management, trading platform)
4. **Transaction Signing:** All market transactions are signed with Ed25519 for immutable audit trails
5. **Quota Enforcement:** PRIVATE tier enforces catch quotas to prevent overfishing

---

## 🔗 **Kafka Integration**

### Produces To

- **Topic:** `market.transactions`
- **Message Format:**

  ```json
  {
    "event_type": "transaction.completed",
    "transaction_id": "TXN-2025-10-28-001",
    "catch_id": "CATCH-2025-10-28-001",
    "buyer_id": "BUYER-12345",
    "seller_id": "SELLER-67890",
    "price_usd": 1500.00,
    "quantity_lbs": 900,
    "transaction_signature": "...",
    "timestamp": "2025-10-28T18:00:00Z"
  }
  ```

### Consumes From

- **Topic:** `dock.origin_records`
- **Purpose:** Receive immutable origin records from DockSide and make them available for marketplace pricing

---

## 🎓 **Dev Hints for AI Agents**

When working with MarketSide:

1. **Read these files first:**
   - `docs/pillars/marketside.md` (this file)
   - `src/marketside/main.py`
   - `src/a2a_handlers/marketside_handler.py`
   - `src/marketside/verification.py`
   - `src/marketside/pricing.py`

2. **Common PR patterns:**
   - Adding new marketplace feature (e.g., "Bid/Ask" pricing) → Update `pricing.py`, models, tests
   - Modifying QR verification format → Update `verification.py`, tests, consumer docs
   - Changing quota enforcement logic → Update entitlements, tests, OpenAPI spec

3. **Testing checklist:**
   - [ ] Unit tests pass: `marketside pytest -q`
   - [ ] PUBLIC tier QR verification works without auth
   - [ ] PRIVATE tier requires valid PK3 (Market Key)
   - [ ] Quota enforcement rejects over-quota transactions
   - [ ] Transaction signatures validate correctly

4. **Security checklist:**
   - [ ] No private keys in repo
   - [ ] All licensed market participants have unique PK3 keys
   - [ ] PRIVATE tier endpoints require authentication
   - [ ] Gitleaks scan passes: `gitleaks detect --source .`

---

## 💰 **Business Model Context**

### Revenue from MarketSide

- **FREE Tier (PUBLIC QR Verification):** $0/month (Commons Good)
- **PAID Tier (PRIVATE Trading Platform):** $1,200/month per licensed market participant (PK3: Market Keys)
- **Typical Customer:** 285 licensed market participants = $342,000/month revenue
- **Cross-Subsidy:** Every $1 on FREE tier generates $34 profit from PAID tier (34:1 ratio)

### Total SeaTrace Revenue (3/4 Pillars Monetized)

- **SeaSide:** FREE only (PUBLIC 🔓)
- **DeckSide:** $342K/month (PK1: Vessel Keys)
- **DockSide:** $342K/month (PK2: Facility Keys)
- **MarketSide:** $342K/month (PK3: Market Keys)
- **Total:** $1.026M/month ($12.3M/year)
- **Profit Margin:** 93.9% ($963K/month net profit)

---

## 📚 **Related Documentation**

- [Four Pillars Architecture](../PROCEEDING_TEAM_DISCOVERIES.md)
- [DockSide Module](./dockside.md)
- [Business Model Economics](../BUSINESS_MODEL_ECONOMICS.md)
- [EMR Metered Licensing](../licensing/EMR-METERED.md)

---

**Last Updated:** 2025-10-28  
**Maintainer:** SeaTrace Programming Team  
**Status:** Production-ready  
**Revenue Model:** 3/4 pillars monetized (not 1.5/4), $120K/month total revenue, 93.9% margin
