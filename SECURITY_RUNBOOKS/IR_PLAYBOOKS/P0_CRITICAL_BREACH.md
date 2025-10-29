# 🚨 P0 - Critical Incident Response Playbook
**Severity:** Critical (Active breach, key compromise, data exfiltration)  
**Response Time:** Immediate (< 15 minutes)  
**Escalation:** CEO, CTO, Security Lead, Legal  
**Four Pillars:** **Accountability**, **Optimization**

---

## 📋 Incident Classification

**P0 triggers include:**
- Active security breach or intrusion
- Private key compromise (Ed25519, JWT, HMAC)
- Customer PII data exfiltration
- Ransomware or destructive malware
- Complete service outage due to security incident
- Real-time exploitation of critical vulnerability

---

## ⚡ Immediate Actions (< 15 minutes)

### 1. Detect & Alert
- [ ] PagerDuty alert sent to on-call security engineer
- [ ] Prometheus/Grafana anomaly detected (failed auth spike, unusual API patterns)
- [ ] Manual report received (customer, internal team, security researcher)
- [ ] Record incident timestamp: `____________________`

### 2. Assemble War Room
- [ ] Create dedicated Slack channel: `#incident-p0-YYYY-MM-DD-HH-MM`
- [ ] Page: CEO, CTO, Security Lead, SRE on-call
- [ ] Join video conference: `https://meet.worldseafoodproducers.com/war-room`
- [ ] Assign Incident Commander: `____________________`

### 3. Contain Immediately (No Approval Required - Pre-Authorized)
- [ ] **If key compromise suspected:** Rotate all keys NOW
  ```powershell
  # Emergency key rotation
  cd C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO\scripts
  .\emergency_key_rotation.ps1 -Severity P0
  ```
- [ ] **If database breach:** Isolate affected database instance
  ```bash
  # Revoke all database access
  REVOKE ALL PRIVILEGES ON *.* FROM 'seatrace_app'@'%';
  FLUSH PRIVILEGES;
  ```
- [ ] **If API compromise:** Enable rate limiting to 1 req/min for all endpoints
  ```bash
  # Emergency rate limit via Cloudflare
  curl -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/rate_limits" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    --data '{"threshold":1,"period":60}'
  ```
- [ ] **If server compromise:** Take affected servers offline
  ```powershell
  # Stop all SeaTrace services
  Stop-Service -Name "SeaTrace*" -Force
  ```

---

## 🔍 Investigate (< 1 hour)

### 4. Determine Scope
- [ ] Review Grafana dashboards: `https://grafana.worldseafoodproducers.com`
- [ ] Check Prometheus alerts for anomalies
- [ ] Query audit logs:
  ```bash
  # Check last 1000 failed authentication attempts
  mongo seatrace --eval 'db.audit_logs.find({event:"auth_failure"}).sort({timestamp:-1}).limit(1000)'
  ```
- [ ] Identify affected systems: `____________________`
- [ ] Identify compromised data: `____________________`
- [ ] Estimate number of affected customers: `____________________`

### 5. Evidence Preservation
- [ ] Snapshot affected servers (do NOT shut down yet - preserve memory)
  ```bash
  # AWS EC2 snapshot
  aws ec2 create-snapshot --volume-id vol-xxxxx --description "P0-incident-YYYY-MM-DD"
  ```
- [ ] Export audit logs to secure location
  ```powershell
  mongoexport --db=seatrace --collection=audit_logs --out="P0-audit-$(Get-Date -Format 'yyyy-MM-dd-HH-mm').json"
  ```
- [ ] Save network traffic captures (if available)
- [ ] Document timeline in `SECURITY_RUNBOOKS/IR_PLAYBOOKS/RETROSPECTIVES/P0-YYYY-MM-DD-timeline.md`

---

## 🛠️ Remediate (< 4 hours)

### 6. Apply Fixes
- [ ] **If key compromise:**
  - [ ] Generate new Ed25519 signing keys
  - [ ] Generate new JWT secrets
  - [ ] Generate new HMAC keys
  - [ ] Update HashiCorp Vault
  - [ ] Redeploy all services with new keys
  - [ ] Revoke all active licenses (force revalidation)
- [ ] **If vulnerability exploitation:**
  - [ ] Apply security patch
  - [ ] Redeploy affected services
  - [ ] Run vulnerability scan to confirm fix
- [ ] **If malware detected:**
  - [ ] Isolate infected systems
  - [ ] Restore from clean backup
  - [ ] Run full malware scan on all systems

### 7. Validate Remediation
- [ ] Run `preflight.ps1` on all systems
- [ ] Verify no anomalies in Grafana (return to baseline)
- [ ] Test end-to-end: SeaSide → DeckSide → DockSide → MarketSide
- [ ] Confirm all security controls active

---

## 📢 Communicate (< 24 hours)

### 8. Internal Communication
- [ ] Update `#incident-p0-YYYY-MM-DD-HH-MM` Slack channel every 30 minutes
- [ ] Send status email to leadership:
  ```
  Subject: P0 Incident Update - [CONTAINED / INVESTIGATING / REMEDIATED]
  
  Timeline: Detected at XX:XX UTC, contained by XX:XX UTC
  Scope: [Brief description]
  Impact: [Customer count, data types, systems affected]
  Status: [Current status]
  Next Update: [Timestamp]
  ```

### 9. Customer Communication (if applicable)
- [ ] Draft customer notification (Legal approval required)
- [ ] Send to affected customers within 24 hours
- [ ] Update status page: `https://status.worldseafoodproducers.com`
- [ ] Prepare FAQ for support team

### 10. Regulatory Reporting (if PII breach)
- [ ] Notify GDPR DPA within 72 hours (if EU customers affected)
- [ ] Notify state AGs (if US customers affected)
- [ ] File SEC 8-K (if material impact to investors)

---

## 📝 Document (< 1 week)

### 11. Post-Mortem Report
**Location:** `SECURITY_RUNBOOKS/IR_PLAYBOOKS/RETROSPECTIVES/P0-YYYY-MM-DD-postmortem.md`

**Template:**
```markdown
# P0 Post-Mortem: [Incident Title]

**Date:** YYYY-MM-DD  
**Incident Commander:** [Name]  
**Severity:** P0 - Critical  
**Duration:** XX hours XX minutes  

## Timeline
- XX:XX UTC - Incident detected
- XX:XX UTC - War room assembled
- XX:XX UTC - Containment complete
- XX:XX UTC - Remediation complete
- XX:XX UTC - Incident closed

## Root Cause
[Detailed explanation]

## Impact
- **Customers Affected:** [Count]
- **Data Compromised:** [Types]
- **Downtime:** [Duration]
- **Revenue Impact:** $[Amount]

## What Went Well
- [List]

## What Went Wrong
- [List]

## Action Items (Four Pillars: Accountability)
- [ ] [Improvement 1] - Owner: [Name] - Due: [Date]
- [ ] [Improvement 2] - Owner: [Name] - Due: [Date]

## Prevention
[Long-term fixes to prevent recurrence]

## Lessons Learned
[Key takeaways]
```

### 12. Update Runbooks
- [ ] Add new detection signatures to Prometheus/Grafana
- [ ] Update pre-commit hooks if relevant
- [ ] Update `preflight.ps1` with new checks
- [ ] Schedule follow-up review: 30 days post-incident

---

## 🔗 Related Documents

- [P1 High Severity Playbook](P1_HIGH_VULNERABILITY.md)
- [Key Compromise Procedure](KEY_COMPROMISE_PROCEDURE.md)
- [SECURITY.md - Incident Response](../../SECURITY.md#incident-response)
- [Continuous Cross-Pillar Safeguards](../../SECURITY.md#continuous-cross-pillar-safeguards)

---

## ✅ Incident Closure Checklist

- [ ] All containment actions complete
- [ ] All remediation actions complete
- [ ] Post-mortem report published
- [ ] Customers notified (if applicable)
- [ ] Regulatory reporting complete (if applicable)
- [ ] Action items assigned with owners and due dates
- [ ] 30-day follow-up review scheduled
- [ ] Incident retrospective logged in `RETROSPECTIVES/`
- [ ] Update key rotation log (if keys rotated)
- [ ] Archive incident Slack channel

---

**Last Updated:** 2025-10-29  
**Owner:** Security Team  
**Review Cycle:** After each P0 incident
