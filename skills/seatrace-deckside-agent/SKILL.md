# SKILL: seatrace-deckside-agent

> **Role:** DeckSide estimate, tally, $CHECK fork
> **Lane:** Codex-1
> **Pillar:** DeckSide (RECORD)
> **Stage Verb:** RECORD
> **MSC Version:** V008
> **Run:** 1 (after SeaSide proxy proof)
> **Port:** 8003
> **License Rail:** #CATCH (read) / $CHECK (write-projections)

---

## Purpose

This skill governs all DeckSide operations: digital fish ticket creation,
captain/deckhand estimates, tally reconciliation, EMR integration, and
the #CATCH/$CHECK fork point where public data separates from private projections.

---

## KPI: Estimate Discipline

Median + 95th percentile delta between estimate and scale.
$CHECK fork correctness verified.

**Measurement:**
```
estimate_delta = abs(captain_estimate - scale_weight) / scale_weight * 100
median_delta = median(all_estimate_deltas)
p95_delta = percentile(all_estimate_deltas, 95)
```

**Target:** median ≤ 5%, p95 ≤ 15%

---

## Components (Documented, Not Invented)

- `app.py` (FastAPI) — DeckSide service
- `emr_integration.py` — Electronic Monitoring & Reporting
- `analyzers/` — catch analysis modules

---

## Endpoints

| Path | Rail | Method | Purpose |
|------|------|--------|---------|
| `/api/v1/deckside/tickets` | #CATCH | GET | Public fish ticket view |
| `/api/v1/deckside/tickets` | $CHECK | POST | Create fish ticket (authenticated) |
| `/api/v1/deckside/projections` | $CHECK | GET | Private deckhand projections |

---

## The #CATCH/$CHECK Fork Point

This is where public separates from private:

```
Captain estimate + Deckhand estimate
         │
         ├── #CATCH (public): ticket_id, species, area, estimated_weight
         │                     → consumer can see what was caught
         │
         └── $CHECK (private): projection, settlement_basis, payout_estimate
                               → only enterprise-licensed parties access
```

**Critical:** Recovery/yield values NEVER appear on the #CATCH side.
Use `"recovery_label": "conversion measured"` on public surfaces.

---

## ETL Jobs (This Pillar)

| Job | Extract | Transform | Load |
|-----|---------|-----------|------|
| `fish_ticket_ingest` | Deckhand input (mobile/tablet) | Validate + pair with estimate | MongoDB |
| `emr_sync` | EM camera + sensor feed | Correlate with ticket | Time-series + document store |
| `prometheus_scrape_deckside` | `/metrics` on :8003 | relabel + rules | Alertmanager + Grafana |

---

## Cost Dimensions

- Fish ticket creation rate
- EMR sync operations
- Counter: `seatrace_api_cost_units_total{pillar="deckside", operation="ticket_create", license_tier="CHECK"}`

---

## Progressive Disclosure (This Pillar)

```
Level 0: SKILL.md read                       ← you are here
Level 1: SeaSide proxy proof PASSES          ← gate opens
Level 2: Fixture data loaded                 ← estimate fields wired
Level 3: Tally UI functional                 ← $CHECK fork proven
Level 4: Run 1 PASS (Antigravity)            ← unlocks DockSide (Run 2)
```

---

## EM Toggle Governance (Cross-Pillar — This Pillar's Responsibility)

The Electronic Monitoring toggle is a cross-pillar disclosure event.
**DeckSide owns Step 05 (Recovery Bridge) unmask behavior.**

When EM is ACTIVE:
- Recovery yield (e.g., 55.8%) unmasks under "Public Output"
- Yield formula unmasks
- Weight ratio (raw→fillet) unmasks
- Institutional Observer Corridor status → ACTIVE (Telemetry Unmasked)

**Rules:**
- EM unmask must NEVER expose private fields to the #CATCH rail outside the observer corridor
- Boundary check must pass after every toggle state change
- Trusted External Information Packet must remain schema-compliant
- v7.5 schema (pairing hashes, scale-matching) must be FROZEN before V008

---

## Gate: What Blocks This Pillar

- [ ] SeaSide proxy/API proof (Run 1 prerequisite)
- [ ] `data/peterpan-publix-sockeye-fixture.json` estimate fields populated
- [ ] $CHECK fork test passes (private data never leaks to #CATCH rail)
- [ ] EM toggle boundary check passes
- [ ] Antigravity verification

---

## Branch Strategy

```
feat/msc-incoming-run1
  ├── DeckSide estimate UI
  ├── DeckSide tally logic
  ├── $CHECK fork implementation
  ├── Fixture: peterpan-publix-sockeye-fixture.json (DeckSide fields)
  └── Proof: VERIFICATION_REPORT_RUN1.md (DeckSide section)
```

---

## See Also

- `ENGINEERING_PLAYBOOK.md Ch 2` — DeckSide deep dive (placeholder, to be expanded)
- `skills/seatrace-seaside-agent/SKILL.md` — prerequisite pillar
- `skills/seatrace-justfile-agent/SKILL.md` — root governance
- `ACTING_MASTER_HANDOFF_MSC-V008.md §3` — lane assignments

---

*DeckSide is where the twin packet is born.*
*Captain estimate + deckhand estimate = the fork point.*
*Public gets the tally. Private gets the projection.*
