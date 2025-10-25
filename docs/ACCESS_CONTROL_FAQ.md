# Access Control FAQ: Token-Based Security in SeaTrace

**Version:** 1.0  
**Last Updated:** October 25, 2025  
**Audience:** Developers, Security Reviewers, Stakeholders

---

## 🔐 The Big Question: "Can Anybody With This Link Make Changes?"

**Short Answer:** No. Having a PUL (Public Unlimited License) token gives you **READ access** to public data endpoints, but **NOT** the ability to arbitrarily modify system data.

**Long Answer:** SeaTrace uses a multi-layered security model that combines:
1. **Token-based authentication** (who you are)
2. **Cryptographic signatures** (proof of authenticity)
3. **Authorization scopes** (what you can access)
4. **Data validation** (what you can do)

### Visual Security Model

```
┌─────────────────────────────────────────────────────────────┐
│  Request: "POST /ingest/packet" with catch data             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Token Verification                                 │
│  ✓ Is token present?                                         │
│  ✓ Is signature valid? (Ed25519 crypto)                     │
│  ✓ Has token expired?                                        │
│  ✓ Is token revoked?                                         │
└────────────────────┬────────────────────────────────────────┘
                     │ PASS ✅
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Scope Validation                                   │
│  ✓ Is route allowed by token type (PUL/PL)?                │
│  ✓ Does scope_digest match allowed routes?                  │
│  ✓ Is this endpoint in the pillar list?                     │
└────────────────────┬────────────────────────────────────────┘
                     │ PASS ✅
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Data Signature Verification                        │
│  ✓ Is data signed by registered vessel?                     │
│  ✓ Does signature match vessel's public key?                │
│  ✓ Is vessel authorized for this operation?                 │
└────────────────────┬────────────────────────────────────────┘
                     │ PASS ✅
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Business Rule Validation                           │
│  ✓ Is data format valid?                                     │
│  ✓ Are values within acceptable ranges?                      │
│  ✓ Is this a duplicate submission?                           │
│  ✓ Does data meet business constraints?                      │
└────────────────────┬────────────────────────────────────────┘
                     │ PASS ✅
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ SUCCESS: Data accepted and stored                        │
└─────────────────────────────────────────────────────────────┘
```

**All 4 layers must pass for a change to be accepted!**

---

## 🎯 Understanding Token Types

### Public Unlimited License (PUL)
**What it grants:**
- ✅ Read access to SeaSide, DeckSide, DockSide public endpoints
- ✅ Ability to query vessel data, catch records, storage info
- ✅ Access to public demo and health check endpoints
- ✅ View Commons Fund transparency reports

**What it does NOT grant:**
- ❌ Write access to modify existing data
- ❌ Ability to create fake vessel records
- ❌ Access to MarketSide premium features
- ❌ Permission to delete or alter blockchain records
- ❌ Administrative privileges

**Example PUL Routes (from PUBLIC-UNLIMITED.md):**
```
GET /api/v1/seaside/status       ← Read only
GET /api/v1/seaside/vessels      ← Read only
GET /api/v1/deckside/batches     ← Read only
GET /api/v1/dockside/inventory   ← Read only
```

### Private Limited License (PL)
**What it grants:**
- ✅ All PUL permissions
- ✅ Access to MarketSide trading platform
- ✅ Advanced pricing algorithms
- ✅ Premium analytics and reporting
- ✅ API access with higher rate limits

**What it does NOT grant (without additional authentication):**
- ❌ Ability to modify other organizations' data
- ❌ Administrative access to the platform
- ❌ Permission to bypass data validation rules

### Visual Comparison: Read vs Write Operations

```
READ Operation (GET /api/v1/seaside/vessels)
┌──────────────────┐
│ User with        │
│ PUL Token        │───────┐
└──────────────────┘       │
                           ▼
                    ┌──────────────┐
                    │ Middleware   │
                    │ Verifies     │
                    │ Token        │
                    └──────┬───────┘
                           │ Token Valid ✅
                           ▼
                    ┌──────────────┐
                    │ Check Scope  │
                    │ Is GET       │
                    │ allowed?     │
                    └──────┬───────┘
                           │ Yes ✅
                           ▼
                    ┌──────────────┐
                    │ Return Data  │
                    │ ✅ SUCCESS   │
                    └──────────────┘

WRITE Operation (POST /ingest/packet)
┌──────────────────┐
│ User with        │
│ PUL Token        │───────┐
└──────────────────┘       │
                           ▼
                    ┌──────────────┐
                    │ Middleware   │
                    │ Verifies     │
                    │ Token        │
                    └──────┬───────┘
                           │ Token Valid ✅
                           ▼
                    ┌──────────────┐
                    │ Check Scope  │
                    │ Is POST      │
                    │ allowed?     │
                    └──────┬───────┘
                           │ Yes ✅
                           ▼
                    ┌──────────────┐
                    │ Verify Data  │
                    │ Signature    │
                    │ from Vessel  │
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │              │
        ❌ No Signature       ✅ Valid Signature
        or Invalid           from Registered
                            Vessel
                    │              │
                    ▼              ▼
            ┌──────────┐    ┌──────────┐
            │ REJECT   │    │ Validate │
            │ 401      │    │ Business │
            │ Unauth   │    │ Rules    │
            └──────────┘    └────┬─────┘
                                 │ Valid ✅
                                 ▼
                          ┌──────────────┐
                          │ Store Data   │
                          │ ✅ SUCCESS   │
                          └──────────────┘
```

**Key Insight:** Token grants *access* to the endpoint, but cryptographic signature grants *authority* to submit data.

---

## 🛡️ Multi-Layer Security Model

### Layer 1: Token Verification
**How it works:**
```
1. Client includes token in request:
   Header: X-ST-License: <JWT_TOKEN>
   OR
   Header: Authorization: Bearer <JWT_TOKEN>

2. Middleware extracts and decodes token

3. Signature is verified using Ed25519 public key cryptography

4. Token claims are validated (expiry, scope, etc.)
```

**What this prevents:**
- Forged tokens (signature verification would fail)
- Expired tokens (expiry check)
- Tampered tokens (any modification breaks signature)

### Layer 2: Scope Restrictions
**How it works:**
```python
# PUL tokens contain a scope_digest
{
  "typ": "PUL",
  "scope_digest": "sha256:a1b2c3d4...",  # Hash of allowed routes
  "pillars": ["seaside", "deckside", "dockside"],
  ...
}

# Middleware checks if requested route is in allowed scope
if route_sig not in self.public_routes:
    raise HTTPException(403, "Route not in public scope")
```

**What this prevents:**
- Accessing MarketSide endpoints with PUL token
- Calling administrative endpoints
- Using endpoints that don't match the scope digest

### Layer 3: Cryptographic Signatures on Data
**How it works:**
```python
# When vessels submit data, they must sign it
@app.post("/ingest/packet")
async def ingest_packet(packet_data: Dict[str, Any]):
    packet = IncomingPacket(
        source="vessel",
        payload=packet_data,
        signature=packet_data.get("signature")  # ← Required!
    )
    
    # Packet switcher verifies signature matches registered vessel
    result = await packet_switcher._handle_seaside(packet)
```

**What this prevents:**
- Submitting fake vessel data (signature won't match)
- Impersonating other vessels
- Man-in-the-middle attacks

### Layer 4: Data Validation and Business Rules
**How it works:**
```python
# Each endpoint validates data according to business rules
async def ingest_packet(packet_data):
    # 1. Verify vessel is registered
    vessel = await verify_vessel_registration(packet_data["vessel_id"])
    
    # 2. Verify timestamp is reasonable
    if not is_timestamp_valid(packet_data["timestamp"]):
        raise HTTPException(400, "Invalid timestamp")
    
    # 3. Verify geolocation is within expected bounds
    if not is_location_valid(packet_data["coordinates"]):
        raise HTTPException(400, "Invalid coordinates")
    
    # 4. Check for duplicate submissions
    if await is_duplicate(packet_data["packet_id"]):
        raise HTTPException(409, "Duplicate packet")
```

**What this prevents:**
- Invalid or malformed data
- Duplicate submissions
- Out-of-bounds values
- Data that violates business constraints

---

## 📊 Real-World Example: Vessel Data Submission

### Scenario: A fishing vessel wants to record a catch

**Step 1: Vessel Authentication**
```
Vessel has been issued:
- Vessel ID: VESSEL_001
- Private key (stored securely on vessel)
- Public key (registered in SeaTrace)
```

**Step 2: Creating a Catch Record**
```python
# Vessel creates catch data
catch_data = {
    "vessel_id": "VESSEL_001",
    "timestamp": "2025-10-25T12:00:00Z",
    "species": "Tuna",
    "weight_kg": 500,
    "coordinates": {"lat": 45.2, "lon": -124.5},
    "packet_id": "unique_packet_id_123"
}

# Vessel signs the data with its PRIVATE key
signature = vessel_private_key.sign(json.dumps(catch_data))
catch_data["signature"] = signature
```

**Step 3: Submission to API**
```bash
# PUL token provides access to the endpoint
# But signature proves vessel identity
curl -X POST https://api.seatrace.com/ingest/packet \
  -H "X-ST-License: <PUL_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "vessel_id": "VESSEL_001",
    "signature": "base64_signature...",
    ...
  }'
```

**Step 4: Server Verification**
```python
# 1. Verify PUL token (grants access to endpoint)
middleware.verify_token(pul_token)

# 2. Verify vessel signature (proves vessel identity)
vessel_public_key = await get_vessel_public_key("VESSEL_001")
if not verify_signature(catch_data, signature, vessel_public_key):
    raise HTTPException(401, "Invalid vessel signature")

# 3. Validate data (business rules)
validate_catch_data(catch_data)

# 4. Record to blockchain/database
await store_catch_record(catch_data)
```

**What if someone tries to fake vessel data?**
```python
# Attacker tries to submit fake data for VESSEL_001
fake_data = {
    "vessel_id": "VESSEL_001",  # Impersonating
    "signature": "fake_signature",  # Invalid!
    ...
}

# ❌ Server rejects: signature verification fails
# Attacker doesn't have VESSEL_001's private key
```

---

## 🔍 Common Attack Scenarios and Mitigations

### Attack 1: "I have a PUL token, let me modify data"
**Attack:** Attacker obtains valid PUL token and tries to POST malicious data

**Mitigation:**
1. PUL token grants access to endpoint, but not authority to submit data
2. Data submission requires cryptographic signature from registered entity
3. Signature verification fails → Request rejected

**Result:** ❌ Attack fails at signature verification layer

---

### Attack 2: "I'll steal someone's signature and replay it"
**Attack:** Attacker captures a valid vessel submission and replays it

**Mitigation:**
1. Each packet includes unique `packet_id` and `timestamp`
2. Duplicate detection checks prevent replay
3. Timestamp validation rejects old submissions
4. Correlation IDs track packet lineage

**Result:** ❌ Attack fails at duplicate detection layer

---

### Attack 3: "I'll forge a PUL token to access premium features"
**Attack:** Attacker creates fake PUL token to access MarketSide

**Mitigation:**
1. Token signature verification using Ed25519 cryptography
2. Attacker doesn't have SeaTrace's private signing key
3. Any tampering breaks signature
4. Scope digest validation ensures token matches allowed routes

**Result:** ❌ Attack fails at token signature verification layer

---

### Attack 4: "I'll modify my PUL token to add more permissions"
**Attack:** Attacker decodes PUL token and changes `pillars` to include `marketside`

**Mitigation:**
1. JWT tokens are cryptographically signed
2. Any modification changes the payload
3. Signature verification fails with modified payload
4. Modified token is rejected

**Example:**
```
Original token: header.payload.signature_of_header_and_payload
Modified token: header.modified_payload.original_signature

Verification: hash(header + modified_payload) ≠ decrypted(signature)
Result: ❌ Invalid signature
```

---

## 📋 Access Control Matrix

| Operation | PUL Token | PL Token | Vessel Signature | Admin Credentials |
|-----------|-----------|----------|------------------|-------------------|
| Read vessel data | ✅ | ✅ | N/A | ✅ |
| Read catch records | ✅ | ✅ | N/A | ✅ |
| Read storage data | ✅ | ✅ | N/A | ✅ |
| Submit vessel telemetry | ✅ | ✅ | ✅ Required | ✅ |
| Submit catch record | ✅ | ✅ | ✅ Required | ✅ |
| Submit storage update | ✅ | ✅ | ✅ Required | ✅ |
| Access MarketSide | ❌ | ✅ | N/A | ✅ |
| Modify other vessel's data | ❌ | ❌ | ❌ | ✅ |
| Delete records | ❌ | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ❌ | ✅ |

**Key:** 
- ✅ = Allowed
- ❌ = Denied
- N/A = Not applicable

---

## 🎓 Best Practices for Developers

### 1. Never Trust Client Input
```python
# ❌ BAD - Trusting user input
@app.post("/update_vessel")
async def update_vessel(vessel_id: str, new_data: dict):
    await db.update(vessel_id, new_data)  # Dangerous!

# ✅ GOOD - Verify signature and validate
@app.post("/update_vessel")
async def update_vessel(vessel_id: str, new_data: dict, signature: str):
    # 1. Verify signature
    vessel_key = await get_vessel_public_key(vessel_id)
    if not verify_signature(new_data, signature, vessel_key):
        raise HTTPException(401, "Invalid signature")
    
    # 2. Validate data
    validated_data = VesselUpdateSchema(**new_data)
    
    # 3. Check authorization
    if not can_update_vessel(request.state.license_claims, vessel_id):
        raise HTTPException(403, "Not authorized")
    
    # 4. Update
    await db.update(vessel_id, validated_data)
```

### 2. Always Verify Signatures
```python
# Every data submission endpoint should:
1. Verify license token (authentication)
2. Verify data signature (authorization)
3. Validate data (integrity)
4. Check business rules (compliance)
```

### 3. Use Scope-Limited Tokens
```python
# When issuing tokens, limit scope to minimum required
{
  "typ": "PUL",
  "pillars": ["seaside"],  # Only SeaSide, not all pillars
  "features": ["read_only"],  # Explicit read-only
  "scope_digest": "sha256:...",  # Restricted routes
}
```

### 4. Implement Rate Limiting
```python
# Even with valid tokens, prevent abuse
@app.post("/ingest/packet")
@rate_limit("100/hour")  # Limit submissions
async def ingest_packet(...):
    ...
```

---

## 🔬 Testing Access Control

### Test Case 1: Invalid Token
```python
def test_invalid_token():
    response = client.post(
        "/ingest/packet",
        headers={"X-ST-License": "invalid_token"},
        json={"data": "test"}
    )
    assert response.status_code == 401  # Unauthorized
```

### Test Case 2: Valid Token, Invalid Signature
```python
def test_valid_token_invalid_signature():
    response = client.post(
        "/ingest/packet",
        headers={"X-ST-License": valid_pul_token},
        json={
            "vessel_id": "VESSEL_001",
            "signature": "fake_signature",
            "data": "test"
        }
    )
    assert response.status_code == 401  # Invalid signature
```

### Test Case 3: PUL Token Accessing Premium Endpoint
```python
def test_pul_token_premium_access():
    response = client.post(
        "/api/v1/marketside/trade",
        headers={"X-ST-License": valid_pul_token},
        json={"trade": "data"}
    )
    assert response.status_code == 403  # Forbidden
```

---

## 📞 Security Contact

If you discover a security vulnerability or have questions about access control:

**Email:** security@worldseafoodproducers.com  
**Response Time:** 24 hours for critical issues  
**Bug Bounty:** Available for verified vulnerabilities

**What to report:**
- Authentication bypass
- Authorization escalation
- Token forgery methods
- Signature verification flaws
- Data validation bypasses

---

## 📚 Related Documentation

- [COMMONS_CHARTER.md](COMMONS_CHARTER.md) - Free pillar governance
- [PUBLIC-UNLIMITED.md](licensing/PUBLIC-UNLIMITED.md) - PUL license terms
- [PRIVATE-LIMITED.md](licensing/PRIVATE-LIMITED.md) - PL license terms
- [PUBLIC_PRIVATE_KEY_DEVELOPMENT_GUIDE.md](PUBLIC_PRIVATE_KEY_DEVELOPMENT_GUIDE.md) - Cryptographic implementation

---

## 🎯 Summary

**"Can anybody with this link make changes?"**

**Answer:** Having a PUL token is like having a **library card** - it lets you:
- ✅ **Read** books (access public data)
- ✅ **Visit** the library (use public endpoints)
- ✅ **Check** availability (query system status)

But it does **NOT** let you:
- ❌ **Write** books (create arbitrary data)
- ❌ **Edit** existing books (modify others' data)
- ❌ **Access** restricted sections (MarketSide premium)
- ❌ **Impersonate** authors (fake vessel signatures)

**To make legitimate changes** (like recording a catch), you need:
1. Valid PUL/PL token (proves you can access the endpoint)
2. Cryptographic signature (proves you are the authorized vessel/processor)
3. Valid data (passes business rule validation)
4. No conflicts (not a duplicate or invalid submission)

**This is security by design** - multiple independent layers that must all succeed for a change to be accepted.

---

**© 2025 SeaTrace | World Sea Food Producers Association**

*Building secure, transparent, and trusted seafood supply chains.*
