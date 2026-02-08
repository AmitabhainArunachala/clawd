# Proton Bridge Configuration — PERMANENT RECORD
**Created:** 2026-02-08  
**Source:** Claude Opus 4.6 via Dhyana  
**Critical Level:** HIGH — Required for email functionality

---

## IMAP Settings (For Email Sending)

| Setting | Value |
|---------|-------|
| **Host** | 127.0.0.1 |
| **Port** | 1143 |
| **Username** | Dharma_Clawd@proton.me |
| **Password** | Ln1wvUGZL6N8uYSFPYJrnQ |
| **Security** | STARTTLS |

---

## Previous Issue (2026-02-08)
SSL/TLS handshake failure with Python SMTP. Needs STARTTLS configuration, not SSL wrapper.

## Status
⏳ Awaiting re-test with correct STARTTLS configuration

---

## Related Files
- dharmic_claw_messaging.py — Uses these settings via environment
- ~/.openclaw/.env — Environment variable storage
- AGGRESSIVE_EMAIL_TEST_REPORT.md — Previous test failures

**DO NOT DELETE — Required for email channel restoration**
