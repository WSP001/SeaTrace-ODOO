# ACTING MASTER HANDOFF — MSC-VERSION NEXT (V008 PREP)

> **SeaTrace 4-Pillar / 3-Lane Progressive Disclosure Protocol**
> **Team Alignment Note — Roberto Scott Echols (Acting Master)**
> **Date:** 2026-06-16
> **MSC Version:** V008 (prep → Run 1 pending)
> **Status:** READY for §0 signature

---

**Team — this is the clean handoff.**

Read this in order.
Follow the lanes.
Do not outrun the proofs.
Do not expand UI before the gates pass.
Do not merge or deploy without explicit Owner GO.

This note sets the marks for MSC-Version Next (V008) and aligns all teammates on where to read, what to measure, and which agent-skill governs each micro-routine.

---

## 1. WHERE TO READ — DIRECTORY MAP (Authoritative)

### A. Skills (recursive, agent-specialty, progressive disclosure)

```
skills/
  seatrace-justfile-agent/        ← global rail map + Owner GO sequence
  seatrace-seaside-agent/         ← SeaSide ping, NGO key, proxy/API proof
  seatrace-deckside-agent/        ← DeckSide estimate, tally, $CHECK fork
  seatrace-dockside-agent/        ← DockSide delta, gate_status, exceptions
  seatrace-marketside-agent/      ← MarketSide QR, proof_status, narrative
```

### B. Justfiles (execution surface)

```
SeaTrace-ODOO/
  justfile                         ← governance + playbook + ETL + twin-parallel
  ENGINEERING_PLAYBOOK.md          ← recursive deep-dive template (9 chapters)
  manifests/MSC-V008-MANIFEST.json ← dynamic manifest (machine-readable)

seatrace-msc-v007/ (harness)
  justfile
  justfile-agents.just
  docs/SEATRACE_ACTING_MASTER_HANDOFF_2026-06-16.md

seatrace-campaign/ (marketing)
  justfile
  justfile-site-check.just
  docs/AGENT_LEDGER.md
```

### C. Obligations not yet claimed

> "These are documented obligations that have not yet been claimed. Any agent picking one up should add an OPEN row above before starting."

These remain unclaimed until an agent adds an OPEN row:

- `SEATRACE_PACKET_CONTRACT_SPEC_v001.md` — Atomicity Invariant
- `F_V_000_TO_014_FLEET_SCENARIO.md` — scenario fixture set

---

## 2. WHAT TO MEASURE — NEXT MSC-VERSION KPIs (High-Weight Culture Indicators)

These are the four KPIs that define MSC-Version Next.
Every lane must measure and report these.

| Pillar | Stage | KPI | Measurement |
|--------|-------|-----|-------------|
| **SeaSide** | HOLD | NGO key integrity | % of trips where all three pings complete with valid NGO authorization |
| **DeckSide** | RECORD | Estimate discipline | Median + 95th percentile delta between estimate and scale |
| **DockSide** | STORE | Gate clarity | % of lots with delta ≤ threshold; % BLOCKED lots with standardized exception_reason |
| **MarketSide** | EXCHANGE | Proof cleanliness | Zero Arbiter Law hits; % of QR traces with all four checkpoints active |

---

## 3. LANE ASSIGNMENTS — WHO TOUCHES WHAT (No Drift)

| Lane | Agent | Scope | Files | Gate |
|------|-------|-------|-------|------|
| SeaSide + Proxy/API | **Claude Code** | .htaccess, _redirects, api/*, ops docs | SeaSide button → live `/api/v1/seaside/*` | Must prove `/healthz` + `/api/*` before UI expands |
| DeckSide (Run 1) | **Codex-1** | data/peterpan-publix-sockeye-fixture.json | Estimate fields, tally UI, $CHECK fork | Cannot start until SeaSide proxy proof passes |
| DockSide (Run 2) | **Codex-2** | data/* product-index | Reconciliation, delta_pct, gate_status | Cannot start until Run 1 PASS |
| MarketSide (Run 3) | **Cascade / Evidence** | QR rail, proof cards, narrative | proof_status, disclosure | Cannot start until Run 2 PASS |
| Audit Only | **Antigravity** | No writes | Runs all proofs, produces VERIFICATION_REPORT.md | Always active |

---

## 4. PROGRESSIVE DISCLOSURE — HOW THE TEAM SHOULD THINK

The culture is recursive:

```
agent → justfile → skill → proof → next disclosure
  ↑                                        │
  └────────────────────────────────────────┘
```

No one jumps ahead.
No one expands UI before the pillar's proof passes.
No one touches another lane's files.

This is how we keep the system safe, predictable, and MSC-aligned.

**The recursive loop per pillar:**
1. Agent reads their `skills/<pillar>-agent/SKILL.md`
2. Agent runs justfile recipes for their lane
3. Agent produces proof (test pass, verification, screenshot)
4. Proof reviewed by Antigravity (audit lane)
5. Owner GO unlocks next disclosure level
6. Next pillar's agent can now start

---

## 5. WHAT IS READY VS BLOCKED (Acting Master Catch-Up)

> "Run1 branches: NONE / Run2 branches: NONE / Run3 branches: NONE."

**Meaning:**
- Run 1 has not started
- Run 2 and Run 3 are blocked
- No OPEN rows exist for the unclaimed obligations
- Campaign PR #1 is tested but not merged
- Proxy/API proof is not yet complete
- No production deploy is authorized

### READY NOW

| Item | Proof |
|------|-------|
| Redaction proof | PASSED |
| Campaign PR #1 preview-safe | `https://6a30430dd4735c28341a3486--seatrace-campaign.netlify.app/seo/peterpan_publix_sockeye.html` |
| Harness proof | `https://6a305e94b29eb97cc5ae8921--seatrace-msc-v007.netlify.app` |
| Engineering Playbook | `SeaTrace-ODOO/ENGINEERING_PLAYBOOK.md` (9 chapters, MSC-V008) |
| MSC-V008 Manifest | `SeaTrace-ODOO/manifests/MSC-V008-MANIFEST.json` |
| Worktree system | Designed and ready to append |

### BLOCKED

| Item | Blocker |
|------|---------|
| Any UI expansion | Proxy/API proof incomplete |
| Any MSC Run 1 branch | Owner §0 signature not given |
| Any merge to main | No production GO |
| Any Netlify production deploy | No production GO |
| Any partner/agency claims | MarketSide not proven |
| Any MarketSide narrative | Run 2 not complete |

---

## 6. NEXT ACTIONS — IN ORDER (Team Execution Marks)

```
┌─ 1. Acting Master GO — §0 signature
│     You sign. This unblocks Phase A.
│
├─ 2. Arbiter Law redaction clearance
│     No forbidden terms. Antigravity confirms.
│
├─ 3. Phase A — Netfirms control panel
│     Human-only. Record document root, SSL, PHP 8.4.
│
├─ 4. Append worktree recipes
│     Claude Code adds to justfile-agents.just.
│
├─ 5. Patch .htaccess with FASTAPI_ORIGIN block
│     Claude Code — after Phase A passes.
│
├─ 6. Proxy/API proof
│     Antigravity runs: /healthz, /api/health, /api/v1/seaside/*
│
├─ 7. SeaSide button wiring
│     Codex-1 — only after proxy proof.
│
├─ 8. OPEN rows for unclaimed obligations
│     Claude Code or Cascade adds OPEN rows for:
│     - Packet Contract Spec
│     - Fleet Scenario Set
│
└─ 9. MSC Run 1 branch creation
      Codex-1 creates worktree branch: feat/msc-incoming-run1
```

---

## 7. MSC RUN SEQUENCE — BRANCH STRATEGY (No Overwrite, Transfer Best-Next)

Each run gets its own branch. No overwrites. Each iteration transfers the best-next version forward.

```
main (production-locked, Owner GO only)
  │
  ├── feat/msc-incoming-run1     ← SeaSide HOLD (one public key, full path)
  │     └── Codex-1: estimate + tally + proxy wire
  │
  ├── feat/msc-incoming-run2     ← DockSide STORE (blocked until Run 1 PASS)
  │     └── Codex-2: reconciliation + delta + gate_status
  │
  └── feat/msc-incoming-run3     ← MarketSide EXCHANGE (blocked until Run 2 PASS)
        └── Cascade: QR rail + proof cards + narrative
```

**Transfer protocol:**
- Run N completes → Antigravity verifies → Owner GO → merge to staging
- Staging passes → Owner GO → merge to main → deploy
- Run N+1 branch created from updated main
- Never overwrite — always create new branch from latest truth

---

## 8. TEAM-READY ANNOUNCEMENT

📣 **TEAM — MSC-VERSION NEXT (V008) — READ THIS BEFORE ANY WORK**

We are moving into MSC-Version Next.
This is a progressive-disclosure cycle.
No one outruns the proofs.

**Where to read:**
- `skills/` for your lane's specialty
- `justfile` for your execution surface
- `ENGINEERING_PLAYBOOK.md` for the recursive deep-dive
- `AGENT_LEDGER.md` for OPEN → WRITE-IN-PROGRESS → COMMITTED

**What to measure:**
- SeaSide: NGO key integrity
- DeckSide: estimate discipline
- DockSide: gate clarity
- MarketSide: proof cleanliness

**What is ready:**
- Redaction proof
- Campaign PR #1 preview-safe
- Harness proof
- Engineering Playbook + Manifest

**What is blocked:**
- UI expansion
- MSC Run 1
- Any merge or deploy
- Any partner/agency claims

**Next steps:**
1. Acting Master signs §0
2. Arbiter Law clearance
3. Phase A (Netfirms)
4. Worktree recipes appended
5. FASTAPI_ORIGIN patch
6. Proxy/API proof
7. SeaSide button wiring
8. OPEN rows for unclaimed obligations
9. MSC Run 1 branch creation

Stay in your lane.
Follow your skill.
Advance only when your pillar's proof passes.
Owner GO is required for every rail crossing.

---

## 9. V7.5 CARRY-FORWARD — MUST LOCK BEFORE V008 PREP BEGINS

### A. EM/Observer Mode Governance Rules

The Electronic Monitoring toggle is a **cross-pillar disclosure event**.
It unmasks recovery yield, formula, raw→fillet ratios, and the EM Yield Pipeline.

**Governance:**
- EM toggle is owned by DeckSide → DockSide → MarketSide (all three skills)
- Must NEVER unmask private fields to the #CATCH rail
- Must ALWAYS pass boundary checks before deploy
- Dynamic unmask transitions verified in Steps 05, 08, 09
- Trusted External Information Packet (NGO-verified JSON) must remain schema-compliant

### B. v7.5 Schema Lock

The following must be FROZEN before V008 PREP work begins:

| Item | Status | Source |
|------|--------|--------|
| Pairing hashes | INTEGRATED | `seatrace_pydantic_public_private_schema.md` |
| Scale-matching fields | INTEGRATED | v7.5 walkthrough verification |
| Updated FastAPI endpoints | INTEGRATED | Pydantic schema alignment |
| Recovery yield display rules | LOCKED | `recovery_label: "conversion measured"` only on public |
| EM Yield Pipeline CSS flowchart | VERIFIED | Antigravity screenshot proof |

**No schema changes after lock. V008 adds behavior, not structure.**

### C. Preview-Safe Narrative Rules

On ALL public surfaces (campaign, harness, README, PR descriptions):

- No partner claims (no "Peter Pan partnership confirmed")
- No agency claims (no "contracted with X")
- No MSC certification claims (no "MSC certified")
- No "verified by NOAA/USDA/FDA" language
- No raw yield percentages
- No settlement amounts or pricing
- Aspirational language only: "designed to support", "aligned with", "scenario-safe"

### D. V008 PREP Goal

One complete SeaSide → DeckSide → DockSide → MarketSide proof rail
with EM toggle integrated and schema v7.5 locked.

```
SeaSide (proxy/API proof)
    → DeckSide (estimate + EM toggle unmask)
        → DockSide (reconciliation + gate + scale-match)
            → MarketSide (QR trace + proof card + narrative)
```

All four checkpoints active. Zero Arbiter Law hits. Schema frozen.
**That is V008 PREP complete.**

---

## 10. WHAT THE ACTING MASTER ISSUES NEXT

```
GO-SEATRACE-V008-PREP-START
  scope:
    - freeze v7.5 schema
    - freeze EM toggle behavior
    - freeze preview URLs
    - authorize worktree creation
    - authorize OPEN rows
    - authorize proxy/API proof
    - block all UI expansion until SeaSide proof passes
```

Once issued, Cascade prepares:
- Pillar-specific SKILL.md updates (EM governance added) ✅
- OPEN rows for unclaimed obligations
- MSC Run 1 branch plan
- Team-ready announcement

---

*Commons Good CC BY-SA 4.0 — Roberto Scott Echols, WorldSeafoodProducers.com*
*Progressive disclosure: agent → justfile → skill → proof → next disclosure*
*Public v007.5 → Private V008 PREP. Wind blows in both directions.*
