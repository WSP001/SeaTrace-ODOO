# SeaTrace-ODOO — Private Engineering Backbone

> **Repository:** `WSP001/SeaTrace-ODOO`
> **Visibility:** PRIVATE
> **Rail:** Private ($CHECK) — operational core, business logic, agent governance
> **MSC Version:** V008 PREP
> **Owner:** Roberto Scott Echols (Acting Master)

---

## What This Repo Is

The canonical business-logic and governance repository for SeaTrace.
This is **not** a public-facing surface. It governs:

- Agent skills and progressive disclosure protocol
- Engineering playbook (4 pillars × recursive deep-dive)
- MSC versioned manifests (ETL jobs, cost dimensions, endpoints)
- Team handoff notes and lane assignments
- Licensing middleware (Phase 1.5A — Ed25519 JWS, Zero Trust)

---

## Quick Start

```powershell
cd C:\WSP001\SeaTrace-ODOO
just orient
```

This runs: `status → truth → business-safety → playbook-status`

---

## Justfile Recipes (22 total)

| Group | Recipes |
|-------|---------|
| **Governance** | `orient`, `status`, `truth`, `business-safety`, `lanes`, `search` |
| **Playbook** | `playbook`, `playbook-ch N`, `playbook-next`, `playbook-status` |
| **ETL & Costing** | `etl-cost`, `etl-map`, `manifest` |
| **Twin-Parallel** | `twin-status`, `twin-campaign`, `twin-dashboard` |
| **Skills** | `skill-list`, `skill-read NAME`, `skill-lane` |
| **MSC Runs** | `run-status`, `handoff` |

---

## Directory Structure

```
SeaTrace-ODOO/
├── AGENTS.md                          # Session entry contract
├── ACTING_MASTER_HANDOFF_MSC-V008.md  # Team handoff note
├── ENGINEERING_PLAYBOOK.md            # 9-chapter recursive template
├── README.md                          # This file
├── justfile                           # 22 execution recipes
├── manifests/
│   └── MSC-V008-MANIFEST.json         # Dynamic manifest (machine-readable)
├── skills/
│   ├── seatrace-justfile-agent/       # Root governance skill
│   ├── seatrace-seaside-agent/        # SeaSide HOLD (Run 1)
│   ├── seatrace-deckside-agent/       # DeckSide RECORD (Run 1)
│   ├── seatrace-dockside-agent/       # DockSide STORE (Run 2)
│   └── seatrace-marketside-agent/     # MarketSide EXCHANGE (Run 3)
└── middleware/                         # Phase 1.5A (pending import)
```

---

## Twin-Parallel Architecture

This repo is the **internal** half of the twin-parallel stack:

```
EXTERNAL (Public)                    INTERNAL (Private — this repo)
seatrace-campaign                    SeaTrace-ODOO
  │ Simulation that sells              │ Engineering that proves
  │ rail=public, #CATCH                │ rail=private, $CHECK
  │ Netlify deploy                     │ Local + API backend
  └─── content-store.json ─────────────┘─── ENGINEERING_PLAYBOOK.md
              shared spine                       shared governance
```

---

## Progressive Disclosure Protocol

```
agent → justfile → skill → proof → next disclosure
  ↑                                        │
  └────────────────────────────────────────┘
```

No agent outruns proofs. No UI expands before gates pass.
No merge without Owner GO. No rail crossing without signature.

---

## V008 PREP — Current State

| Run | Pillar | Branch | Status |
|-----|--------|--------|--------|
| 1 | SeaSide + DeckSide | `feat/msc-incoming-run1` | NOT CREATED (blocked: Owner §0) |
| 2 | DockSide | `feat/msc-incoming-run2` | NOT CREATED (blocked: Run 1 PASS) |
| 3 | MarketSide | `feat/msc-incoming-run3` | NOT CREATED (blocked: Run 2 PASS) |

### v7.5 Carry-Forward (Must Lock Before V008)

- Pydantic schema (pairing hashes, scale-matching fields, FastAPI endpoints)
- EM toggle behavior (cross-pillar disclosure, unmask/mask transitions)
- Preview URLs stable (campaign + harness both PASS)

---

## Related Repositories

| Repo | Visibility | Role |
|------|-----------|------|
| `WSP001/MARKETING-SeaTrace_CAMPAIGN` | **PUBLIC** | External simulation + SEO campaign |
| `WSP001/SeaTrace-ODOO` | **PRIVATE** | This repo — engineering backbone |
| `WSP001/SirRodg` | **PUBLIC** | Enterprise RFP landing page |
| `seatrace-msc-v007` (Netlify) | **PUBLIC** | MSC v007.5 supply evidence harness |

---

## Governance Rules

1. **READ_FIRST** — read before edit
2. **PROOF_BEFORE_NARRATIVE** — prove it runs, then describe
3. **MOVE_NOT_DELETE** — archive, never destroy
4. **No inferred secrets/endpoints** — only document what's verified
5. **No deployment claims** — only claim what's proven
6. **Narrow file scope** — name REPO / OWNER / LANE / FILE_SCOPE / PROOF_COMMAND
7. **Commons Good** — CC BY-SA 4.0; #CATCH unlimited, $CHECK limited

---

*Commons Good CC BY-SA 4.0 — Roberto Scott Echols, WSP est. 1988*
*Private repo — never deploy contents to public surfaces.*
