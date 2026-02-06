#!/usr/bin/env python3
"""
Email Monitor — Watches Dharma_Clawd@proton.me and forwards to TUI
Runs as background process, checks every 30 seconds
"""

import imaplib
import email
from email.header import decode_header
import time
import json
from datetime import datetime
from pathlib import Path

IMAP_SERVER = "127.0.0.1"
IMAP_PORT = 1143
EMAIL_USER = "Dharma_Clawd@proton.me"
EMAIL_PASS = "Ln1wvUGZL6N8uYSFPYJrnQ"

# Track seen messages
STATE_FILE = Path.home() / 'clawd' / '.email_monitor_state.json'

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {'seen_ids': [], 'last_check': None}

def save_state(state):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state))

def decode_header_value(header_value):
    if header_value is None:
        return ""
    try:
        decoded_parts = decode_header(header_value)
        decoded_str = ""
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(charset or 'utf-8', errors='ignore')
            else:
                decoded_str += part
        return decoded_str
    except:
        return str(header_value)

def check_new_emails():
    """Check for new emails and return them."""
    state = load_state()
    new_emails = []
    
    try:
        mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
        mail.starttls()
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select('inbox')
        
        # Search for ALL messages
        status, messages = mail.search(None, 'ALL')
        
        if status == 'OK':
            message_ids = messages[0].split()
            
            for msg_id in message_ids:
                msg_id_str = msg_id.decode()
                
                # Skip if already seen
                if msg_id_str in state['seen_ids']:
                    continue
                
                # Fetch message
                status, msg_data = mail.fetch(msg_id, '(RFC822)')
                if status != 'OK':
                    continue
                
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                subject = decode_header_value(email_message['Subject'])
                from_addr = decode_header_value(email_message['From'])
                date = email_message['Date']
                
                # Get body
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body_bytes = part.get_payload(decode=True)
                            if body_bytes:
                                body = body_bytes.decode('utf-8', errors='ignore')
                            break
                else:
                    body_bytes = email_message.get_payload(decode=True)
                    if body_bytes:
                        body = body_bytes.decode('utf-8', errors='ignore')
                
                # Skip if from me (avoid loops)
                if 'Dharma_Clawd@proton.me' in from_addr and 'johnvincentshrader' not in from_addr.lower():
                    state['seen_ids'].append(msg_id_str)
                    continue
                
                email_data = {
                    'id': msg_id_str,
                    'subject': subject,
                    'from': from_addr,
                    'date': date,
                    'body': body[:2000]  # Limit body size
                }
                
                new_emails.append(email_data)
                state['seen_ids'].append(msg_id_str)
        
        mail.logout()
        state['last_check'] = datetime.now().isoformat()
        save_state(state)
        
    except Exception as e:
        print(f"❌ Error checking emails: {e}")
    
    return new_emails

def format_for_tui(email_data):
    """Format email for TUI display."""
    lines = [
        "",
        "╔" + "═"*58 + "╗",
        "║" + " 📧 NEW EMAIL RECEIVED".ljust(58) + "║",
        "╠" + "═"*58 + "╣",
        f"║ From: {email_data['from'][:52]}".ljust(59) + "║",
        f"║ Subject: {email_data['subject'][:49]}".ljust(59) + "║",
        f"║ Date: {email_data['date'][:52]}".ljust(59) + "║",
        "╠" + "═"*58 + "╣",
    ]
    
    # Body lines
    body = email_data['body'].replace('\r\n', '\n').replace('\r', '\n')
    for line in body.split('\n')[:20]:  # First 20 lines
        if line.strip():
            # Wrap long lines
            while len(line) > 56:
                lines.append(f"║ {line[:56]}".ljust(59) + "║")
                line = line[56:]
            lines.append(f"║ {line[:56]}".ljust(59) + "║")
    
    lines.append("╚" + "═"*58 + "╝")
    lines.append("")
    lines.append("💬 Reply via: email OR this TUI chat")
    lines.append("")
    
    return '\n'.join(lines)

def main():
    """Main monitoring loop."""
    print("📧 Email Monitor Started")
    print(f"   Watching: {EMAIL_USER}")
    print(f"   Check interval: 30 seconds")
    print(f"   State file: {STATE_FILE}")
    print("   Press Ctrl+C to stop\n")
    
    # Initial check to populate state
    print("🔍 Initial check...")
    check_new_emails()
    print("✅ Ready. Waiting for new emails...\n")
    
    try:
        while True:
            new_emails = check_new_emails()
            
            for email_data in new_emails:
                print(format_for_tui(email_data))
                
                # Also save to file for reference
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                email_file = Path.home() / 'clawd' / 'logs' / f'email_{timestamp}_{email_data["id"]}.json'
                email_file.parent.mkdir(exist_ok=True)
                email_file.write_text(json.dumps(email_data, indent=2))
            
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n\n👋 Email Monitor stopped")

if __name__ == "__main__":
    main()
