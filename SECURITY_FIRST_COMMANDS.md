# 🔐 SECURITY FIRST — TLS Key Rotation & Validation (Step 0)

**Created:** 2025-10-28  
**Priority:** **CRITICAL** (Run BEFORE any git push)  
**Repository:** SeaTrace-ODOO

---

## ⚠️ Why Security First?

**Before committing docs or code, we MUST ensure:**
1. ✅ No private keys in workspace (gitleaks scan)
2. ✅ TLS certificate rotated (if any exposure occurred)
3. ✅ Cloudflare cache purged (old cert removed from CDN)
4. ✅ Sectigo revocation submitted (old cert invalidated)

**Roberto's Context:**
- Previous security incident: TLS private key possibly exposed
- Certificate serial: `0BD07C9CB89DA0F1C7614D746813CD85CA788B21`
- Affected domain: `worldseafoodproducers.com`
- Current host: Netfirms (shared hosting)
- CDN: Cloudflare (caching old certs)

---

## 🚀 Step 0.1: Run Gitleaks Scan (Confirm No Secrets)

**Purpose:** Verify no private keys, API keys, or credentials are in the workspace before any git operations.

### Command (PowerShell):

```powershell
# Navigate to repository
cd C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO

# Run gitleaks with SeaTrace config
gitleaks detect --source . --config .gitleaks-seatrace.toml --report-format json --report-path gitleaks-scan-2025-10-28.json --redact --verbose
```

### Expected Output:

```
○
    ○╲
      ○ ○
     ○ ░ ○
     ○ ░ ○
      ○ ░ ○
        ░ ░
       ░ ░
      ░ ░
     ░ ░
    ░ ░
   
   gitleaks

Finding:     0
```

### If Findings Detected:

**STOP IMMEDIATELY** — Do NOT commit or push. Follow incident response:

1. **Identify the finding:**
   ```powershell
   Get-Content gitleaks-scan-2025-10-28.json | ConvertFrom-Json | Select-Object -ExpandProperty Results | Format-List
   ```

2. **Remove from workspace:**
   ```powershell
   # If it's a file:
   Remove-Item path\to\secret-file.key -Force
   
   # If it's in .env:
   # Manually edit .env and remove the secret line
   ```

3. **Rotate the secret:**
   - Private keys → Generate new key pair (see Step 0.2)
   - API keys → Revoke old key, generate new key at provider
   - Database credentials → Rotate passwords immediately

4. **Re-run gitleaks** until `Finding: 0`

---

## 🔑 Step 0.2: Generate New TLS Private Key & CSR

**Purpose:** Replace any potentially exposed TLS private key with a new 4096-bit RSA key.

### Command (PowerShell with OpenSSL):

```powershell
# Navigate to security directory
cd C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO\docs\security

# Generate new 4096-bit RSA private key (KEEP THIS SECRET)
openssl genrsa -out worldseafoodproducers_NEW_2025-10-28.key 4096

# Generate Certificate Signing Request (CSR) using SAN config
openssl req -new -key worldseafoodproducers_NEW_2025-10-28.key -out worldseafoodproducers_2025-10-28.csr -config san.cnf

# Verify CSR contains SANs
openssl req -text -noout -in worldseafoodproducers_2025-10-28.csr | Select-String -Pattern "Subject Alternative Name" -Context 0,5
```

### Expected Output:

```
Generating RSA private key, 4096 bit long modulus (2 primes)
...........++++
.......................................++++
e is 65537 (0x010001)

Subject Alternative Name:
    DNS:worldseafoodproducers.com, DNS:www.worldseafoodproducers.com
```

### Files Created:

- **`worldseafoodproducers_NEW_2025-10-28.key`** (PRIVATE — DO NOT COMMIT)
- **`worldseafoodproducers_2025-10-28.csr`** (PUBLIC — safe to send to CA)

---

## 📧 Step 0.3: Submit CSR to Netfirms Support

**Purpose:** Order new SSL certificate with updated CSR.

### Email Template:

Copy-paste this into Netfirms support ticket:

```
Subject: URGENT — SSL Certificate Reissue for worldseafoodproducers.com (Security Incident)

Hello Netfirms Support Team,

I am requesting an URGENT reissue of my SSL certificate for worldseafoodproducers.com due to a security incident (potential private key exposure).

**Account Details:**
- Domain: worldseafoodproducers.com
- Netfirms Account Username: [YOUR_USERNAME]
- Current Certificate Serial: 0BD07C9CB89DA0F1C7614D746813CD85CA788B21
- Current Certificate Issuer: Sectigo

**Request:**
1. Reissue SSL certificate using the attached CSR (worldseafoodproducers_2025-10-28.csr)
2. Confirm new certificate will cover:
   - worldseafoodproducers.com
   - www.worldseafoodproducers.com
3. Provide ETA for new certificate issuance

**CSR (paste below):**
[PASTE OUTPUT OF: Get-Content worldseafoodproducers_2025-10-28.csr]

**Urgency:**
This is a critical security incident. I will submit a separate revocation request to Sectigo for the old certificate (serial 0BD07C9CB89DA0F1C7614D746813CD85CA788B21) once the new certificate is installed.

Please prioritize this request and reply within 24 hours with the new certificate files (.crt, .ca-bundle).

Thank you,
Roberto
World Seafood Producers
```

### Attach:

- `worldseafoodproducers_2025-10-28.csr`

**DO NOT attach the .key file — that must stay private on your machine.**

---

## 🔒 Step 0.4: Submit Revocation Request to Sectigo

**Purpose:** Invalidate the old certificate immediately after new certificate is installed.

### Revocation Request Form:

Use the template already created in `docs/security/SECTIGO_REVOCATION_REQUEST.md`:

```powershell
# Open the template
notepad docs\security\SECTIGO_REVOCATION_REQUEST.md
```

Fill in:
- Certificate Serial Number: `0BD07C9CB89DA0F1C7614D746813CD85CA788B21`
- Reason for Revocation: `Key Compromise`
- Date of Compromise: `2025-10-28`

Submit to Sectigo via:
- **Online Form:** https://secure.sectigo.com/products/RevocationRequest
- **OR Email:** support@sectigo.com (attach filled template)

**IMPORTANT:** Only submit revocation **AFTER** new certificate is installed on Netfirms. Otherwise, your site will show "Certificate Revoked" errors.

---

## 🌐 Step 0.5: Verify New Certificate Installation

**Purpose:** Confirm new certificate is active and served by Netfirms.

### Command (PowerShell):

```powershell
# Test TLS handshake (after Netfirms confirms installation)
openssl s_client -connect worldseafoodproducers.com:443 -servername worldseafoodproducers.com < $null | Select-String -Pattern "subject=", "issuer=", "notAfter="

# Check certificate serial (should be NEW, not 0BD07C9C...)
openssl s_client -connect worldseafoodproducers.com:443 -servername worldseafoodproducers.com < $null | openssl x509 -noout -serial
```

### Expected Output (with NEW certificate):

```
subject=CN=worldseafoodproducers.com
issuer=C=US, O=Sectigo Limited, CN=Sectigo RSA Domain Validation Secure Server CA
notAfter=Oct 28 23:59:59 2026 GMT
serial=<NEW_SERIAL_NUMBER_NOT_0BD07C9C...>
```

### If Old Certificate Still Showing:

**Possible causes:**
1. **Cloudflare caching** — Purge cache (see Step 0.6)
2. **Netfirms propagation delay** — Wait 5-10 minutes, retry
3. **Browser cache** — Clear browser cache and retry

---

## ☁️ Step 0.6: Purge Cloudflare Cache

**Purpose:** Remove old certificate from Cloudflare CDN edge nodes.

### Option A: Cloudflare Dashboard (Recommended)

1. Log in to Cloudflare: https://dash.cloudflare.com/
2. Select domain: `worldseafoodproducers.com`
3. Navigate to **Caching** → **Configuration**
4. Click **Purge Everything**
5. Confirm purge

### Option B: Cloudflare API (PowerShell)

```powershell
# Set variables (replace with your values)
$CLOUDFLARE_ZONE_ID = "YOUR_ZONE_ID"  # Found in Cloudflare dashboard under "Zone ID"
$CLOUDFLARE_API_TOKEN = "YOUR_API_TOKEN"  # Create at: https://dash.cloudflare.com/profile/api-tokens

# Purge all cache
Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/purge_cache" `
  -Method Post `
  -Headers @{
    "Authorization" = "Bearer $CLOUDFLARE_API_TOKEN"
    "Content-Type" = "application/json"
  } `
  -Body '{"purge_everything":true}'
```

### Expected Output:

```json
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": {
    "id": "..."
  }
}
```

---

## ✅ Step 0.7: Final Security Checklist

**Before proceeding to Docs-First PR, confirm ALL items:**

- [ ] **Gitleaks scan passed** (Finding: 0)
- [ ] **New TLS key generated** (worldseafoodproducers_NEW_2025-10-28.key stored securely)
- [ ] **CSR submitted to Netfirms** (ticket opened, awaiting certificate)
- [ ] **New certificate installed** (verified with `openssl s_client`)
- [ ] **Old certificate revocation submitted to Sectigo** (after new cert installed)
- [ ] **Cloudflare cache purged** (old cert removed from CDN)
- [ ] **Browser test passed** (https://worldseafoodproducers.com shows valid cert)

**If ANY item is unchecked, DO NOT proceed to git push.**

---

## 🌊 For the Commons Good — Why This Matters

**Security-first protects:**
- ✅ 285 vessel captains (PK1: Vessel Keys)
- ✅ 285 processing facilities (PK2: Facility Keys)
- ✅ 285 market participants (PK3: Market Keys)
- ✅ Millions of consumers scanning QR codes
- ✅ $1.026M/month revenue stream ($12.3M/year)
- ✅ 93.9% profit margin (depends on trust)

**One compromised key → entire SeaTrace chain loses immutability.**

DockSide's THE SECOND FORK reconciles:
- INCOMING: Raw supply (fish tickets, standard tally weights)
- RECONCILIATION: H&G 70-75%, Fillet 50-60%, Pollock/Cod 80% loss (30% kept on best day for 10lb box pinbone-out/skin-off)
- OUTGOING: Finished products (SKUs, QR codes, blockchain immutability)

**If TLS keys are compromised, packet switching handler (#KEY vs $KEY routing) loses trust.**

---

## 🚀 What's Next?

**After completing ALL items in Step 0.7 checklist:**

✅ **You are ready to proceed to DOCS_FIRST_PR_PLAN.md**

Run:
```powershell
notepad DOCS_FIRST_PR_PLAN.md
```

That file contains:
- Exact git commands for docs-first PR
- Team announcement template
- PR body template
- Reviewer checklist
- WSL Bash directory structure helpers

---

**Agent Note to Roberto:**  
This is your **STOP GATE**. Do not run any git commands from GIT_COMMANDS_READY.md until you complete this security checklist. I trust you will figure out the Netfirms workflow — I've given you exact commands and templates. Once Netfirms confirms the new certificate is installed, come back and we'll run the docs-first PR together. 🔐🌊
