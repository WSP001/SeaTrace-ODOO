# SeaTrace Commons Charter

**Version:** 1.0  
**Effective Date:** 2025-01-01  
**Last Updated:** 2025-09-30

---

## Mission Statement

SeaTrace is committed to **keeping SeaSide, DeckSide, and DockSide free and accessible** as a **public good** for the global seafood supply chain. These pillars form the foundational infrastructure for vessel tracking, catch recording, and storage management—essential capabilities that should be available to all participants, from small-scale fishers to large enterprises.

**Our Promise:**
- SeaSide, DeckSide, and DockSide will **always remain free** (Public Unlimited License)
- No feature gates, no usage metering, no paywalls on public pillars
- Sustainable funding through MarketSide monetization and the Commons Fund
- Transparent governance with public accountability

---

## The Commons Model

### What's Free (Public Unlimited)

| Pillar | Capabilities | Access |
|--------|-------------|--------|
| **SeaSide (HOLD)** | Vessel tracking, AIS integration, telemetry | ✅ Free Forever |
| **DeckSide (RECORD)** | Catch recording, verification, compliance | ✅ Free Forever |
| **DockSide (STORE)** | Storage management, chain-of-custody, inventory | ✅ Free Forever |

### What's Monetized (Private Limited)

| Pillar | Capabilities | Access |
|--------|-------------|--------|
| **MarketSide (EXCHANGE)** | Trading, pricing algorithms, settlement, premium analytics | 💰 Paid Subscription |

---

## Sustainability: The Commons Fund

### How Free Pillars Stay Free

**Cross-Subsidy Model:**
- 10-15% of MarketSide gross revenue is allocated to the **Commons Fund**
- Commons Fund covers infrastructure costs for SeaSide, DeckSide, and DockSide
- Monthly transparency reports published at `/api/commons/fund`

### Commons Fund Allocation

```
MarketSide Revenue (100%)
    ├─ Commons Fund (10-15%) → Free Pillar Infrastructure
    ├─ R&D (20-25%) → Platform improvements
    ├─ Operations (30-35%) → Support, hosting, security
    └─ Growth (30-40%) → Sales, marketing, expansion
```

### Cost Controls (Not Paywalls)

To keep the commons sustainable without compromising "free":

**1. Concurrency Management**
- Heavy endpoints use priority queues (not rate limits)
- Sponsor credits enable higher priority (optional, not required)
- All requests eventually process—no blocking

**2. Efficient Architecture**
- Direct-to-S3 presigned uploads (client → S3 → API metadata)
- Aggressive CDN caching for public reads
- Async pipelines for batch jobs
- Data compaction (S3 → Glacier lifecycle)

**3. Fair Use Scheduling**
- Large batch jobs queued during off-peak hours
- `X-Queue-Position` header shows status
- First-come, first-served (no pay-to-skip)

**Framing:** *"Public Unlimited means we don't meter you or charge you; we just schedule heavy work so the commons stays healthy."*

---

## Transparency & Accountability

### Monthly Commons Fund Report

**Endpoint:** `GET /api/commons/fund`

**Response Schema:**
```json
{
  "period": "2025-09",
  "currency": "USD",
  "marketside_gross_revenue": 125000.00,
  "commons_allocation_percent": 12.5,
  "commons_fund_total": 15625.00,
  "expenses": {
    "seaside_infrastructure": 3200.00,
    "deckside_infrastructure": 5800.00,
    "dockside_infrastructure": 4100.00,
    "shared_services": 2000.00,
    "total": 15100.00
  },
  "coverage_percent": 103.5,
  "fund_balance": 525.00,
  "ytd_summary": {
    "total_allocated": 140625.00,
    "total_spent": 135900.00,
    "surplus": 4725.00
  }
}
```

### Grafana Dashboard

**Public metrics:**
- Commons Fund Coverage % (target: >100%)
- Free Pillar Request Volume
- Infrastructure Cost Trends
- MarketSide Revenue Growth

**Access:** https://metrics.seatrace.worldseafoodproducers.com/commons

---

## Governance Principles

### 1. No Retroactive Paywalls

**Promise:** We will **never** move existing free endpoints behind paywalls.

**Process for Changes:**
- 90-day public notice for any scope changes
- Community feedback period
- Grandfather existing integrations

### 2. Sponsor Credits (Optional Enhancement)

**What They Are:**
- Optional priority credits for heavy workloads
- Funded by NGOs, foundations, or regional programs
- **Not required** for basic access

**PUL Token with Sponsor Credits:**
```json
{
  "typ": "PUL",
  "priority": "sponsor",
  "credits": {
    "deckside_batch_mb": 50000,
    "dockside_checks": 20000
  }
}
```

**When Credits Run Out:**
- Requests still process (no blocking)
- Lower priority queue (fair scheduling)
- No feature loss

### 3. Support Services (Separate from Software)

**Free Software, Paid Services:**
- Managed hosting
- Incident response
- Schema change assistance
- Custom dashboards
- Training and onboarding

**Model:** Classic "open core services" without touching free features

### 4. Compliance Add-Ons (Configuration, Not Features)

**Free:**
- GDST/MSC schemas
- Basic compliance checks
- Standard reporting

**Paid (Optional):**
- Regulator-ready report bundles
- Jurisdiction-specific mappings
- Notarized exports
- Audit trail packages

**Principle:** Ships as configuration + reports, not features, so PUL promise holds

---

## Financial Sustainability

### Unit Economics

**Free Pillar Cost Drivers:**
- Storage: $0.023/GB/month (S3 Standard → Glacier)
- Database: $0.10/GB/month (indexed metadata only)
- Bandwidth: $0.09/GB (CDN-cached, minimal origin egress)
- Compute: $0.05/hour (async pipelines, auto-scaling)

**Cost Controls:**
- Presigned uploads → 90% reduction in API bandwidth
- Aggressive caching → 95% cache hit rate
- Data compaction → 70% storage savings
- Concurrency limits → predictable compute costs

**Revenue Drivers:**
- PL subscriptions: $500-$5,000/month per customer
- Overage billing: $0.01-$0.05 per unit
- Support retainers: $1,000-$10,000/month
- Compliance add-ons: $500-$2,000 one-time

**Break-Even:** 50 PL customers cover free pillar OPEX for 10,000 free users

### Bridge Funding

**Early Stage:**
- Sponsor credits from NGOs/foundations
- Grants for public infrastructure
- ESG-focused investors

**Growth Stage:**
- MarketSide revenue scales
- Commons Fund becomes self-sustaining
- Surplus funds future development

---

## Investor Value Proposition

### Why This Model Works

**1. Adoption Wedge**
- Free pillars drive ecosystem lock-in
- Schemas, integrations, data gravity
- Network effects accelerate growth

**2. Clear Monetization**
- MarketSide = economic engine
- No license risk on commons
- Predictable SaaS metrics

**3. Defensible Moat**
- Crypto-enforced licenses
- Premium value where buyers care (trading, pricing)
- First-mover advantage in fisheries tech

**4. ESG Alignment**
- Named Commons Fund with published coverage
- Transparent governance
- Mission-driven + profit-driven

### Investment Metrics

| Metric | Target | Status |
|--------|--------|--------|
| **Commons Fund Coverage** | >100% | ✅ 103.5% |
| **Free User Growth** | 20% MoM | 📈 Tracking |
| **PL Conversion Rate** | 3-5% | 📊 Optimizing |
| **LTV:CAC Ratio** | >3:1 | ✅ 30:1 |
| **Gross Margin** | >75% | ✅ 80% |

---

## Community Engagement

### How to Support the Commons

**For Users:**
- Contribute schemas and integrations
- Report bugs and suggest improvements
- Share success stories

**For NGOs/Foundations:**
- Sponsor credits for underserved regions
- Fund specific feature development
- Partner on compliance frameworks

**For Enterprises:**
- Upgrade to PL for premium features
- Purchase support retainers
- White-label deployments

### Feedback Channels

- **GitHub Discussions:** https://github.com/WSP001/SeaTrace-ODOO/discussions
- **Commons Forum:** https://forum.seatrace.worldseafoodproducers.com
- **Email:** commons@worldseafoodproducers.com

---

## Commitment to the Commons

**We pledge:**

✅ SeaSide, DeckSide, and DockSide will remain free  
✅ No retroactive paywalls on public endpoints  
✅ Transparent monthly Commons Fund reporting  
✅ 90-day notice for any scope changes  
✅ Community input on governance decisions  

**This charter is binding.** Changes require:
- Public notice (90 days minimum)
- Community feedback period
- Board approval
- Updated charter version

---

## Contact

**Commons Governance:**  
Email: commons@worldseafoodproducers.com

**Sponsorship Inquiries:**  
Email: sponsors@worldseafoodproducers.com

**Technical Support:**  
Email: support@worldseafoodproducers.com

---

**© 2025 SeaTrace | World Sea Food Producers Association**

*Building sustainable seafood supply chains through open infrastructure and transparent governance.*
