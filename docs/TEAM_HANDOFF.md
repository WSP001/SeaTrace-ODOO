# TEAM_HANDOFF

Coordinated playbook for finishing the docs-first rollout of the SeaTrace suite.
Follow the phases in order: **Security → Dev → QA → SRE**. Stop at every gate
until the owning role signs off.

---

## At-a-glance Flow

1. **Security/Ops** – gitleaks scan (`Finding: 0`) and TLS readiness
2. **Dev Lead** – docs-first commit on `feature/pillars-dev-quickstart`
3. **QA** – Newman/k6 runs plus doc validation
4. **SRE** – secrets, embeddings workflow, runtime smoke checks

---

## Role 1 — Security / Ops (must run first)

**Goal:** Ensure no secrets ship and that TLS material is ready to rotate if
needed.

### Core Checklist

- ✅ `gitleaks` scan completed with zero findings
- ✅ TLS materials reviewed (`docs/security/san.cnf`,
  `docs/security/NETFIRMS_SUPPORT_TICKET.md`,
  `docs/security/SECTIGO_REVOCATION_REQUEST.md`)
- ✅ No private key material staged
- ✅ Cloudflare/Netfirms contacts on standby

### Command Block

```powershell
cd "C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO"
gitleaks detect `
  --source . `
  --config .gitleaks-seatrace.toml `
  --report-format json `
  --report-path gitleaks-scan-2025-10-28.json `
  --redact `
  --verbose `
  --exit-code 1
```

- Exit code `0` → continue.  
- Exit code `1` → follow `docs/security/INCIDENT_2025-10-28_TLS_EXPOSURE.md`.

### Optional TLS Rotation (only if cert/private key exposure is confirmed)

1. Generate key & CSR:

   ```bash
   openssl genrsa -out worldseafoodproducers_new.key 4096
   openssl req -new -key worldseafoodproducers_new.key \
     -out worldseafoodproducers.csr \
     -config docs/security/san.cnf
   ```

2. Submit CSR via Netfirms ticket (`docs/security/NETFIRMS_SUPPORT_TICKET.md`).
3. Install the issued cert, verify with `openssl s_client` + `curl`.
4. Revoke the old cert (template in `docs/security/SECTIGO_REVOCATION_REQUEST.md`).
5. Purge Cloudflare cache if in front of Netfirms.

### Slack Clearance Template

```
:lock: SECURITY CLEARANCE :lock:
Repo: SeaTrace-ODOO
gitleaks report: gitleaks-scan-2025-10-28.json (Finding: 0)
No private keys or secrets detected.

:white_check_mark: Dev Lead may proceed.
```

Tag @dev-lead @qa-team @sre @ops @security.

---

## Role 2 — Dev Lead / Repo Owner

**Goal:** Stage the docs-first commit, pause for Roberto’s review before any push.

### Prep

- Confirm Security clearance message.
- Ensure staged files already exist in repo:
  - `docs/pillars/*.md`
  - `.ai/assistant_context.json`
  - `postman/collection.json`
  - `scripts/dev-quickstart.sh`
  - `scripts/create-pillars-md.sh`
  - `scripts/bashrc_roberto002`
  - `.gitleaks-seatrace.toml`
  - `.github/embedding-requirements.txt`
  - `.github/scripts/create_embeddings.py`
  - `.github/workflows/update-embeddings.yml`
  - `README_EMBEDDINGS.md`
  - `READY_FOR_SEQUENTIAL_RUNS.md`
  - `GIT_COMMANDS_READY.md`

### Command Block

```powershell
cd "C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO"
git checkout -b feature/pillars-dev-quickstart
git add docs/pillars/*.md `
        .ai/assistant_context.json `
        postman/collection.json `
        scripts/dev-quickstart.sh `
        scripts/create-pillars-md.sh `
        scripts/bashrc_roberto002 `
        .gitleaks-seatrace.toml `
        .github/embedding-requirements.txt `
        .github/scripts/create_embeddings.py `
        .github/workflows/update-embeddings.yml `
        README_EMBEDDINGS.md `
        READY_FOR_SEQUENTIAL_RUNS.md `
        GIT_COMMANDS_READY.md
git commit -m "chore(docs): add pillars docs, assistant_context, Postman skeleton, dev quickstart and embeddings workflow (docs-first)"
```

**STOP HERE.** Share `git --no-pager show --stat --pretty=fuller HEAD` with
Roberto. Do not push until he replies with “Approved — push it.”

### After Approval

```powershell
git push origin feature/pillars-dev-quickstart
gh pr create `
  --base main `
  --head feature/pillars-dev-quickstart `
  --title "chore(docs): add pillar docs, assistant_context, Postman skeleton & embeddings workflow" `
  --body-file DOCS_FIRST_PR_PLAN.md
```

Change `--body-file` if you prefer a different PR body.

Post PR notification:

```
:bookmark_tabs: PR created — Docs-first
PR: <URL>
Please review docs/pillars/* and assistant_context.json.
QA: run Newman + k6
Security: ensure CI gitleaks stays green
```

---

## Role 3 — QA Team

**Goal:** Validate documentation accuracy and public API flows.

### Steps

1. Spin up local stack (use existing scripts under `scripts/` or docker compose).
2. **Newman regression:**

   ```bash
   newman run postman/collection.json \
     -e postman/environment.json \
     --reporters cli,junit \
     --reporter-junit-export newman-report.xml
   ```

3. **k6 smoke (optional but recommended):**

   ```bash
   k6 run tests/k6/k6-verify-burst.js -e BASE_URL=https://seatrace.local
   ```

   Adjust path/env if k6 script differs.

4. Review `docs/pillars/*.md`, `README_EMBEDDINGS.md`,
   and `READY_FOR_SEQUENTIAL_RUNS.md` for accuracy.

5. Log findings on the PR. If blocking, set PR status to “Changes requested.”

---

## Role 4 — SRE / Release Team

**Goal:** Wire automation, secrets, and runtime checks once the PR merges.

### Post-Merge Actions

1. **GitHub secrets:** add `OPENAI_API_KEY`, `VECTOR_DB_TYPE`,
   `PINECONE_API_KEY/PINECONE_ENV` or `WEAVIATE_URL/WEAVIATE_API_KEY`, and
   `VECTOR_DB_INDEX` as needed.
2. **Embeddings workflow:** verify `.github/workflows/update-embeddings.yml`
   runs to completion. Inspect uploaded artifact or vector DB status.
3. **Dev environment health:** run `scripts/dev-quickstart.sh` inside WSL,
   confirm `.devcontainer` (if added later) builds, ensure ports 8000–8003
   forward correctly.
4. **Production smoke:** check Netfirms/Netlify logs, confirm TLS chain with
   `openssl s_client`, crawl critical endpoints with `curl` or Postman.

---

## Decision Gates

| Gate             | Owner        | Pass Criteria                              | Action on Fail                                           |
|------------------|--------------|--------------------------------------------|----------------------------------------------------------|
| Security scan    | Security/Ops | `gitleaks` exit code `0`                    | Follow incident runbook, rotate secrets if required      |
| Docs commit      | Dev Lead     | Roberto signs off on `git show` output      | Amend commit and re-review                               |
| QA validation    | QA           | Newman/k6 acceptable, docs accurate         | File PR comments, block merge                            |
| Runtime readiness| SRE          | Secrets set, embeddings workflow healthy    | Troubleshoot automation, retry after fixes               |

---

## Contact Directory

- Security Lead – security@worldseafoodproducers.com
- Dev Lead – devlead@worldseafoodproducers.com
- SRE / Ops – ops@worldseafoodproducers.com
- Owner (Roberto) – scott@worldseafoodproducers.com

---

## Using this Document

1. Security runs Section 1 and posts clearance.
2. Dev Lead executes Section 2 up to the STOP, then waits.
3. After approval, Dev Lead finishes Section 2 and notifies QA/SRE.
4. QA completes Section 3, updating PR status.
5. After merge, SRE completes Section 4 and reports back.

Track sign-offs in your team chat or by appending initials/date at the bottom
of this file.
