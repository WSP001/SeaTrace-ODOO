# SKILL: seatrace-marketside-agent

> **Role:** MarketSide QR, proof_status, narrative
> **Lane:** Cascade / Evidence
> **Pillar:** MarketSide (EXCHANGE)
> **Stage Verb:** EXCHANGE
> **MSC Version:** V008
> **Run:** 3 (blocked until Run 2 PASS)
> **Port:** 8002
> **License Rail:** #CATCH (QR trace) / $CHECK (settlement + pricing)

---

## Purpose

This skill governs all MarketSide operations: consumer QR reverse-trace,
public proof cards, settlement transactions, pricing feeds, and the
narrative layer that tells the story of catch-to-consumer.

This is where the wind reaches the shore.
External simulation (campaign) and internal truth (ODOO) meet here.

---

## KPI: Proof Cleanliness

- Zero Arbiter Law hits
- % of QR traces with all four checkpoints active

**Measurement:**
```
arbiter_hits = count(traces_with_forbidden_terms)
checkpoint_completeness = (traces_with_4_checkpoints / total_traces) * 100
```

**Target:** arbiter_hits = 0, checkpoint_completeness ≥ 95%

---

## Components (Documented, Not Invented)

- `app.py` — MarketSide service
- `traceability.py` — QR reverse-trace logic
- `pricing.py` — settlement pricing engine

---

## Endpoints

| Path | Rail | Method | Purpose |
|------|------|--------|---------|
| `/api/v1/marketside/trace` | #CATCH | GET | Consumer QR reverse-trace |
| `/api/v1/marketside/settlement` | $CHECK | GET | Enterprise settlement data |
| `/api/v1/marketside/pricing` | $CHECK | GET | Private pricing feed |

---

## The QR Reverse-Trace (Consumer Path)

```
Consumer scans QR on package
         │
         ▼
MarketSide /api/v1/marketside/trace?qr=<code>
         │
         ├── Checkpoint 1: Origin (SeaSide)   — vessel, area, date
         ├── Checkpoint 2: Record (DeckSide)  — ticket_id, species, weight
         ├── Checkpoint 3: Store (DockSide)   — certification, gate_status
         └── Checkpoint 4: Exchange (MarketSide) — retailer, date_sold
         │
         ▼
Consumer sees: complete chain from vessel to shelf
         │
         ▼
proof_status: "all_checkpoints_active" | "partial" | "pending"
```

---

## The Proof Card (Public Narrative)

Each QR trace produces a proof card — the public-facing story:

```json
{
  "proof_status": "all_checkpoints_active",
  "origin": {"vessel": "F/V Pacific Star", "area": "Copper River, AK"},
  "record": {"species": "Sockeye Salmon", "ticket": "PP-2026-001"},
  "store": {"certification": "MSC-CERT-2026-4421", "gate": "PASS"},
  "exchange": {"retailer": "Publix", "date": "2026-06-10"},
  "recovery_label": "conversion measured"
}
```

**CRITICAL:** No raw yield percentages. No settlement amounts. No pricing.
Those live on the $CHECK rail only.

---

## ETL Jobs (This Pillar)

| Job | Extract | Transform | Load |
|-----|---------|-----------|------|
| `qr_trace_pipeline` | QR scan event | Assemble 4-checkpoint chain | Cache + response |
| `settlement_engine` | Certified lot + pricing | Compute settlement | PostgreSQL ($CHECK only) |
| `pricing_feed` | Market data sources | Normalize pricing | Redis cache ($CHECK only) |
| `prometheus_scrape_marketside` | `/metrics` on :8002 | relabel + rules | Alertmanager + Grafana |

---

## Cost Dimensions

- QR scans (volume-based, metered for revenue model)
- Settlement transactions (enterprise-tier)
- Pricing feed updates
- Counter: `seatrace_api_cost_units_total{pillar="marketside", operation="qr_trace", license_tier="CATCH"}`

---

## Twin-Parallel Intersection

This is where the twin-parallel stack converges:

```
EXTERNAL (Campaign)                    INTERNAL (ODOO)
  │                                      │
  │  Simulation of QR trace              │  Real QR trace pipeline
  │  in peterpan_publix_sockeye.html     │  in MarketSide service
  │                                      │
  └──── proof cards (visual) ────────────┘──── proof cards (data)
                    │
                    ▼
         Same schema. Same rail rules.
         External shows the story.
         Internal proves the math.
```

---

## Progressive Disclosure (This Pillar)

```
Level 0: SKILL.md read                       ← you are here
Level 1: Run 2 PASSES (DockSide)            ← gate opens
Level 2: QR trace pipeline wired            ← 4 checkpoints assembled
Level 3: Proof cards rendering              ← narrative proven
Level 4: Run 3 PASS (Antigravity)            ← production ready
Level 5: Owner GO → MarketSide live          ← partner claims unlocked
```

---

## Gate: What Blocks This Pillar

- [ ] Run 2 PASS (DockSide proof verified)
- [ ] QR trace assembles all 4 checkpoints from fixture data
- [ ] Proof cards render with zero Arbiter Law hits
- [ ] No raw yield/pricing on public surface
- [ ] Antigravity verification

---

## Branch Strategy

```
feat/msc-incoming-run3
  ├── QR trace pipeline
  ├── Proof card rendering
  ├── Settlement stub ($CHECK gated)
  ├── Narrative layer (Arbiter-Law-clean)
  └── Proof: VERIFICATION_REPORT_RUN3.md
```

---

## See Also

- `ENGINEERING_PLAYBOOK.md Ch 4` — MarketSide deep dive (placeholder)
- `ENGINEERING_PLAYBOOK.md Ch 8` — Twin-Parallel Campaign (external surface)
- `skills/seatrace-dockside-agent/SKILL.md` — prerequisite pillar
- `skills/seatrace-justfile-agent/SKILL.md` — root governance
- `ACTING_MASTER_HANDOFF_MSC-V008.md §3` — lane assignments
- `SEATRACE_MARKETING_TWO_APPS_ARCHITECTURE.md §4.4` — event hooks

---

*MarketSide is where the wave reaches the consumer.*
*The proof card is the story. The QR trace is the evidence.*
*Wind blows in both directions — the campaign sells, the backend proves.*
