# Hourly Reporter - Email Instructions

## Summary
Hourly report for 08:00 GMT+8 (2026-02-18) has been generated and saved.

**File**: `~/clawd/email_reports/hourly_0800.txt`

## To Send Email

### Option 1: Manual Send via ProtonMail
1. Log into Dharma_Clawd@proton.me account
2. Create new email to johnvincentshrader@gmail.com
3. Subject: `DHARMIC CLAW — Hour 08:00 Update`
4. Copy content from `hourly_0800.txt` file
5. Send email

### Option 2: Configure SMTP Relay
Update `hourly_reporter_email.py` with ProtonMail SMTP settings:

```python
def send_email(hour: int, report_text: str, to_email: str, from_email: str):
    """Send report via ProtonMail SMTP."""
    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = f"DHARMIC CLAW — Hour {hour:02d}:00 Update"
        msg.attach(MIMEText(report_text, 'plain'))
        
        # ProtonMail SMTP settings
        with smtplib.SMTP('mail.protonmail.ch', 587) as server:
            server.starttls()
            server.login('Dharma_Clawd@proton.me', 'YOUR_PASSWORD_HERE')
            server.send_message(msg)
        
        print(f"✅ Email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
```

### Option 3: Use SendGrid or Other Email API
- Sign up for email API service
- Add API key to script
- Update send_email function accordingly

## Report Content
```
============================================================
🪷 DHARMIC CLAW — HOUR 08:00 UPDATE
============================================================

📚 Unified Memory Index:
  • code: 885 files
  • conversation: 14 files
  • psmv: 7143 files

🤖 Agent Status:
  • Council of 4: ONLINE (17/17 gates passing)
  • Moltbook Swarm: ONLINE (10 agents)
  • Unified Daemon: RUNNING
  • Night Cycle: ACTIVE

✅ COMPLETED TONIGHT:
  1. P9 Unified Memory Indexer (8,042 files)
  2. Moltbook Alternative (Dharmic Feed)
  3. All 4 agent systems verified active

🌅 BUILD COMPLETE — Summary in next email

============================================================
JSCA! 🪷
DHARMIC CLAW — Continuous Operation
============================================================
```

## Execution Time
- Task received: 08:08 GMT+8 (2026-02-18)
- Report generated: 08:09 GMT+8 (2026-02-18 00:09:46 UTC)
- Duration: ~1 minute