# 🛡️ SeaTrace 8-Layer Security Architecture

**For the Commons Good!** 🌊

## Overview

This security module implements a **Zero Trust Architecture** with 8 independent defensive layers. Each layer blocks specific attack vectors, creating defense-in-depth protection.

---

## 🏈 The 8 Defensive Layers

### Layer 1: Rate Limiting
**Blocks:** DDoS, Brute Force, Resource Exhaustion

**Implementation:**
- `slowapi` + Redis for distributed rate limiting
- Per-endpoint limits (100 req/min for verify, 10 req/min for login)
- Automatic 429 responses with retry-after headers

**Usage:**
```python
from security.rate_limiting import limiter

@app.get("/api/verify")
@limiter.limit("100/minute")
async def verify_license(request: Request):
    ...
```

---

### Layer 2: Input Validation
**Blocks:** SQL Injection, XSS, Command Injection

**Implementation:**
- Pydantic models with automatic sanitization
- HTML escaping, SQL pattern removal
- Type enforcement and length limits

**Usage:**
```python
from security.input_validation import LicenseKeyInput

@app.post("/api/verify")
async def verify(data: LicenseKeyInput):
    # data.license_key is validated and sanitized
    ...
```

---

### Layer 3: Timing Attack Defense
**Blocks:** Timing Attacks, Side-Channel Analysis

**Implementation:**
- Constant-time string comparison (`hmac.compare_digest`)
- Random delays to mask processing time
- Prevents secret extraction via timing analysis

**Usage:**
```python
from security.timing_defense import constant_time_compare

if await constant_time_compare(signature, expected):
    # Comparison took same time regardless of match
    ...
```

---

### Layer 4: Replay Attack Defense
**Blocks:** Replay Attacks, Token Reuse

**Implementation:**
- Nonce + timestamp validation
- In-memory cache (Redis in production)
- 5-minute request window

**Usage:**
```python
from security.replay_defense import verify_request_freshness

await verify_request_freshness(nonce, timestamp)
```

---

### Layer 5: Secret Management
**Blocks:** Secret Leakage, Credential Exposure

**Implementation:**
- Environment variables only (never hardcoded)
- Fernet encryption at rest
- Automatic secret rotation support

**Usage:**
```python
from security.secret_manager import get_secret

JWT_SECRET = get_secret('JWT_SECRET_KEY')
```

---

### Layer 6: TLS Encryption
**Blocks:** Man-in-the-Middle, Eavesdropping

**Implementation:**
- TLS 1.3 enforcement
- Strong cipher suites only
- Automatic HTTP → HTTPS redirect

**Usage:**
```python
from security.tls_config import create_ssl_context

ssl_context = create_ssl_context(
    certfile="cert.pem",
    keyfile="key.pem"
)
```

---

### Layer 7: CRL Validation
**Blocks:** Revoked License Usage, Stolen Credentials

**Implementation:**
- Cached CRL checks (1-hour TTL)
- Fail-open mode (availability > security)
- Automatic refresh

**Usage:**
```python
from security.crl_validator import is_license_revoked

if await is_license_revoked(license_key):
    raise HTTPException(401, "License revoked")
```

---

### Layer 8: RBAC (Role-Based Access Control)
**Blocks:** Privilege Escalation, Unauthorized Access

**Implementation:**
- Least privilege principle
- Granular permissions (read, write, delete, admin)
- Decorator-based enforcement

**Usage:**
```python
from security.rbac import require_permission, Permission

@app.delete("/api/users/{user_id}")
@require_permission(Permission.MANAGE_USERS)
async def delete_user(user_id: str, current_user: User):
    # Only ADMIN role can execute this
    ...
```

---

## 🎯 Quick Start

### 1. Install Dependencies

```bash
pip install slowapi redis pydantic cryptography httpx
```

### 2. Set Environment Variables

```bash
# Required
export JWT_SECRET_KEY="your-secret-key"
export ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"

# Optional
export DATABASE_URL="postgresql://user:pass@localhost/seatrace"
export REDIS_URL="redis://localhost:6379/0"
```

### 3. Integrate into FastAPI

```python
from fastapi import FastAPI
from security.rate_limiting import limiter
from security.tls_config import HTTPSRedirectMiddleware
from security.crl_validator import init_crl_validator

app = FastAPI()

# Add rate limiting
app.state.limiter = limiter

# Add HTTPS redirect
app.add_middleware(HTTPSRedirectMiddleware)

# Initialize CRL validator
@app.on_event("startup")
async def startup():
    init_crl_validator("https://example.com/crl/revoked.json")
```

---

## 🏆 Security Checklist

- [x] **Layer 1:** Rate limiting active on all endpoints
- [x] **Layer 2:** Input validation on all user inputs
- [x] **Layer 3:** Constant-time comparisons for secrets
- [x] **Layer 4:** Nonce validation on authenticated requests
- [x] **Layer 5:** No hardcoded secrets (environment only)
- [x] **Layer 6:** TLS 1.3 enforced in production
- [x] **Layer 7:** CRL checks on license verification
- [x] **Layer 8:** RBAC on all protected endpoints

---

## 🌊 For the Commons Good!

This security architecture protects both:
- **Public users** (PUL license holders)
- **Paid users** (PL license holders)

While maintaining the **Commons Charter** principles:
- Transparency (open source security)
- Fairness (equal protection for all)
- Sustainability (scalable security)

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Zero Trust Architecture](https://www.nist.gov/publications/zero-trust-architecture)

---

**Last Updated:** 2025-10-13  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
