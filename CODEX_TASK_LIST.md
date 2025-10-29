# CODEX Task List - SeaTrace Commons Good Infrastructure

## 📋 Context

GitHub Copilot has completed the architectural analysis and discovered the **NGO/GFW (Global Fishing Watch) integration** which is the foundation of **SeaSide (HOLD) module**. The Four Pillars architecture is now understood:

1. **SeaSide (HOLD)** - F/V MASTER AIS overlay with NGO/GFW API integration (PUBLIC KEY 🔓)
2. **DeckSide (RECORD)** - THE FORK where packet switching handler splits #CATCH (PUBLIC) vs $CHECK (PRIVATE) streams
3. **DockSide (STORE)** - Landing reconciliation and cold chain monitoring (PUBLIC KEY 🔓)
4. **MarketSide (EXCHANGE)** - QR verification (PUBLIC) + Trading platform (PRIVATE KEY 🔐)

## 🎯 Your Tasks (In Order)

### ✅ **COMPLETED BY YOU** (Codex has already done these!)
- [x] Added `contracts/packet.proto` + `buf.yaml` 
- [x] Created `.github/workflows/buf-check.yml`
- [x] Published JWKS route at `pages/.well-known/jwks.js`
- [x] Wired dual-key toggle in `pages/api-portal.jsx`
- [x] Dropped k6 burst harness at `tests/k6/k6-verify-burst.js`
- [x] Verified repo state (untracked files ready for commit)

### 🔄 **PENDING MANUAL ACTIONS** (For GitHub Copilot to help with)

#### 1. **Validate Packet.proto Schema** 🔍
- **File:** `contracts/packet.proto`
- **Action:** Review protobuf schema and verify it matches:
  - GFW API response structure from `gfw_integration.py`
  - NGO agent packet format from `ngo_agent.py`
  - Packet switching handler expectations from `packet_handler.py`
- **Expected Fields:**
  - `source` (e.g., "SeaSide", "DeckSide")
  - `destination` (e.g., "DeckSide", "DockSide", "MarketSide")
  - `payload` (nested structure with `ais_data`, `vessel_info`, `activity_prediction`)
  - `timestamp` (ISO 8601 format)
  - `packet_type` (PUBLIC #CATCH vs PRIVATE $CHECK indicator)

#### 2. **Review buf-check.yml Workflow** ✅
- **File:** `.github/workflows/buf-check.yml`
- **Action:** Verify CI pipeline includes:
  - `buf lint` check on PR
  - `buf breaking --against ".git#branch=main"` for schema compatibility
  - Failure blocks merge if proto schema breaks

#### 3. **Setup JWKS Environment Variables** 🔐
- **Context:** JWKS (JSON Web Key Set) for PUBLIC key verification
- **Action:** Document required environment variables:
  - `SEATRACE_JWKS_JSON` (full JWKS object) OR
  - `SEATRACE_VERIFY_KEYS` (array of public keys)
- **Deployment Targets:** Next.js dev server, Netlify, staging environment
- **Note:** Commons Good practice - JWKS should be PUBLIC (no private keys in this repo)

#### 4. **Run buf Lint & Breaking Checks Locally** 🧪
- **Command:** `buf lint && buf breaking --against ".git#branch=main"`
- **Expected Output:** All checks pass (no linting errors, no breaking changes vs main branch)
- **If Fails:** Document errors and suggest fixes

#### 5. **Test k6 Harness** 📊
- **File:** `tests/k6/k6-verify-burst.js`
- **Command:** `k6 run tests/k6/k6-verify-burst.js -e BASE_URL=https://seatrace.worldseafoodproducers.com`
- **Expected Metrics:**
  - Rate limit headers present (`X-RateLimit-Remaining`)
  - Response time < 2000ms (SLO threshold)
  - No precise GPS in PUBLIC payloads
  - No private pricing data exposed
- **Save Output:** For PR notes/documentation

#### 6. **Install Pre-commit Hooks** 🛡️
- **Command:** `pre-commit install`
- **Expected Behavior:** 
  - Gitleaks scans for secrets before each commit
  - detect-secrets validates baseline
  - Hooks trigger automatically on `git commit`
- **Verify:** Make test commit with fake secret (should be blocked)

#### 7. **Plan Netlify Migration** 🌐
- **Context:** Move from Netfirms FTP to Netlify
- **Current State:** `staging/index.html` is ready for deployment
- **Required Actions:**
  - Document DNS CNAME change: `seatrace.worldseafoodproducers.com CNAME <netlify-site>.netlify.app`
  - Decide build strategy:
    - **Option A:** Static export (`staging/index.html` + assets)
    - **Option B:** Full Next.js build (`npm run build && npm run export`)
  - Configure Netlify:
    - Base directory: repo root
    - Build command: `npm run build && npm run export` (if Option B)
    - Publish directory: `out` (if Option B) or `staging` (if Option A)
  - Test SSL certificate (Netlify auto-provisions Let's Encrypt)

---

## 📊 Success Criteria

### For "PROCEED: PR BUNDLE" (PUBLIC)
- ✅ `contracts/packet.proto` validated and matches GFW API structure
- ✅ `buf-check.yml` CI pipeline passes on PR
- ✅ JWKS environment variables documented
- ✅ `buf lint` and `buf breaking` checks pass locally
- ✅ k6 test output saved (proves rate limits + no IP leakage)
- ✅ Pre-commit hooks installed and tested
- ✅ Netlify migration plan documented (DNS, build config, SSL)

### For "CASE: PRIVATE CI" (PRIVATE)
- ✅ `.gitleaks.toml` (PRIVATE) with relaxed allowlist for `infra/env/*.example`
- ✅ `.github/workflows/k6-nightly.yml` scheduled job configured
- ✅ Environment secrets documented (`PRIVATE_BASE_URL`, `SEATRACE_LICENSE`)
- ✅ Postman backup stub created (`postman-enumerate-v2.ps1`)

---

## 🤝 Handoff Notes

**From GitHub Copilot:**
- Found NGO/GFW integration files in `SeaTrace002/services/seaside/`
- Read `gfw_integration.py` (async GFW API client with rate limiting)
- Read `ngo_agent.py` (NGO data access agent with Prometheus metrics)
- Read `ngo_routes.py` (FastAPI routes for NGO access requests)
- Read OneDrive docs: `GFW001.txt`, `a. Hold Systems SUBJECT TO BEST Sea.txt`
- Updated `README.md` mermaid diagram with CORRECT architecture (SeaSide → DeckSide FORK → DockSide/MarketSide)

**Waiting for Codex:**
- Validate packet.proto schema against GFW API
- Test k6 harness and save output
- Install pre-commit hooks
- Plan Netlify migration (DNS/build strategy)

**What I'll Do Next (GitHub Copilot):**
- Complete Pillar Details sections in `README.md` (SeaSide with NGO/GFW context, DeckSide Fork explanation, DockSide reconciliation, MarketSide QR vs Trading split)
- Update `SeaTrace002/README.md` (PRIVATE) with packet_handler.py implementation details, WCCOE architecture, ML integration

---

## 🔄 When You're Ready

**Say one of these:**
- **"PROCEED: PR BUNDLE"** → I'll generate all PUBLIC repo files/commands
- **"CASE: PRIVATE CI"** → I'll generate all PRIVATE repo files/commands
- **"FILES READY"** → If you want me to read diffs first before proceeding

**Or ask questions about:**
- Packet.proto schema structure
- JWKS key format
- k6 test scenarios
- Netlify build configuration
- Pre-commit hook setup

---

> 💡 **Tip:** Start with **packet.proto validation** (Task #1) - that's the foundation for everything else! The protobuf schema must match the GFW API response structure from `gfw_integration.py`.
