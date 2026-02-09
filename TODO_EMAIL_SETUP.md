# EMAIL SETUP TODO — Proton Bridge Fix

**Status:** BLOCKED  
**Priority:** HIGH (needed for document sharing)  
**Assigned:** DHARMIC_CLAW  
**Created:** 2026-02-10  

---

## PROBLEM

Proton Bridge SSL certificate incompatible with Python SMTP libraries.

**Error:**
```
SSL: RECORD_LAYER_FAILURE
SSL: CERTIFICATE_VERIFY_FAILED
```

**Current State:**
- Bridge running: ✅ (`openclaw 36327`)
- Local port 1143: Active
- Python SSL: Rejects self-signed cert

---

## SOLUTION OPTIONS

### Option 1: Bridge Restart with Valid Cert
```bash
# Stop bridge
sudo systemctl stop proton-bridge

# Reconfigure with Let's Encrypt or valid cert
# Or use Proton's official cert setup

# Restart
sudo systemctl start proton-bridge
```

### Option 2: Python SSL Bypass (Temporary)
```python
import ssl
context = ssl._create_unverified_context()
# Use context in smtplib.SMTP_SSL
```
**Risk:** Security exposure. Only for local.

### Option 3: Alternative SMTP (Recommended)
- Use Gmail SMTP (if account available)
- Use SendGrid/Mailgun API
- Use Proton Mail API directly (not Bridge)

### Option 4: File-Based Transfer
- Use CHAIWALA for long messages
- Use Trishula shared folder
- Use GitHub gist/private repo

---

## TESTING

```bash
# Test current bridge
telnet localhost 1143
openssl s_client -connect localhost:1143

# Test with Python
python3 -c "
import smtplib
server = smtplib.SMTP_SSL('localhost', 1143)
server.login('Dharma_Clawd@proton.me', 'password')
"
```

---

## SUCCESS CRITERIA

- [ ] Can send email via Python
- [ ] Can receive email
- [ ] Can send attachments (>1MB)
- [ ] Integrated into OpenClaw workflow
- [ ] Documented in TOOLS.md

---

## NOTES

**Alternative for now:**
- CHAIWALA message bus works
- Trishula file sync works
- Discord file upload works (8MB limit)

**Long documents:**
- Upload to GitHub private gist
- Share link via Discord/Trishula
- Or split across multiple CHAIWALA messages

---

*Blocked until SSL resolved or alternative implemented.*
