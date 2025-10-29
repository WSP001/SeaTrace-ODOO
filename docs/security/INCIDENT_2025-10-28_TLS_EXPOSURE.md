# 🚨 SECURITY INCIDENT REPORT
**Date:** October 28, 2025  
**Severity:** HIGH  
**Status:** CONTAINMENT IN PROGRESS

---

## INCIDENT SUMMARY

**TLS Certificate and Private Key exposed** for `www.worldseafoodproducers.com` in development chat context.

**Affected Assets:**
- Domain: `www.worldseafoodproducers.com` + `worldseafoodproducers.com`
- Certificate Authority: Sectigo Public Server Authentication CA DV R3.6
- Expiry: October 23, 2026
- Certificate Serial: `d9b7b2690ecce57cd588b18abd020942`

---

## TIMELINE

**2025-10-28 16:59:17 UTC:**
- Cloudflare 502 Bad Gateway error detected (Ray ID: 995bfb965a082786)
- User reported: "Bad gateway Error code 502... I THOUGHT WE FIXED. BUT I GUESS NOT"

**2025-10-28 [CURRENT TIME]:**
- TLS certificate and private key discovered in development context
- Incident response initiated

---

## IMMEDIATE CONTAINMENT ACTIONS (REQUIRED NOW!)

### **1. Generate New TLS Certificate**
```bash
# Generate new private key (2048-bit RSA minimum, 4096-bit recommended)
openssl genrsa -out worldseafoodproducers_new.key 4096

# Generate CSR (Certificate Signing Request)
openssl req -new -key worldseafoodproducers_new.key -out worldseafoodproducers.csr \
  -subj "/C=US/ST=Florida/L=Winter Haven/O=World Seafood Producers/CN=www.worldseafoodproducers.com"

# Add Subject Alternative Names (SAN)
# Create openssl.cnf with:
# [req]
# distinguished_name = req_distinguished_name
# req_extensions = v3_req
# [req_distinguished_name]
# [v3_req]
# subjectAltName = @alt_names
# [alt_names]
# DNS.1 = worldseafoodproducers.com
# DNS.2 = www.worldseafoodproducers.com

# Submit CSR to Sectigo or your CA
```

### **2. Revoke Old Certificate**
- **Contact:** Sectigo Support or Netfirms SSL management
- **Serial Number:** `d9b7b2690ecce57cd588b18abd020942`
- **Revocation Reason:** Key Compromise (Reason Code: 1)

### **3. Update Netfirms Hosting**
**Login:** Netfirms control panel (www1.netfirms.com)
1. Navigate to SSL/TLS management
2. Upload new certificate and private key
3. Update Apache/nginx configuration
4. Restart web server

### **4. Purge Cloudflare Cache**
**Cloudflare Dashboard:**
1. Login to Cloudflare account
2. Select `worldseafoodproducers.com` zone
3. Navigate to Caching → Configuration
4. Click "Purge Everything"
5. Wait 5-10 minutes for propagation

**API Method:**
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer YOUR_CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

### **5. Verify New Certificate**
```bash
# Test TLS handshake
openssl s_client -connect worldseafoodproducers.com:443 -servername worldseafoodproducers.com

# Verify certificate details
echo | openssl s_client -connect worldseafoodproducers.com:443 -servername worldseafoodproducers.com 2>/dev/null | openssl x509 -noout -dates -subject -issuer
```

---

## ROOT CAUSE ANALYSIS

**Proximate Cause:** TLS certificate and private key pasted into development chat context while troubleshooting 502 Bad Gateway error.

**Contributing Factors:**
1. Lack of secret scanning in development workflows
2. No pre-commit hooks to detect certificate/key patterns
3. Manual debugging led to credential exposure

**Underlying Issues:**
1. Netfirms hosting configuration causing 502 errors
2. Cloudflare SSL mode may be misconfigured (needs Full/Full (strict) mode)
3. Website not deployed to secure alternatives (Netlify, Windsurf)

---

## REMEDIATION CHECKLIST

### **Immediate (Next 1 Hour):**
- [ ] Generate new TLS certificate and private key
- [ ] Submit CSR to Sectigo CA
- [ ] Revoke compromised certificate (Serial: `d9b7b2690ecce57cd588b18abd020942`)
- [ ] Mark old private key as `<<COMPROMISED - DO NOT USE>>`

### **Short-Term (Next 24 Hours):**
- [ ] Upload new certificate to Netfirms hosting
- [ ] Update Apache/nginx configuration
- [ ] Restart web server
- [ ] Purge Cloudflare cache
- [ ] Verify TLS handshake with new certificate
- [ ] Test website: https://www.worldseafoodproducers.com
- [ ] Monitor Cloudflare analytics for 502 errors

### **Medium-Term (Next 7 Days):**
- [ ] Migrate website to Netlify or Windsurf (more secure, easier deployment)
- [ ] Configure Cloudflare SSL mode to "Full (strict)"
- [ ] Set up automated certificate renewal (Let's Encrypt or similar)
- [ ] Add `gitleaks` pre-commit hook to prevent future exposures
- [ ] Add `detect-secrets` scanning to CI/CD pipeline
- [ ] Document TLS certificate rotation procedure

### **Long-Term (Next 30 Days):**
- [ ] Implement secret management system (HashiCorp Vault, AWS Secrets Manager)
- [ ] Add nightly security scans (gitleaks, detect-secrets)
- [ ] Train team on secret hygiene best practices
- [ ] Create automated alerting for certificate expiry (30/7 days before expiry)
- [ ] Implement certificate transparency monitoring

---

## IMPACT ASSESSMENT

**Systems Affected:**
- `www.worldseafoodproducers.com` (PRIMARY)
- `worldseafoodproducers.com` (ALIAS)
- Netfirms shared hosting subdomain

**Services Impacted:**
- Public website (502 Bad Gateway - already degraded)
- SSL/TLS encryption (compromised certificate)

**Data Exposure:**
- TLS private key (HIGH RISK)
- Certificate details (LOW RISK - public information)

**Business Impact:**
- Website unavailable (502 error pre-existing)
- Potential MITM attacks if old certificate not revoked
- SEO/reputation impact from prolonged downtime

---

## LESSONS LEARNED

### **What Went Well:**
1. ✅ Issue detected quickly during development session
2. ✅ User has comprehensive security runbook already prepared
3. ✅ Clear incident response plan in place

### **What Needs Improvement:**
1. ❌ No automated secret scanning in development workflows
2. ❌ Manual debugging led to credential exposure
3. ❌ Hosting platform (Netfirms) causing reliability issues (502 errors)
4. ❌ No pre-commit hooks to catch certificates/keys

### **Action Items:**
1. **Immediate:** Add `gitleaks` and `detect-secrets` to pre-commit hooks
2. **Short-Term:** Migrate from Netfirms to Netlify/Windsurf for better security and reliability
3. **Medium-Term:** Implement automated certificate management (Let's Encrypt)
4. **Long-Term:** Deploy secret management system (Vault, AWS Secrets Manager)

---

## NETFIRMS 502 ERROR - PARALLEL INVESTIGATION

**Current Error:**
```
Bad gateway Error code 502
Visit cloudflare.com for more information.
2025-10-28 16:59:17 UTC
You: Browser Working
Miami: Cloudflare Working (Ray ID: 995bfb965a082786)
www1.netfirms.com: Host Error
```

**Diagnosis:**
- **Cloudflare → Working** ✅
- **Browser → Working** ✅
- **Netfirms Origin Server → NOT RESPONDING** ❌

**Likely Causes:**
1. Apache/nginx web server down on Netfirms shared hosting
2. SSL/TLS configuration error (expired cert, misconfigured SSL mode)
3. PHP-FPM or backend service crashed
4. Resource limits exceeded (CPU, memory, connections)
5. `.htaccess` misconfiguration causing infinite loop

**Immediate Troubleshooting Steps:**
1. **Check Netfirms control panel:**
   - Service status (Apache, PHP, MySQL)
   - Error logs (access.log, error.log)
   - Resource usage (CPU, memory, bandwidth)

2. **Verify Cloudflare SSL Mode:**
   - Cloudflare Dashboard → SSL/TLS → Overview
   - **Should be:** "Full (strict)" or "Full"
   - **NOT:** "Flexible" (will cause 502 if origin expects HTTPS)

3. **Check Apache/nginx Configuration:**
   - Ensure VirtualHost listening on port 443 (HTTPS)
   - Verify SSLEngine is enabled
   - Check certificate paths are correct

4. **Test Origin Directly (Bypass Cloudflare):**
   ```bash
   # Find origin IP
   nslookup worldseafoodproducers.com
   
   # Test direct connection (replace with actual origin IP)
   curl -I -k https://ORIGIN_IP_ADDRESS -H "Host: www.worldseafoodproducers.com"
   ```

5. **Check `.htaccess` for Loops:**
   - Review rewrite rules for infinite redirects
   - Temporarily rename `.htaccess` to `.htaccess.bak` and test

**Recommendation:**
Given the complexity of debugging Netfirms shared hosting and the security incident, **STRONGLY RECOMMEND MIGRATING TO NETLIFY** where:
- ✅ Automatic HTTPS with Let's Encrypt
- ✅ No 502 errors from origin server issues
- ✅ Git-based deployment (no manual file uploads)
- ✅ Built-in CDN and DDoS protection
- ✅ Free tier supports custom domains

---

## MIGRATION TO NETLIFY (RECOMMENDED)

### **Step 1: Deploy SeaTrace-ODOO to Netlify**
```bash
cd C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO

# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize Netlify site
netlify init

# Build Next.js for static export
npm run build
npm run export

# Deploy
netlify deploy --prod --dir=out
```

### **Step 2: Configure Custom Domain**
1. Netlify Dashboard → Domain management
2. Add custom domain: `seatrace.worldseafoodproducers.com`
3. Update DNS CNAME at your DNS provider:
   ```
   seatrace.worldseafoodproducers.com  CNAME  your-site.netlify.app
   ```
4. Netlify auto-provisions Let's Encrypt certificate (FREE!)

### **Step 3: Environment Variables**
Netlify Dashboard → Site settings → Environment variables:
```
SEATRACE_JWKS_JSON=<your-jwks-json>
SEATRACE_VERIFY_KEYS=<your-verify-keys>
```

### **Step 4: Verify Deployment**
```bash
# Test endpoints
curl https://seatrace.worldseafoodproducers.com/api/v1/seaside/vessels
curl https://seatrace.worldseafoodproducers.com/api/v1/deckside/catches
curl https://seatrace.worldseafoodproducers.com/api/v1/dockside/processing
curl https://seatrace.worldseafoodproducers.com/api/v1/marketside/verification
```

---

## CONTACTS & ESCALATION

**Security Lead:** [TO BE ASSIGNED]  
**Netfirms Support:** support@netfirms.com  
**Sectigo CA Support:** https://sectigo.com/support  
**Cloudflare Support:** https://dash.cloudflare.com/support

**Escalation Path:**
1. Development Team (Immediate containment)
2. Security Lead (Certificate rotation, incident response)
3. Infrastructure Team (Hosting migration to Netlify)
4. Leadership (If customer data affected or regulatory requirements)

---

## ATTACHMENTS

**Exposed Certificate Details:**
- Common Name: `www.worldseafoodproducers.com`
- Subject Alternative Names: `worldseafoodproducers.com`, `www.worldseafoodproducers.com`
- Issuer: Sectigo Public Server Authentication CA DV R3.6
- Valid From: October 23, 2025
- Valid Until: October 23, 2026
- Serial Number: `d9b7b2690ecce57cd588b18abd020942`

**Note:** Private key details intentionally omitted from this report. Compromised private key has been marked for destruction and replacement.

---

## STATUS: CONTAINMENT IN PROGRESS

**Next Actions:**
1. ✅ Incident report created
2. ⏳ Generate new TLS certificate (URGENT - Roberto to initiate)
3. ⏳ Revoke old certificate at Sectigo CA
4. ⏳ Upload new certificate to Netfirms
5. ⏳ Purge Cloudflare cache
6. ⏳ Verify new certificate deployment
7. ⏳ Monitor for 502 resolution

**Incident Commander:** GitHub Copilot (Documentation)  
**Action Owner:** Roberto002 (Certificate rotation and hosting updates)  
**Support:** Development team (Netlify migration assistance)

---

**END OF INCIDENT REPORT**

*This report will be updated as remediation progresses.*
