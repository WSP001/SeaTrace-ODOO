# SKILL: seatrace-dockside-agent

> **Role:** DockSide delta, gate_status, exceptions
> **Lane:** Codex-2
> **Pillar:** DockSide (STORE)
> **Stage Verb:** STORE
> **MSC Version:** V008
> **Run:** 2 (blocked until Run 1 PASS)
> **Port:** 8004
> **License Rail:** #CATCH (certifications) / $CHECK (reconciliation)

---

## Purpose

This skill governs all DockSide operations: secure storage of certified catch,
consensus handshake, reconciliation between estimates and actuals, fish-ticket
indexing, and the gate_status system that flags exceptions.

---

## KPI: Gate Clarity

- % of lots with delta ≤ threshold
- % of BLOCKED lots with standardized exception_reason

**Measurement:**
```
gate_clarity_pass = (lots_with_delta_lte_threshold / total_lots) * 100
exception_standardized = (blocked_lots_with_reason / total_blocked_lots) * 100
```

**Target:** gate_clarity_pass ≥ 90%, exception_standardized = 100%

---

## Components (Documented, Not Invented)

- `app.py` — DockSide service
- `handlers/` — event handlers for incoming catch
- `security/` — encryption at rest (AES-256)
- `blockchain_mint` — Hyperledger Fabric certification record

---

## Endpoints

| Path | Rail | Method | Purpose |
|------|------|--------|---------|
| `/api/v1/dockside/certifications` | #CATCH | GET | Public cert lookup |
| `/api/v1/dockside/reconciliation` | $CHECK | GET | Private reconciliation data |

---

## The Delta Gate System

```
DeckSide estimate → DockSide scale
         │
         ├── delta_pct = abs(estimate - actual) / actual * 100
         │
         ├── IF delta_pct ≤ threshold → gate_status: PASS
         │     └── Lot proceeds to certification
         │
         └── IF delta_pct > threshold → gate_status: BLOCKED
               └── exception_reason REQUIRED (standardized enum)
               └── Human review triggered
               └── No certification until resolved
```

**Exception reasons (standardized enum):**
- `SPECIES_MISIDENTIFICATION`
- `WEIGHT_INSTRUMENT_CALIBRATION`
- `PARTIAL_OFFLOAD`
- `MIXED_SPECIES_LOT`
- `ENVIRONMENTAL_LOSS`
- `TRANSIT_DAMAGE`

---

## ETL Jobs (This Pillar)

| Job | Extract | Transform | Load |
|-----|---------|-----------|------|
| `certification_store` | DeckSide ticket + scale weight | Compute delta, gate check | Hyperledger + MongoDB |
| `reconciliation_engine` | Paired records | Delta analysis, exception routing | PostgreSQL + alerts |
| `prometheus_scrape_dockside` | `/metrics` on :8004 | relabel + rules | Alertmanager + Grafana |

---

## Cost Dimensions

- Certification events (blockchain write)
- Storage I/O operations
- Counter: `seatrace_api_cost_units_total{pillar="dockside", operation="certify", license_tier="CATCH"}`

---

## Progressive Disclosure (This Pillar)

```
Level 0: SKILL.md read                       ← you are here
Level 1: Run 1 PASSES (SeaSide + DeckSide)   ← gate opens
Level 2: Reconciliation logic wired           ← delta_pct computed
Level 3: Gate system functional              ← PASS/BLOCKED proven
Level 4: Run 2 PASS (Antigravity)            ← unlocks MarketSide (Run 3)
```

---

## EM Toggle Governance (Cross-Pillar — This Pillar's Responsibility)

The Electronic Monitoring toggle is a cross-pillar disclosure event.
**DockSide owns Step 08 (Public/Private Split) and EM Yield Pipeline alignment.**

When EM is ACTIVE:
- Observer Corridor Disclosures show secure unmasking notifications
- EM Yield Pipeline CSS flowchart renders (#CATCH → fillet PRODUCT weight)
- Scale-matching fields align with v7.5 schema

**Rules:**
- DockSide reconciliation must use v7.5 scale-matching fields (FROZEN)
- EM yield pipeline must not expose raw yield outside observer corridor
- Gate system must still enforce delta threshold regardless of EM state
- Boundary check: `campaign-boundary-check.ps1 → PASS` required

---

## Gate: What Blocks This Pillar

- [ ] Run 1 PASS (SeaSide + DeckSide proof verified)
- [ ] Reconciliation logic tested with fixture data
- [ ] Gate system produces standardized exception_reason for BLOCKED lots
- [ ] Scale-matching fields align with v7.5 schema (FROZEN)
- [ ] EM yield pipeline boundary check passes
- [ ] Antigravity verification

---

## Branch Strategy

```
feat/msc-incoming-run2
  ├── DockSide reconciliation engine
  ├── Delta gate system
  ├── Exception reason enum
  ├── Certification proof (mock Hyperledger)
  └── Proof: VERIFICATION_REPORT_RUN2.md
```

---

## See Also

- `ENGINEERING_PLAYBOOK.md Ch 3` — DockSide deep dive (placeholder)
- `skills/seatrace-deckside-agent/SKILL.md` — prerequisite pillar
- `skills/seatrace-justfile-agent/SKILL.md` — root governance
- `ACTING_MASTER_HANDOFF_MSC-V008.md §3` — lane assignments

---

*DockSide is where truth meets reality.*
*The delta gate is the honesty check.*
*If the numbers don't match, the gate blocks until a human explains why.*
