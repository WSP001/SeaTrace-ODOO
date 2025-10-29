# 🔒 SSL/TLS INFRASTRUCTURE FIX GUIDE: seatrace.worldseafoodproducers.com

**Date:** October 26, 2025  
**Critical Issue:** `net::ERR_CERT_COMMON_NAME_INVALID`  
**Impact:** Users see "Your connection is not private" warning  
**Root Cause:** SSL certificate is for `www.worldseafoodproducers.com`, NOT `seatrace.worldseafoodproducers.com`

---

## 🚨 **PROBLEM: Certificate Mismatch**

### **What Users See:**

```
⚠️  Your connection is not private

Attackers might be trying to steal your information from 
seatrace.worldseafoodproducers.com 
(for example, passwords, messages, or credit cards).

NET::ERR_CERT_COMMON_NAME_INVALID

This server could not prove that it is seatrace.worldseafoodproducers.com; 
its security certificate is from www.worldseafoodproducers.com. 

This may be caused by a misconfiguration or an attacker 
intercepting your connection.

[Back to safety]  [Proceed to seatrace.worldseafoodproducers.com (unsafe)]
```

### **Why This Happens:**

Your SSL certificate **Common Name (CN)** or **Subject Alternative Name (SAN)** does NOT include:
- ❌ `seatrace.worldseafoodproducers.com`

But it DOES include:
- ✅ `www.worldseafoodproducers.com`
- ✅ `worldseafoodproducers.com` (maybe)

**Result:** Browser rejects the certificate because the domain name doesn't match.

---

## 🎯 **SOLUTION OPTIONS** (Choose ONE)

### **Option 1: Multi-Domain (SAN) Certificate** ✅ **RECOMMENDED**

**What it is:** One certificate that covers ALL your domains

**Domains to include:**
```
✅ worldseafoodproducers.com
✅ www.worldseafoodproducers.com
✅ seatrace.worldseafoodproducers.com
✅ api.worldseafoodproducers.com (if you use this)
✅ staging.seatrace.worldseafoodproducers.com (for testing)
```

**Pros:**
- ✅ One certificate for all domains
- ✅ Easy to manage
- ✅ Cost-effective
- ✅ Works with Let's Encrypt (FREE)

**Cons:**
- ⚠️ If one domain is compromised, ALL domains are affected
- ⚠️ Larger certificate file size

**Cost:**
- **Let's Encrypt:** FREE (auto-renewal with Certbot)
- **Commercial (Sectigo, DigiCert):** $50-200/year

---

### **Option 2: Wildcard Certificate** ⭐ **BEST FOR GROWTH**

**What it is:** One certificate for `*.worldseafoodproducers.com`

**Covers:**
```
✅ seatrace.worldseafoodproducers.com
✅ api.worldseafoodproducers.com
✅ staging.worldseafoodproducers.com
✅ dev.worldseafoodproducers.com
✅ investor.worldseafoodproducers.com
✅ ANY-SUBDOMAIN.worldseafoodproducers.com
❌ worldseafoodproducers.com (apex domain NOT covered)
```

**Pros:**
- ✅ Future-proof (any new subdomain works)
- ✅ No need to re-issue for new subdomains
- ✅ Clean, scalable architecture

**Cons:**
- ⚠️ Apex domain (worldseafoodproducers.com) needs separate cert OR included as SAN
- ⚠️ Slightly more expensive than single-domain

**Cost:**
- **Let's Encrypt:** FREE (requires DNS-01 challenge)
- **Commercial:** $100-300/year

**Recommendation:** Combine wildcard + apex domain in ONE cert:
```
CN: *.worldseafoodproducers.com
SAN: worldseafoodproducers.com, *.worldseafoodproducers.com
```

---

### **Option 3: Separate Certificate per Subdomain**

**What it is:** Individual cert for each subdomain

**Pros:**
- ✅ Maximum security isolation
- ✅ Compromise of one domain doesn't affect others

**Cons:**
- ❌ Management nightmare (multiple renewals)
- ❌ Higher cost
- ❌ More complex deployment

**Recommendation:** ❌ NOT recommended for your use case

---

## 🛠️ **IMPLEMENTATION: Let's Encrypt (FREE) with Certbot**

### **Step 1: Install Certbot**

**For Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

**For CentOS/RHEL:**
```bash
sudo yum install certbot python3-certbot-nginx
```

**For Windows (IIS):** Use [win-acme](https://www.win-acme.com/)

---

### **Step 2A: Multi-Domain Certificate (HTTP-01 Challenge)**

```bash
# Generate cert for multiple domains (HTTP-01 challenge)
sudo certbot certonly --webroot \
  -w /var/www/html \
  -d worldseafoodproducers.com \
  -d www.worldseafoodproducers.com \
  -d seatrace.worldseafoodproducers.com \
  -d api.worldseafoodproducers.com \
  --email scott@worldseafoodproducers.com \
  --agree-tos \
  --non-interactive

# Certificate will be saved to:
# /etc/letsencrypt/live/worldseafoodproducers.com/fullchain.pem
# /etc/letsencrypt/live/worldseafoodproducers.com/privkey.pem
```

**Requirements:**
- ✅ Port 80 must be open
- ✅ All domains must point to your server's IP
- ✅ Webroot directory accessible

---

### **Step 2B: Wildcard Certificate (DNS-01 Challenge)** ⭐ **RECOMMENDED**

```bash
# Generate wildcard cert (requires DNS TXT record)
sudo certbot certonly --manual \
  --preferred-challenges dns \
  -d worldseafoodproducers.com \
  -d "*.worldseafoodproducers.com" \
  --email scott@worldseafoodproducers.com \
  --agree-tos \
  --non-interactive

# Certbot will prompt you to add TXT record to DNS:
# _acme-challenge.worldseafoodproducers.com TXT "random-verification-string"

# Add TXT record to your DNS provider (GoDaddy, Cloudflare, Route53, etc.)
# Wait 5 minutes for DNS propagation
# Press Enter to continue verification
```

**DNS TXT Record Example (Cloudflare):**
```
Type: TXT
Name: _acme-challenge.worldseafoodproducers.com
Content: "random-verification-string-from-certbot"
TTL: Auto
```

**Automation (Cloudflare DNS):**
```bash
# Install Cloudflare DNS plugin
sudo apt install python3-certbot-dns-cloudflare

# Create Cloudflare credentials file
cat > /etc/letsencrypt/cloudflare.ini <<EOF
dns_cloudflare_api_token = YOUR_CLOUDFLARE_API_TOKEN
EOF

chmod 600 /etc/letsencrypt/cloudflare.ini

# Generate cert with automatic DNS verification
sudo certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
  -d worldseafoodproducers.com \
  -d "*.worldseafoodproducers.com" \
  --email scott@worldseafoodproducers.com \
  --agree-tos
```

---

### **Step 3: Configure Nginx (or Apache)**

**Nginx Configuration:**

```nginx
# /etc/nginx/sites-available/seatrace.worldseafoodproducers.com

server {
    listen 80;
    server_name seatrace.worldseafoodproducers.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seatrace.worldseafoodproducers.com;

    # SSL Certificate (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/worldseafoodproducers.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/worldseafoodproducers.com/privkey.pem;

    # SSL Configuration (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;

    # HSTS (force HTTPS for 1 year)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Document root for SeaTrace API Portal
    root /var/www/seatrace/public;
    index index.html;

    # Serve static files
    location / {
        try_files $uri $uri/ =404;
    }

    # Serve JWKS endpoint (PUBLIC key only)
    location /.well-known/jwks.json {
        alias /var/www/seatrace/public/.well-known/jwks.json;
        add_header Content-Type application/json;
        add_header Access-Control-Allow-Origin "*";
        add_header Cache-Control "public, max-age=3600";
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Rate limiting (PUBLIC endpoints)
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=200r/h;
    location /api/v1/marketside/ {
        limit_req zone=api_limit burst=10 nodelay;
        proxy_pass http://localhost:8000;
    }
}
```

**Test Nginx configuration:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

### **Step 4: Auto-Renewal (Cron Job)**

```bash
# Test renewal (dry-run)
sudo certbot renew --dry-run

# Add cron job for auto-renewal (runs twice daily)
sudo crontab -e

# Add this line:
0 */12 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

**Certbot will:**
- ✅ Check if certificate expires in <30 days
- ✅ Automatically renew if needed
- ✅ Reload Nginx after renewal

---

## 🌐 **DNS CONFIGURATION**

### **Required DNS Records:**

```
# Main domain
A       worldseafoodproducers.com           →  YOUR_SERVER_IP
A       www.worldseafoodproducers.com       →  YOUR_SERVER_IP

# SeaTrace API Portal
A       seatrace.worldseafoodproducers.com  →  YOUR_SERVER_IP

# API endpoint (optional, can use seatrace subdomain)
A       api.worldseafoodproducers.com       →  YOUR_SERVER_IP

# Staging/Dev (optional)
A       staging.seatrace.worldseafoodproducers.com  →  YOUR_STAGING_IP
A       dev.seatrace.worldseafoodproducers.com      →  YOUR_DEV_IP

# ACME challenge (for Let's Encrypt DNS-01)
TXT     _acme-challenge.worldseafoodproducers.com  →  "verification-string"
```

**Cloudflare Settings (if using):**
- ✅ Proxy status: **Proxied** (orange cloud) for DDoS protection
- ✅ SSL/TLS mode: **Full (strict)** (NOT Flexible)
- ✅ Always Use HTTPS: **ON**
- ✅ Automatic HTTPS Rewrites: **ON**

---

## 🔐 **SECURITY BEST PRACTICES**

### **1. HSTS (HTTP Strict Transport Security)**

```nginx
# Force HTTPS for 1 year (including all subdomains)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

**Preload HSTS (optional but recommended):**
1. Submit to [hstspreload.org](https://hstspreload.org/)
2. Browsers will ALWAYS enforce HTTPS (even on first visit)

---

### **2. Certificate Pinning (Advanced)**

```nginx
# Public Key Pins (HPKP) - WARNING: Can lock out users if misconfigured
# NOT recommended unless you fully understand the risks

# Better alternative: Certificate Transparency (CT)
add_header Expect-CT "max-age=86400, enforce" always;
```

---

### **3. TLS 1.3 Only (Modern Browsers)**

```nginx
# For maximum security (drops support for old browsers)
ssl_protocols TLSv1.3;
```

**Compatibility:**
- ✅ Chrome 70+, Firefox 63+, Safari 12.1+, Edge 79+
- ❌ IE 11, old Android browsers

---

## 🧪 **TESTING & VALIDATION**

### **Test 1: SSL Labs**

```bash
# Open in browser:
https://www.ssllabs.com/ssltest/analyze.html?d=seatrace.worldseafoodproducers.com

# Target: A+ rating
```

**Expected Results:**
- ✅ Certificate matches domain name
- ✅ TLS 1.2+ supported
- ✅ Strong ciphers only
- ✅ HSTS enabled

---

### **Test 2: Browser DevTools**

```javascript
// Open browser console on https://seatrace.worldseafoodproducers.com
// Check certificate details

// Chrome: Lock icon → Certificate → Details
// Firefox: Lock icon → Connection Secure → More Information
// Safari: Lock icon → Show Certificate

// Verify:
// - Issued to: seatrace.worldseafoodproducers.com (or *.worldseafoodproducers.com)
// - Issued by: Let's Encrypt Authority X3
// - Valid from/to: Current date + 90 days
```

---

### **Test 3: OpenSSL**

```bash
# Check certificate details
openssl s_client -connect seatrace.worldseafoodproducers.com:443 -servername seatrace.worldseafoodproducers.com

# Expected output:
# subject=CN = *.worldseafoodproducers.com
# issuer=C = US, O = Let's Encrypt, CN = R3
# Verify return code: 0 (ok)
```

---

### **Test 4: Postman Collection**

```bash
# Import SeaTrace Commons KPI Demo collection
# Run all requests

# Expected:
# ✅ All requests succeed (200, 429)
# ✅ NO SSL certificate errors
# ✅ HTTPS lock icon in Postman
```

---

## 📋 **PUBLIC vs PRIVATE CLASSIFICATION**

### **PUBLIC Files (SeaTrace-ODOO repo):**

```
✅ staging/.well-known/jwks.json               (PUBLIC keys only)
✅ scripts/jwks-export.cjs                     (Tool to generate JWKS)
✅ nginx/seatrace-api-portal.conf              (Nginx config - sanitized)
✅ docs/SSL_INFRASTRUCTURE.md                  (This guide)
✅ postman/collections/SeaTrace_Commons_KPI_Demo.postman_collection.json
```

### **PRIVATE Files (SeaTrace003 repo OR local only):**

```
🔒 keys/private.pem                            (Private signing key)
🔒 /etc/letsencrypt/live/.../privkey.pem       (SSL private key)
🔒 /etc/letsencrypt/cloudflare.ini             (API tokens)
🔒 .env                                        (Environment secrets)
```

### **NEVER COMMIT TO GIT:**
```
❌ private.pem
❌ privkey.pem
❌ *.key
❌ *.p12
❌ *.pfx
❌ cloudflare.ini
❌ API tokens
❌ Private keys of any kind
```

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment:**
- [ ] Backup current SSL certificate (if exists)
- [ ] Verify DNS records point to correct IP
- [ ] Test port 80/443 are open and accessible
- [ ] Backup Nginx configuration
- [ ] Create rollback plan

### **Deployment:**
- [ ] Install Certbot
- [ ] Generate Let's Encrypt certificate (wildcard or multi-domain)
- [ ] Update Nginx configuration with new cert paths
- [ ] Test Nginx config: `sudo nginx -t`
- [ ] Reload Nginx: `sudo systemctl reload nginx`
- [ ] Verify HTTPS works in browser (NO warnings)

### **Post-Deployment:**
- [ ] Test SSL Labs (target: A+ rating)
- [ ] Run Postman collection (all requests succeed)
- [ ] Verify JWKS endpoint: `https://seatrace.worldseafoodproducers.com/.well-known/jwks.json`
- [ ] Enable auto-renewal cron job
- [ ] Document certificate expiry date (90 days)
- [ ] Monitor logs for SSL errors

### **User Validation:**
- [ ] Users can access `https://seatrace.worldseafoodproducers.com` WITHOUT warnings
- [ ] NO "Your connection is not private" message
- [ ] Green lock icon in browser
- [ ] All Four Pillars (SeaSide, DeckSide, DockSide, MarketSide) accessible

---

## 🌊 **FOR THE COMMONS GOOD!**

**Expected Outcome:**
```
✅ https://seatrace.worldseafoodproducers.com
   → GREEN LOCK 🔒
   → NO WARNINGS
   → USERS TRUST THE SITE
```

**Certificate Details:**
```
Common Name: *.worldseafoodproducers.com
Subject Alternative Names:
  - worldseafoodproducers.com
  - *.worldseafoodproducers.com
Issuer: Let's Encrypt Authority X3
Valid: Oct 26, 2025 - Jan 24, 2026 (90 days)
```

**Classification:** PUBLIC-UNLIMITED (This guide)  
**FOR THE COMMONS GOOD!** 🌍🐟🚀

---

## 📞 **SUPPORT RESOURCES**

- **Let's Encrypt Docs:** https://letsencrypt.org/docs/
- **Certbot Docs:** https://certbot.eff.org/
- **SSL Labs Test:** https://www.ssllabs.com/ssltest/
- **Mozilla SSL Config Generator:** https://ssl-config.mozilla.org/
- **Cloudflare SSL/TLS:** https://developers.cloudflare.com/ssl/

**Next Steps:** Apply this fix, then continue with Postman demo practices! 🚀
