# AGENTS.md -- SeaTrace ODOO Session Entry Contract

**Version:** 1.0.0
**Last Updated:** 2026-04-16
**Owner:** Scott / Acting Master
**Canonical Path:** `C:\WSP001\SeaTrace-ODOO`

```text
STATUS: ACTIVE
MODE: READ_FIRST
PROOF_RULE: PROOF_BEFORE_NARRATIVE
SAFETY_RULE: MOVE_NOT_DELETE
ZONE: BUSINESS
```

This workspace is treated as a business repo.
Use stricter scope control and do not infer secrets, endpoints, or deploy steps.

## Session Start

Name these first:

```text
REPO
OWNER
LANE
FILE_SCOPE
PROOF_COMMAND
```

Then run:

```powershell
just orient
just truth
just business-safety
```

## Current Lanes

```text
Scott / Acting Master
  Role: governance, business truth, merge decision, next owner

Frontend lane
  Role: UI, static assets, presentation shell

Backend / integration lane
  Role: scripts, services, connectors, data plumbing

QA lane
  Role: verification only, no implementation
```

## Rules

- Read first.
- Use narrow file scope.
- Do not move public patterns into private execution without review.
- Do not invent deployment claims.
- Record next owner at the end of meaningful work.

## OMX-Compatible Workflow

```text
$deep-interview  -> clarify repo boundary, lane, and file scope
$ralplan         -> approve the safest business plan
$ralph           -> execute one approved lane through proof
$team            -> split work only after owner/lane/proof are explicit
```

## Durable State

Shared restart-safe notes belong under `.omx/`.
