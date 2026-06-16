# SeaTrace Engineering Playbook — Recursive Deep-Dive Template

> **Owner:** Roberto Scott Echols (Acting Master)
> **Prepared by:** Cascade (Acting Master Assistant)
> **Date:** 2026-06-16
> **MSC Version:** MSC-V008
> **Status:** ACTIVE — twin-parallel stack (campaign + ODOO)
> **Rail:** rail=public (template structure); rail=private (implementation internals)

---

## Meta-Template: The Recursive Loop

Every pillar, every microservice, every ETL job follows this loop:

```
┌──────────────────────────────────────────────────┐
│  1. QUESTION  — What problem are we solving?     │
│  2. PLAN      — Strategy (Zero Trust, JWT, RBAC, │
│                 TDD, CI/CD, licensing)            │
│  3. DEEP DIVE — Numbered sections + code +       │
│                 backend + frontend + tests        │
│  4. NEXT STEPS — Actionable items                │
│  5. SEE ALSO  — Cross-references to other        │
│                 modules in the playbook           │
│  6. FOLLOW-UP — Prompt for the next deep dive    │
│                                                  │
│       ↻ Loop: output of 6 feeds into 1           │
└──────────────────────────────────────────────────┘
```

**Expert Roles** (assigned per deep dive):
- **Security Engineer** — Zero Trust, JWT, Ed25519 JWS, RBAC, license gates
- **Backend Architect** — FastAPI, Pydantic, async middleware, ETL pipelines
- **Frontend Architect** — React, Three.js, campaign pages, SEO workbench
- **DevOps Engineer** — Docker, K8s, CI/CD, Prometheus, Grafana
- **Data Engineer** — MongoDB, PostgreSQL, Redis, Supabase, vector stores
- **QA Engineer** — pytest, Playwright, site-check gates, regression suites

---

## Chapter Index (MSC-V008 Dynamic Manifest)

Each chapter = one recursive loop. Chapters are versioned with MSC tags.

| Ch | Pillar | Stage Verb | Question Entry Point | MSC Tag | Status |
|----|--------|-----------|----------------------|---------|--------|
| 1 | **SeaSide** | HOLD | How do we track vessels and validate catch origin in real-time? | MSC-V008-SS | STUDY |
| 2 | **DeckSide** | RECORD | How do we create tamper-proof digital fish tickets at sea? | MSC-V008-DS | STUDY |
| 3 | **DockSide** | STORE | How do we store, reconcile, and certify landed catch? | MSC-V008-DK | STUDY |
| 4 | **MarketSide** | EXCHANGE | How do we enable consumer reverse-trace and marketplace settlement? | MSC-V008-MS | STUDY |
| 5 | **Cross-Cutting: Auth** | — | How do we implement Zero Trust auth across all 4 pillars? | MSC-V008-AUTH | Phase 1.5A |
| 6 | **Cross-Cutting: ETL** | — | How do we observe, extract, transform, and load across the pipeline? | MSC-V008-ETL | STUDY |
| 7 | **Cross-Cutting: Licensing** | — | How does #CATCH (public) vs $CHECK (private) enforce at middleware? | MSC-V008-LIC | Phase 1.5A |
| 8 | **Twin-Parallel: Campaign** | — | How does the external simulation app mirror the real architecture? | MSC-V008-CAMP | ACTIVE |
| 9 | **Twin-Parallel: Dashboard** | — | How does the internal SEO dashboard measure campaign truth? | MSC-V008-DASH | SPEC |

---

## Ch 1: SeaSide (HOLD) — Vessel Tracking & Catch Origin

### 1. Question
How do we track vessels and validate catch origin in real-time using GFW AIS data, with Prometheus observability, while respecting the #CATCH/$CHECK license boundary?

### 2. Plan
- **Data Source:** GFW API v3 (`gateway.api.globalfishingwatch.org`)
- **Pattern:** GFW → MongoDB cache → FastAPI → JWT auth → JSON response
- **Observability:** Prometheus scrape on `/metrics` (#CATCH) and `/metrics/sustainability` (#CATCH) and `/metrics/security` ($CHECK)
- **Security:** Zero Trust — every request authenticated, no implicit trust from network position
- **License Gate:** SeaSide data = #CATCH (public, unlimited) except auth/key-rotation metrics = $CHECK (private)
- **ETL Lens:** Extract (scrape_configs) → Transform (metric_relabel + rule_files) → Load (Alertmanager + Grafana)

### 3. Deep Dive

#### 3.1 Core Components (documented, not invented)
- `ais_integration.py` — AIS feed consumer
- `predictive_analytics.py` — vessel pattern analysis
- `hold_system.py` / `hold_system_ai.py` — hold monitoring
- `GFWClient` — GFW API wrapper
- `VesselDataProvider` (MCP) — MCP server exposing vessel data to agents

#### 3.2 Prometheus ETL Stack (per SEASIDE_PROMETHEUS_ETL.md)

**Rung 1:** Library primitives — `prometheus_client.Counter`, `Histogram`, `Gauge`
**Rung 2:** Minimal scrape — one app job, HTTPS, env-var auth
**Rung 3:** Infrastructure sidecars — cadvisor, node-exporter, blackbox
**Rung 4:** Per-connector observability — 9 MCP connector jobs
**Rung 5:** Full 4-pillar fanout — all pillars on ports 8000/8002/8003/8004

#### 3.3 API Endpoint Pattern
```python
# FastAPI route — SeaSide vessel endpoint
@router.get("/api/v1/seaside/vessels", tags=["seaside"])
async def get_vessels(
    request: Request,
    license: LicensePayload = Depends(verify_license),
):
    """Public #CATCH endpoint — vessel positions from GFW cache."""
    vessels = await gfw_client.get_vessels(request.query_params)
    return {"rail": "public", "license": "CATCH", "data": vessels}
```

#### 3.4 License Middleware (Phase 1.5A — Devin output)
- Async-safe `LicenseMiddleware` with `_verify_jws()` using Ed25519
- JWK `kid` key rotation
- Timing-floor mitigation (non-blocking async sleep)
- `X-Correlation-Id` generation/preservation
- PL 14-day expiration grace period
- Bearer token + `X-SeaTrace-License` header support

### 4. Next Steps
1. Import Phase 1.5A patch pack into `SeaTrace-ODOO/middleware/`
2. Wire `LicenseMiddleware` to SeaSide FastAPI app
3. Add Prometheus counter for license verification (pass/fail/grace)
4. Run 25 Devin-generated tests
5. Add `/metrics/sustainability` scrape job (Option C from ETL study)

### 5. See Also
- `SEASIDE_PROMETHEUS_ETL.md` — full ETL study with 5-rung ladder
- `SEATRACE_MASTER_PLAN.md §2A` — pillar mapping table
- `SEATRACE_MASTER_PLAN.md §4 Phase 3` — one real endpoint, end-to-end
- Ch 5 (Auth) — cross-cutting Zero Trust patterns
- Ch 6 (ETL) — Prometheus observation layer
- Ch 7 (Licensing) — #CATCH/$CHECK enforcement

### 6. Follow-up Question
"How do we add the sustainability disclosure path (`/metrics/sustainability`) to the SeaSide Prometheus config while keeping security metrics on a separate $CHECK-gated path?"

---

## Ch 5: Cross-Cutting Auth — Zero Trust Across All Pillars

### 1. Question
How do we implement secure authentication across SeaSide, DeckSide, DockSide, MarketSide with JWT, Ed25519 JWS, RBAC, and license-tier enforcement?

### 2. Plan
- **Architecture:** Zero Trust — no implicit trust from network position
- **Token Pattern:** JWT access tokens (short-lived) + refresh tokens (long-lived, rotated)
- **Signing:** Ed25519 JWS with JWK `kid` key rotation
- **RBAC Tiers:**
  - `public` — #CATCH endpoints, no auth required
  - `operator` — authenticated, vessel/catch write access
  - `enterprise` — $CHECK settlement, pricing, reconciliation
  - `admin` — key rotation, user management, audit
- **Middleware:** `LicenseMiddleware` (Phase 1.5A) validates on every request
- **TDD:** 25 focused tests covering all auth paths

### 3. Deep Dive

#### 5.1 JWT Flow
```
Client → POST /auth/token (credentials) → Server
Server → validate → issue JWT (access_token, 15min) + refresh_token (7d)
Client → GET /api/v1/seaside/vessels + Authorization: Bearer <jwt>
Server → LicenseMiddleware → verify_jws() → route handler → response
```

#### 5.2 Key Rotation Pattern
```python
# Ed25519 JWK key rotation
async def _verify_jws(self, token: str) -> LicensePayload:
    header = decode_header(token)
    kid = header.get("kid")
    key = await self.key_store.get_key(kid)  # JWK store with kid lookup
    if not key:
        raise InvalidLicenseError(f"Unknown kid: {kid}")
    payload = verify_ed25519(token, key)
    return LicensePayload(**payload)
```

#### 5.3 License Tiers at Middleware
```python
class LicenseMiddleware:
    async def __call__(self, request, call_next):
        correlation_id = request.headers.get(
            "X-Correlation-Id", str(uuid4())
        )
        token = self._extract_token(request)  # Bearer or X-SeaTrace-License
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)  # #CATCH — no auth needed
        payload = await self._verify_jws(token)
        if payload.is_expired() and payload.within_grace_period(days=14):
            # PL 14-day grace — allow but flag
            request.state.license_grace = True
        request.state.license = payload
        response = await call_next(request)
        response.headers["X-Correlation-Id"] = correlation_id
        return response
```

#### 5.4 Timing-Floor Mitigation
```python
# Non-blocking async sleep to prevent timing attacks
import asyncio, time
async def _verify_with_timing_floor(self, token):
    start = time.monotonic()
    try:
        return await self._verify_jws(token)
    finally:
        elapsed = time.monotonic() - start
        floor = 0.05  # 50ms minimum
        if elapsed < floor:
            await asyncio.sleep(floor - elapsed)
```

### 4. Next Steps
1. Locate or recreate Phase 1.5A patch pack on this machine
2. Create `SeaTrace-ODOO/middleware/license.py`
3. Create `SeaTrace-ODOO/middleware/tests/test_license.py` (25 tests)
4. Wire to FastAPI app with `app.add_middleware(LicenseMiddleware)`
5. Add CRL check (optional, fail-open default)

### 5. See Also
- Ch 1 (SeaSide) §3.4 — where the middleware plugs in
- Ch 7 (Licensing) — #CATCH/$CHECK business rules
- `SEATRACE_MASTER_PLAN.md §2C` — MCP/A2A agent protocol with public/private keys
- `SEATRACE_MASTER_PLAN.md §2E` — documented tech stack (RSA, JWT, AES-256, TLS 1.3)

### 6. Follow-up Question
"How do we implement refresh token rotation with revocation lists, and where does the token store live (Redis vs PostgreSQL vs Supabase)?"

---

## Ch 6: Cross-Cutting ETL — Prometheus Observation Layer

### 1. Question
How do we observe, extract, transform, and load metrics across the entire SeaTrace pipeline, using Prometheus as the ETL backbone?

### 2. Plan
- **ETL = Prometheus:** Extract (scrape_configs) → Transform (relabel + rules) → Load (Alertmanager + Grafana)
- **Instrumentation upstream:** `prometheus_client` in app code (Counter, Histogram, Gauge)
- **Progressive complexity:** 5-rung ladder from library primitives to full 4-pillar fanout
- **License boundary:** `/metrics` and `/metrics/sustainability` = #CATCH; `/metrics/security` = $CHECK
- **Disclosure paths:** separate scrape paths per concern (sustainability, security, per-connector)

### 3. Deep Dive

#### 6.1 ETL Mapping
| Stage | Prometheus Term | Files |
|-------|----------------|-------|
| **Extract** | `scrape_configs` | `prometheus.yml` jobs |
| **Transform** | `metric_relabel_configs` + `rule_files` | `rules/*.yml` |
| **Load** | `alerting.alertmanagers` + Grafana | `alerting:` block |

#### 6.2 Four Reference Points (verified on disk)
1. **Library:** `prometheus_client` (venv) — Counter/Histogram/Gauge primitives
2. **MCP layer:** `mcp_connectors.yml` (9 jobs) + `mcp_connector_alerts.yml` (12 alerts)
3. **Legacy runtime:** `prometheus.yml` (all 4 pillars + sustainability + key rotation)
4. **Study target:** `src/seaside/prometheus/prometheus.yml` (single app + sidecars)

#### 6.3 Disclosure Path Split (Recommended Option C)
```yaml
# Add to prometheus.yml — public sustainability path
- job_name: 'seatrace-sustainability'
  metrics_path: '/metrics/sustainability'
  static_configs:
    - targets: ['app:8001']
  scheme: 'https'
  basic_auth:
    username: '${PROMETHEUS_USER}'
    password: '${PROMETHEUS_PASSWORD}'
```

#### 6.4 Per-Microservice Costing Model
Each microservice scrape job produces metrics that feed a cost model:

| Pillar | Port | Metrics Path | Cost Dimension |
|--------|------|-------------|----------------|
| SeaSide | 8000 | `/metrics` | GFW API calls, AIS ingestion rate |
| DeckSide | 8003 | `/metrics` | Fish ticket creation rate, EMR sync |
| DockSide | 8004 | `/metrics` | Certification events, storage I/O |
| MarketSide | 8002 | `/metrics` | QR scans, settlement transactions |

Cost counters:
```python
from prometheus_client import Counter
api_cost = Counter(
    "seatrace_api_cost_units_total",
    "Billable API units consumed",
    ["pillar", "operation", "license_tier"]
)
```

### 4. Next Steps
1. Add Option C disclosure split to study target prometheus.yml
2. Add `seatrace_api_cost_units_total` counter to each pillar's app code
3. Create Grafana dashboard JSON for per-pillar cost tracking
4. Wire alerts: `HighAPICost` (>threshold per hour per pillar)

### 5. See Also
- `SEASIDE_PROMETHEUS_ETL.md` — full 5-rung study
- Ch 1 (SeaSide) §3.2 — Prometheus stack for SeaSide specifically
- Ch 5 (Auth) — security metrics path ($CHECK gated)
- Ch 7 (Licensing) — cost tied to license tier

### 6. Follow-up Question
"How do we build the Grafana cost dashboard that shows real-time per-pillar API spend against budget thresholds, with the license tier breakdown?"

---

## Ch 7: Cross-Cutting Licensing — #CATCH/$CHECK Enforcement

### 1. Question
How does the #CATCH (public, unlimited) vs $CHECK (private, limited) licensing model enforce at the middleware, API, and observability layers?

### 2. Plan
- **#CATCH (Public):** Vessel positions, catch tallies, sustainability scores, consumer QR reverse-trace, NGO/regulator audit — unlimited license
- **$CHECK (Private):** Enterprise settlement, deckhand projections, processor reconciliation, payout records, recovery/yield formulas — limited license
- **Enforcement point:** `LicenseMiddleware` (Ch 5) checks license tier → gates endpoint access
- **Observability:** Prometheus `/metrics` split by disclosure path
- **Revenue:** Proportional unlimited license usage plan (Phase 5 in Master Plan)

### 3. Deep Dive

#### 7.1 Endpoint Classification
```python
PUBLIC_CATCH_PATHS = [
    "/api/v1/seaside/vessels",
    "/api/v1/seaside/sustainability",
    "/api/v1/deckside/tickets",       # read-only public view
    "/api/v1/dockside/certifications", # public cert lookup
    "/api/v1/marketside/trace",       # consumer QR reverse-trace
    "/metrics",
    "/metrics/sustainability",
    "/health",
]

PRIVATE_CHECK_PATHS = [
    "/api/v1/marketside/settlement",
    "/api/v1/marketside/pricing",
    "/api/v1/deckside/projections",
    "/api/v1/dockside/reconciliation",
    "/metrics/security",
]
```

#### 7.2 Recovery/Yield Rule (CRITICAL — Owner-mandated)
On PUBLIC surfaces: `"recovery_label": "conversion measured"` or `yield_band: "reviewed"`.
**NEVER** a raw value like `"yield_percentage": 95.2` — this is plant-economics-adjacent, $CHECK rail only.
The species/product-form-specific formula table belongs exclusively to the private $CHECK rail.

#### 7.3 Revenue Model Skeleton (Phase 5, not yet designed)
| Tier | Access | Price Model |
|------|--------|-------------|
| **Commons** | #CATCH endpoints, public metrics | Free forever (CC BY-SA 4.0) |
| **Operator** | DeckSide write, DockSide certify | Per-vessel monthly |
| **Enterprise** | MarketSide settlement, $CHECK analytics | Proportional usage |

### 4. Next Steps
1. Finalize endpoint classification with Roberto
2. Wire `PUBLIC_CATCH_PATHS` / `PRIVATE_CHECK_PATHS` into LicenseMiddleware
3. Design `REVENUE_MODEL.md` (Master Plan Phase 5 prerequisite)
4. Add yield-field scrub test to CI gate

### 5. See Also
- `docs/PUBLIX_SOCKEYE_DATA_CONTRACT.md` line 120 — GO-CODEX-YIELD-FIELD-SCRUB
- Ch 5 (Auth) — LicenseMiddleware implementation
- Ch 6 (ETL) — cost counters per license tier
- `SEATRACE_MASTER_PLAN.md §2D` — #CATCH/$CHECK definition
- `SEATRACE_MASTER_PLAN.md §4 Phase 5` — revenue loop design

### 6. Follow-up Question
"What does 'proportional unlimited license usage' mean concretely — per vessel, per QR scan, per catch event — and how do we meter it through the Prometheus cost counters?"

---

## Ch 8: Twin-Parallel — Campaign (External Simulation)

### 1. Question
How does the external simulation app mirror the real 4-pillar architecture without making false claims about live backend functionality?

### 2. Plan
- **Purpose:** Convince a visitor in 15 seconds that SeaTrace is real, credible, working
- **Rail:** `rail=public` — no private data, no internal metrics, no false API claims
- **Spine:** `content-store.json` (shared with Internal Dashboard)
- **Gate:** `just site-check` must pass before any deploy
- **Governance:** NOFAKESUCCESS rule — aspirational language only, no invented deployment claims

### 3. Deep Dive
See `SEATRACE_MARKETING_TWO_APPS_ARCHITECTURE.md §3` for full specification.

Key constraint: the campaign pages show the 4-pillar architecture as **design intent**, not as a live running system. Language scrub rules:
- "PRIVATE" → "permissioned"
- "LIVE" only if actually deployed
- "VERIFIED" → "designed to verify"

### 4. Next Steps
1. Run `just site-check` on current campaign
2. Confirm v3 vs v4 promotion decision
3. Add event hooks for Internal Dashboard (§4.4 of Two-Apps Architecture)

### 5. See Also
- `SEATRACE_MARKETING_TWO_APPS_ARCHITECTURE.md` — full two-apps spec
- Ch 9 (Dashboard) — the internal measurement surface
- `seatrace-campaign/content-store.json` — shared spine

### 6. Follow-up Question
"Which campaign pages need updated copy now that the Phase 1.5A auth middleware exists as real code, not just architecture?"

---

## Ch 9: Twin-Parallel — Dashboard (Internal SEO Measurement)

### 1. Question
How does the internal SEO dashboard measure the actual performance of the external campaign, with real backlinks, real rankings, real traffic?

### 2. Plan
- **Rail:** `rail=private-internal` — operator-side only
- **Data:** GSC backlinks, GSC rankings, Plausible/Netlify traffic, event hooks
- **Six panels:** Backlinks Flow, Keyword Rankings, Traffic, Conversions, Coverage Matrix, Health Score
- **Deploy:** Local-only (Phase 1), gated Netlify (Phase 2)

### 3. Deep Dive
See `SEATRACE_MARKETING_TWO_APPS_ARCHITECTURE.md §4` for full specification.

### 4. Next Steps
Per Two-Apps Architecture §9 file creation list.

### 5. See Also
- `SEATRACE_MARKETING_TWO_APPS_ARCHITECTURE.md §4-§10`
- `seatrace-campaign-dashboard/` — target folder
- Ch 8 (Campaign) — the public surface this measures

### 6. Follow-up Question
"How do we set up the GSC API integration for automated backlink and ranking ingestion?"

---

## Appendix A: MSC Version History

| MSC Tag | Date | Scope | Status |
|---------|------|-------|--------|
| MSC-V007 | 2026-05 | Deploy package, site-check, campaign gate | Complete |
| MSC-V008 | 2026-06 | Engineering playbook, Phase 1.5A auth, ETL costing | ACTIVE |
| MSC-V009 | TBD | First real endpoint (SeaSide vessels), revenue model | PLANNED |

## Appendix B: Justfile Entry Points

```
just playbook          # Show chapter index
just playbook-ch N     # Open chapter N deep dive
just playbook-next     # Show all NEXT STEPS across chapters
just playbook-status   # Show MSC version + chapter statuses
just etl-cost          # Show per-pillar cost model
just twin-status       # Campaign + Dashboard twin-parallel status
```

---

*Commons Good CC BY-SA 4.0 — Roberto Scott Echols, WorldSeafoodProducers.com*
*Recursive loop: Question → Plan → Deep Dive → Next Steps → See Also → Follow-up*
*Twin-parallel: External simulation sells, Internal dashboard measures. Never blend the rails.*
