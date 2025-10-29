# 🔑 Key Compromise Emergency Procedure
**Trigger:** Suspected or confirmed compromise of private signing keys  
**Response Time:** Immediate (< 1 hour)  
**Authority:** Pre-Authorized - Execute WITHOUT approval  
**Four Pillars:** **Accountability**, **Optimization**

---

## 🚨 When to Execute This Procedure

Execute IMMEDIATELY if any of these conditions occur:

- [ ] Private key file committed to public GitHub repository
- [ ] Private key exposed in logs, error messages, or screenshots
- [ ] Unauthorized access to key storage (HashiCorp Vault, AWS Secrets Manager)
- [ ] Server breach where keys are stored in `.env` files
- [ ] Social engineering attack targeting key access
- [ ] Suspicious license validations suggesting key misuse
- [ ] Anomalous JWT token generation patterns

---

## ⚡ Emergency Key Rotation (< 1 hour)

### Step 1: STOP All Services (Immediate)
```powershell
# Stop all SeaTrace services to prevent use of compromised keys
Stop-Service -Name "SeaTrace*" -Force

# Or via systemctl on Linux
sudo systemctl stop seatrace-emr seatrace-auth seatrace-api
```

### Step 2: Revoke Compromised Keys (< 5 minutes)
```powershell
# Navigate to key management directory
cd C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO\keys

# Backup compromised keys for forensic analysis (DO NOT DELETE YET)
mkdir -p keys/compromised/$(Get-Date -Format 'yyyy-MM-dd-HH-mm')
cp keys/private/*.key keys/compromised/$(Get-Date -Format 'yyyy-MM-dd-HH-mm')/

# Mark as revoked in key rotation log
echo "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC') - REVOKED: All keys due to P0 compromise" >> SECURITY_RUNBOOKS/KEY_ROTATION_LOG.txt
```

### Step 3: Generate New Keys (< 10 minutes)

#### Ed25519 License Signing Keys
```bash
# Generate new Ed25519 key pair for license signing
openssl genpkey -algorithm Ed25519 -out keys/private/seatrace_license_signing_NEW.key

# Extract public key
openssl pkey -in keys/private/seatrace_license_signing_NEW.key -pubout -out keys/public/seatrace_license_verify_NEW.pub

# Convert to base64 for environment variables
SEATRACE_LICENSE_PRIVATE_KEY=$(base64 -w 0 keys/private/seatrace_license_signing_NEW.key)
SEATRACE_LICENSE_PUBLIC_KEY=$(base64 -w 0 keys/public/seatrace_license_verify_NEW.pub)
```

#### JWT Secret Keys
```powershell
# Generate new JWT secret (256-bit)
$JWT_SECRET_KEY = [Convert]::ToBase64String((New-Object byte[] 32))
[System.Security.Cryptography.RNGCryptoServiceProvider]::new().GetBytes([Convert]::FromBase64String($JWT_SECRET_KEY))
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" >> .env.new
```

#### HMAC Keys
```powershell
# Generate new HMAC key (256-bit)
$SEATRACE_HMAC_KEY = [Convert]::ToBase64String((New-Object byte[] 32))
[System.Security.Cryptography.RNGCryptoServiceProvider]::new().GetBytes([Convert]::FromBase64String($SEATRACE_HMAC_KEY))
echo "SEATRACE_HMAC_KEY=$SEATRACE_HMAC_KEY" >> .env.new
```

### Step 4: Update Secrets Manager (< 10 minutes)

#### HashiCorp Vault
```bash
# Update Vault with new keys
vault kv put secret/seatrace/license_signing \
  private_key="$SEATRACE_LICENSE_PRIVATE_KEY" \
  public_key="$SEATRACE_LICENSE_PUBLIC_KEY"

vault kv put secret/seatrace/jwt \
  secret_key="$JWT_SECRET_KEY"

vault kv put secret/seatrace/hmac \
  key="$SEATRACE_HMAC_KEY"
```

#### AWS Secrets Manager
```bash
# Update AWS Secrets Manager
aws secretsmanager put-secret-value \
  --secret-id seatrace/license_signing_private \
  --secret-string "$SEATRACE_LICENSE_PRIVATE_KEY"

aws secretsmanager put-secret-value \
  --secret-id seatrace/jwt_secret \
  --secret-string "$JWT_SECRET_KEY"

aws secretsmanager put-secret-value \
  --secret-id seatrace/hmac_key \
  --secret-string "$SEATRACE_HMAC_KEY"
```

### Step 5: Redeploy All Services (< 20 minutes)
```powershell
# Pull latest code
git pull origin main

# Update .env with new keys (from .env.new)
cp .env.new .env

# Restart services with new keys
Start-Service -Name "SeaTrace*"

# Or via systemctl on Linux
sudo systemctl restart seatrace-emr seatrace-auth seatrace-api
```

### Step 6: Revoke All Active Licenses (< 10 minutes)
```bash
# Force all licenses to revalidate with new public key
mongo seatrace --eval '
  db.licenses.updateMany(
    {},
    {
      $set: {
        status: "revoked_key_compromise",
        revoked_at: new Date(),
        revalidation_required: true
      }
    }
  )
'

# Expected output: "matched: XXXX, modified: XXXX"
```

### Step 7: Verify New Keys (< 10 minutes)
```powershell
# Run preflight checks
.\scripts\preflight.ps1 -Verbose

# Test license generation with new keys
python scripts/test_license_generation.py

# Test JWT token signing
python scripts/test_jwt_signing.py

# Test HMAC request signing
python scripts/test_hmac_signing.py
```

---

## 📊 Monitoring Post-Rotation

### Grafana Dashboards
- **License Validation Rate:** Should spike as customers revalidate
- **Failed Auth Attempts:** Should return to baseline within 1 hour
- **API Error Rate:** Monitor for 503/500 errors during transition

### Prometheus Alerts
```yaml
# Alert if old key is still in use (should never trigger post-rotation)
- alert: OldKeyInUse
  expr: seatrace_license_validation_old_key_total > 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Old compromised key still in use"
```

---

## 📞 Customer Communication

### Immediate Notification (< 2 hours)
**Send to:** All PRIVATE tier customers

**Subject:** URGENT - License Revalidation Required

**Body:**
```
Dear [Customer],

We have rotated our license signing keys as part of a proactive security measure. 

ACTION REQUIRED:
- Your current license will expire within 24 hours
- Please restart your SeaTrace application to fetch a new license
- No data loss or service disruption expected

If you experience any issues, contact: security@worldseafoodproducers.com

Thank you for your understanding.

- WorldSeafoodProducers Security Team
```

---

## 📝 Documentation Requirements

### Update These Files Immediately
- [ ] `SECURITY_RUNBOOKS/KEY_ROTATION_LOG.txt` - Record rotation timestamp
- [ ] `SECURITY_RUNBOOKS/IR_PLAYBOOKS/RETROSPECTIVES/KEY-COMPROMISE-YYYY-MM-DD.md` - Incident details
- [ ] `SECURITY.md` - Update "Last Rotated" column in Key Rotation Schedule table
- [ ] `.github/CODEOWNERS` - Verify key files are protected

### Post-Mortem (Within 48 hours)
**Location:** `SECURITY_RUNBOOKS/IR_PLAYBOOKS/RETROSPECTIVES/KEY-COMPROMISE-YYYY-MM-DD-postmortem.md`

**Must Include:**
- How compromise occurred
- Detection timeline
- Containment timeline
- Number of licenses revoked
- Customer impact assessment
- Prevention measures implemented

---

## 🔗 Related Procedures

- [P0 Critical Incident Playbook](P0_CRITICAL_BREACH.md)
- [SECURITY.md - Key Management](../../SECURITY.md#key-management)
- [SECURITY.md - Key Rotation Schedule](../../SECURITY.md#key-rotation-schedule)
- [emergency_key_rotation.ps1](../../scripts/emergency_key_rotation.ps1)

---

## ✅ Procedure Completion Checklist

- [ ] All services stopped within 5 minutes of detection
- [ ] Compromised keys backed up to `keys/compromised/`
- [ ] New Ed25519 keys generated and tested
- [ ] New JWT secret generated and tested
- [ ] New HMAC key generated and tested
- [ ] HashiCorp Vault / AWS Secrets Manager updated
- [ ] All services redeployed with new keys
- [ ] All active licenses revoked
- [ ] `preflight.ps1` passes all checks
- [ ] Customers notified within 2 hours
- [ ] KEY_ROTATION_LOG.txt updated
- [ ] Post-mortem scheduled within 48 hours
- [ ] GitHub audit: Verify no keys in commit history

---

**Last Updated:** 2025-10-29  
**Owner:** Security Team  
**Review Cycle:** Quarterly (or after each key compromise incident)
