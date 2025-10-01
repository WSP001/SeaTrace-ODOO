# SeaTrace Private-Limited License (PL)

**License Type:** Private-Limited (Monetized)  
**Version:** 2.0  
**Effective Date:** 2025-01-01  
**Module:** MarketSide (EXCHANGE)

---

## Overview

The **Private-Limited (PL) License** grants access to SeaTrace's **premium MarketSide module**, including advanced trading, pricing algorithms, market analytics, and settlement features.

### 🔐 Premium Features

| Feature | Description | Tier Availability |
|---------|-------------|-------------------|
| **Dynamic Trading** | Real-time marketplace with smart contract settlement | Pro, Enterprise |
| **Pricing Algorithms** | AI-powered price discovery and optimization | Pro, Enterprise |
| **Premium QR Analytics** | Advanced consumer engagement tracking | All tiers |
| **Market Settlement** | Automated payment processing and reconciliation | Pro, Enterprise |
| **White-Label Deployment** | Custom branding and domain binding | Enterprise |
| **Advanced Compliance** | Automated SIMP, EU IUU, MSC reporting | All tiers |

---

## Licensing Tiers

### Starter Tier (PL-S)
**Target:** Small operations (1-10 vessels)

**Pricing:** $500/month or $5,000/year (save 17%)

**Included:**
- ✅ Basic MarketSide trading APIs
- ✅ Premium QR code generation (10,000 scans/month)
- ✅ Basic market analytics
- ✅ Email support (48-hour response)

**Limits:**
- 10,000 QR scans/month
- 2,000 transactions/month
- 10 API requests/second
- 5 user seats

**Overage Policy:** Soft throttling + upgrade prompt

---

### Professional Tier (PL-P)
**Target:** Mid-size operations (11-50 vessels)

**Pricing:** $2,000/month or $20,000/year (save 17%)

**Included:**
- ✅ Full MarketSide trading platform
- ✅ Advanced pricing algorithms
- ✅ Premium QR analytics (100,000 scans/month)
- ✅ Real-time settlement
- ✅ Priority support (24-hour response)
- ✅ SLA: 99.5% uptime (Gold)

**Limits:**
- 100,000 QR scans/month
- 25,000 transactions/month
- 50 API requests/second
- 25 user seats

**Overage Policy:** Automatic billing at $0.01/scan, $0.05/transaction

---

### Enterprise Tier (PL-E)
**Target:** Large operations (50+ vessels)

**Pricing:** Custom (starting at $5,000/month)

**Included:**
- ✅ Unlimited QR scans and transactions
- ✅ White-label deployment
- ✅ Custom domain binding
- ✅ Private API routes
- ✅ Dedicated support (4-hour response)
- ✅ SLA: 99.9% uptime (Platinum)
- ✅ Custom integrations
- ✅ On-premise deployment option

**Limits:**
- Custom negotiated limits
- Unlimited user seats
- Dedicated infrastructure

**Overage Policy:** Custom billing arrangements

---

## License Token Structure

### Ed25519 JWS Claims

```json
{
  "typ": "PL",
  "ver": 2,
  "license_id": "pl-AB12CD34",
  "org": "Acme Seafood LLC",
  "pillars": ["marketside"],
  "tier": "pro",
  "features": [
    "trade",
    "pricing",
    "qr_premium",
    "settlement",
    "analytics"
  ],
  "limits": {
    "qr_scans": 100000,
    "tx_per_month": 25000,
    "rps": 50
  },
  "seats": 25,
  "sla": "gold",
  "exp": 1767225599,
  "domain_bind": ["market.acme.com"],
  "billing": {
    "model": "hybrid",
    "overage": "bill"
  }
}
```

### Verification Process

**1. Signature Validation:**
- Token signed with SeaTrace private Ed25519 key
- Middleware verifies using public key
- Invalid signatures result in 401 Unauthorized

**2. Expiry Check:**
- Token includes Unix timestamp expiry
- Grace period: 14 days for billing failures
- Expired tokens result in 403 Forbidden

**3. Feature Entitlement:**
- Each API endpoint checks required features
- Missing features result in 403 Forbidden
- Feature list is cryptographically bound

**4. Usage Limits:**
- Real-time quota tracking via Redis
- Soft limits trigger upgrade prompts
- Hard limits enforce throttling or billing

---

## API Entitlements

### MarketSide Endpoints (PL Required)

**Trading:**
- `POST /api/v1/marketside/trade` - Create trade order
- `GET /api/v1/marketside/trades` - List trades
- `PUT /api/v1/marketside/trade/{id}` - Update trade
- `DELETE /api/v1/marketside/trade/{id}` - Cancel trade

**Pricing:**
- `GET /api/v1/marketside/pricing` - Get dynamic pricing
- `POST /api/v1/marketside/pricing/optimize` - Run optimization
- `GET /api/v1/marketside/pricing/history` - Price history

**Settlement:**
- `POST /api/v1/marketside/settlement` - Initiate settlement
- `GET /api/v1/marketside/settlement/{id}` - Settlement status
- `POST /api/v1/marketside/settlement/reconcile` - Reconcile payments

**Premium QR:**
- `POST /api/v1/marketside/qr/premium` - Generate premium QR
- `GET /api/v1/marketside/qr/analytics` - QR analytics dashboard
- `POST /api/v1/marketside/qr/track` - Track QR scan events

---

## Usage Quotas & Overage

### Quota Tracking

**Real-time metering:**
- QR scans: Incremented on each `/qr/track` call
- Transactions: Incremented on each `/trade` creation
- API calls: Rate-limited per second

**Quota enforcement:**
```python
# Soft limit (90% of quota)
if usage >= limit * 0.9:
    response.headers["X-Quota-Warning"] = "Approaching limit"
    
# Hard limit (100% of quota)
if usage >= limit:
    if billing_model == "bill":
        # Allow overage, bill later
        usage_events.emit(overage_event)
    elif billing_model == "throttle":
        raise HTTPException(429, "Quota exceeded")
    elif billing_model == "block":
        raise HTTPException(402, "Payment required")
```

### Overage Pricing

| Resource | Overage Rate | Billing Cycle |
|----------|--------------|---------------|
| QR Scans | $0.01/scan | Monthly |
| Transactions | $0.05/transaction | Monthly |
| API Calls | $0.001/call | Monthly |
| Storage | $0.10/GB | Monthly |

---

## Billing Events

### Event Types

**License Lifecycle:**
- `license_activated` - New license issued
- `license_renewed` - Subscription renewed
- `license_expired` - Subscription lapsed
- `license_revoked` - License terminated

**Usage Events:**
- `heartbeat_ok` - Periodic check-in successful
- `heartbeat_grace` - Grace period activated
- `quota_exceeded` - Soft limit reached
- `overage_incurred` - Billable overage occurred

**Security Events:**
- `invalid_signature` - Token signature failed
- `scope_violation` - Attempted unauthorized access
- `rate_limit_exceeded` - Too many requests

### Event Schema

```json
{
  "event_id": "evt_1234567890",
  "event_type": "overage_incurred",
  "timestamp": "2025-01-15T14:30:00Z",
  "license_id": "pl-AB12CD34",
  "org": "Acme Seafood LLC",
  "tier": "pro",
  "metadata": {
    "resource": "qr_scans",
    "limit": 100000,
    "usage": 105000,
    "overage": 5000,
    "cost": 50.00
  }
}
```

---

## Security & Compliance

### Domain Binding (Optional)

**Enterprise tier feature:**
- Restrict license to specific domains
- Prevents unauthorized deployments
- Validated via HTTP headers

```json
"domain_bind": ["market.acme.com", "api.acme.com"]
```

### Certificate Revocation List (CRL)

**Published daily:**
```bash
curl https://seatrace.worldseafoodproducers.com/crl/revoked.json
```

**Format:**
```json
{
  "version": 1,
  "updated": "2025-01-15T00:00:00Z",
  "revoked": [
    {
      "license_id": "pl-REVOKED1",
      "reason": "payment_failure",
      "revoked_at": "2025-01-10T12:00:00Z"
    }
  ]
}
```

**Middleware caching:**
- Cache CRL for 24 hours
- Check on license validation
- Deny access if revoked

### Offline Mode

**Grace period for offline deployments:**
- Accept signed PL tokens offline for **7 days**
- Require periodic heartbeat every 24 hours
- After 7 days, require online verification

**Heartbeat endpoint:**
```bash
POST /api/license/heartbeat
Authorization: Bearer {PL_TOKEN}

Response:
{
  "status": "ok",
  "next_check": "2025-01-16T14:30:00Z",
  "grace_remaining": "6 days"
}
```

---

## Telemetry & Monitoring

### Prometheus Metrics

**License metrics:**
```
st_license_active{tier="pro"} 150
st_license_expired_total 5
st_license_revoked_total 2
```

**Usage metrics:**
```
st_qr_scans_total{org="acme"} 95000
st_trades_total{org="acme"} 23000
st_api_requests_total{endpoint="/trade"} 50000
```

**Quota metrics:**
```
st_quota_exceeded_total{resource="qr_scans"} 3
st_overage_incurred_total{resource="transactions"} 1
st_overage_cost_usd{org="acme"} 125.50
```

### Grafana Dashboards

**License Health:**
- Active licenses by tier
- Expiry timeline
- Revocation events

**Usage Analytics:**
- QR scans over time
- Transaction volume
- API request rates

**Billing Insights:**
- Overage costs by org
- Revenue by tier
- Churn indicators

---

## Upgrade & Downgrade

### In-Product Upgrade

**Trigger points:**
- 90% quota utilization
- Feature access denied
- Manual upgrade request

**Upgrade flow:**
```
1. User clicks "Upgrade" in dashboard
2. Redirect to pricing page with pre-filled org info
3. Select new tier and payment method
4. Generate new PL token with upgraded entitlements
5. Deploy new token (zero downtime)
```

### Downgrade Policy

**Voluntary downgrade:**
- Allowed at end of billing cycle
- Pro-rated refund available
- 30-day notice required

**Involuntary downgrade:**
- Payment failure after 14-day grace
- Downgrade to Starter or suspend
- Data retention: 90 days

---

## Support & SLA

### Support Tiers

| Tier | Response Time | Channels | Availability |
|------|---------------|----------|--------------|
| **Starter** | 48 hours | Email | Business hours |
| **Professional** | 24 hours | Email, Chat | 24/5 |
| **Enterprise** | 4 hours | Email, Chat, Phone | 24/7 |

### Service Level Agreements

**Gold SLA (Professional):**
- 99.5% uptime guarantee
- $100 credit per 0.1% below target
- Scheduled maintenance: 4 hours/month

**Platinum SLA (Enterprise):**
- 99.9% uptime guarantee
- $500 credit per 0.1% below target
- Scheduled maintenance: 2 hours/quarter

---

## How to Obtain PL License

### 1. Contact Sales

**Email:** licensing@worldseafoodproducers.com  
**Phone:** [Contact Number]  
**Web:** https://seatrace.worldseafoodproducers.com/pricing

**Provide:**
- Organization name and details
- Estimated vessel count
- Expected transaction volume
- Desired tier (Starter/Pro/Enterprise)

### 2. Contract & Payment

**Contract terms:**
- Monthly or annual billing
- Auto-renewal (opt-out available)
- 30-day money-back guarantee

**Payment methods:**
- Credit card (Stripe)
- ACH/Wire transfer
- Purchase order (Enterprise only)

### 3. License Provisioning

**Delivery timeline:**
- Starter: Instant (automated)
- Professional: 1 business day
- Enterprise: 3-5 business days (custom setup)

**Receive:**
- Signed PL token (Ed25519 JWS)
- Verification public key
- Integration documentation
- Support contact information

### 4. Integration

**Deploy PL token:**
```python
from seatrace.licensing import LicenseMiddleware

app.add_middleware(
    LicenseMiddleware,
    license_token=PL_TOKEN,
    verify_key=VERIFY_KEY,
    crl_url="https://seatrace.com/crl/revoked.json"
)
```

**Verify entitlements:**
```bash
curl -H "X-ST-License: ${PL_TOKEN}" \
     https://api.seatrace.com/api/license/status
```

---

## Legal

**Governing Law:** Delaware, USA  
**Warranty:** LIMITED WARRANTY (see contract)  
**Liability:** LIMITED TO 12 MONTHS FEES PAID  

**Termination:**
- Either party: 30-day written notice
- For cause: Immediate termination
- Data export: 90-day window

---

## FAQ

**Q: Can I use PL features with PUL token?**  
A: No. MarketSide requires a valid PL token. Attempting to access with PUL results in 403 Forbidden.

**Q: What happens if my license expires?**  
A: 14-day grace period with warnings. After that, MarketSide access is suspended. Public modules (PUL) remain accessible.

**Q: Can I transfer my license to another organization?**  
A: Enterprise tier only, with written approval. Contact licensing@worldseafoodproducers.com.

**Q: Do you offer discounts for non-profits?**  
A: Yes, 30% discount for registered 501(c)(3) organizations. Contact sales for details.

**Q: Can I test MarketSide before purchasing?**  
A: Yes, 14-day free trial available. No credit card required. Contact sales to activate.

---

**© 2025 SeaTrace | World Sea Food Producers Association**

*For Public-Unlimited (PUL) licensing, see [PUBLIC-UNLIMITED.md](PUBLIC-UNLIMITED.md)*
