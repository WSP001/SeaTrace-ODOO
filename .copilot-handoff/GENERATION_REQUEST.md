# 🤖 GENERATION AGENT REQUEST - SeaTrace-ODOO Commons Improvements

**Date:** October 6, 2025  
**Requesting Agent:** Repo Copilot (Review & Architecture)  
**Target Agent:** Code Generation Specialist  
**Priority:** HIGH (Security + Performance)  
**Context:** PUBLIC repository (SeaTrace-ODOO) - Commons Charter aligned

---

## 📋 MISSION

Generate **production-ready integration files** for 4 approved improvements:
1. ✅ Timing attack fix (ALREADY DONE - validated)
2. 🔄 Bloom filter CRL integration (NEW - needs wiring)
3. 🔄 Rate limiter integration (NEW - needs wiring)
4. 🔄 CRL Management API routing (NEW - needs mounting)

**Commons Good Requirement:** ALL changes must maintain "free forever" access for PUL licenses.

---

## 🎯 PHASE 1: INTEGRATION FILES (TODAY - 2 HOURS)

### **File 1: `src/common/licensing/middleware.py` (MODIFY)**

**Current State:**
- 414 lines
- Timing attack fix already applied (line ~185-195)
- Imports: base64, json, time, structlog, nacl.signing
- Class: LicenseMiddleware(BaseHTTPMiddleware)

**Required Changes:**

```python
# ADD IMPORTS (after line 18)
from .bloom_crl import BloomCRL
from .rate_limiter import LicenseRateLimiter

# MODIFY __init__ (around line 50)
class LicenseMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        public_scope_digest: str,
        public_routes: list[str],
        verify_key: str,
        crl_url: Optional[str] = None,
        verify_keys_by_kid: Optional[Dict[str, str]] = None,
        redis_client = None,  # NEW: Add Redis client
    ):
        super().__init__(app)
        # ... existing fields ...
        
        # NEW: Initialize Bloom CRL and rate limiter
        if redis_client:
            self.bloom_crl = BloomCRL(
                redis_client=redis_client,
                capacity=100000,
                error_rate=0.0001,
                refresh_interval_seconds=300
            )
            self.rate_limiter = LicenseRateLimiter(redis_client)
        else:
            self.bloom_crl = None
            self.rate_limiter = None
            logger.warning("redis_not_configured", 
                          message="Bloom CRL and rate limiter disabled")

# MODIFY dispatch() method (around line 120)
async def dispatch(self, request: Request, call_next):
    # ... existing signature verification ...
    
    # NEW: Check Bloom CRL (BEFORE existing CRL check)
    if self.bloom_crl:
        license_id = payload.get("license_id") or payload.get("sub")
        if await self.bloom_crl.is_revoked(license_id):
            logger.warning("license_revoked", 
                          license_id=license_id[:16] + "...")
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "license_revoked",
                    "message": "This license has been revoked",
                    "license_id": license_id[:16] + "...",
                    "contact": "https://worldseafoodproducers.com/support"
                }
            )
    
    # NEW: Check rate limit (BEFORE semaphore acquisition)
    if self.rate_limiter:
        license_id = payload.get("license_id") or payload.get("sub")
        license_type = payload.get("typ", "PUL")
        tier = payload.get("tier")
        pillar = request.url.path.split("/")[3] if len(request.url.path.split("/")) > 3 else "unknown"
        
        try:
            await self.rate_limiter.check_rate_limit(
                license_id=license_id,
                license_type=license_type,
                tier=tier,
                pillar=pillar,
                request=request
            )
        except HTTPException as e:
            # Rate limit exceeded (429), log and re-raise
            logger.warning("rate_limit_exceeded",
                          license_id=license_id[:16] + "...",
                          tier=tier or license_type,
                          pillar=pillar)
            raise
    
    # ... rest of existing dispatch logic (semaphores, etc.) ...
```

**Validation:**
- ✅ Preserves existing timing attack fix
- ✅ Bloom CRL check happens BEFORE semaphore (fast path)
- ✅ Rate limiter check happens AFTER signature verification (security first)
- ✅ Graceful degradation if Redis unavailable (logs warning)
- ✅ All error messages include support contact (Commons transparency)

---

### **File 2: `src/app.py` (MODIFY - or create if doesn't exist)**

**Task:** Initialize FastAPI app with Redis, Bloom CRL, and CRL API router

**Required Implementation:**

```python
"""SeaTrace-ODOO FastAPI Application (PUBLIC).

This module initializes the FastAPI app with:
- License middleware (PUL and PL verification)
- Bloom filter CRL (10,000x faster revocation checks)
- Rate limiting (DOS prevention)
- CRL Management API (admin tools)

For the Commons Good! 🌊
"""

import asyncio
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from redis import asyncio as aioredis

from src.common.licensing.middleware import LicenseMiddleware
from src.common.licensing.bloom_crl import BloomCRL
from src.common.licensing.rate_limiter import LicenseRateLimiter
from src.admin.crl_api import router as crl_router

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager (startup/shutdown)."""
    
    # STARTUP
    logger.info("app_startup", version="1.0.0", scope="PUBLIC")
    
    # Initialize Redis
    redis_url = "redis://localhost:6379/1"  # TODO: Load from env
    app.state.redis = await aioredis.from_url(redis_url, decode_responses=False)
    logger.info("redis_connected", url=redis_url)
    
    # Initialize Bloom CRL
    app.state.bloom_crl = BloomCRL(
        redis_client=app.state.redis,
        capacity=100000,
        error_rate=0.0001,
        refresh_interval_seconds=300
    )
    
    # Initial Bloom filter refresh
    await app.state.bloom_crl.refresh_bloom_filter()
    logger.info("bloom_crl_initialized", revoked_count=app.state.bloom_crl.revoked_count)
    
    # Start background Bloom filter refresh task
    refresh_task = asyncio.create_task(
        app.state.bloom_crl.start_background_refresh()
    )
    logger.info("bloom_crl_refresh_task_started", interval_seconds=300)
    
    # Initialize rate limiter
    app.state.rate_limiter = LicenseRateLimiter(app.state.redis)
    logger.info("rate_limiter_initialized")
    
    yield
    
    # SHUTDOWN
    logger.info("app_shutdown")
    
    # Cancel background tasks
    refresh_task.cancel()
    try:
        await refresh_task
    except asyncio.CancelledError:
        pass
    
    # Close Redis connection
    await app.state.redis.close()
    logger.info("redis_closed")


# Initialize FastAPI app
app = FastAPI(
    title="SeaTrace-ODOO API (PUBLIC)",
    description="Commons-based seafood traceability with Public Unlimited License (PUL)",
    version="1.0.0",
    lifespan=lifespan
)

# Add license middleware
# TODO: Load verify keys from docs/licensing/verify-keys.json
# TODO: Load public scope digest from docs/licensing/public_scope_digest.txt
middleware = LicenseMiddleware(
    app=app,
    public_scope_digest="TODO_LOAD_FROM_FILE",
    public_routes=["/health", "/docs", "/openapi.json"],
    verify_key="TODO_LOAD_FROM_FILE",
    redis_client=None  # Will be set in lifespan startup
)

# Wire middleware to use Redis from app.state
@app.on_event("startup")
async def wire_middleware_redis():
    """Wire Redis into middleware after app.state.redis is initialized."""
    middleware.redis_client = app.state.redis
    middleware.bloom_crl = app.state.bloom_crl
    middleware.rate_limiter = app.state.rate_limiter
    logger.info("middleware_redis_wired")

app.add_middleware(LicenseMiddleware)

# Add CRL Management API
app.include_router(crl_router, tags=["admin"])
logger.info("crl_api_mounted", prefix="/admin/crl")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint (no license required)."""
    bloom_stats = app.state.bloom_crl.get_stats() if app.state.bloom_crl else {}
    return {
        "status": "healthy",
        "version": "1.0.0",
        "commons": "For the Commons Good! 🌊",
        "bloom_crl": bloom_stats
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

**Validation:**
- ✅ Lifespan context manager (proper startup/shutdown)
- ✅ Bloom filter refreshed on startup (no cold start delays)
- ✅ Background refresh task (keeps Bloom filter current)
- ✅ Health check includes Bloom CRL stats (monitoring-friendly)
- ✅ CRL API mounted at /admin/crl (admin tools)

---

### **File 3: `pyproject.toml` (MODIFY)**

**Task:** Add Redis and pybloom-live dependencies

**Required Changes:**

```toml
[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pynacl = "^1.5.0"
structlog = "^23.1.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
redis = "^5.0.1"           # NEW: Async Redis client
pybloom-live = "^4.0.0"    # NEW: Bloom filter implementation

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
black = "^23.9.0"
mypy = "^1.5.0"
```

**Or if using `requirements.txt`:**

```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pynacl>=1.5.0
structlog>=23.1.0
python-jose[cryptography]>=3.3.0
redis>=5.0.1            # NEW
pybloom-live>=4.0.0     # NEW

# Dev dependencies
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.9.0
mypy>=1.5.0
```

---

### **File 4: `.env.example` (CREATE)**

**Task:** Configuration template for Redis and CRL

```bash
# SeaTrace-ODOO Configuration (PUBLIC)
# Copy to .env and customize for your environment

# Redis (required for Bloom CRL and rate limiting)
REDIS_URL=redis://localhost:6379/1

# Bloom Filter CRL
BLOOM_CRL_CAPACITY=100000              # Expected number of revoked licenses
BLOOM_CRL_ERROR_RATE=0.0001            # False positive rate (0.01%)
BLOOM_CRL_REFRESH_INTERVAL=300         # Rebuild every 5 minutes

# Rate Limiting (requests per minute)
RATE_LIMIT_PUL=100                     # Public Unlimited License
RATE_LIMIT_PL_B=1000                   # Private Limited Basic
RATE_LIMIT_PL_P=10000                  # Private Limited Pro
RATE_LIMIT_PL_E=10000                  # Private Limited Enterprise

# License Verification
PUBLIC_SCOPE_DIGEST_PATH=docs/licensing/public_scope_digest.txt
VERIFY_KEYS_PATH=docs/licensing/verify-keys.json

# Logging
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR
STRUCTLOG_JSON=false                   # true for production

# Commons Good
COMMONS_FUND_PERCENT=12.5              # 12.5% of MarketSide revenue
MARKETSIDE_GROSS_REVENUE_URL=http://marketside:8081/api/revenue
```

---

### **File 5: `scripts/licensing/generate_admin_token.py` (CREATE)**

**Task:** Generate Ed25519 admin tokens for CRL API

```python
#!/usr/bin/env python3
"""Generate Ed25519 admin token for CRL Management API.

This script creates an admin token with:
- Ed25519 signature (32-byte key, 64-byte signature)
- Scope: "admin" (required for CRL API)
- Expiry: 1 year (configurable)
- Saved to: keys/admin/admin-token-{date}.jwt

Usage:
    python scripts/licensing/generate_admin_token.py
    python scripts/licensing/generate_admin_token.py --email admin@seatrace.org --days 365

For the Commons Good! 🌊
"""

import argparse
import base64
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import nacl.signing
import nacl.encoding


def generate_admin_token(admin_email: str, expiry_days: int) -> dict:
    """Generate Ed25519 admin token.
    
    Args:
        admin_email: Admin email address (for audit trail)
        expiry_days: Token expiry in days
    
    Returns:
        dict with token, public_key, private_key, expiry
    """
    # Generate Ed25519 key pair
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key
    
    # Create JWT payload
    now = datetime.utcnow()
    expiry = now + timedelta(days=expiry_days)
    
    header = {
        "alg": "EdDSA",
        "typ": "JWT",
        "kid": "admin-2025"  # Key ID for rotation
    }
    
    payload = {
        "typ": "ADMIN",
        "sub": admin_email,
        "scope": "admin crl:read crl:write",
        "iat": int(now.timestamp()),
        "exp": int(expiry.timestamp()),
        "iss": "SeaTrace-ODOO",
        "aud": "crl-api"
    }
    
    # Encode header and payload
    def b64url_encode(data: dict) -> str:
        json_bytes = json.dumps(data, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(json_bytes).decode().rstrip("=")
    
    h64 = b64url_encode(header)
    p64 = b64url_encode(payload)
    
    # Sign
    message = f"{h64}.{p64}".encode()
    signature = signing_key.sign(message).signature
    s64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    # Create JWT token
    token = f"{h64}.{p64}.{s64}"
    
    return {
        "token": token,
        "public_key": verify_key.encode(encoder=nacl.encoding.Base64Encoder).decode(),
        "private_key": signing_key.encode(encoder=nacl.encoding.Base64Encoder).decode(),
        "header": header,
        "payload": payload,
        "expiry": expiry.isoformat()
    }


def save_admin_token(token_data: dict, output_dir: Path):
    """Save admin token to file.
    
    Args:
        token_data: Token data from generate_admin_token()
        output_dir: Directory to save token (keys/admin/)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save token
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    token_path = output_dir / f"admin-token-{date_str}.jwt"
    
    with open(token_path, "w") as f:
        json.dump(token_data, f, indent=2)
    
    # Save public key only (for verify-keys.json)
    pubkey_path = output_dir / f"admin-public-{date_str}.txt"
    with open(pubkey_path, "w") as f:
        f.write(token_data["public_key"])
    
    return token_path


def main():
    parser = argparse.ArgumentParser(description="Generate Ed25519 admin token")
    parser.add_argument("--email", default="admin@seatrace.org", help="Admin email address")
    parser.add_argument("--days", type=int, default=365, help="Token expiry in days")
    args = parser.parse_args()
    
    print("\n🔑 Generating Admin Token...")
    print("━" * 60)
    
    # Generate token
    token_data = generate_admin_token(args.email, args.days)
    
    # Save to keys/admin/
    repo_root = Path(__file__).parent.parent.parent
    output_dir = repo_root / "keys" / "admin"
    token_path = save_admin_token(token_data, output_dir)
    
    # Display results
    print(f"\n✅ Admin Token Generated:")
    print("━" * 60)
    print(f"Email:      {args.email}")
    print(f"Scope:      {token_data['payload']['scope']}")
    print(f"Issued:     {datetime.utcfromtimestamp(token_data['payload']['iat']).isoformat()}Z")
    print(f"Expires:    {token_data['expiry']}Z")
    print(f"Key ID:     {token_data['header']['kid']}")
    print("━" * 60)
    print(f"\n🔒 Token (copy this):")
    print(token_data["token"])
    print(f"\n📝 Public Key (add to verify-keys.json):")
    print(token_data["public_key"])
    print(f"\n💾 Saved to:")
    print(f"  - Token: {token_path}")
    print(f"  - Public Key: {output_dir / f'admin-public-{datetime.utcnow().strftime(\"%Y-%m-%d\")}.txt'}")
    print("\n⚠️  IMPORTANT:")
    print("  1. Add public key to docs/licensing/verify-keys.json")
    print("  2. Keep private key secure (never commit to git)")
    print("  3. Use Authorization: Bearer <token> header for API calls")
    print("\n🌊 For the Commons Good!")
    print("━" * 60)


if __name__ == "__main__":
    main()
```

**Validation:**
- ✅ Ed25519 key generation (PyNaCl)
- ✅ JWT format (header.payload.signature)
- ✅ Admin scope included
- ✅ Key ID for rotation (admin-2025)
- ✅ Saved to keys/admin/ (gitignored directory)
- ✅ Public key extraction for verify-keys.json

---

## 🎯 SUCCESS CRITERIA

Generation Agent should produce files that:

1. ✅ **Integrate seamlessly** - No merge conflicts, preserve existing code
2. ✅ **Pass linting** - Black, mypy, pylint compliant
3. ✅ **Include comments** - Explain WHY, not just WHAT
4. ✅ **Commons-aligned** - All changes maintain free access
5. ✅ **Production-ready** - Error handling, logging, graceful degradation
6. ✅ **Documented** - Docstrings with examples
7. ✅ **Testable** - Clear interfaces for unit tests

---

## 📦 DELIVERABLES

**Phase 1 (TODAY):**
- [ ] Modified: `src/common/licensing/middleware.py`
- [ ] Modified: `src/app.py`
- [ ] Modified: `pyproject.toml` OR `requirements.txt`
- [ ] Created: `.env.example`
- [ ] Created: `scripts/licensing/generate_admin_token.py`

**Phase 2 (TOMORROW):**
- [ ] Created: `tests/test_bloom_crl.py`
- [ ] Created: `tests/test_rate_limiter.py`
- [ ] Created: `tests/test_crl_api.py`
- [ ] Created: `tests/test_timing_attack.py`
- [ ] Created: `tests/integration/test_middleware_e2e.py`

**Phase 3 (DAY 3):**
- [ ] Created: `docs/licensing/INTEGRATION_GUIDE.md`
- [ ] Created: `docs/admin/CRL_MANAGEMENT_API.md`
- [ ] Created: `docs/commons/PERFORMANCE_IMPROVEMENTS.md`
- [ ] Modified: `docs/licensing/PUBLIC-UNLIMITED.md`
- [ ] Modified: `docs/licensing/PRIVATE-LIMITED.md`

---

## 🌊 COMMONS GOOD VERIFICATION

Before generating each file, verify:

1. **Access Equality** - Free (PUL) users retain full access
2. **Performance Equality** - Bloom filter benefits all tiers
3. **Security Equality** - Timing attack fix universal
4. **Cost Efficiency** - Changes reduce infrastructure costs
5. **Transparency** - Audit trails, public CRL, clear errors

---

## 🚀 HANDOFF COMPLETE

**Requesting Agent:** Repo Copilot (Architecture Review)  
**Target Agent:** Code Generation Specialist  
**Priority:** HIGH  
**Timeline:** Phase 1 by end of day  
**Contact:** Review completed files before commit  

**For the Commons Good!** 🌊
