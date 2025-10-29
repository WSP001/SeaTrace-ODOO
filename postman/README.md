# 📮 SeaTrace Commons KPI Demo (PUBLIC)

**Classification:** PUBLIC-UNLIMITED  
**Purpose:** Developer adoption, QR verification, regulatory transparency  
**FOR THE COMMONS GOOD!** 🌍🐟🚀

---

## 🎯 **What is This?**

This Postman collection provides **PUBLIC** access to SeaTrace's Four Pillars API:
- 🌊 **SeaSide** (HOLD) - Vessel tracking
- 📊 **DeckSide** (RECORD) - Catch verification  
- 🏗️ **DockSide** (STORE) - Supply chain management
- 🏪 **MarketSide** (EXCHANGE) - Consumer verification

**NO PRIVATE DATA** - This collection contains:
- ✅ Health checks
- ✅ Public key distribution (JWKS)
- ✅ QR verification (rate-limited demo)
- ✅ Public read-only models

**NO SECRETS** - This collection does NOT contain:
- ❌ Private keys
- ❌ Investor endpoints
- ❌ Precise GPS coordinates
- ❌ Financial data
- ❌ ML model predictions

---

## 📥 **Import & Run**

### **Method 1: Postman Desktop/Web**

1. **Download** the collection:
   - File: `postman/collections/SeaTrace_Commons_KPI_Demo.postman_collection.json`

2. **Import** into Postman:
   - Open Postman
   - Click **Import** (top-left)
   - Drag & drop the JSON file
   - Click **Import**

3. **Set the Base URL** (Collection Variables):
   - Click on the collection name
   - Go to **Variables** tab
   - Set `baseUrl` to your environment:
     - **Production:** `https://seatrace.worldseafoodproducers.com`
     - **Staging:** `https://staging.seatrace.worldseafoodproducers.com`
     - **Local Dev:** `http://localhost:8000`

4. **Run** the collection:
   - Click **Runner** (top-right)
   - Select **SeaTrace Commons KPI Demo**
   - Click **Run SeaTrace Commons...**
   - Watch the tests pass! ✅

---

### **Method 2: Newman (CLI)**

```bash
# Install Newman
npm install -g newman

# Run collection (replace BASE_URL with your environment)
newman run postman/collections/SeaTrace_Commons_KPI_Demo.postman_collection.json \
  --env-var "baseUrl=https://seatrace.worldseafoodproducers.com" \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export newman-report.html

# View HTML report
open newman-report.html  # macOS
start newman-report.html  # Windows
xdg-open newman-report.html  # Linux
```

---

### **Method 3: GitHub Actions (CI/CD)**

```yaml
# .github/workflows/postman-smoke-test.yml
name: Postman Smoke Test

on:
  pull_request:
    paths:
      - 'postman/**'
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  smoke-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Newman
        run: npm install -g newman newman-reporter-htmlextra
      
      - name: Run Postman Collection
        env:
          BASE_URL: ${{ secrets.PUBLIC_BASE_URL }}
        run: |
          newman run postman/collections/SeaTrace_Commons_KPI_Demo.postman_collection.json \
            --env-var "baseUrl=$BASE_URL" \
            --reporters cli,htmlextra \
            --reporter-htmlextra-export newman-report.html \
            --bail
      
      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: newman-report
          path: newman-report.html
```

---

## 📊 **Endpoints**

### **1. Health & Status** ✅

#### **GET /health**
- **Purpose:** Simple health check (200 = service operational)
- **Auth:** None
- **Rate Limit:** Unlimited
- **Response:**
  ```json
  {
    "status": "healthy",
    "timestamp": "2025-10-26T12:34:56Z"
  }
  ```

#### **GET /status**
- **Purpose:** Detailed status (version, uptime)
- **Auth:** None
- **Rate Limit:** Unlimited
- **Response:**
  ```json
  {
    "version": "1.0.0",
    "uptime": 123456,
    "environment": "production"
  }
  ```

---

### **2. JWKS (Public Keys)** 🔐

#### **GET /.well-known/jwks.json**
- **Purpose:** Public keys for JWT signature verification (RFC 7517)
- **Auth:** None
- **Rate Limit:** 1000/hour
- **Cache:** 1 hour
- **Response:**
  ```json
  {
    "keys": [
      {
        "kty": "RSA",
        "n": "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx...",
        "e": "AQAB",
        "use": "sig",
        "alg": "RS256",
        "kid": "kid-001"
      }
    ]
  }
  ```

**Security:**
- ✅ Contains ONLY public key components (`n`, `e`)
- ❌ NO private key components (`d`, `p`, `q`)
- ✅ Safe to distribute publicly

**Usage:**
```javascript
// Verify JWT signature using JWKS
const jwks = await fetch('https://seatrace.worldseafoodproducers.com/.well-known/jwks.json');
const keys = await jwks.json();
// Use keys.keys[0] to verify JWT
```

---

### **3. MarketSide (QR Verification)** 🏪

#### **POST /api/v1/marketside/qr/verify**
- **Purpose:** Verify QR code and retrieve catch provenance
- **Auth:** `X-License-ID` header (demo: `PUBLIC-DEMO-LICENSE`)
- **Rate Limit:** 200 requests/hour (demo license)
- **Request:**
  ```json
  {
    "qr_code": "DEMO-QR-0001",
    "scan_location": {
      "lat": 47.6062,
      "lon": -122.3321,
      "city": "Seattle"
    },
    "scanner_type": "mobile_app"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "verification_status": "verified",
    "catch_id": "CATCH-000-001",
    "vessel_id": "F/V 000",
    "species": "Pacific Salmon",
    "timestamp": "2025-10-26T08:15:00Z",
    "location": {
      "approximate_lat": 47.6,
      "approximate_lon": -122.3,
      "region": "Pacific Northwest"
    }
  }
  ```
- **Response (429 Rate Limited):**
  ```json
  {
    "error": "rate_limit_exceeded",
    "message": "Demo license allows 200 requests/hour",
    "reset_time": "2025-10-26T13:00:00Z"
  }
  ```

**Tests:**
- ✅ Accepts 200 (verified) OR 429 (rate-limited)
- ✅ Validates rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`)
- ✅ Response time < 2 seconds

#### **GET /api/v1/marketside/qr/{qr_code}/status**
- **Purpose:** Get QR code status (active, expired, revoked)
- **Auth:** `X-License-ID` header
- **Rate Limit:** 200 requests/hour
- **Response:**
  ```json
  {
    "qr_code": "DEMO-QR-0001",
    "status": "active",
    "verification_count": 42,
    "created_at": "2025-10-01T00:00:00Z"
  }
  ```

---

### **4. Public Models (Read-Only)** 📖

#### **GET /api/v1/public/vessels**
- **Purpose:** List public vessels (NO precise GPS, NO financial data)
- **Auth:** None
- **Rate Limit:** 500/hour
- **Query Params:**
  - `limit` (default: 10, max: 100)
  - `offset` (default: 0)
- **Response:**
  ```json
  [
    {
      "vessel_id": "F/V 000",
      "vessel_name": "Pacific Explorer",
      "registration": "WA-1234",
      "last_updated": "2025-10-26T12:00:00Z"
    }
  ]
  ```

#### **GET /api/v1/public/catch/{catch_id}**
- **Purpose:** Get PUBLIC catch details (approximate location only)
- **Auth:** None
- **Rate Limit:** 500/hour
- **Response:**
  ```json
  {
    "catch_id": "CATCH-000-001",
    "species": "Pacific Salmon",
    "timestamp": "2025-10-26T08:15:00Z",
    "location": {
      "approximate_lat": 47.6,
      "approximate_lon": -122.3,
      "region": "Pacific Northwest"
    },
    "vessel_id": "F/V 000"
  }
  ```

**Security:**
- ✅ NO `precise_lat` or `precise_lon` fields
- ✅ NO `pricing` or `valuation` fields
- ✅ Commons Good transparency only

---

### **5. Load Testing Endpoints** 📈

#### **GET /api/v1/metrics/prometheus**
- **Purpose:** Prometheus metrics for monitoring
- **Auth:** None
- **Rate Limit:** Unlimited
- **Response:** Prometheus text format
  ```
  # HELP http_requests_total Total HTTP requests
  # TYPE http_requests_total counter
  http_requests_total{method="GET",status="200"} 12345
  ```

**Usage:** k6 load tests, Grafana dashboards

---

## 🧪 **Tests Included**

Every endpoint has **5-7 automated tests**:

### **Global Tests (All Requests):**
1. ✅ Response code is valid (200, 429, 404)
2. ✅ Response time is acceptable
3. ✅ Content-Type is JSON
4. ✅ Rate limit headers present (`X-RateLimit-*`)

### **Endpoint-Specific Tests:**
- **Health:** Status field is string
- **JWKS:** Keys array exists, has JWK properties, NO private components
- **QR Verify:** Verification status field, catch metadata
- **Public Models:** Array response, required fields present

### **Security Tests:**
- ✅ JWKS endpoint does NOT expose private key components (`d`, `p`, `q`)
- ✅ Public catch data does NOT include `precise_lat` or `pricing`

---

## 🔒 **Security & Scope**

### **What is PUBLIC:**
- ✅ This collection (no secrets)
- ✅ JWKS public keys
- ✅ QR verification (rate-limited)
- ✅ Approximate catch locations
- ✅ Vessel registration numbers

### **What is PRIVATE:**
- 🔒 Environment files (`.env`, `.postman_environment.json`)
- 🔒 API keys and tokens
- 🔒 Precise GPS coordinates
- 🔒 Financial data (pricing, valuations)
- 🔒 ML model predictions
- 🔒 Investor dashboards

### **Rate Limits:**
- **Demo License:** 200 requests/hour
- **Production License:** Contact sales@worldseafoodproducers.com
- **Burst:** Up to 10 requests in quick succession

---

## 🌊 **Four Pillars Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                   SeaTrace API Portal                   │
│          https://seatrace.worldseafoodproducers.com     │
└─────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
    ┌─────▼─────┐     ┌─────▼─────┐     ┌───▼───────┐
    │  SeaSide  │     │ DeckSide  │     │ DockSide  │
    │  (HOLD)   │────▶│ (RECORD)  │────▶│  (STORE)  │
    │  Vessel   │     │   Catch   │     │  Supply   │
    │ Tracking  │     │   Verify  │     │   Chain   │
    └───────────┘     └───────────┘     └───────────┘
                            │
                      ┌─────▼─────┐
                      │MarketSide │
                      │(EXCHANGE) │
                      │ Consumer  │
                      │  Verify   │
                      └───────────┘
```

**Stack Operator Valuation:** $4.2M USD  
**Classification:** PUBLIC-UNLIMITED (Commons Good)

---

## 🚀 **Next Steps**

1. **Import** the collection into Postman
2. **Set** the `baseUrl` variable to your environment
3. **Run** the collection (all tests should pass ✅)
4. **Review** the test results in Postman
5. **Explore** the API documentation at `https://seatrace.worldseafoodproducers.com/docs`

---

## 📞 **Support**

- **API Documentation:** https://seatrace.worldseafoodproducers.com/docs
- **Main Site:** https://worldseafoodproducers.com
- **Email:** scott@worldseafoodproducers.com
- **GitHub:** [WSP001/SeaTrace-ODOO](https://github.com/WSP001/SeaTrace-ODOO) (PUBLIC repo)

---

## 📄 **License**

**Classification:** PUBLIC-UNLIMITED  
**License:** MIT (for Commons Good)  
**FOR THE COMMONS GOOD!** 🌍🐟🚀

© 2024-2025 WorldSeafoodProducers.com - SeaTrace API Portal
