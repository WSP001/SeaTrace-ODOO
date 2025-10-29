# 📧 SECTIGO CERTIFICATE REVOCATION REQUEST TEMPLATE
**URGENT: Certificate Revocation - Key Compromise**

---

## COPY-PASTE THIS INTO SECTIGO SUPPORT PORTAL OR EMAIL

**Subject:** URGENT Certificate Revocation Request - Key Compromise (Serial: d9b7b2690ecce57cd588b18abd020942)

**To:** Sectigo Support (support@sectigo.com) OR your Certificate Authority contact

**Priority:** URGENT

---

**Revocation Request Details:**

I am requesting immediate revocation of the following TLS certificate due to a **private key compromise**:

**Certificate Information:**
- Common Name (CN): www.worldseafoodproducers.com
- Subject Alternative Names (SANs):
  - www.worldseafoodproducers.com
  - worldseafoodproducers.com
- Certificate Authority: Sectigo Public Server Authentication CA DV R3.6
- Serial Number: **d9b7b2690ecce57cd588b18abd020942**
- Valid From: October 23, 2025
- Valid Until: October 23, 2026
- Fingerprint (SHA-256): [IF AVAILABLE - RUN: openssl x509 -in cert.crt -noout -fingerprint -sha256]

**Revocation Reason:**
**Key Compromise (Reason Code: 1)**

The private key associated with this certificate was exposed in a development context on October 28, 2025. As a precautionary security measure, I am requesting immediate revocation to prevent potential man-in-the-middle attacks.

**Incident Details:**
- Incident ID: INCIDENT_2025-10-28_TLS_EXPOSURE
- Date of Discovery: October 28, 2025
- Exposure Vector: Private key inadvertently exposed during development troubleshooting
- Remediation: New certificate has been generated with a new private key

**Required Actions:**

1. ✅ **Revoke certificate** with Serial Number: d9b7b2690ecce57cd588b18abd020942
2. ✅ **Reason Code:** Key Compromise (Code: 1)
3. ✅ **Effective Date:** Immediate (as of submission time)
4. ✅ **Update Certificate Revocation List (CRL)** to reflect this revocation
5. ✅ **Update OCSP responder** to show certificate status as "revoked"
6. ✅ **Provide confirmation** of revocation timestamp and CRL/OCSP status

**Verification Information:**

To verify my authority to revoke this certificate, I can provide:
- Original CSR (Certificate Signing Request)
- Domain validation proof (email/DNS record)
- Current private key (if required for verification - will send via secure channel ONLY)
- Account credentials for Sectigo portal

**Urgency:**

This is a **CRITICAL SECURITY INCIDENT**. I request this certificate be revoked within **1-2 hours** of this submission to minimize the window of potential exploitation.

**Confirmation Request:**

Please confirm:
1. Certificate has been successfully revoked
2. Revocation timestamp (date and time)
3. Certificate Revocation List (CRL) has been updated
4. OCSP responder status (verify with: `openssl ocsp -issuer sectigo_ca.crt -cert old_cert.crt -url http://ocsp.sectigo.com -resp_text`)

**New Certificate Request:**

I have already generated a new CSR with a new private key and will be requesting a replacement certificate immediately after this revocation is confirmed. Please expedite the issuance process given the security incident circumstances.

**Contact Information:**

- **Name:** Roberto [LAST_NAME]
- **Organization:** World Seafood Producers
- **Email:** [YOUR_EMAIL]
- **Phone:** [YOUR_PHONE] (available for immediate callback)
- **Sectigo Account ID:** [IF APPLICABLE]

**Supporting Documentation:**

I can provide the following supporting documentation if needed:
- Incident report (INCIDENT_2025-10-28_TLS_EXPOSURE.md)
- Timeline of key exposure discovery
- Remediation plan and new certificate generation proof

**Verification Commands (For Your Records):**

```bash
# Check current certificate status (BEFORE revocation)
openssl s_client -connect www.worldseafoodproducers.com:443 -servername www.worldseafoodproducers.com

# Verify certificate details
echo | openssl s_client -connect www.worldseafoodproducers.com:443 -servername www.worldseafoodproducers.com 2>/dev/null | openssl x509 -noout -serial -dates

# Expected output AFTER revocation:
# Serial Number: d9b7b2690ecce57cd588b18abd020942 [REVOKED]
```

**Acknowledgment:**

I understand that:
1. This revocation is permanent and cannot be undone
2. The certificate will appear in the CRL and OCSP as "revoked"
3. Browsers will display security warnings for the revoked certificate
4. I am responsible for installing a new valid certificate on my server

**Next Steps After Revocation:**

1. ✅ Confirm revocation with you (Sectigo)
2. ✅ Request new certificate with new CSR
3. ✅ Install new certificate on hosting (Netfirms)
4. ✅ Purge Cloudflare cache
5. ✅ Verify new certificate is working

Thank you for your immediate attention to this critical security matter.

---

**Submitted By:** Roberto [LAST_NAME]  
**Date:** October 28, 2025  
**Time:** [CURRENT_TIME] UTC  
**Ticket Priority:** URGENT - Key Compromise

---

**END OF REVOCATION REQUEST TEMPLATE**

---

## 📋 POST-SUBMISSION CHECKLIST

After submitting this revocation request:

- [ ] Receive revocation confirmation from Sectigo (within 1-2 hours)
- [ ] Verify CRL update: Download and check Certificate Revocation List
- [ ] Verify OCSP status: Test with `openssl ocsp` command
- [ ] Submit new CSR to Sectigo for replacement certificate
- [ ] Upload new certificate to Netfirms hosting
- [ ] Purge Cloudflare cache
- [ ] Verify new certificate with `openssl s_client -connect worldseafoodproducers.com:443`
- [ ] Update INCIDENT_2025-10-28_TLS_EXPOSURE.md with revocation timestamp

---

## 🔐 SECURITY REMINDER

**DO NOT EMAIL THE PRIVATE KEY!**

If Sectigo requests verification via private key:
- Use their secure upload portal
- Or provide fingerprint/hash instead: `openssl rsa -in old.key -pubout | openssl sha256`

The private key should ONLY be transmitted via secure encrypted channels.
