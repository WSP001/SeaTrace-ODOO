# SKILL: seatrace-justfile-agent

> **Role:** Global rail map + Owner GO sequence
> **Lane:** All (governance overlay)
> **MSC Version:** V008
> **Recursive depth:** Root — all other skills inherit from this one

---

## Purpose

This skill governs the justfile execution surface across all repos.
It defines the Owner GO sequence, rail crossings, and the proof gates
that every other skill must pass before advancing.

---

## Governed Justfiles

| Repo | Justfile | Purpose |
|------|----------|---------|
| SeaTrace-ODOO | `justfile` | Governance + playbook + ETL + twin-parallel |
| seatrace-msc-v007 | `justfile` | Harness build + test |
| seatrace-msc-v007 | `justfile-agents.just` | Agent worktree recipes |
| seatrace-campaign | `justfile` | Campaign build |
| seatrace-campaign | `justfile-site-check.just` | Public deploy gate |

---

## Owner GO Sequence (Progressive Disclosure)

```
§0  Acting Master signature         → unblocks Phase A
§1  Arbiter Law clearance           → unblocks file writes
§2  Phase A human verification      → unblocks patch recipes
§3  Proxy/API proof (Antigravity)   → unblocks UI wiring
§4  Run N proof (Antigravity)       → unblocks Run N+1
§5  Staging verification            → unblocks production deploy
§6  Production deploy               → unblocks partner claims
```

No step runs without the prior step's proof passing.
No agent skips a step.
No shortcut exists.

---

## Rail Crossing Rules

- **Public → Private:** Requires Owner GO + AGENT_LEDGER OPEN row
- **Private → Public:** Requires site-check gate + language scrub + Owner GO
- **Lane → Lane:** Requires proof from departing lane + Owner GO
- **Branch → Main:** Requires Antigravity verification + Owner GO
- **Draft → Production:** Requires staging proof + Owner GO

---

## Justfile Recipe Categories

```
GOVERNANCE     → orient, status, truth, business-safety, lanes
PLAYBOOK       → playbook, playbook-ch, playbook-next, playbook-status
ETL & COSTING  → etl-cost, etl-map, manifest
TWIN-PARALLEL  → twin-status, twin-campaign, twin-dashboard
SKILLS         → skill-list, skill-read, skill-lane
```

---

## Proof Pattern (Every Skill Follows This)

```
1. Read SKILL.md for your lane
2. Run justfile recipe for your gate
3. Produce proof artifact (test output, screenshot, verification report)
4. Antigravity audits proof
5. Owner GO advances to next disclosure
```

---

*This skill is the root of the recursive tree. All other skills inherit these rules.*
