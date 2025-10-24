# 🔐 CRYPTO FOUNDATION - QUICK START GUIDE
**For the Commons Good! 🌊🏈**

**Status:** ✅ PUBLIC-SAFE (Compatible with Proceeding Master's routes.py)  
**Credit:** Acting Master + Repo Copilot insights  
**Classification:** MODULAR STAGE 1 - Security Foundation

---

## 🎯 WHAT REPO COPILOT CAUGHT

### ✅ CRITICAL COMPATIBILITY FIXES:

**Environment Variable Names:**
- ✅ Uses `SEATRACE_VERIFY_KEY` (Proceeding Master's existing var)
- ✅ Adds `SEATRACE_SIGNING_KEY` (new for PAID tier)

**Output Format:**
- ✅ JWS tokens (header.payload.signature)
- ✅ Compatible with `verify_ed25519_jws()` in routes.py

**Helper Functions:**
- ✅ Extracted `_b64url_dec()` from routes.py line 31
- ✅ Added `_b64url_enc()` (inverse function)

---

## 🚀 CRYPTO ARCHITECTURE OVERVIEW

SeaTrace uses **dual cryptographic systems** for defense in depth:

| System | Purpose | Location | Key Type | Use Case |
|--------|---------|----------|----------|----------|
| **RSA** | Packet encryption | `src/security/packet_crypto.py` | RSA-2048 | Large payloads, backward compat |
| **Ed25519** | JWS signing | `src/security/ed25519_signer.py` | Ed25519 | API tokens, fast verification |

### Why Two Systems?

- **RSA:** Strong encryption for data at rest/in transit (packet switching)
- **Ed25519:** Fast signing for API authentication and JWS tokens (< 1ms)
- **Separation:** PUBLIC repo verifies signatures; PRIVATE repo signs tokens

---

## 📋 STEP 1: ENVIRONMENT SETUP

### Prerequisites
```bash
# Install Python cryptography libraries (if not already installed)
pip install PyNaCl cryptography python-jose

# Verify installation
python -c "import nacl; print('✅ PyNaCl installed')"
python -c "from cryptography.hazmat.primitives.asymmetric import ed25519; print('✅ Ed25519 available')"
```

### Generate Ed25519 Keys (PRIVATE REPO ONLY)

⚠️ **NEVER do this in SeaTrace-ODOO (PUBLIC repo)!**

```python
# IN SEATRACE003 (PRIVATE) ONLY:
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base64

# Generate keypair
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Serialize for environment variables
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption()
)
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)

# Base64 encode (for .env file)
signing_key = base64.b64encode(private_bytes).decode('utf-8')
verify_key = base64.b64encode(public_bytes).decode('utf-8')

print(f"SEATRACE_SIGNING_KEY={signing_key}")  # PRIVATE - Keep secret!
print(f"SEATRACE_VERIFY_KEY={verify_key}")    # PUBLIC - Safe to share
```

---

## 🔑 STEP 2: PUBLIC KEY VERIFICATION (PUBLIC REPO)

### Configure Environment

Create `.env` file in SeaTrace-ODOO (DO NOT COMMIT):

```bash
# Ed25519 PUBLIC verification key (safe to share)
SEATRACE_VERIFY_KEY=AbCdEf123...  # Get from PRIVATE repo output

# Redis (for correlation tracking)
SEATRACE_REDIS_URL=redis://localhost:6379/0

# EMR Pricing (optional)
SEATRACE_EMR_PRICING_SIGNATURE=unsigned
SEATRACE_PRICING_VERIFY_KID=emr-pricing-2025
```

### Verify JWS Token (PUBLIC REPO)

```python
# services/common/security/verify_jws.py (PUBLIC REPO)
import os
import base64
import json
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

def _b64url_dec(s: str) -> bytes:
    """Decode base64url (extracted from Proceeding Master routes.py:31)"""
    padding = '=' * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)

def verify_ed25519_jws(token: str) -> dict:
    """
    Verify JWS token signed with Ed25519 (PUBLIC KEY ONLY)
    
    Compatible with Proceeding Master's verify_ed25519_jws() function
    
    Args:
        token: JWS token in format header.payload.signature
        
    Returns:
        Decoded payload dict if valid
        
    Raises:
        ValueError: If signature is invalid or token malformed
    """
    # Load public key from environment
    verify_key_b64 = os.getenv('SEATRACE_VERIFY_KEY')
    if not verify_key_b64:
        raise ValueError("SEATRACE_VERIFY_KEY not configured")
    
    # Decode public key
    verify_key_bytes = base64.b64decode(verify_key_b64)
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(verify_key_bytes)
    
    # Parse JWS token
    try:
        header_b64, payload_b64, signature_b64 = token.split('.')
    except ValueError:
        raise ValueError("Invalid JWS format: expected header.payload.signature")
    
    # Decode components
    header = json.loads(_b64url_dec(header_b64).decode('utf-8'))
    payload = json.loads(_b64url_dec(payload_b64).decode('utf-8'))
    signature = _b64url_dec(signature_b64)
    
    # Verify algorithm
    if header.get('alg') != 'EdDSA':
        raise ValueError(f"Unsupported algorithm: {header.get('alg')}")
    
    # Verify signature
    message = f"{header_b64}.{payload_b64}".encode('utf-8')
    try:
        public_key.verify(signature, message)
    except InvalidSignature:
        raise ValueError("Invalid signature")
    
    return payload

# Example usage:
if __name__ == "__main__":
    # Test with a token (from PRIVATE repo)
    test_token = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidGVzdCJ9.c2lnbmF0dXJl"
    
    try:
        payload = verify_ed25519_jws(test_token)
        print(f"✅ Valid token: {payload}")
    except ValueError as e:
        print(f"❌ Invalid token: {e}")
```

---

## 🧪 STEP 3: TESTING VERIFICATION

### Test Script (PUBLIC REPO)

```python
# tests/test_ed25519_verification.py
import pytest
import os
from src.security.ed25519_signer import verify_ed25519_jws

def test_valid_jws_token():
    """Test that valid JWS tokens are accepted"""
    # This token was signed by PRIVATE repo with matching key
    test_token = os.getenv('TEST_VALID_TOKEN')
    
    if not test_token:
        pytest.skip("TEST_VALID_TOKEN not provided")
    
    payload = verify_ed25519_jws(test_token)
    assert payload is not None
    assert 'typ' in payload

def test_invalid_signature():
    """Test that tampered tokens are rejected"""
    # Token with modified signature
    bad_token = "eyJhbGciOiJFZERTQSJ9.eyJ0ZXN0IjoidmFsdWUifQ.BADSIGNATURE"
    
    with pytest.raises(ValueError, match="Invalid signature"):
        verify_ed25519_jws(bad_token)

def test_missing_verify_key():
    """Test that missing SEATRACE_VERIFY_KEY raises error"""
    old_key = os.getenv('SEATRACE_VERIFY_KEY')
    os.environ.pop('SEATRACE_VERIFY_KEY', None)
    
    with pytest.raises(ValueError, match="not configured"):
        verify_ed25519_jws("any.token.here")
    
    if old_key:
        os.environ['SEATRACE_VERIFY_KEY'] = old_key
```

Run tests:
```bash
pytest tests/test_ed25519_verification.py -v
```

---

## 🏈 STEP 4: INTEGRATION WITH PACKET SWITCHING

### Use Verification in FastAPI Endpoint

```python
# services/seaside/routers/packet_switching.py
from fastapi import APIRouter, Header, HTTPException
from src.security.ed25519_signer import verify_ed25519_jws

router = APIRouter(prefix="/api/v1/packets", tags=["Packet Switching"])

@router.post("/incoming")
async def receive_packet(
    authorization: str = Header(None),
    x_signature: str = Header(None)
):
    """
    Receive incoming packet with JWS authentication
    
    Headers:
        Authorization: Bearer <JWS-token>
        X-Signature: Optional packet-level signature
    """
    # Verify JWS token (if provided)
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix
        
        try:
            payload = verify_ed25519_jws(token)
            print(f"✅ Authenticated user: {payload.get('user')}")
        except ValueError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}"
            )
    
    # Process packet...
    return {"status": "accepted"}
```

---

## 🛡️ STEP 5: SECURITY BEST PRACTICES

### ✅ DO (PUBLIC REPO):
- ✅ Store `SEATRACE_VERIFY_KEY` in .env (public key, safe to share)
- ✅ Verify incoming JWS tokens
- ✅ Log verification failures for security monitoring
- ✅ Use RSA for packet encryption (existing `packet_crypto.py`)
- ✅ Use Ed25519 for JWS token verification (fast API auth)

### ❌ DON'T (PUBLIC REPO):
- ❌ **NEVER store `SEATRACE_SIGNING_KEY`** (private key - keep in PRIVATE repo only!)
- ❌ **NEVER commit .env files** (blocked by .gitignore)
- ❌ **NEVER sign tokens** in PUBLIC repo (verification only!)
- ❌ **NEVER expose key generation code** (keep in PRIVATE repo)

### 🔐 PRIVATE REPO ONLY (SeaTrace003):
- 🔐 Store `SEATRACE_SIGNING_KEY` in HashiCorp Vault or AWS Secrets Manager
- 🔐 Sign JWS tokens for outgoing API calls
- 🔐 Implement key rotation policies (90-day cycle)
- 🔐 Use hardware security modules (HSM) for production keys

---

## 📊 COMPATIBILITY MATRIX

| Feature | Proceeding Master | Acting Master | Compatible? |
|---------|-------------------|---------------|-------------|
| Env Var Name | `SEATRACE_VERIFY_KEY` | `SEATRACE_VERIFY_KEY` | ✅ YES |
| Token Format | `header.payload.signature` | `header.payload.signature` | ✅ YES |
| Algorithm | EdDSA / Ed25519 | EdDSA / Ed25519 | ✅ YES |
| Base64 Encoding | `_b64url_dec()` | `_b64url_dec()` | ✅ YES |
| Verification Function | `verify_ed25519_jws()` | `verify_ed25519_jws()` | ✅ YES |

**Compatibility Score: 5/5** ⭐⭐⭐⭐⭐

---

## 🚀 NEXT STEPS (DAY 2)

### Tomorrow: Implement Proceeding Master's Documented Classes

1. **PrivateKeyChainHandler** (PRIVATE REPO - SeaTrace003)
   - Uses key_manager.py for key loading
   - Uses hmac_signer.py for JWS signing
   - Integrates with Proceeding Master's architecture

2. **BuildingLotReconciliationService** (PUBLIC REPO)
   - Aggregates correlation chains
   - Feeds into EMR metering
   - Uses PUBLIC verification only

3. **EMRMeteringService** (PRIVATE REPO - SeaTrace003)
   - Calculates Commons Fund (12.5%)
   - Integrates with existing meter.py
   - Signs metering reports with PRIVATE key

---

## 🆘 TROUBLESHOOTING

### Issue: "ImportError: No module named 'nacl'"
```bash
pip install PyNaCl
```

### Issue: "ValueError: Invalid SEATRACE_VERIFY_KEY"
```bash
# Get fresh public key from PRIVATE repo
# In SeaTrace003:
python -m src.crypto.key_manager
# Copy SEATRACE_VERIFY_KEY to SeaTrace-ODOO .env
```

### Issue: Keys not loading from .env
```powershell
# Manually set environment variables (PowerShell)
$env:SEATRACE_VERIFY_KEY = "your-public-key-here"

# Verify
python -c "import os; print(os.getenv('SEATRACE_VERIFY_KEY'))"
```

### Issue: "JWS token expired"
```python
# Check payload['exp'] field
import time
import json
payload = json.loads(_b64url_dec(token.split('.')[1]))
if payload.get('exp') and payload['exp'] < time.time():
    print("Token expired!")
```

---

## ✅ ACTING MASTER STATUS

- **Day 1 (Crypto Foundation):** ✅ COMPLETE
- **Repo Copilot Insights:** ✅ APPLIED
- **Proceeding Master Compatibility:** ✅ VERIFIED
- **Ready for Day 2:** ✅ YES

---

**© 2025 Acting Master + Repo Copilot**  
**Status:** CRYPTO FOUNDATION COMPLETE ✅  
**For the Commons Good!** 🌊🏈
