# SeaTrace Public-Unlimited License (PUL)

**License Type:** Public Unlimited  
**Version:** 1.0  
**Effective Date:** 2025-01-01  
**License ID:** `pul-2025-01`

---

## Scope

This Public-Unlimited License (PUL) grants **FREE, UNLIMITED** access to the following SeaTrace modules:

### ✅ Covered Modules (FREE)

| Module | Description | Access Level |
|--------|-------------|--------------|
| **SeaSide (HOLD)** | Vessel operations, telemetry, AIS tracking | Full |
| **DeckSide (RECORD)** | Catch recording, verification, compliance | Full |
| **DockSide (STORE)** | Storage management, inventory, chain-of-custody | Full |

### ❌ Excluded Modules (Requires Private License)

| Module | Description | License Required |
|--------|-------------|------------------|
| **MarketSide (EXCHANGE)** | Trading, pricing, settlement, premium QR | Private-Limited (PL) |

---

## Terms & Conditions

### 1. Fees
- **$0 USD** - No fees under this PUL
- **No time limits** - Perpetual license
- **No user limits** - Unlimited seats
- **No transaction limits** - Unlimited usage

### 2. Allowed Uses
✅ **Production deployment** of SeaSide, DeckSide, DockSide  
✅ **Modification** of public module source code  
✅ **Redistribution** of public modules (with attribution)  
✅ **Commercial use** of public modules  
✅ **Integration** with ODOO and third-party systems  

### 3. Prohibited Uses
❌ **Circumventing scope restrictions** to access MarketSide features  
❌ **Exposing, simulating, or reverse-engineering** MarketSide endpoints  
❌ **Removing or altering** the scope digest signature  
❌ **Claiming** MarketSide functionality under PUL license  
❌ **Creating derivative works** that replicate MarketSide premium features  

### 4. Attribution Requirements
All deployments using PUL must include:
- **UI Attribution:** "Powered by SeaTrace" with link to https://github.com/WSP001/SeaTrace-ODOO
- **README Attribution:** Reference to SeaTrace public repository
- **API Documentation:** Link to SeaTrace public docs

### 5. Security & Verification

**Cryptographic Binding:**
- PUL tokens are signed using **Ed25519** public key cryptography
- Each token includes a **scope digest** (SHA-256 hash of allowed routes)
- Tampering with scope digest invalidates the license

**Token Structure:**
```json
{
  "typ": "PUL",
  "ver": 1,
  "license_id": "pul-2025-01",
  "org": "any",
  "pillars": ["seaside", "deckside", "dockside"],
  "features": ["qr_public", "schemas_v1", "otel_metrics"],
  "scope_digest": "sha256:a1b2c3d4...",
  "exp": 4070908800,
  "notice": "Public Unlimited (FREE). No MarketSide premium access."
}
```

**Verification:**
- Use only the **signed PUL token** published by SeaTrace
- Do NOT alter the `scope_digest` field
- Middleware validates signature on every request

### 6. Allowed Public Routes

The following API endpoints are accessible under PUL:

**Health & Status:**
- `GET /api/health`
- `GET /api/metrics`

**SeaSide (HOLD):**
- `GET /api/v1/seaside/status`
- `POST /api/v1/seaside/activity`
- `GET /api/v1/seaside/vessels`
- `POST /api/v1/seaside/telemetry`

**DeckSide (RECORD):**
- `GET /api/v1/deckside/status`
- `POST /api/v1/deckside/catch`
- `GET /api/v1/deckside/batches`
- `POST /api/v1/deckside/verification`

**DockSide (STORE):**
- `GET /api/v1/dockside/status`
- `POST /api/v1/dockside/storage`
- `GET /api/v1/dockside/inventory`
- `POST /api/v1/dockside/compliance`

**Public Demo:**
- `GET /api/demo/investor`
- `GET /api/demo/public`

### 7. Revocation & Key Rotation

**SeaTrace reserves the right to:**
- Rotate the public verification key if security issues arise
- Revoke specific license tokens in case of abuse
- Update the scope digest when public routes change

**Grace Period:**
- 30-day notice for key rotation
- 14-day grace period for scope digest updates
- Backward compatibility for one major version

### 8. Support & Updates

**Community Support:**
- GitHub Issues: https://github.com/WSP001/SeaTrace-ODOO/issues
- Discussions: https://github.com/WSP001/SeaTrace-ODOO/discussions
- Documentation: https://seatrace.worldseafoodproducers.com/docs

**Updates:**
- Security patches: Immediate
- Feature updates: Quarterly
- Breaking changes: 90-day notice

---

## How to Use PUL

### 1. Obtain PUL Token

**Download the signed PUL token:**
```bash
curl -O https://seatrace.worldseafoodproducers.com/licenses/pul-2025-01.token
```

**Or use the embedded token in your deployment:**
```python
PUL_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJ0eXAiOiJQVUwiLCJ2ZXIiOjEsImxpY2Vuc2VfaWQiOiJwdWwtMjAyNS0wMSIsIm9yZyI6ImFueSIsInBpbGxhcnMiOlsic2Vhc2lkZSIsImRlY2tzaWRlIiwiZG9ja3NpZGUiXSwiZmVhdHVyZXMiOlsicXJfcHVibGljIiwic2NoZW1hc192MSIsIm90ZWxfbWV0cmljcyJdLCJzY29wZV9kaWdlc3QiOiJzaGEyNTY6YTFiMmMzZDQuLi4iLCJleHAiOjQwNzA5MDg4MDAsIm5vdGljZSI6IlB1YmxpYyBVbmxpbWl0ZWQgKEZSRUUpLiBObyBNYXJrZXRTaWRlIHByZW1pdW0gYWNjZXNzLiJ9.signature"
```

### 2. Configure Your Application

**FastAPI Example:**
```python
from fastapi import FastAPI, Request
from seatrace.licensing import LicenseMiddleware

app = FastAPI()

# Add PUL middleware
app.add_middleware(
    LicenseMiddleware,
    license_token=PUL_TOKEN,
    verify_key="base64_encoded_public_key"
)
```

**Docker Compose Example:**
```yaml
services:
  seatrace:
    image: seatrace/public:latest
    environment:
      - SEATRACE_LICENSE_TOKEN=${PUL_TOKEN}
      - SEATRACE_LICENSE_TYPE=PUL
```

### 3. Verify License Status

**Check license validity:**
```bash
curl -H "X-ST-License: ${PUL_TOKEN}" \
     https://api.seatrace.com/api/license/status
```

**Expected response:**
```json
{
  "status": "valid",
  "type": "PUL",
  "org": "any",
  "pillars": ["seaside", "deckside", "dockside"],
  "expires": "2099-01-01T00:00:00Z",
  "features": ["qr_public", "schemas_v1", "otel_metrics"]
}
```

---

## Upgrade to Private-Limited (PL)

**Need MarketSide premium features?**

Upgrade to a **Private-Limited (PL) license** for:
- ✅ Dynamic trading platform
- ✅ Advanced pricing algorithms
- ✅ Premium QR analytics
- ✅ Real-time market settlement
- ✅ White-label deployments

**Contact Sales:**
- Email: licensing@worldseafoodproducers.com
- Phone: [Contact Number]
- Web: https://seatrace.worldseafoodproducers.com/pricing

---

## Legal

**Governing Law:** Delaware, USA  
**Warranty:** AS-IS, NO WARRANTY  
**Liability:** LIMITED TO $0 USD  

**Disclaimer:**
This software is provided "as is" without warranty of any kind. SeaTrace shall not be liable for any damages arising from the use of this software under the PUL license.

---

**© 2025 SeaTrace | World Sea Food Producers Association**

*For Private-Limited (PL) licensing, see [PRIVATE-LIMITED.md](PRIVATE-LIMITED.md)*
