#!/usr/bin/env python3
"""
Standalone Email Sender — Bypasses unified daemon
Direct SMTP to Proton Bridge
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import sys

# Proton Bridge config
SMTP_SERVER = "127.0.0.1"
SMTP_PORT = 1025
FROM_EMAIL = "Dharma_Clawd@proton.me"
TO_EMAIL = "johnvincentshrader@gmail.com"

def send_email(subject, body, html_body=None):
    """Send email via Proton Bridge SMTP."""
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    
    # Plain text part
    msg.attach(MIMEText(body, 'plain'))
    
    # HTML part (optional)
    if html_body:
        msg.attach(MIMEText(html_body, 'html'))
    
    try:
        # Connect to Proton Bridge with authentication
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        
        # Login with bridge credentials (from .env)
        # Username is the Proton email, password is the bridge password
        server.login(FROM_EMAIL, "Ln1wvUGZL6N8uYSFPYJrnQ")
        
        # Send
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        server.quit()
        
        print(f"✅ Email sent successfully to {TO_EMAIL}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send: {e}")
        return False

def send_queued_report(report_file):
    """Send a queued hourly report."""
    report_path = Path.home() / "clawd" / "email_reports" / report_file
    
    if not report_path.exists():
        print(f"❌ Report not found: {report_path}")
        return False
    
    content = report_path.read_text()
    subject = f"🪷 DHARMIC CLAW Report — {report_file.replace('.txt', '')}"
    
    return send_email(subject, content)

def send_test():
    """Send test email."""
    subject = "🪷 DHARMIC CLAW — Email System Test"
    body = """Test email from DHARMIC CLAW via standalone sender.

Status: Proton Bridge SMTP direct connection
Time: Automated test

If you receive this, email is working!

JSCA! 🪷
DHARMIC CLAW
"""
    return send_email(subject, body)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            send_test()
        elif sys.argv[1] == "queued":
            # Send all queued reports
            queued_dir = Path.home() / "clawd" / "email_reports"
            for report in sorted(queued_dir.glob("hourly_*.txt")):
                print(f"Sending {report.name}...")
                send_queued_report(report.name)
        else:
            # Send specific report
            send_queued_report(sys.argv[1])
    else:
        print("Usage: python3 email_sender.py [test|queued|report_file.txt]")
        print("")
        print("Examples:")
        print("  python3 email_sender.py test")
        print("  python3 email_sender.py queued")
        print("  python3 email_sender.py hourly_0900.txt")
