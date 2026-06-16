# SKILL: seatrace-seaside-agent

> **Role:** SeaSide ping, NGO key integrity, proxy/API proof
> **Lane:** Claude Code (SeaSide + Proxy/API)
> **Pillar:** SeaSide (HOLD)
> **Stage Verb:** HOLD
> **MSC Version:** V008
> **Run:** 1 (first to execute)
> **Port:** 8000
> **License Rail:** #CATCH (public, unlimited)

---

## Purpose

This skill governs all SeaSide operations: vessel tracking, AIS integration,
GFW API calls, NGO key validation, and the proxy/API proof that gates
all downstream UI expansion.

**One public key. All the way through. This is the path.**

---

## KPI: NGO Key Integrity

% of trips where all three pings complete with valid NGO authorization.
Proxy/API proof must pass before UI expands.

**Measurement:**
```
ngo_key_integrity = (trips_with_3_valid_pings / total_trips) * 100
```

**Target:** 100% in test fixtures, ≥95% in production

---

## Components (Documented, Not Invented)

- `ais_integration.py` — AIS feed consumer
- `predictive_analytics.py` — vessel pattern analysis
- `hold_system.py` / `hold_system_ai.py` — hold monitoring
- `GFWClient` — GFW API wrapper (gateway.api.globalfishingwatch.org/v3)
- `VesselDataProvider` (MCP) — MCP server exposing vessel data to agents

---

## Endpoints

| Path | Rail | Method | Purpose |
|------|------|--------|---------|
| `/api/v1/seaside/vessels` | #CATCH | GET | Vessel positions from GFW cache |
| `/api/v1/seaside/sustainability` | #CATCH | GET | Sustainability metrics |
| `/healthz` | public | GET | Health check (proxy proof) |
| `/api/health` | public | GET | API health (proxy proof) |

---

## Proxy/API Proof Sequence (MUST PASS BEFORE UI)

```
1. .htaccess FASTAPI_ORIGIN block patched     ← Phase A prerequisite
2. /healthz returns 200                        ← basic proof
3. /api/health returns {"status": "ok"}        ← API layer proof
4. /api/v1/seaside/vessels returns valid JSON   ← full endpoint proof
5. Antigravity verifies all three              ← audit proof
6. Owner GO                                    ← UI expansion unlocked
```

---

## ETL Jobs (This Pillar)

| Job | Extract | Transform | Load |
|-----|---------|-----------|------|
| `gfw_vessel_ingest` | GFW API v3 scrape | Normalize vessel records | MongoDB cache |
| `ais_feed_consumer` | AIS stream | Filter + enrich | Time-series DB |
| `prometheus_scrape_seaside` | `/metrics` on :8000 | relabel + rules | Alertmanager + Grafana |

---

## Cost Dimensions

- GFW API calls (metered, external)
- AIS ingestion rate (volume-based)
- Prometheus counter: `seatrace_api_cost_units_total{pillar="seaside", operation="gfw_fetch", license_tier="CATCH"}`

---

## Progressive Disclosure (This Pillar)

```
Level 0: SKILL.md read                     ← you are here
Level 1: Proxy/API proof passes            ← unlocks button wiring
Level 2: SeaSide button live in harness    ← unlocks fixture data
Level 3: Fixture data validated            ← unlocks Run 1 branch
Level 4: Run 1 PASS (Antigravity)          ← unlocks DeckSide (Run 2)
```

---

## Gate: What Blocks This Pillar

- [ ] Acting Master §0 signature
- [ ] Phase A (Netfirms control panel — human-only)
- [ ] .htaccess FASTAPI_ORIGIN patch
- [ ] /healthz proof
- [ ] /api/v1/seaside/* proof
- [ ] Antigravity verification

---

## Branch Strategy

```
feat/msc-incoming-run1
  ├── SeaSide proxy wire
  ├── SeaSide button wiring
  ├── Fixture: peterpan-publix-sockeye-fixture.json (SeaSide fields)
  └── Proof: VERIFICATION_REPORT_RUN1.md
```

No overwrite. Transfer best-next. Owner GO to merge.

---

## See Also

- `ENGINEERING_PLAYBOOK.md Ch 1` — SeaSide deep dive
- `SEASIDE_PROMETHEUS_ETL.md` — full ETL study
- `skills/seatrace-justfile-agent/SKILL.md` — root governance
- `ACTING_MASTER_HANDOFF_MSC-V008.md §6` — next actions

---

*One public key. Full path. SeaSide HOLD is the foundation.*
*Nothing downstream moves until this pillar's proof passes.*
